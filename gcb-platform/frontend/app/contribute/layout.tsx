import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

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
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Contribute", path: "/contribute" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
