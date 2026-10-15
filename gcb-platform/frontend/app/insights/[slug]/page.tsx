import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { NewsletterButton, NewsletterOffer } from "@/components/marketing/NewsletterOffer";
import Link from "next/link";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Tag } from "lucide-react";
import { ModelBenchmarkLink } from "@/components/blog/ModelBenchmarkLink";
import { generateInsightMetadata } from "@/lib/seo";
import { buildArticleSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { decodeRouteParam, getBlogPost, type PublicBlogPost } from "@/lib/server-data";

type InsightParams = { params: Promise<{ slug: string }> };

async function loadPost(slug: string): Promise<{ post: PublicBlogPost | null; error: boolean }> {
  try {
    return { post: await getBlogPost(slug), error: false };
  } catch (error) {
    console.error("Failed to load insight post:", error);
    return { post: null, error: true };
  }
}

export async function generateMetadata({ params }: InsightParams): Promise<Metadata> {
  const slug = decodeRouteParam((await params).slug);
  const { post, error } = await loadPost(slug);
  if (!post) {
    return {
      title: "Insight Article",
      description: "Read insights and analysis about AI models and the Great Commission Benchmark.",
      // Don't let crawlers index the error state shown when the post fails to load.
      ...(error && { robots: { index: false, follow: false } }),
    };
  }
  return generateInsightMetadata({
    title: post.title,
    excerpt: post.excerpt || post.title,
    slug: post.slug,
    publishedAt: post.published_at,
    author: post.author?.name,
    imageUrl: post.featured_image_url,
  });
}

function formatDate(dateString?: string) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default async function BlogPostPage({ params }: InsightParams) {
  const slug = decodeRouteParam((await params).slug);
  const { post, error } = await loadPost(slug);
  if (error) {
    return (
      <article className="w-full py-8 max-w-[800px] mx-auto px-4">
        <Button asChild variant="ghost" className="mb-8">
          <Link href="/insights">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Insights
          </Link>
        </Button>
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          This article could not be loaded. Please try again shortly.
        </div>
      </article>
    );
  }
  if (!post) notFound();

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
    categories: post.categories?.map(c => ({ name: c.name, slug: c.slug })),
    section: post.categories?.[0]?.name,
    wordCount,
    readingTime,
  });

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Insights", path: "/insights" },
    { name: post.title, path: `/insights/${encodeURIComponent(slug)}` },
  ]);

  return (
    <article className="w-full py-8 max-w-[800px] mx-auto px-4">
      <JsonLdScript data={[articleSchema, breadcrumbSchema]} />

      {/* Back Button */}
      <Link href="/insights">
        <Button variant="ghost" className="mb-8">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Back to Insights
        </Button>
      </Link>

      {/* Header */}
      <header className="mb-8">
        {/* Categories */}
        {post.categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {post.categories.map((cat) => (
              <Link key={cat.id} href={`/insights?category=${cat.slug}`}>
                <Badge variant="secondary" className="hover:bg-secondary/80">
                  <Tag className="h-3 w-3 mr-1" />
                  {cat.name}
                </Badge>
              </Link>
            ))}
          </div>
        )}

        {/* Title */}
        <h1 className="text-4xl font-bold">{post.title}</h1>
        <NewsletterButton source="article_header" variant="link" className="mt-3 px-0">Get the GCB digest</NewsletterButton>
      </header>

      {/* Featured Image */}
      {post.featured_image_url && (
        <div className="relative w-screen left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] mb-8">
          {/* Blurred background covering full width */}
          <div className="absolute inset-0 h-64 md:h-96 overflow-hidden">
            <Image
              src={post.featured_image_url}
              alt=""
              fill
              className="object-cover blur-2xl scale-110 opacity-60"
              priority
              unoptimized
              aria-hidden="true"
            />
          </div>
          {/* Main image centered with container constraints */}
          <div className="relative container max-w-[800px] h-64 md:h-96 mx-auto flex items-center justify-center px-4">
            <div className="relative h-full w-auto max-w-full rounded-lg overflow-hidden flex items-center justify-center">
              <img
                src={post.featured_image_url}
                alt={post.title}
                className="h-full w-auto max-w-full object-contain rounded-lg"
                loading="eager"
              />
            </div>
          </div>
        </div>
      )}

      {/* Excerpt */}
      {post.excerpt && (
        <div className="mb-8">
          <p className="text-xl text-muted-foreground leading-relaxed">
            {post.excerpt}
          </p>
        </div>
      )}

      <Separator className="mb-8" />

      {/* Content — stored as Markdown, rendered to HTML at read time.
           rehype-raw allows legacy HTML content to pass through unchanged. */}
      <div
        className="prose prose-lg prose-invert max-w-full
          prose-headings:font-bold prose-headings:text-foreground
          prose-p:text-muted-foreground prose-p:leading-relaxed
          prose-a:text-primary prose-a:no-underline hover:prose-a:underline
          prose-strong:text-foreground
          prose-blockquote:border-primary prose-blockquote:text-muted-foreground
          prose-code:text-foreground prose-code:bg-muted prose-code:px-1 prose-code:rounded
          prose-pre:bg-muted prose-pre:text-foreground
          prose-img:rounded-lg prose-img:shadow-md
          prose-ul:text-muted-foreground prose-ol:text-muted-foreground
          prose-li:marker:text-primary"
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
          {post.content || ""}
        </ReactMarkdown>
      </div>

      <div className="my-8"><NewsletterOffer source="article_end" title="Get more insights like this in your inbox." /></div>
      {/* Benchmark Results Link */}
      {post.related_models && post.related_models.length > 0 && (
        <div className="my-8">
          <ModelBenchmarkLink models={post.related_models} />
        </div>
      )}

      <Separator className="my-12" />

      {/* Footer */}
      <footer className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <p className="text-sm text-muted-foreground">
            Published on {formatDate(post.published_at)}
          </p>
          {post.updated_at !== post.published_at && (
            <p className="text-xs text-muted-foreground">
              Last updated {formatDate(post.updated_at)}
            </p>
          )}
        </div>
        <Link href="/insights">
          <Button variant="outline">
            <ChevronLeft className="h-4 w-4 mr-2" />
            More Articles
          </Button>
        </Link>
      </footer>

      {/* Related Categories */}
      {post.categories.length > 0 && (
        <Card className="mt-8 bg-muted/50">
          <CardHeader>
            <CardTitle className="text-lg">Related Topics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {post.categories.map((cat) => (
                <Link key={cat.id} href={`/insights?category=${cat.slug}`}>
                  <Button variant="secondary" size="sm">
                    {cat.name}
                  </Button>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </article>
  );
}

