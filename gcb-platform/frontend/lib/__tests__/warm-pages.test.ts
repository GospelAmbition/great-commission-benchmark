/** @jest-environment node */
import { createServer, Server, ServerResponse } from "node:http";
import { warmPages, createWarmJobStarter } from "../warm-pages";

let server: Server;
let baseUrl: string;
beforeEach(async () => {
  server = createServer();
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Missing test server address");
  baseUrl = `http://127.0.0.1:${address.port}`;
});
afterEach(async () => {
  server.closeAllConnections();
  await new Promise<void>((resolve) => server.close(() => resolve()));
});

it("does not admit the next batch when only streamed response headers have arrived", async () => {
  const responses: ServerResponse[] = [];
  const visited: string[] = [];
  let firstBatchReady!: () => void;
  const ready = new Promise<void>((resolve) => { firstBatchReady = resolve; });
  server.on("request", (request, response) => {
    visited.push(request.url!);
    response.writeHead(200, { "Content-Type": "text/html" });
    response.write("shell");
    if (request.url === "/third") response.end("complete");
    else {
      responses.push(response);
      if (responses.length === 2) firstBatchReady();
    }
  });
  const result = warmPages(baseUrl, ["/first", "/second", "/third"], { concurrency: 2 });
  await ready;
  // Give fetch time to receive the flushed headers while both bodies stay open.
  await new Promise((resolve) => setTimeout(resolve, 50));
  expect(visited).toEqual(["/first", "/second"]);
  responses[0].end("complete");
  await new Promise((resolve) => setTimeout(resolve, 20));
  expect(visited).toEqual(["/first", "/second"]);
  responses[1].end("complete");
  await expect(result).resolves.toEqual({ ok: 3, failed: 0, errors: [] });
  expect(visited).toEqual(["/first", "/second", "/third"]);
});

it("aborts a stalled streaming body and continues to the next batch", async () => {
  let stalledClosed!: () => void;
  const closed = new Promise<void>((resolve) => { stalledClosed = resolve; });
  server.on("request", (request, response) => {
    if (request.url === "/stalled") {
      response.writeHead(200);
      response.write("shell");
      response.on("close", stalledClosed);
    } else response.end("complete");
  });
  const result = await warmPages(baseUrl, ["/stalled", "/healthy"], { concurrency: 1, timeoutMs: 100 });
  expect(result.ok).toBe(1);
  expect(result.failed).toBe(1);
  expect(result.errors[0]).toMatch(/^\/stalled:/);
  await closed;
});

it("counts non-success responses as failures", async () => {
  server.on("request", (_request, response) => { response.writeHead(503); response.end(); });
  await expect(warmPages(baseUrl, ["/unavailable"])).resolves.toEqual({
    ok: 0, failed: 1, errors: ["/unavailable: HTTP 503"],
  });
});

it("rejects overlapping jobs and releases the guard after a failure", async () => {
  const failed = jest.fn();
  const start = createWarmJobStarter(failed);
  let reject!: (error: Error) => void;
  const job = new Promise<void>((_resolve, rejectJob) => { reject = rejectJob; });
  const duplicate = jest.fn(async () => {});
  expect(start(() => job)).toBe(true);
  expect(start(duplicate)).toBe(false);
  reject(new Error("failed job"));
  await new Promise((resolve) => setImmediate(resolve));
  expect(failed).toHaveBeenCalledWith(new Error("failed job"));
  expect(duplicate).not.toHaveBeenCalled();
  expect(start(duplicate)).toBe(true);
  await new Promise((resolve) => setImmediate(resolve));
  expect(duplicate).toHaveBeenCalledTimes(1);
});
