import { Clock3 } from "lucide-react";
import { RecentTestsList } from "@/components/recent-tests/RecentTestsList";
import { API_URL, type RecentTestsResponse } from "@/lib/api";
import { getCanonicalUrl } from "@/lib/seo";
import {
  buildBreadcrumbSchema,
  buildItemListSchema,
  JsonLdScript,
} from "@/lib/structured-data";

async function loadRecentTests(): Promise<{
  data: RecentTestsResponse | null;
  error: string | null;
}> {
  try {
    const response = await fetch(`${API_URL}/api/public/recent-tests?limit=50`, {
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`Recent tests request failed with ${response.status}`);
    return { data: await response.json(), error: null };
  } catch {
    return { data: null, error: "Recent tests could not be loaded. Please try again shortly." };
  }
}

export default async function RecentTestsPage() {
  const { data, error } = await loadRecentTests();
  const items = data?.items || [];
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: "Home", path: "/" },
    { name: "Recent Tests", path: "/recent-tests" },
  ]);
  const itemListSchema = buildItemListSchema(
    items.map((item, index) => ({
      name: item.model.name,
      url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(item.model.model_id)}`),
      position: index + 1,
      description: `${item.model.name} scored ${item.score.toFixed(1)}% and is ranked #${item.rank} on the current Great Commission Benchmark.`,
    }))
  );

  return (
    <div className="flex flex-col">
      <JsonLdScript data={items.length > 0 ? [breadcrumbSchema, itemListSchema] : breadcrumbSchema} />

      <section className="relative overflow-hidden border-b border-white/[0.06]">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute right-0 top-1/2 h-96 w-96 -translate-y-1/2 gradient-red-glow opacity-40" />
        <div className="container relative py-10 md:py-14">
          <div className="mb-3 flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <Clock3 className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-3xl font-light text-foreground md:text-4xl">Recent Tests</h1>
          </div>
          <p className="max-w-2xl font-light leading-relaxed text-muted-foreground">
            The newest models evaluated on the current Great Commission Benchmark, with their latest scores and overall leaderboard ranks.
          </p>
          {data?.current_version && (
            <p className="mt-3 text-sm text-muted-foreground">
              Current benchmark version: {data.current_version}
            </p>
          )}
        </div>
      </section>

      <section className="container py-8 md:py-10">
        <RecentTestsList items={items} error={error} />
      </section>
    </div>
  );
}
