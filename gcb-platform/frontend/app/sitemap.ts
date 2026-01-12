/**
 * Dynamic Sitemap Generator
 * Generates sitemap.xml with all public pages and dynamic routes
 */

import { MetadataRoute } from "next";
import { getBaseUrl } from "@/lib/seo";
import { API_URL } from "@/lib/api";

// Static pages with their priorities and change frequencies
const staticPages: {
  path: string;
  priority: number;
  changeFrequency: MetadataRoute.Sitemap[0]["changeFrequency"];
}[] = [
  { path: "", priority: 1.0, changeFrequency: "daily" },
  { path: "/leaderboard", priority: 0.9, changeFrequency: "daily" },
  { path: "/about", priority: 0.8, changeFrequency: "weekly" },
  { path: "/categories", priority: 0.8, changeFrequency: "weekly" },
  { path: "/contribute", priority: 0.7, changeFrequency: "monthly" },
  { path: "/contribute/support", priority: 0.6, changeFrequency: "monthly" },
  { path: "/faq", priority: 0.7, changeFrequency: "monthly" },
  { path: "/contact", priority: 0.5, changeFrequency: "monthly" },
  { path: "/runner", priority: 0.7, changeFrequency: "monthly" },
  { path: "/sponsor", priority: 0.6, changeFrequency: "monthly" },
  { path: "/newsletter", priority: 0.5, changeFrequency: "monthly" },
  { path: "/insights", priority: 0.8, changeFrequency: "weekly" },
  { path: "/privacy", priority: 0.3, changeFrequency: "yearly" },
  { path: "/terms", priority: 0.3, changeFrequency: "yearly" },
  { path: "/tester-agreement", priority: 0.3, changeFrequency: "yearly" },
];

// Fetch models from API for dynamic routes
async function fetchModels(): Promise<
  { model_id: string; updated_at?: string }[]
> {
  try {
    const response = await fetch(`${API_URL}/api/public/leaderboard?limit=1000`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    if (!response.ok) return [];

    const data = await response.json();
    return (data.entries || []).map(
      (entry: { model?: { model_id?: string }; updated_at?: string }) => ({
        model_id: entry.model?.model_id || "",
        updated_at: entry.updated_at,
      })
    );
  } catch {
    return [];
  }
}

// Fetch categories from API
async function fetchCategories(): Promise<string[]> {
  try {
    const response = await fetch(`${API_URL}/api/public/filter-options`, {
      next: { revalidate: 86400 }, // Cache for 24 hours
    });
    if (!response.ok) return [];

    const data = await response.json();
    return data.categories || [];
  } catch {
    return [];
  }
}

// Fetch published blog posts
async function fetchBlogPosts(): Promise<
  { slug: string; published_at?: string }[]
> {
  try {
    const response = await fetch(`${API_URL}/api/blog/posts?limit=1000`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    if (!response.ok) return [];

    const data = await response.json();
    return (data.items || []).map(
      (post: { slug: string; published_at?: string }) => ({
        slug: post.slug,
        published_at: post.published_at,
      })
    );
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = getBaseUrl();
  const now = new Date().toISOString();

  // Generate static page entries
  const staticEntries: MetadataRoute.Sitemap = staticPages.map((page) => ({
    url: `${baseUrl}${page.path}`,
    lastModified: now,
    changeFrequency: page.changeFrequency,
    priority: page.priority,
  }));

  // Fetch dynamic content in parallel
  const [models, categories, blogPosts] = await Promise.all([
    fetchModels(),
    fetchCategories(),
    fetchBlogPosts(),
  ]);

  // Generate model detail page entries
  const modelEntries: MetadataRoute.Sitemap = models
    .filter((m) => m.model_id)
    .map((model) => ({
      url: `${baseUrl}/leaderboard/models/${encodeURIComponent(model.model_id)}`,
      lastModified: model.updated_at || now,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));

  // Generate category page entries
  const categoryEntries: MetadataRoute.Sitemap = categories.map((category) => ({
    url: `${baseUrl}/categories/${encodeURIComponent(category)}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: 0.6,
  }));

  // Generate blog post entries
  const blogEntries: MetadataRoute.Sitemap = blogPosts
    .filter((p) => p.slug)
    .map((post) => ({
      url: `${baseUrl}/insights/${encodeURIComponent(post.slug)}`,
      lastModified: post.published_at || now,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    }));

  return [...staticEntries, ...modelEntries, ...categoryEntries, ...blogEntries];
}
