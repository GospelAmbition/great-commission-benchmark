"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ChevronRight, Search, X } from "lucide-react";
import { ArticleIcon } from "@/lib/icons";

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
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: BlogCategory[];
  created_at: string;
  published_at?: string;
}

function InsightsContent() {
  const searchParams = useSearchParams();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Initialize from URL params
  useEffect(() => {
    const categoryParam = searchParams.get("category");
    const searchParam = searchParams.get("search");
    
    if (categoryParam) {
      setSelectedCategory(categoryParam);
    }
    if (searchParam) {
      setSearchQuery(searchParam);
    }
  }, [searchParams]);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadPosts();
  }, [selectedCategory, searchQuery]);

  async function loadCategories() {
    try {
      const response = await fetch("/api/blog/categories");
      if (response.ok) {
        const data = await response.json();
        setCategories(data.items || []);
      }
    } catch (error) {
      console.error("Failed to load categories:", error);
    }
  }

  async function loadPosts() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory && selectedCategory !== "all") {
        params.append("category", selectedCategory);
      }
      if (searchQuery) {
        params.append("search", searchQuery);
      }
      params.append("limit", "12");
      
      const response = await fetch(`/api/blog/posts?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setPosts(data.items || []);
        setTotal(data.total || 0);
      }
    } catch (error) {
      console.error("Failed to load posts:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-40" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <ArticleIcon className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-3xl md:text-4xl font-light text-foreground">Insights</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl font-light">
            Practical guides, insights, and resources for Christian missionaries and outreach workers 
            navigating AI guardrails in their ministry work.
          </p>
        </div>
      </div>

      <div className="container py-8">
        {/* Filters and Search */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Category:</span>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.slug}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="relative w-full md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search articles..."
                className="pl-9 pr-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground">
            {total} {total === 1 ? "article" : "articles"}
          </p>
        </div>

        {/* Posts Grid */}
        {loading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i}>
                <Skeleton className="h-48 w-full rounded-t-lg" />
                <CardHeader>
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3 mt-2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : posts.length === 0 ? (
          <Card className="p-12 text-center">
            <CardContent>
              <div className="w-16 h-16 rounded-full bg-white/[0.06] mx-auto mb-4 flex items-center justify-center">
                <ArticleIcon className="h-8 w-8 text-muted-foreground" />
              </div>
              <p className="text-foreground font-medium mb-2">No articles yet</p>
              <p className="text-muted-foreground">
                {searchQuery || selectedCategory !== "all" 
                  ? "Try adjusting your filters to find what you're looking for." 
                  : "Check back soon for practical guides and insights on using AI for ministry work."}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden group border-glow">
                <Link href={`/insights/${post.slug}`}>
                  {post.featured_image_url ? (
                    <div className="relative h-48 w-full bg-white/[0.02]">
                      <Image
                        src={post.featured_image_url}
                        alt={post.title}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    </div>
                  ) : (
                    <div className="h-48 w-full bg-gradient-to-br from-primary/10 to-white/[0.02] flex items-center justify-center">
                      <span className="text-4xl font-bold text-primary/20">GCB</span>
                    </div>
                  )}
                </Link>
                <CardHeader>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {post.categories.map((cat) => (
                      <Badge key={cat.id} variant="muted" className="text-xs">
                        {cat.name}
                      </Badge>
                    ))}
                  </div>
                  <CardTitle className="line-clamp-2">
                    <Link href={`/insights/${post.slug}`} className="hover:text-primary transition-colors">
                      {post.title}
                    </Link>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {post.excerpt && (
                    <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                      {post.excerpt}
                    </p>
                  )}
                  <Link href={`/insights/${post.slug}`}>
                    <Button variant="link" className="p-0 h-auto text-primary">
                      Read more <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default function InsightsPage() {
  return (
    <Suspense fallback={
      <div className="container py-8">
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading Insights...</p>
        </div>
      </div>
    }>
      <InsightsContent />
    </Suspense>
  );
}
