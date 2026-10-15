/**
 * Railway start script: runs Next.js then triggers /api/warm after the server is ready.
 * Set WARM_SECRET in Railway (and optionally WARM_DELAY_MS). If WARM_SECRET is unset, warm is skipped.
 */
const { spawn } = require("child_process");
const http = require("http");

const PORT = process.env.PORT || 3000;
const WARM_SECRET = process.env.WARM_SECRET;
const WARM_DELAY_MS = parseInt(process.env.WARM_DELAY_MS || "45000", 10);

function waitForServer() {
  return new Promise((resolve) => {
    const attempt = () => {
      let finished = false;
      const retry = () => {
        if (finished) return;
        finished = true;
        setTimeout(attempt, 3000);
      };
      const req = http.get(`http://127.0.0.1:${PORT}/`, (res) => {
        // Drain the streaming page before declaring readiness and starting more work.
        res.resume();
        res.on("end", () => {
          if (res.statusCode !== 200) return retry();
          if (finished) return;
          finished = true;
          resolve(true);
        });
        res.on("error", retry);
      });
      req.on("error", retry);
      req.setTimeout(15000, () => {
        req.destroy();
        retry();
      });
    };
    setTimeout(() => attempt(), WARM_DELAY_MS);
  });
}

function warm() {
  if (!WARM_SECRET) {
    console.log("[warm] WARM_SECRET not set, skipping warm-up");
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const url = `http://127.0.0.1:${PORT}/api/warm`;
    const req = http.get(url, { headers: { Authorization: `Bearer ${WARM_SECRET}` } }, (res) => {
      let body = "";
      res.on("data", (c) => (body += c));
      res.on("end", () => {
        if (res.statusCode === 202) {
          console.log("[warm] started in background (pages will prime shortly)");
        } else {
          try {
            const j = JSON.parse(body);
            if (j.warmed != null) {
              console.log("[warm] result:", j.warmed, "ok,", j.failed, "failed, total", j.total);
            } else {
              console.log("[warm] response:", res.statusCode, body.slice(0, 100));
            }
          } catch (_) {
            console.log("[warm] response:", res.statusCode, body.slice(0, 100));
          }
        }
        resolve();
      });
    });
    req.on("error", (err) => {
      console.warn("[warm] request error:", err.message);
      resolve();
    });
    req.setTimeout(30000, () => {
      req.destroy();
      resolve();
    });
  });
}

const next = spawn("npx", ["next", "start", "--port", String(PORT)], {
  stdio: "inherit",
  env: process.env,
});

next.on("error", (err) => {
  console.error(err);
  process.exit(1);
});

next.on("exit", (code) => {
  process.exit(code ?? 0);
});

waitForServer().then(warm).catch(() => {});
