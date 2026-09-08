import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Newsletter Signup",
  description: "Get the GCB monthly digest of model evaluations and insights for Great Commission work, plus occasional highlights on important model releases.",
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
