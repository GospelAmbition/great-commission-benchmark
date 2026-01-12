import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Insights & Analysis",
  description: "Read insights, analysis, and articles about AI models, the Great Commission Benchmark, and how different models perform for ministry work.",
  path: "/insights",
  keywords: ["insights", "articles", "analysis", "blog", "AI analysis", "benchmark insights"],
});

export default function InsightsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Insights", path: "/insights" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
