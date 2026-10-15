import { getBlogCategories, getBlogPosts } from "@/lib/server-data";
import { INSIGHTS_PAGE_SIZE } from "./constants";
import { InsightsContent, type InsightsInitialData } from "./insights-content";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function param(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

async function loadInitialData(searchParams: Awaited<SearchParams>): Promise<InsightsInitialData | null> {
  const category = param(searchParams.category);
  const pageNumber = parseInt(param(searchParams.page) || "1", 10);
  const page = pageNumber > 0 ? pageNumber : 1;
  try {
    const [posts, categories] = await Promise.all([
      getBlogPosts({
        category: category && category !== "all" ? category : undefined,
        search: param(searchParams.search),
        model_id: param(searchParams.model_id),
        provider: param(searchParams.provider),
        limit: INSIGHTS_PAGE_SIZE,
        offset: (page - 1) * INSIGHTS_PAGE_SIZE,
      }),
      getBlogCategories(),
    ]);
    return { posts: posts.items, total: posts.total, categories };
  } catch (error) {
    // Fall back to the client fetching the posts itself.
    console.error("Failed to load insights:", error);
    return null;
  }
}

export default async function InsightsPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const initialData = await loadInitialData(params);
  // Remount on server navigations with new params so state matches the new data.
  return <InsightsContent key={JSON.stringify(params)} initialData={initialData} />;
}
