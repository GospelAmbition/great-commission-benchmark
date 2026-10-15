/** @jest-environment node */

import { createServer, type Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { ApiClient } from '@/lib/api';

describe('public API read deadline', () => {
  let server: Server;

  afterEach(async () => {
    if (server) {
      // Also close the stalled response if the regression makes the test fail.
      server.closeAllConnections();
      await new Promise<void>((resolve, reject) => {
        server.close((error) => error ? reject(error) : resolve());
      });
    }
  });

  it('aborts an unfinished JSON body after receiving successful response headers', async () => {
    let headersSent!: () => void;
    const receivedHeaders = new Promise<void>((resolve) => { headersSent = resolve; });
    server = createServer((_request, response) => {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.write('{"total_models_tested":');
      headersSent();
      // Deliberately never complete the body: a fetch-only timeout is insufficient.
    });
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
    const { port } = server.address() as AddressInfo;
    const client = new ApiClient(`http://127.0.0.1:${port}`);
    const timeoutSpy = jest.spyOn(AbortSignal, 'timeout');
    try {
      const result = client.getStats();
      const outcome = result.then(
        () => 'unexpected success',
        (error: Error) => error.name,
      );
      await receivedHeaders;
      expect(timeoutSpy).toHaveBeenCalledWith(10_000);
      // Node fetch versions expose body cancellation as AbortError or TimeoutError.
      expect(['AbortError', 'TimeoutError']).toContain(await outcome);
      const deadline = timeoutSpy.mock.results[0].value as AbortSignal;
      expect(deadline.aborted).toBe(true);
      expect(deadline.reason.name).toBe('TimeoutError');
    } finally {
      timeoutSpy.mockRestore();
    }
  }, 15_000);
});
