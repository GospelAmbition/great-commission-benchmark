import type { Metadata } from "next";
import { generatePageMetadata, getCanonicalUrl } from "@/lib/seo";
import { buildItemListSchema, buildDatasetSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { API_URL } from "@/lib/api";
import { LeaderboardDataProvider } from "@/components/leaderboard/LeaderboardDataProvider";
import type { LeaderboardDataItem } from "@/components/leaderboard/LeaderboardDataProvider";

export const metadata: Metadata = generatePageMetadata({
  title: "AI Model Leaderboard",
  description: "Compare AI models on the Great Commission Benchmark. See which models perform best for ministry work, evangelism, and discipleship. Filter by provider, category, and tier.",
  path: "/leaderboard",
  keywords: ["leaderboard", "AI models", "benchmark results", "model comparison", "scores", "rankings"],
  openGraph: {
    type: "website",
  },
});

// Transform backend leaderboard entries to frontend format
function transformToFrontendItems(entries: Array<{
  model?: { id?: string; model_id?: string; name?: string; provider?: string };
  scores?: { overall?: number; tier1?: number; tier2?: number; tier3?: number };
  test_run?: { trust_tier?: string };
  category_scores?: Record<string, number>;
}>): LeaderboardDataItem[] {
  return (entries || []).map((entry) => ({
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
  }));
}

// Fetch full leaderboard server-side for initial paint + SEO structured data
async function getLeaderboardData() {
  try {
    const response = await fetch(`${API_URL}/api/public/leaderboard?limit=1000`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    if (!response.ok) return { items: [], total: 0 };
    const data = await response.json();
    const entries = data.entries || [];
    const items = transformToFrontendItems(entries);
    return { items, total: data.total_models ?? items.length };
  } catch {
    return { items: [], total: 0 };
  }
}

export default async function LeaderboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { items, total } = await getLeaderboardData();

  // Generate ItemList schema with top models (first 10 for SEO)
  const itemListData = items.slice(0, 10).map((item, index) => ({
    name: item.model_name || item.model_id || "Unknown Model",
    url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(item.model_id || "")}`),
    position: index + 1,
    description: `${item.model_name || "AI Model"} by ${item.provider || "Unknown"} - ${(item.overall_score || 0).toFixed(1)}% score on Great Commission Benchmark`,
  }));

  const itemListSchema = itemListData.length > 0 ? buildItemListSchema(itemListData) : null;
  const datasetSchema = buildDatasetSchema({
    totalModels: total,
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
      <LeaderboardDataProvider initialItems={items} initialTotal={total}>
        {children}
      </LeaderboardDataProvider>
    </>
  );
}
