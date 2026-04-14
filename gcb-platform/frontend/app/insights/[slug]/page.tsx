"use client";

import { useEffect, useState } from "react";
import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Tag } from "lucide-react";

interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  content?: string;
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: BlogCategory[];
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export default function BlogPostPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [post, setPost] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (slug) {
      loadPost();
    }
  }, [slug]);

  async function loadPost() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/blog/posts/${slug}`);
      if (response.ok) {
        const data = await response.json();
        setPost(data);
      } else if (response.status === 404) {
        setError("Post not found");
      } else {
        setError("Failed to load post");
      }
    } catch (err) {
      console.error("Failed to load post:", err);
      setError("Failed to load post");
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString?: string) {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  if (loading) {
    return (
      <div className="w-full py-8 max-w-[800px] mx-auto px-4">
        <Skeleton className="h-8 w-32 mb-8" />
        <Skeleton className="h-12 w-3/4 mb-4" />
        <Skeleton className="h-6 w-1/2 mb-8" />
        <Skeleton className="h-64 w-full mb-8" />
        <div className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="w-full py-8 max-w-[800px] mx-auto px-4">
        <Link href="/insights">
          <Button variant="ghost" className="mb-8">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Insights
          </Button>
        </Link>
        <Card className="p-12 text-center">
          <CardContent>
            <h1 className="text-2xl font-bold mb-4">Post Not Found</h1>
            <p className="text-muted-foreground mb-6">
              The article you&apos;re looking for doesn&apos;t exist or has been removed.
            </p>
            <Link href="/insights">
              <Button>Browse All Articles</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <article className="w-full py-8 max-w-[800px] mx-auto px-4">
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

