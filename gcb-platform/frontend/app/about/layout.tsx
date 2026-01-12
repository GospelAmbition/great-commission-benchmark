import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";

export const metadata: Metadata = generatePageMetadata({
  title: "About the Great Commission Benchmark",
  description: "Learn about the Great Commission Benchmark methodology, mission, and three-tier evaluation system. Understand how we measure AI models for ministry work, evangelism, and discipleship.",
  path: "/about",
  keywords: ["methodology", "benchmark", "evaluation", "three-tier", "task capability", "gospel core", "worldview confession", "guardrails"],
});

export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
