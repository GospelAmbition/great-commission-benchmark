import type { Metadata } from "next";
import { generateInsightMetadata } from "@/lib/seo";
import { buildArticleSchema, JsonLdScript } from "@/lib/structured-data";
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
    
    const articleSchema = buildArticleSchema({
      title: post.title,
      description: post.excerpt || post.title,
      slug: post.slug,
      publishedAt: post.published_at || post.created_at,
      author: post.author?.name,
      imageUrl: post.featured_image_url,
    });
    
    return (
      <>
        <JsonLdScript data={articleSchema} />
        {children}
      </>
    );
  } catch {
    return <>{children}</>;
  }
}
