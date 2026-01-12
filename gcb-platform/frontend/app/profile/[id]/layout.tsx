import type { Metadata } from "next";
import { generateProfileMetadata } from "@/lib/seo";
import { buildProfilePageSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  
  try {
    // Note: This would need a public profile API endpoint
    // For now, using basic metadata
    return generateProfileMetadata({
      username: id,
      displayName: id,
    });
  } catch {
    return {
      title: "User Profile",
      description: "View user profile and contributions to the Great Commission Benchmark.",
    };
  }
}

export default async function ProfileLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  
  try {
    // Note: Would need profile API endpoint
    const profileSchema = buildProfilePageSchema({
      username: id,
      displayName: id,
    });
    
    const breadcrumbSchema = buildBreadcrumbSchema([
      { name: "Home", path: "/" },
      { name: "Profile", path: `/profile/${id}` },
    ]);
    
    return (
      <>
        <JsonLdScript data={[profileSchema, breadcrumbSchema]} />
        {children}
      </>
    );
  } catch {
    return <>{children}</>;
  }
}
