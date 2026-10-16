/**
 * Edge guards for the public Next.js origin.
 *
 * Scanner probes never render a page. Page-level per-IP limits stop a crawler
 * from forcing SSR (and therefore backend) work for every model/provider URL.
 * Backend rate limits still apply to direct API clients.
 */

export const PAGE_RATE_LIMIT = {
  windowMs: 60_000,
  limit: 90,
  burstWindowMs: 10_000,
  burstLimit: 25,
} as const;

const SCANNER_EXACT = new Set([
  "/env",
  "/.htaccess",
  "/xmlrpc.php",
  "/web.config",
  "/config.php",
  "/phpinfo.php",
  "/info.php",
]);

const SCANNER_PREFIXES = [
  "/.env",
  "/.git",
  "/.aws",
  "/actuator",
  "/wp-admin",
  "/wp-login",
  "/wp-content",
  "/wp-includes",
  "/wp-config",
  "/wordpress",
  "/phpmyadmin",
  "/phpinfo",
];

const hitsByIp = new Map<string, number[]>();

export function isScannerPath(path: string): boolean {
  if (!path) return false;
  const normalized = path.toLowerCase().replace(/\/{2,}/g, "/");
  if (SCANNER_EXACT.has(normalized)) return true;
  if (normalized.includes("phpinfo")) return true;
  if (normalized.includes("/.git") || normalized.startsWith("/.git")) return true;
  if (normalized.includes("/wp-") || normalized.startsWith("/wp-")) return true;
  if (normalized.startsWith("/.env")) return true;
  if (SCANNER_PREFIXES.some((prefix) => normalized === prefix || normalized.startsWith(`${prefix}/`))) {
    return true;
  }
  return normalized.endsWith(".php") || normalized.endsWith(".env");
}

export function allowRequest(ip: string, now = Date.now()): boolean {
  const windowHits = (hitsByIp.get(ip) || []).filter(
    (timestamp) => now - timestamp < PAGE_RATE_LIMIT.windowMs,
  );
  const burstHits = windowHits.filter(
    (timestamp) => now - timestamp < PAGE_RATE_LIMIT.burstWindowMs,
  );
  if (
    burstHits.length >= PAGE_RATE_LIMIT.burstLimit ||
    windowHits.length >= PAGE_RATE_LIMIT.limit
  ) {
    hitsByIp.set(ip, windowHits);
    return false;
  }
  windowHits.push(now);
  hitsByIp.set(ip, windowHits);
  return true;
}

export function resetCrawlerGuardForTests(): void {
  hitsByIp.clear();
}

export function clientIpFromHeaders(headers: {
  get(name: string): string | null;
}): string {
  const forwarded = headers.get("x-forwarded-for");
  if (forwarded) return forwarded.split(",")[0]?.trim() || "unknown";
  return headers.get("x-real-ip") || "unknown";
}
