import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Support the Great Commission Benchmark",
  description: "Support the Great Commission Benchmark through financial contributions. Help us continue evaluating AI models for ministry work and making the results freely available.",
  path: "/contribute/support",
  keywords: ["support", "donate", "contribute", "funding", "financial support"],
});

export default function SupportLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Contribute", path: "/contribute" },
    { name: "Support", path: "/contribute/support" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
