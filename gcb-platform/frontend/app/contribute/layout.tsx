import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";

export const metadata: Metadata = generatePageMetadata({
  title: "Contribute to the Great Commission Benchmark",
  description: "Help build the Great Commission Benchmark community. Become a tester, submit results, contribute to development, or support the project financially.",
  path: "/contribute",
  keywords: ["contribute", "tester", "submit", "development", "support", "donate"],
});

export default function ContributeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
