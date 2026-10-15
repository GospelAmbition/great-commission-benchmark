/** @jest-environment node */
import { NextRequest } from "next/server";
import { GET } from "../route";
import { warmPages } from "@/lib/warm-pages";

jest.mock("@/lib/api", () => ({ API_URL: "https://backend.example" }));
jest.mock("@/lib/warm-pages", () => ({
  ...jest.requireActual("@/lib/warm-pages"), warmPages: jest.fn(),
}));

const originalSecret = process.env.WARM_SECRET;
afterEach(() => {
  if (originalSecret === undefined) delete process.env.WARM_SECRET;
  else process.env.WARM_SECRET = originalSecret;
  jest.restoreAllMocks();
});

it("requires configuration and authentication before starting any work", async () => {
  const fetchMock = jest.spyOn(global, "fetch");
  delete process.env.WARM_SECRET;
  expect((await GET(new NextRequest("https://frontend.example/api/warm"))).status).toBe(503);
  process.env.WARM_SECRET = "unit-test-secret";
  expect((await GET(new NextRequest("https://frontend.example/api/warm?secret=wrong"))).status).toBe(401);
  expect(fetchMock).not.toHaveBeenCalled();
  expect(warmPages).not.toHaveBeenCalled();
});

it("accepts existing auth formats but starts only one job while it is running", async () => {
  process.env.WARM_SECRET = "unit-test-secret";
  jest.spyOn(global, "fetch").mockImplementation(async () => Response.json({ entries: [], categories: [], items: [] }));
  jest.spyOn(console, "log").mockImplementation(() => {});
  let finish!: (value: { ok: number; failed: number; errors: string[] }) => void;
  jest.mocked(warmPages).mockReturnValue(new Promise((resolve) => { finish = resolve; }));
  const first = await GET(new NextRequest("https://frontend.example/api/warm", { headers: { authorization: "Bearer unit-test-secret" } }));
  const second = await GET(new NextRequest("https://frontend.example/api/warm?secret=unit-test-secret"));
  expect(first.status).toBe(202);
  expect(await first.json()).toMatchObject({ status: "started" });
  expect(await second.json()).toMatchObject({ status: "already_running" });
  await new Promise((resolve) => setImmediate(resolve));
  expect(warmPages).toHaveBeenCalledTimes(1);
  expect(warmPages).toHaveBeenCalledWith("https://frontend.example", expect.arrayContaining(["", "/leaderboard"]));
  finish({ ok: 16, failed: 0, errors: [] });
  await new Promise((resolve) => setImmediate(resolve));
});
