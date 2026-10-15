/** Consume each streamed render before admitting another batch of warm-up work. */
export async function warmPages(
  baseUrl: string,
  paths: string[],
  { concurrency = 2, timeoutMs = 15_000 } = {}
): Promise<{ ok: number; failed: number; errors: string[] }> {
  if (!Number.isInteger(concurrency) || concurrency < 1) {
    throw new Error("Warm concurrency must be a positive integer");
  }
  let ok = 0;
  let failed = 0;
  const errors: string[] = [];

  for (let i = 0; i < paths.length; i += concurrency) {
    const batch = paths.slice(i, i + concurrency);
    const results = await Promise.allSettled(batch.map(async (path) => {
      const controller = new AbortController();
      // Keep the deadline active through body consumption, not just headers.
      const deadline = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const response = await fetch(`${baseUrl.replace(/\/$/, "")}${path || "/"}`, {
          headers: { "User-Agent": "GCB-Warm/1.0" },
          signal: controller.signal,
        });
        if (!response.ok) {
          await response.body?.cancel();
          throw new Error(`HTTP ${response.status}`);
        }
        const reader = response.body?.getReader();
        if (reader) {
          try {
            while (!(await reader.read()).done) {
              // Discard chunks without retaining hundreds of rendered pages in memory.
            }
          } finally {
            reader.releaseLock();
          }
        }
      } finally {
        clearTimeout(deadline);
      }
    }));
    results.forEach((result, index) => {
      if (result.status === "fulfilled") {
        ok++;
      } else {
        failed++;
        if (errors.length < 10) errors.push(`${batch[index]}: ${result.reason?.message ?? "Request failed"}`);
      }
    });
  }
  return { ok, failed, errors };
}

/** One warm-up job per server process; authorization remains the route's responsibility. */
export function createWarmJobStarter(onError: (error: unknown) => void) {
  let running = false;
  return (job: () => Promise<void>): boolean => {
    if (running) return false;
    running = true;
    void Promise.resolve().then(job).catch(onError).finally(() => { running = false; });
    return true;
  };
}
