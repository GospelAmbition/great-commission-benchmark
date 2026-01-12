import type { Metadata } from "next";
import { generateCategoryMetadata, getCanonicalUrl } from "@/lib/seo";
import { CATEGORY_NAMES, TIER_CATEGORIES } from "@/lib/benchmark-definitions";
import { buildItemListSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { API_URL } from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  
  // Find category info
  const categoryName = CATEGORY_NAMES[id] || id.replace(/_/g, " ");
  let tier = 1;
  
  // Determine tier from category code
  for (const [tierNum, categories] of Object.entries(TIER_CATEGORIES)) {
    if (categories.includes(id)) {
      tier = parseInt(tierNum.replace("tier", ""));
      break;
    }
  }
  
  return generateCategoryMetadata({
    categoryName,
    categoryCode: id,
    tier,
  });
}

// Fetch category rankings server-side for structured data
async function getCategoryRankings(categoryId: string) {
  try {
    const response = await fetch(`${API_URL}/api/public/leaderboard?category=${categoryId}&limit=10`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.entries || [];
  } catch {
    return null;
  }
}

export default async function CategoryLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const categoryName = CATEGORY_NAMES[id] || id.replace(/_/g, " ");
  const entries = await getCategoryRankings(id);
  
  // Generate ItemList schema with top models for this category
  const itemListData = entries
    ? entries.slice(0, 10).map((entry: {
        model?: { model_id?: string; name?: string; provider?: string };
        scores?: { overall?: number };
        category_scores?: Record<string, number>;
      }, index: number) => {
        const categoryScore = entry.category_scores?.[id] || entry.scores?.overall || 0;
        return {
          name: entry.model?.name || entry.model?.model_id || "Unknown Model",
          url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(entry.model?.model_id || "")}`),
          position: index + 1,
          description: `${entry.model?.name || "AI Model"} scored ${categoryScore.toFixed(1)}% in ${categoryName}`,
        };
      })
    : [];

  const itemListSchema = itemListData.length > 0 ? buildItemListSchema(itemListData) : null;
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Categories", path: "/categories" },
    { name: categoryName, path: `/categories/${id}` },
  ]);

  return (
    <>
      {itemListSchema && <JsonLdScript data={itemListSchema} />}
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
