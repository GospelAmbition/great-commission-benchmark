/**
 * Warm-up API route: primes all public pages so the first real user gets fast responses.
 * Call after deploy (e.g. via Railway start script) with WARM_SECRET.
 *
 * Next.js renders dynamic routes on first request and caches them; this route
 * triggers that rendering so the cache is warm.
 */

import { NextRequest, NextResponse } from "next/server";
import { API_URL } from "@/lib/api";

const LEADERBOARD_PAGE_SIZE = 100;
const BLOG_PAGE_SIZE = 50;
const BATCH_SIZE = 8; // concurrent requests per batch

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
        { next: { revalidate: 3600 } }
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
        { next: { revalidate: 3600 } }
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

async function fetchInBatches(
  baseUrl: string,
  paths: string[]
): Promise<{ ok: number; failed: number; errors: string[] }> {
  let ok = 0;
  let failed = 0;
  const errors: string[] = [];

  for (let i = 0; i < paths.length; i += BATCH_SIZE) {
    const batch = paths.slice(i, i + BATCH_SIZE);
    const results = await Promise.allSettled(
      batch.map((path) => {
        const url = path
          ? `${baseUrl}${path}`
          : baseUrl.replace(/\/$/, "") || `${baseUrl}/`;
        return fetch(url, { headers: { "User-Agent": "GCB-Warm/1.0" } });
      })
    );
    for (let j = 0; j < results.length; j++) {
      const r = results[j];
      const path = batch[j];
      if (r.status === "fulfilled" && r.value.ok) {
        ok++;
      } else {
        failed++;
        const msg =
          r.status === "rejected"
            ? (r as PromiseRejectedResult).reason?.message
            : (r as PromiseFulfilledResult<Response>).value?.status;
        if (errors.length < 10) errors.push(`${path}: ${msg}`);
      }
    }
  }

  return { ok, failed, errors };
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

  const paths = await buildPaths();
  const { ok, failed, errors } = await fetchInBatches(baseUrl, paths);

  return NextResponse.json({
    warmed: ok,
    failed,
    total: paths.length,
    errors: errors.length ? errors : undefined,
  });
}
