import { buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { formatProvider } from "@/lib/model-utils";

export default async function ProviderLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ provider: string }>;
}) {
  const { provider: rawProvider } = await params;
  const provider = decodeURIComponent(rawProvider);
  const providerDisplayName = formatProvider(provider);

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Leaderboard", path: "/leaderboard" },
    { name: providerDisplayName, path: `/leaderboard/providers/${encodeURIComponent(provider)}` },
  ]);

  return (
    <>
      <JsonLdScript data={breadcrumbSchema} />
      {children}
    </>
  );
}
