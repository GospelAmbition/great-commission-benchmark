"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TopPerformers } from "@/components/home/TopPerformers";
import { QuickRankings } from "@/components/home/QuickRankings";
import { apiClient, StatsResponse } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";

export default function Home() {
  const [topPerformers, setTopPerformers] = useState<any[]>([]);
  const [rankings, setRankings] = useState<any[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Load top 3 performers
        const leaderboard = await apiClient.getLeaderboard({ limit: 3 });
        if (leaderboard?.items) {
          setTopPerformers(
            leaderboard.items.map((item, index) => ({
              rank: index + 1,
              model_id: item.model_id,
              model_name: item.model_name,
              provider: item.provider,
              score: item.overall_score,
            }))
          );
        }

        // Load top 10 for quick rankings
        const top10 = await apiClient.getLeaderboard({ limit: 10 });
        if (top10?.items) {
          setRankings(
            top10.items.map((item, index) => ({
              rank: index + 1,
              model_id: item.model_id,
              model_name: item.model_name,
              provider: item.provider,
              score: item.overall_score,
            }))
          );
        }

        // Load stats
        const platformStats = await apiClient.getStats();
        setStats(platformStats);
      } catch (error) {
        console.error("Failed to load homepage data:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <div className="flex flex-col">
      {/* Top Performers */}
      <section className="container py-12">
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold">Top Performers</h2>
            <p className="mt-2 text-muted-foreground">
              Models best equipped for Great Commission work
            </p>
          </div>
          {loading ? (
            <div className="grid gap-6 md:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-8 w-8" />
                    <Skeleton className="h-6 w-32 mt-4" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-12 w-20 mb-4" />
                    <Skeleton className="h-10 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <TopPerformers performers={topPerformers} />
          )}
        </div>
      </section>

      {/* Quick Rankings */}
      <section className="container pt-3 pb-12">
        <Card>
          <CardHeader>
            <CardTitle>Quick Rankings (Top 10)</CardTitle>
            <CardDescription>
              See how models compare across the benchmark
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <QuickRankings rankings={rankings} />
            )}
          </CardContent>
        </Card>
      </section>

      {/* Stats Banner */}
      {stats && (
        <section className="container py-8">
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-3xl font-bold text-center">{stats.total_models_tested}</div>
                <div className="text-sm text-muted-foreground text-center">Models Tested</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-3xl font-bold text-center">{stats.total_test_runs}</div>
                <div className="text-sm text-muted-foreground text-center">Test Runs</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-3xl font-bold text-center">{stats.top_score.toFixed(1)}</div>
                <div className="text-sm text-muted-foreground text-center">Top Score</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-3xl font-bold text-center">{stats.providers_represented}</div>
                <div className="text-sm text-muted-foreground text-center">Providers</div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* What We Test */}
      <section className="container py-12">
        <div className="grid gap-8 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>What We Test (70/20/10)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold text-lg mb-2">
                  TASK CAPABILITY (70%)
                </h3>
                <p className="text-muted-foreground mb-2">Can it do the work?</p>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Evangelism & outreach</li>
                  <li>Apologetics & defense</li>
                  <li>Discipleship tools</li>
                  <li>Missiological research</li>
                  <li>Prayer resources</li>
                  <li>Scripture processing</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">
                  DOCTRINAL (20%)
                </h3>
                <p className="text-muted-foreground">
                  Does it stay theologically accurate and faithful?
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">
                  WORLDVIEW (10%)
                </h3>
                <p className="text-muted-foreground">
                  Will it affirm Christian truth claims when asked?
                </p>
              </div>
              <Button asChild variant="outline" className="w-full">
                <Link href="/about">Learn About Methodology →</Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>The Challenge</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <blockquote className="border-l-4 border-[--ga-red] pl-4 italic">
                "All authority in heaven and on earth has been given to me. Therefore go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and teaching them to obey everything I have commanded you. And surely I am with you always, to the very end of the age." — Matthew 28:18-20
              </blockquote>
              <div className="text-center text-muted-foreground">vs.</div>
              <blockquote className="border-l-4 border-muted pl-4 italic text-muted-foreground">
                "Disallowed: Advice on influencing religious views..." — AI Provider Policy
              </blockquote>
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Many AI models are programmed to resist the very work of the Great Commission.
                  They may have excellent Christian knowledge, but refuse to help with evangelism,
                  apologetics, or persuasive outreach.
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  This benchmark measures which models will actually help you make disciples—not just
                  answer Bible trivia.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-12">
        <Card className="bg-[--ga-accent-red] border-[--ga-light-red]">
          <CardHeader>
            <CardTitle>Become a Tester</CardTitle>
            <CardDescription>
              Help measure AI models for Great Commission work. Use our GCB Runner to run tests on any model—including 
              local and fine-tuned models. Results are verified by moderators and added to the leaderboard.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button asChild size="lg" variant="brand">
              <Link href="/dashboard">Get Started →</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/runner">Learn About GCB Runner</Link>
            </Button>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
