import type { Metadata } from "next";
import { generateInsightMetadata } from "@/lib/seo";
import { buildArticleSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { apiClient } from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  
  try {
    const post = await apiClient.getBlogPost(slug);
    
    return generateInsightMetadata({
      title: post.title,
      excerpt: post.excerpt || post.title,
      slug: post.slug,
      publishedAt: post.published_at,
      author: post.author?.name,
      imageUrl: post.featured_image_url,
    });
  } catch {
    return {
      title: "Insight Article",
      description: "Read insights and analysis about AI models and the Great Commission Benchmark.",
    };
  }
}

export default async function InsightLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  
  try {
    const post = await apiClient.getBlogPost(slug);
    
    // Estimate word count and reading time from content
    const wordCount = post.content ? post.content.split(/\s+/).length : undefined;
    const readingTime = wordCount ? Math.ceil(wordCount / 200) : undefined; // ~200 words per minute
    
    const articleSchema = buildArticleSchema({
      title: post.title,
      description: post.excerpt || post.title,
      slug: post.slug,
      publishedAt: post.published_at || post.created_at,
      modifiedAt: post.updated_at,
      author: post.author?.name,
      imageUrl: post.featured_image_url,
      // Enhanced metadata
      categories: post.categories?.map(c => ({ name: c.name, slug: c.slug })),
      section: post.categories?.[0]?.name,
      wordCount,
      readingTime,
    });
    
    const breadcrumbSchema = buildBreadcrumbSchema([
      { name: "Home", path: "/" },
      { name: "Insights", path: "/insights" },
      { name: post.title, path: `/insights/${slug}` },
    ]);
    
    return (
      <>
        <JsonLdScript data={[articleSchema, breadcrumbSchema]} />
        {children}
      </>
    );
  } catch {
    return <>{children}</>;
  }
}
