import type { Metadata } from "next";
import { generatePageMetadata, getCanonicalUrl } from "@/lib/seo";
import { buildItemListSchema, buildDatasetSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { API_URL, LEADERBOARD_PAGE_ENDPOINT } from "@/lib/api";
import { LeaderboardDataProvider, type LeaderboardInitialData } from "@/components/leaderboard/LeaderboardDataProvider";

export const metadata: Metadata = generatePageMetadata({
  title: "AI Model Leaderboard",
  description: "Compare AI models on the Great Commission Benchmark. See which models perform best for ministry work, evangelism, and discipleship. Filter by provider, category, and tier.",
  path: "/leaderboard",
  keywords: ["leaderboard", "AI models", "benchmark results", "model comparison", "scores", "rankings"],
  openGraph: {
    type: "website",
  },
});

// Fetch combined leaderboard-page data server-side.
// This populates the provider so the page has data on first paint,
// and also supplies entries for JSON-LD structured data.
async function getLeaderboardPageData(): Promise<{
  initialData: LeaderboardInitialData | null;
  rawEntries: Array<{
    model?: { model_id?: string; name?: string; provider?: string };
    scores?: { overall?: number };
  }> | null;
}> {
  try {
    const response = await fetch(`${API_URL}${LEADERBOARD_PAGE_ENDPOINT}`, {
      // The API response is already backed by Redis and invalidated whenever a
      // result is published. Avoid a second, deployment-local Next.js cache
      // that can continue serving an older model catalog when cross-service
      // revalidation is delayed or unavailable.
      cache: "no-store",
    });
    if (!response.ok) return { initialData: null, rawEntries: null };
    const data = await response.json();

    // Transform backend leaderboard entries to frontend shape
    const backendEntries: Array<{
      rank?: number;
      model?: { id?: string; model_id?: string; name?: string; provider?: string; description?: string };
      scores?: { overall?: number; tier1?: number; tier2?: number; tier3?: number };
      test_run?: { trust_tier?: string; question_set_version?: string; completed_at?: string };
      category_scores?: Record<string, number>;
    }> = data.leaderboard?.entries || [];

    const items = backendEntries
      .map((entry) => ({
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
      }))
      .filter((item) => item.overall_score > 0);

    const initialData: LeaderboardInitialData = {
      leaderboard: {
        items,
        total: data.leaderboard?.total_models || items.length,
      },
      filter_options: data.filter_options,
    };

    // Keep raw entries for JSON-LD (same data, different shape)
    const rawEntries = backendEntries.map((e) => ({
      model: e.model,
      scores: e.scores,
    }));

    return { initialData, rawEntries };
  } catch {
    return { initialData: null, rawEntries: null };
  }
}

export default async function LeaderboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { initialData, rawEntries } = await getLeaderboardPageData();

  // Generate ItemList schema with top 10 models
  const itemListData = rawEntries
    ? rawEntries.slice(0, 10).map((entry, index) => ({
        name: entry.model?.name || entry.model?.model_id || "Unknown Model",
        url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(entry.model?.model_id || "")}`),
        position: index + 1,
        description: `${entry.model?.name || "AI Model"} by ${entry.model?.provider || "Unknown"} - ${(entry.scores?.overall || 0).toFixed(1)}% score on Great Commission Benchmark`,
      }))
    : [];

  const itemListSchema = itemListData.length > 0 ? buildItemListSchema(itemListData) : null;
  const datasetSchema = buildDatasetSchema({
    totalModels: rawEntries?.length || 0,
    lastUpdated: new Date().toISOString().split("T")[0],
  });
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Leaderboard", path: "/leaderboard" },
  ]);

  return (
    <>
      {itemListSchema && <JsonLdScript data={itemListSchema} />}
      <JsonLdScript data={[datasetSchema, breadcrumbSchema]} />
      {/* Provider seeds the page with server-fetched data for instant first paint */}
      <LeaderboardDataProvider initialData={initialData}>
        {children}
      </LeaderboardDataProvider>
    </>
  );
}
