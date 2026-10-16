import {
  PAGE_RATE_LIMIT,
  allowRequest,
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
