import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildItemListSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "AI Model Leaderboard",
  description: "Compare AI models on the Great Commission Benchmark. See which models perform best for ministry work, evangelism, and discipleship. Filter by provider, category, and tier.",
  path: "/leaderboard",
  keywords: ["leaderboard", "AI models", "benchmark results", "model comparison", "scores", "rankings"],
  openGraph: {
    type: "website",
  },
});

export default function LeaderboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Note: For dynamic ItemList schema with actual rankings, this would need to be
  // generated server-side with data fetching. For now, we'll use a basic schema.
  return <>{children}</>;
}
