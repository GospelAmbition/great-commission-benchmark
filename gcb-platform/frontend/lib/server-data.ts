/**
 * Server-side data loaders for server-rendered public pages.
 *
 * Fetches go straight to the backend (no Next.js proxy hop) with
 * `cache: "no-store"`: the backend's Redis cache is the source of truth,
 * matching the leaderboard and model pages. Each loader is wrapped in
 * React `cache()` so a layout/generateMetadata and its page share one
 * request per render.
 */
import { cache } from "react";
import { API_URL, apiClient, type BlogCategory, type BlogPost } from "@/lib/api";

export interface PublicBlogRelatedModel {
  id: string;
  model_id: string;
  name: string;
  provider: string;
}

// Author email is returned by the public API but must never be embedded in
// server-rendered HTML, where crawlers would index it.
export type PublicBlogPost = Omit<BlogPost, "author"> & {
  author: { id: string; name?: string };
  related_models?: PublicBlogRelatedModel[];
};

function toPublicPost(post: BlogPost & { related_models?: PublicBlogRelatedModel[] }): PublicBlogPost {
  return { ...post, author: { id: post.author?.id, name: post.author?.name } };
}

async function getJson<T>(path: string): Promise<T | null> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`${path} failed with ${response.status}`);
  return response.json();
}

/** Published post by slug, or null when it doesn't exist. */
export const getBlogPost = cache(async (slug: string): Promise<PublicBlogPost | null> => {
  const post = await getJson<BlogPost>(`/api/blog/posts/${encodeURIComponent(slug)}`);
  return post ? toPublicPost(post) : null;
});

export interface BlogPostsQuery {
  category?: string;
  search?: string;
  model_id?: string;
  provider?: string;
  limit: number;
  offset: number;
}

export async function getBlogPosts(query: BlogPostsQuery): Promise<{ items: PublicBlogPost[]; total: number }> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const data = await getJson<{ items: BlogPost[]; total: number }>(`/api/blog/posts?${params}`);
  return { items: (data?.items || []).map(toPublicPost), total: data?.total || 0 };
}

export const getBlogCategories = cache(async (): Promise<BlogCategory[]> => {
  const data = await getJson<{ items: BlogCategory[] }>("/api/blog/categories");
  return data?.items || [];
});

/** Leaderboard entries for one provider (shared by generateMetadata and the page). */
export const getProviderModels = cache((provider: string) =>
  apiClient.getLeaderboard({ provider, limit: 200 })
);

/** Leaderboard entries for one category, best category score first. */
export const getCategoryModels = cache((category: string) =>
  apiClient.getLeaderboard({ category, limit: 50, sort: "score", order: "desc" })
);
