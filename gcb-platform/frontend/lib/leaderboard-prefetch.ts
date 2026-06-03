/**
 * Client-side prefetch cache for leaderboard-page data.
 *
 * Usage:
 *   - Call prefetchLeaderboardPage() on Leaderboard link hover/focus to
 *     start loading before the user navigates.
 *   - Call getPrefetchedLeaderboardPage() in the provider/page to consume
 *     the preloaded data immediately on mount.
 */

import type { LeaderboardItem, FilterOptionsResponse } from "./api";
import { API_URL, LEADERBOARD_PAGE_ENDPOINT } from "./api";

export interface PrefetchedLeaderboardPage {
  leaderboard: { items: LeaderboardItem[]; total: number };
  filter_options: FilterOptionsResponse;
}

// Module-level cache — survives SPA navigations within the same session.
let cachedData: PrefetchedLeaderboardPage | null = null;
let loadingPromise: Promise<void> | null = null;
// Simple 5-minute TTL so we don't serve stale data if the user lingers
const TTL_MS = 5 * 60 * 1000;
let cachedAt = 0;

function isFresh(): boolean {
  return cachedData !== null && Date.now() - cachedAt < TTL_MS;
}

function transformResponse(raw: {
  leaderboard: {
    entries?: Array<{
      rank?: number;
      model?: { id?: string; model_id?: string; name?: string; provider?: string; description?: string };
      scores?: { overall?: number; tier1?: number; tier2?: number; tier3?: number };
      test_run?: { trust_tier?: string; question_set_version?: string; completed_at?: string };
      category_scores?: Record<string, number>;
    }>;
    total_models?: number;
  };
  filter_options: FilterOptionsResponse;
}): PrefetchedLeaderboardPage {
  const items: LeaderboardItem[] = (raw.leaderboard?.entries || []).map((entry) => ({
    rank: entry.rank,
    id: entry.model?.id || "",
    model_id: entry.model?.model_id || entry.model?.id || "",
    model_name: entry.model?.name || "",
    provider: entry.model?.provider || "",
    description: entry.model?.description,
    overall_score: entry.scores?.overall || 0,
    tier1_score: entry.scores?.tier1,
    tier2_score: entry.scores?.tier2,
    tier3_score: entry.scores?.tier3,
    trust_tier: entry.test_run?.trust_tier,
    question_set_version: entry.test_run?.question_set_version,
    completed_at: entry.test_run?.completed_at,
    category_scores: entry.category_scores || {},
  }));
  return {
    leaderboard: { items, total: raw.leaderboard?.total_models ?? items.length },
    filter_options: raw.filter_options,
  };
}

/**
 * Kick off a background fetch of leaderboard-page data.
 * Safe to call multiple times — only one request flies at a time.
 * No-op if data is already fresh.
 */
export function prefetchLeaderboardPage(): void {
  if (isFresh()) return;
  if (loadingPromise) return;

  loadingPromise = (async () => {
    try {
      const url = `${API_URL}${LEADERBOARD_PAGE_ENDPOINT}`;
      const res = await fetch(url, { headers: { "Content-Type": "application/json" } });
      if (!res.ok) return;
      const raw = await res.json();
      cachedData = transformResponse(raw);
      cachedAt = Date.now();
    } catch {
      // Prefetch is best-effort; silently ignore failures.
    } finally {
      loadingPromise = null;
    }
  })();
}

/**
 * Return prefetched data if available, otherwise null.
 * Does NOT clear the cache on read — the TTL controls freshness.
 */
export function getPrefetchedLeaderboardPage(): PrefetchedLeaderboardPage | null {
  return isFresh() ? cachedData : null;
}
