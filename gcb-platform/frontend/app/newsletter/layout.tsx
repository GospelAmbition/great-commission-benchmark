import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Newsletter Signup",
  description: "Subscribe to the Great Commission Benchmark newsletter for updates on new model evaluations, benchmark methodology improvements, and community news.",
  path: "/newsletter",
  keywords: ["newsletter", "subscribe", "updates", "email"],
});

export default function NewsletterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Newsletter", path: "/newsletter" },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
