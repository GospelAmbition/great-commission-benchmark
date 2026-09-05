import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";

export const metadata: Metadata = generatePageMetadata({
  title: "Recent AI Model Tests",
  description: "See the latest AI models tested on the Great Commission Benchmark, with current scores, leaderboard ranks, model details, and analysis.",
  path: "/recent-tests",
  keywords: ["recent AI tests", "AI model results", "benchmark scores", "AI leaderboard"],
  openGraph: { type: "website" },
});

export default function RecentTestsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
