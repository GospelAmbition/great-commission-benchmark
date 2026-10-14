import type { Metadata } from "next";
import { generateCategoryMetadata } from "@/lib/seo";
import { CATEGORY_NAMES, TIER_CATEGORIES } from "@/lib/benchmark-definitions";
import { getCategoryModels } from "@/lib/server-data";

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
  
  const metadata = generateCategoryMetadata({
    categoryName,
    categoryCode: id,
    tier,
  });

  // Shares the page's cached request. Don't let crawlers index the error
  // state shown when results fail to load.
  const loadFailed = await getCategoryModels(id).then(() => false, () => true);
  return loadFailed ? { ...metadata, robots: { index: false, follow: false } } : metadata;
}

export default function CategoryLayout({ children }: { children: React.ReactNode }) {
  return children;
}
