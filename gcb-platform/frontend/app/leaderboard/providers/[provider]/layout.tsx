import type { Metadata } from "next";
import { generatePageMetadata, getCanonicalUrl } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { apiClient } from "@/lib/api";
import { formatProvider } from "@/lib/model-utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ provider: string }>;
}): Promise<Metadata> {
  const { provider: rawProvider } = await params;
  const provider = decodeURIComponent(rawProvider);
  const providerDisplayName = formatProvider(provider);

  try {
    const data = await apiClient.getLeaderboard({ provider, limit: 100 });
    const modelCount = data.items?.length || 0;
    const avgScore = modelCount > 0
      ? data.items.reduce((sum, m) => sum + m.overall_score, 0) / modelCount
      : 0;
    const topScore = modelCount > 0
      ? Math.max(...data.items.map((m) => m.overall_score))
      : 0;

    const description = modelCount > 0
      ? `${providerDisplayName} has ${modelCount} AI model${modelCount !== 1 ? "s" : ""} tested on the Great Commission Benchmark. Top score: ${topScore.toFixed(1)}%, average: ${avgScore.toFixed(1)}%.`
      : `View ${providerDisplayName} AI models on the Great Commission Benchmark.`;

    return generatePageMetadata({
      title: `${providerDisplayName} AI Models`,
      description,
      path: `/leaderboard/providers/${encodeURIComponent(provider)}`,
      keywords: [
        providerDisplayName,
        "AI models",
        "benchmark results",
        "model comparison",
        "LLM",
        "Great Commission",
      ],
      openGraph: {
        type: "website",
      },
    });
  } catch {
    return generatePageMetadata({
      title: `${providerDisplayName} AI Models`,
      description: `View ${providerDisplayName} AI models on the Great Commission Benchmark.`,
      path: `/leaderboard/providers/${encodeURIComponent(provider)}`,
    });
  }
}

export default async function ProviderLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ provider: string }>;
}) {
  const { provider: rawProvider } = await params;
  const provider = decodeURIComponent(rawProvider);
  const providerDisplayName = formatProvider(provider);

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Leaderboard", path: "/leaderboard" },
    { name: providerDisplayName, path: `/leaderboard/providers/${encodeURIComponent(provider)}` },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
