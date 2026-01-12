/**
 * Dynamic robots.txt Generator
 * Controls search engine crawler access to site sections
 */

import { MetadataRoute } from "next";
import { getBaseUrl } from "@/lib/seo";

export default function robots(): MetadataRoute.Robots {
  const baseUrl = getBaseUrl();

  return {
    rules: [
      {
        // Default rules for all crawlers
        userAgent: "*",
        allow: [
          "/",
          "/leaderboard",
          "/leaderboard/models/",
          "/leaderboard/compare",
          "/about",
          "/categories/",
          "/contribute",
          "/contribute/support",
          "/faq",
          "/contact",
          "/runner",
          "/sponsor",
          "/newsletter",
          "/insights/",
          "/privacy",
          "/terms",
          "/tester-agreement",
          "/profile/",
        ],
        disallow: [
          // Admin and dashboard routes
          "/admin",
          "/admin/",
          "/dashboard",
          "/dashboard/",
          "/moderator",
          "/moderator/",
          "/blog-manager",
          "/blog-manager/",
          "/benchmark",
          "/benchmark/",
          // API routes
          "/api/",
          // Auth pages
          "/auth/",
          // Error pages
          "/_next/",
        ],
      },
      {
        // Specific rules for GPTBot (ChatGPT)
        userAgent: "GPTBot",
        allow: [
          "/",
          "/leaderboard",
          "/about",
          "/faq",
          "/llms.txt",
        ],
        disallow: [
          "/admin/",
          "/dashboard/",
          "/moderator/",
          "/api/",
        ],
      },
      {
        // Specific rules for Google-Extended (Bard/Gemini training)
        userAgent: "Google-Extended",
        allow: [
          "/",
          "/leaderboard",
          "/about",
          "/faq",
          "/llms.txt",
        ],
        disallow: [
          "/admin/",
          "/dashboard/",
          "/moderator/",
          "/api/",
        ],
      },
      {
        // Specific rules for CCBot (Common Crawl)
        userAgent: "CCBot",
        allow: [
          "/",
          "/leaderboard",
          "/about",
          "/faq",
          "/llms.txt",
        ],
        disallow: [
          "/admin/",
          "/dashboard/",
          "/moderator/",
          "/api/",
        ],
      },
      {
        // Specific rules for Anthropic Claude
        userAgent: "anthropic-ai",
        allow: [
          "/",
          "/leaderboard",
          "/about",
          "/faq",
          "/llms.txt",
        ],
        disallow: [
          "/admin/",
          "/dashboard/",
          "/moderator/",
          "/api/",
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  };
}
