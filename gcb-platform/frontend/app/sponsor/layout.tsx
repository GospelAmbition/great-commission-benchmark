import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Sponsor a Model Test",
  description: "Sponsor benchmark testing for an AI model on the Great Commission Benchmark. Request testing for specific models or support the evaluation of new AI systems.",
  path: "/sponsor",
  keywords: ["sponsor", "sponsorship", "model testing", "request", "funding"],
});

export default function SponsorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Sponsor", path: "/sponsor" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
