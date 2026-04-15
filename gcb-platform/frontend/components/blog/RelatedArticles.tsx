"use client";

import Link from "next/link";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import { ArticleIcon } from "@/lib/icons";

interface RelatedArticle {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  featured_image_url?: string;
  published_at?: string;
}

interface RelatedArticlesProps {
  articles: RelatedArticle[];
  title?: string;
  viewAllHref?: string;
  viewAllLabel?: string;
}

export function RelatedArticles({
  articles,
  title = "Related Articles",
  viewAllHref,
  viewAllLabel = "View all articles",
}: RelatedArticlesProps) {
  if (!articles || articles.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ArticleIcon className="h-5 w-5 text-primary" />
            {title}
          </CardTitle>
          {viewAllHref && (
            <Link href={viewAllHref}>
              <Button variant="ghost" size="sm">
                {viewAllLabel}
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {articles.map((article) => (
            <Link
              key={article.id}
              href={`/insights/${article.slug}`}
              className="flex gap-4 group rounded-lg p-2 -mx-2 hover:bg-white/[0.04] transition-colors"
            >
              {article.featured_image_url ? (
                <div className="relative w-20 h-14 rounded-md overflow-hidden flex-shrink-0 bg-white/[0.02]">
                  <Image
                    src={article.featured_image_url}
                    alt=""
                    fill
                    className="object-cover"
                    unoptimized
                  />
                </div>
              ) : (
                <div className="w-20 h-14 rounded-md flex-shrink-0 bg-gradient-to-br from-primary/10 to-white/[0.02] flex items-center justify-center">
                  <span className="text-xs font-bold text-primary/30">GCB</span>
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium line-clamp-2 group-hover:text-primary transition-colors">
                  {article.title}
                </h4>
                {article.published_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(article.published_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </p>
                )}
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0 mt-1" />
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
