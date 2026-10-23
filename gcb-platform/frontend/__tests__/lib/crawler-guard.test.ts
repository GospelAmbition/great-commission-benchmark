import {
  PAGE_RATE_LIMIT,
  allowRequest,
  allowPageRequest,
  clientIpFromHeaders,
  isScannerPath,
  resetCrawlerGuardForTests,
} from "@/lib/crawler-guard";
import robots from "@/app/robots";

describe("scanner path matching", () => {
  it.each([
    "/.env",
    "/.env.production",
    "/actuator/env",
    "/phpinfo.php",
    "/phpinfo",
    "/wp-admin",
    "/wp-login.php",
    "/.git/config",
  ])("blocks %s", (path) => {
    expect(isScannerPath(path)).toBe(true);
  });

  it.each([
    "/",
    "/leaderboard",
    "/leaderboard/models/openai/gpt-4",
    "/leaderboard/providers/openai",
    "/api/warm",
  ])("allows %s", (path) => {
    expect(isScannerPath(path)).toBe(false);
  });
});

describe("page rate limit", () => {
  beforeEach(() => {
    resetCrawlerGuardForTests();
  });

  it("allows a normal browsing burst then rejects extras in the burst window", () => {
    const now = 1_000_000;
    for (let i = 0; i < PAGE_RATE_LIMIT.burstLimit; i += 1) {
      expect(allowRequest("1.2.3.4", now + i)).toBe(true);
    }
    expect(allowRequest("1.2.3.4", now + PAGE_RATE_LIMIT.burstLimit)).toBe(false);
  });

  it("tracks IPs independently", () => {
    const now = 1_000_000;
    for (let i = 0; i < PAGE_RATE_LIMIT.burstLimit; i += 1) {
      expect(allowRequest("10.0.0.1", now)).toBe(true);
    }
    expect(allowRequest("10.0.0.2", now)).toBe(true);
  });

  it("reads the original client from X-Forwarded-For", () => {
    const headers = { get: (name: string) => (name === "x-forwarded-for" ? "8.8.8.8, 1.1.1.1" : null) };
    expect(clientIpFromHeaders(headers)).toBe("8.8.8.8");
  });
});

describe("robots.txt", () => {
  it("asks polite crawlers to slow down on the leaderboard", () => {
    const result = robots();
    const rules = Array.isArray(result.rules) ? result.rules : [result.rules];
    const star = rules.find((rule) => rule.userAgent === "*");
    expect(star?.crawlDelay).toBe(10);
    expect(star?.allow).toEqual(expect.arrayContaining(["/leaderboard", "/leaderboard/models/"]));

    const aggressive = rules.find((rule) => Array.isArray(rule.userAgent) && rule.userAgent.includes("AhrefsBot"));
    expect(aggressive?.crawlDelay).toBe(30);
  });
});


describe("navigation and speculative fetch budgets", () => {
  const headers = (values: Record<string, string>) => ({
    get: (name: string) => values[name] ?? null,
  });
  beforeEach(resetCrawlerGuardForTests);

  it.each([
    { "next-router-prefetch": "1" },
    { "next-router-prefetch": "2" },
    { "next-router-segment-prefetch": "/_tree" },
    { purpose: "prefetch" },
    { "sec-purpose": "prefetch;prerender" },
  ])("keeps a homepage prefetch burst from blocking refreshes and clicks: %o", (signals) => {
    const now = 1_000_000;
    const ip = "192.0.2.1";
    expect(allowPageRequest(ip, headers({}), now)).toBe(true);
    for (let i = 0; i < PAGE_RATE_LIMIT.burstLimit; i++) {
      expect(allowPageRequest(ip, headers(signals as Record<string, string>), now)).toBe(true);
    }
    // Prefetch still has a limit, including when a crawler supplies the headers.
    expect(allowPageRequest(ip, headers(signals as Record<string, string>), now)).toBe(false);
    expect(allowPageRequest(ip, headers({}), now)).toBe(true);
    expect(allowPageRequest(ip, headers({ rsc: "1" }), now)).toBe(true);
  });

  it("still limits repeated navigation, including client-side RSC clicks, and recovers", () => {
    const now = 1_000_000;
    for (let i = 0; i < PAGE_RATE_LIMIT.burstLimit; i++) {
      expect(allowPageRequest("192.0.2.1", headers({ rsc: "1" }), now)).toBe(true);
    }
    expect(allowPageRequest("192.0.2.1", headers({}), now)).toBe(false);
    expect(allowPageRequest("192.0.2.2", headers({}), now)).toBe(true);
    expect(allowPageRequest("192.0.2.1", headers({}), now + PAGE_RATE_LIMIT.burstWindowMs)).toBe(true);
  });
});
