/**
 * Same-origin leaderboard data endpoint.
 * Fetches from backend and caches with ISR for fast, same-origin delivery.
 * Avoids cross-origin backend calls and leverages Next.js/edge caching.
 */

import { NextResponse } from "next/server";
import { API_URL } from "@/lib/api";

export const revalidate = 3600; // ISR: revalidate every hour

function transformEntry(entry: {
  model?: { id?: string; model_id?: string; name?: string; provider?: string };
  scores?: { overall?: number; tier1?: number; tier2?: number; tier3?: number };
  test_run?: { trust_tier?: string };
  category_scores?: Record<string, number>;
}) {
  return {
    id: entry.model?.id || "",
    model_id: entry.model?.model_id || entry.model?.id || "",
    model_name: entry.model?.name || "",
    provider: entry.model?.provider || "",
    overall_score: entry.scores?.overall || 0,
    tier1_score: entry.scores?.tier1,
    tier2_score: entry.scores?.tier2,
    tier3_score: entry.scores?.tier3,
    trust_tier: entry.test_run?.trust_tier,
    category_scores: entry.category_scores || {},
  };
}

export async function GET() {
  try {
    const res = await fetch(
      `${API_URL}/api/public/leaderboard?limit=1000&offset=0&sort=score&order=desc`,
      { next: { revalidate: 3600 } }
    );
    if (!res.ok) {
      return NextResponse.json(
        { error: "Failed to fetch leaderboard" },
        { status: res.status }
      );
    }
    const data = await res.json();
    const entries = data.entries || [];
    const items = entries.map(transformEntry);
    return NextResponse.json({
      items,
      total: data.total_models ?? items.length,
    });
  } catch (error) {
    console.error("[leaderboard-data] fetch error:", error);
    return NextResponse.json(
      { error: "Failed to fetch leaderboard" },
      { status: 500 }
    );
  }
}
