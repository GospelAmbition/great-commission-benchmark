import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Volunteer for the Great Commission Benchmark",
  description: "Help advance the Great Commission Benchmark through volunteering. Sponsor a test, become a tester, or join our moderation or advisory team.",
  path: "/contribute",
  keywords: ["volunteer", "sponsor", "tester", "moderation", "advisory", "contribute"],
});

export default function ContributeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Volunteer", path: "/contribute" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
