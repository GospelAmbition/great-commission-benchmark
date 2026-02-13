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
      const req = http.get(`http://127.0.0.1:${PORT}/`, (res) => {
        resolve(true);
      });
      req.on("error", () => {
        setTimeout(attempt, 3000);
      });
      req.setTimeout(2000, () => {
        req.destroy();
        setTimeout(attempt, 3000);
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
    const url = `http://127.0.0.1:${PORT}/api/warm?secret=${encodeURIComponent(WARM_SECRET)}`;
    const req = http.get(url, (res) => {
      let body = "";
      res.on("data", (c) => (body += c));
      res.on("end", () => {
        try {
          const j = JSON.parse(body);
          console.log(
            "[warm] result:",
            j.warmed,
            "ok,",
            j.failed,
            "failed, total",
            j.total
          );
        } catch (_) {
          console.log("[warm] non-JSON response");
        }
        resolve();
      });
    });
    req.on("error", (err) => {
      console.warn("[warm] request error:", err.message);
      resolve();
    });
    req.setTimeout(120000, () => {
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
