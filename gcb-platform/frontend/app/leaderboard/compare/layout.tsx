import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Compare AI Models",
  description: "Compare multiple AI models side-by-side on the Great Commission Benchmark. See detailed performance differences across categories, tiers, and scores.",
  path: "/leaderboard/compare",
  keywords: ["compare", "comparison", "side-by-side", "model comparison", "benchmark comparison"],
});

export default function CompareLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Leaderboard", path: "/leaderboard" },
    { name: "Compare Models", path: "/leaderboard/compare" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
