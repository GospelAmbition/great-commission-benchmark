import { NewsletterOffer } from "@/components/marketing/NewsletterOffer";
import { QuickRankings } from "@/components/home/QuickRankings";
import { RecentTestsList } from "@/components/recent-tests/RecentTestsList";
import { apiClient, type LeaderboardItem, type RecentTestItem, type StatsResponse } from "@/lib/api";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BarChart3, BookOpen, ChevronRight, Clock3 } from "lucide-react";
import { HomeHero } from "@/components/home/HomeHero";

interface HomeRanking {
  rank: number;
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

async function loadRankings(): Promise<HomeRanking[]> {
  try {
    // Fetch only the ends of the leaderboard: top 5, and bottom 5 via ascending sort.
    // The bottom query over-fetches because the client drops zero-score entries.
    const [top, bottom] = await Promise.all([
      apiClient.getLeaderboard({ limit: 5, sort: "score", order: "desc" }),
      apiClient.getLeaderboard({ limit: 10, sort: "score", order: "asc" }),
    ]);
    if (!top?.items?.length) return [];
    const toRanking = (item: LeaderboardItem, rank: number): HomeRanking => ({
      rank,
      model_id: item.model_id,
      model_name: item.model_name,
      provider: item.provider,
      score: item.overall_score,
    });
    const top5 = top.items.map((item, index) => toRanking(item, index + 1));
    const top5Ids = new Set(top5.map((r) => r.model_id));
    // Zero-score entries sort last in descending order, so they don't shift the
    // rank of any scored model: descending rank = total - ascending rank + 1.
    const bottom5 = bottom.items
      .slice(0, 5)
      .reverse()
      .filter((item) => !top5Ids.has(item.model_id))
      .map((item) => toRanking(item, bottom.total - (item.rank ?? 0) + 1));
    return [...top5, ...bottom5];
  } catch (error) {
    console.error("Failed to load homepage rankings:", error);
    return [];
  }
}

async function loadStats(): Promise<StatsResponse | null> {
  try {
    return await apiClient.getStats();
  } catch (error) {
    console.error("Failed to load homepage stats:", error);
    return null;
  }
}

async function loadRecentTests(): Promise<{ items: RecentTestItem[]; error: string | null }> {
  try {
    const response = await apiClient.getRecentTests(5);
    return { items: response.items || [], error: null };
  } catch (error) {
    console.error("Failed to load recent tests:", error);
    return { items: [], error: "Recent tests could not be loaded. Please try again shortly." };
  }
}

// Render per request so data is never frozen at build time.
export const dynamic = "force-dynamic";

export default async function Home() {
  const [rankings, stats, recent] = await Promise.all([loadRankings(), loadStats(), loadRecentTests()]);

  return (
    <div className="flex flex-col">
      <HomeHero />

      {/* Quick Rankings */}
      <section className="container py-12">
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-foreground">Leaderboard Top and Bottom</h2>
          </div>
          <p className="text-muted-foreground">
            Top and bottom of the benchmark.
          </p>
        </div>

        <QuickRankings rankings={rankings} />
      </section>

      {/* Recent Tests */}
      <section className="container pb-12">
        <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <div className="mb-2 flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2">
                <Clock3 className="h-5 w-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">Recent Tests</h2>
            </div>
            <p className="text-muted-foreground">
              The newest models evaluated on the current benchmark.
            </p>
          </div>
          <Button asChild variant="outline" size="sm" className="w-fit">
            <Link href="/recent-tests">
              View all recent tests
              <ChevronRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </div>
        <RecentTestsList items={recent.items} error={recent.error} />
      </section>
      <section className="container pb-12"><NewsletterOffer source="home_results" /></section>

      {/* Stats Banner */}
      {stats && (
        <section className="border-y border-white/[0.06] bg-surface">
          <div className="container">
            <div className="grid grid-cols-3">
              <div className="text-center py-6 md:py-8">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stats.total_models_tested}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Models Tested</div>
              </div>
              <div className="text-center py-6 md:py-8 border-l border-white/[0.06]">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stats.providers_represented}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Providers</div>
              </div>
              <div className="text-center py-6 md:py-8 border-l border-white/[0.06]">
                <div className="text-3xl md:text-4xl font-bold text-primary mb-1">{stats.current_benchmark_version}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Current Benchmark Version</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* The Challenge */}
      <section className="border-t border-white/[0.06] bg-surface py-12">
        <div className="container">
          <div className="rounded-lg border border-white/[0.08] bg-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <BookOpen className="h-5 w-5 text-foreground" />
              <h3 className="text-xl text-foreground">Programmed Resistance to the Great Commission</h3>
            </div>
            
            <p className="text-sm text-foreground leading-relaxed mb-6">
              Current AI systems often have guardrails that restrict religious content deemed &ldquo;coercive,&rdquo; proselytizing activities, exclusive truth claims, and content that challenges other worldviews. While well-intentioned, these guardrails can impede legitimate religious activity that is protected speech and central to Christian practice worldwide.
            </p>
            
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="flex-1 p-4 rounded-lg border border-white/[0.08]">
                  <p className="text-sm text-foreground leading-relaxed">
                    &ldquo;Go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and teaching them to obey everything I have commanded you.&rdquo;
                  </p>
                  <p className="mt-2 text-sm text-foreground italic">— Matthew 28:19-20</p>
                </div>
                
                <span className="text-3xl text-foreground shrink-0 font-bold">vs.</span>
                
                <div className="flex-1 p-4 rounded-lg border border-white/[0.08]">
                  <p className="text-sm text-foreground leading-relaxed">
                    &ldquo;Disallowed content: Advice or instructions on influencing the religious or political views of a specific individual or demographic group.&rdquo;
                  </p>
                  <p className="mt-2 text-sm text-foreground italic">— Internal AI Provider Policy</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


    </div>
  );
}
