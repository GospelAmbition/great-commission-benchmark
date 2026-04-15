"use client";

import { useEffect, useState, Suspense, useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ChevronRight, Search, X, ChevronLeft, LayoutGrid, List } from "lucide-react";
import { ArticleIcon } from "@/lib/icons";
import { GuardrailsAnimation } from "@/components/home/GuardrailsAnimation";

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
  const router = useRouter();
  const pathname = usePathname();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  
  // Initialize state from URL params synchronously
  const categoryParam = searchParams.get("category");
  const searchParam = searchParams.get("search");
  const pageParam = searchParams.get("page");
  
  const [selectedCategory, setSelectedCategory] = useState<string>(
    () => categoryParam || "all"
  );
  const [searchQuery, setSearchQuery] = useState<string>(
    () => searchParam || ""
  );
  const [currentPage, setCurrentPage] = useState<number>(() => {
    if (pageParam) {
      const page = parseInt(pageParam, 10);
      return page > 0 ? page : 1;
    }
    return 1;
  });
  
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const pageSize = 50;
  const isInitialized = useRef(false);
  const prevCategoryRef = useRef<string | null>(null);
  const prevSearchRef = useRef<string | null>(null);
  const isUpdatingUrlRef = useRef(false);

  useEffect(() => {
    loadCategories();
  }, []);

  // Initial load after state is initialized from URL params
  useEffect(() => {
    if (!isInitialized.current) {
      isInitialized.current = true;
      prevCategoryRef.current = selectedCategory;
      prevSearchRef.current = searchQuery;
      loadPosts();
    }
  }, []);

  // Update state when URL params change (e.g., browser back/forward) - but only after initial load
  useEffect(() => {
    if (!isInitialized.current || isUpdatingUrlRef.current) {
      isUpdatingUrlRef.current = false; // Reset flag after skipping
      return;
    }
    
    const newCategoryParam = searchParams.get("category");
    const newSearchParam = searchParams.get("search");
    const newPageParam = searchParams.get("page");
    
    // Only update state if URL params differ from current state
    // This handles browser navigation (back/forward) but not our own URL updates
    if (newCategoryParam !== selectedCategory) {
      setSelectedCategory(newCategoryParam || "all");
    }
    
    if (newSearchParam !== searchQuery) {
      setSearchQuery(newSearchParam || "");
    }
    
    // Only update page if URL param differs from current state
    if (newPageParam) {
      const pageFromUrl = parseInt(newPageParam, 10);
      if (pageFromUrl > 0 && pageFromUrl !== currentPage) {
        setCurrentPage(pageFromUrl);
      }
    }
  }, [searchParams]); // Only depend on searchParams - sync FROM URL TO state

  useEffect(() => {
    // Reset to page 1 when filters change (but not on initial load)
    if (isInitialized.current && 
        (prevCategoryRef.current !== null || prevSearchRef.current !== null) &&
        (prevCategoryRef.current !== selectedCategory || prevSearchRef.current !== searchQuery)) {
      setCurrentPage(1);
    }
    prevCategoryRef.current = selectedCategory;
    prevSearchRef.current = searchQuery;
  }, [selectedCategory, searchQuery]);

  useEffect(() => {
    // Load posts when filters or page change (but not on initial mount)
    if (isInitialized.current) {
      loadPosts();
    }
  }, [selectedCategory, searchQuery, currentPage]);

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
      params.append("limit", pageSize.toString());
      params.append("offset", ((currentPage - 1) * pageSize).toString());
      
      // Update URL without reload using Next.js router
      isUpdatingUrlRef.current = true; // Flag that we're updating URL ourselves
      const urlParams = new URLSearchParams();
      if (selectedCategory && selectedCategory !== "all") {
        urlParams.set("category", selectedCategory);
      }
      if (searchQuery) {
        urlParams.set("search", searchQuery);
      }
      if (currentPage > 1) {
        urlParams.set("page", currentPage.toString());
      }
      const newUrl = urlParams.toString() 
        ? `${pathname}?${urlParams.toString()}`
        : pathname;
      router.replace(newUrl, { scroll: false });
      
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
        
        {/* Guardrails Animation - positioned on right */}
        <div className="hidden lg:block absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none">
          <GuardrailsAnimation />
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
          
          <div className="flex items-center gap-4">
            <p className="text-sm text-muted-foreground">
              {total} {total === 1 ? "article" : "articles"}
            </p>
            <div className="flex items-center border rounded-lg">
              <Button 
                variant={viewMode === "grid" ? "secondary" : "ghost"} 
                size="sm" 
                onClick={() => setViewMode("grid")}
                className="rounded-r-none"
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button 
                variant={viewMode === "list" ? "secondary" : "ghost"} 
                size="sm" 
                onClick={() => setViewMode("list")}
                className="rounded-l-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Posts Grid/List */}
        {loading ? (
          viewMode === "grid" ? (
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
          ) : (
            <div className="flex flex-col gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="flex flex-col sm:flex-row overflow-hidden">
                  <Skeleton className="h-32 sm:h-auto sm:w-48 flex-shrink-0" />
                  <div className="flex-1 p-4">
                    <Skeleton className="h-4 w-20 mb-2" />
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-2/3 mt-1" />
                  </div>
                </Card>
              ))}
            </div>
          )
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
        ) : viewMode === "grid" ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden group border-glow">
                <Link href={`/insights/${post.slug}`}>
                  {post.featured_image_url ? (
                    <div className="relative h-48 w-full bg-white/[0.02] overflow-hidden">
                      {/* Blurred background */}
                      <div className="absolute inset-0">
                        <Image
                          src={post.featured_image_url}
                          alt=""
                          fill
                          className="object-cover blur-xl scale-110 opacity-40"
                          unoptimized
                          aria-hidden="true"
                        />
                      </div>
                      {/* Main image centered */}
                      <div className="relative h-full w-full flex items-center justify-center">
                        <div className="relative h-full w-auto max-w-full">
                          <img
                            src={post.featured_image_url}
                            alt={post.title}
                            className="h-full w-auto max-w-full object-contain"
                            loading="lazy"
                          />
                        </div>
                      </div>
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
        ) : (
          <div className="flex flex-col gap-4">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden group border-glow">
                <Link href={`/insights/${post.slug}`} className="flex flex-col sm:flex-row">
                  {/* Thumbnail */}
                  {post.featured_image_url ? (
                    <div className="relative h-32 sm:h-auto sm:w-48 flex-shrink-0 bg-white/[0.02] overflow-hidden">
                      {/* Blurred background */}
                      <div className="absolute inset-0">
                        <Image
                          src={post.featured_image_url}
                          alt=""
                          fill
                          className="object-cover blur-xl scale-110 opacity-40"
                          unoptimized
                          aria-hidden="true"
                        />
                      </div>
                      {/* Main image centered */}
                      <div className="relative h-full w-full flex items-center justify-center">
                        <img
                          src={post.featured_image_url}
                          alt={post.title}
                          className="h-full w-auto max-w-full object-contain"
                          loading="lazy"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="h-32 sm:h-auto sm:w-48 flex-shrink-0 bg-gradient-to-br from-primary/10 to-white/[0.02] flex items-center justify-center">
                      <span className="text-2xl font-bold text-primary/20">GCB</span>
                    </div>
                  )}
                  {/* Content */}
                  <div className="flex-1 p-4 flex flex-col justify-center">
                    <div className="flex flex-wrap gap-2 mb-2">
                      {post.categories.map((cat) => (
                        <Badge key={cat.id} variant="muted" className="text-xs">
                          {cat.name}
                        </Badge>
                      ))}
                    </div>
                    <h3 className="font-semibold line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                      {post.title}
                    </h3>
                    {post.excerpt && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {post.excerpt}
                      </p>
                    )}
                  </div>
                </Link>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {!loading && posts.length > 0 && total > pageSize && (
          <div className="mt-8 flex items-center justify-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.ceil(total / pageSize) }, (_, i) => i + 1)
                .filter(page => {
                  const totalPages = Math.ceil(total / pageSize);
                  // Show first, last, current, and pages around current
                  return (
                    page === 1 ||
                    page === totalPages ||
                    Math.abs(page - currentPage) <= 1
                  );
                })
                .reduce((acc: (number | string)[], page, i, arr) => {
                  // Add ellipsis between non-consecutive pages
                  if (i > 0 && page - (arr[i - 1] as number) > 1) {
                    acc.push("...");
                  }
                  acc.push(page);
                  return acc;
                }, [])
                .map((item, i) =>
                  typeof item === "string" ? (
                    <span key={`ellipsis-${i}`} className="px-2 text-muted-foreground">
                      {item}
                    </span>
                  ) : (
                    <Button
                      key={item}
                      variant={item === currentPage ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentPage(item)}
                      className="min-w-[2.5rem]"
                    >
                      {item}
                    </Button>
                  )
                )}
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= Math.ceil(total / pageSize)}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
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
