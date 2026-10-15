/**
 * Warm-up API route: exercises public routes and their underlying data caches.
 * Call after deploy (e.g. via Railway start script) with WARM_SECRET.
 *
 * Dynamic routes still render per request; warming does not cache their HTML.
 */

import { NextRequest, NextResponse } from "next/server";
import { API_URL } from "@/lib/api";
import { warmPages, createWarmJobStarter } from "@/lib/warm-pages";

const LEADERBOARD_PAGE_SIZE = 200;
const BLOG_PAGE_SIZE = 50;
const startWarmJob = createWarmJobStarter((error) => {
  console.warn("[warm] background error:", error);
});

const STATIC_PATHS = [
  "",
  "/leaderboard",
  "/leaderboard/compare",
  "/about",
  "/categories",
  "/contribute",
  "/contribute/support",
  "/faq",
  "/contact",
  "/runner",
  "/sponsor",
  "/newsletter",
  "/insights",
  "/privacy",
  "/terms",
  "/tester-agreement",
];

async function fetchModels(): Promise<string[]> {
  const ids: string[] = [];
  let offset = 0;
  try {
    for (;;) {
      const res = await fetch(
        `${API_URL}/api/public/leaderboard?limit=${LEADERBOARD_PAGE_SIZE}&offset=${offset}`,
        { next: { revalidate: 3600 }, signal: AbortSignal.timeout(15_000) }
      );
      if (!res.ok) break;
      const data = await res.json();
      const entries = data.entries || [];
      for (const e of entries) {
        const id = e.model?.model_id;
        if (id) ids.push(id);
      }
      if (!data.pagination?.has_more || entries.length === 0) break;
      offset += LEADERBOARD_PAGE_SIZE;
    }
  } catch {
    // ignore
  }
  return ids;
}

async function fetchCategories(): Promise<string[]> {
  try {
    const res = await fetch(`${API_URL}/api/public/filter-options`, {
      next: { revalidate: 86400 },
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.categories || [];
  } catch {
    return [];
  }
}

async function fetchBlogSlugs(): Promise<string[]> {
  const slugs: string[] = [];
  let offset = 0;
  try {
    for (;;) {
      const res = await fetch(
        `${API_URL}/api/blog/posts?limit=${BLOG_PAGE_SIZE}&offset=${offset}`,
        { next: { revalidate: 3600 }, signal: AbortSignal.timeout(15_000) }
      );
      if (!res.ok) break;
      const data = await res.json();
      const items = data.items || [];
      const total = typeof data.total === "number" ? data.total : 0;
      for (const p of items) {
        if (p.slug) slugs.push(p.slug);
      }
      if (items.length < BLOG_PAGE_SIZE || offset + items.length >= total) break;
      offset += BLOG_PAGE_SIZE;
    }
  } catch {
    // ignore
  }
  return slugs;
}

async function buildPaths(): Promise<string[]> {
  const paths = [...STATIC_PATHS];

  const [modelIds, categories, slugs] = await Promise.all([
    fetchModels(),
    fetchCategories(),
    fetchBlogSlugs(),
  ]);

  for (const id of modelIds) {
    if (id) paths.push(`/leaderboard/models/${encodeURIComponent(id)}`);
  }
  for (const cat of categories) {
    paths.push(`/categories/${encodeURIComponent(cat)}`);
  }
  for (const slug of slugs) {
    if (slug) paths.push(`/insights/${encodeURIComponent(slug)}`);
  }

  return paths;
}

export async function GET(request: NextRequest) {
  const secret = process.env.WARM_SECRET;
  if (!secret) {
    return NextResponse.json(
      { error: "Warm endpoint not configured (missing WARM_SECRET)" },
      { status: 503 }
    );
  }

  const provided =
    request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ||
    request.nextUrl.searchParams.get("secret");
  if (provided !== secret) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const origin = new URL(request.url).origin;
  const baseUrl = origin.endsWith("/") ? origin.slice(0, -1) : origin;

  // Run warming in background so the client gets a quick response (avoids socket hang up)
  const started = startWarmJob(async () => {
    const paths = await buildPaths();
    const { ok, failed, errors } = await warmPages(baseUrl, paths);
    console.log(
      "[warm] background done:",
      ok,
      "ok,",
      failed,
      "failed, total",
      paths.length
    );
    if (errors.length) console.warn("[warm] sample errors:", errors);
  });

  return NextResponse.json(
    { status: started ? "started" : "already_running", message: started ? "Warming in background" : "Warm-up already in progress" },
    { status: 202 }
  );
}
