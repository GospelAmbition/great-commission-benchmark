import type { Metadata } from "next";
import { generateCategoryMetadata } from "@/lib/seo";
import { CATEGORY_NAMES, TIER_CATEGORIES } from "@/lib/benchmark-definitions";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  
  // Find category info
  const categoryName = CATEGORY_NAMES[id] || id.replace(/_/g, " ");
  let tier = 1;
  let categoryCode = id;
  
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

export default function CategoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
