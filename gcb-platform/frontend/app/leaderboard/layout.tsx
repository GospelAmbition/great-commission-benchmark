import type { Metadata } from "next";
import { generatePageMetadata, getCanonicalUrl } from "@/lib/seo";
import { buildItemListSchema, buildDatasetSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { API_URL } from "@/lib/api";

export const metadata: Metadata = generatePageMetadata({
  title: "AI Model Leaderboard",
  description: "Compare AI models on the Great Commission Benchmark. See which models perform best for ministry work, evangelism, and discipleship. Filter by provider, category, and tier.",
  path: "/leaderboard",
  keywords: ["leaderboard", "AI models", "benchmark results", "model comparison", "scores", "rankings"],
  openGraph: {
    type: "website",
  },
});

// Fetch leaderboard data server-side for structured data
async function getLeaderboardData() {
  try {
    const response = await fetch(`${API_URL}/api/public/leaderboard?limit=10`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.entries || [];
  } catch {
    return null;
  }
}

export default async function LeaderboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const entries = await getLeaderboardData();
  
  // Generate ItemList schema with top models
  const itemListData = entries
    ? entries.slice(0, 10).map((entry: {
        model?: { model_id?: string; name?: string; provider?: string };
        scores?: { overall?: number };
      }, index: number) => ({
        name: entry.model?.name || entry.model?.model_id || "Unknown Model",
        url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(entry.model?.model_id || "")}`),
        position: index + 1,
        description: `${entry.model?.name || "AI Model"} by ${entry.model?.provider || "Unknown"} - ${(entry.scores?.overall || 0).toFixed(1)}% score on Great Commission Benchmark`,
      }))
    : [];

  const itemListSchema = itemListData.length > 0 ? buildItemListSchema(itemListData) : null;
  const datasetSchema = buildDatasetSchema({
    totalModels: entries?.length || 0,
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
      {children}
    </>
  );
}
