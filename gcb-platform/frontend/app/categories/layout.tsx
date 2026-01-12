import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";

export const metadata: Metadata = generatePageMetadata({
  title: "Benchmark Categories",
  description: "Explore benchmark results by category. See how AI models perform across different ministry tasks, gospel core tests, and worldview confession evaluations.",
  path: "/categories",
  keywords: ["categories", "category results", "tier 1", "tier 2", "tier 3", "task capability", "gospel core", "worldview"],
});

export default function CategoriesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
