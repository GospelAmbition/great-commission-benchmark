"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TopPerformers } from "@/components/home/TopPerformers";
import { QuickRankings } from "@/components/home/QuickRankings";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";

export default function Home() {
  const [topPerformers, setTopPerformers] = useState<any[]>([]);
  const [rankings, setRankings] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Load top 3 performers
        const leaderboard = await apiClient.getLeaderboard({ limit: 3 });
        if (leaderboard.items) {
          setTopPerformers(
            leaderboard.items.map((item: any, index: number) => ({
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
        if (top10.items) {
          setRankings(
            top10.items.map((item: any, index: number) => ({
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
      {/* Hero Section */}
      <section className="container py-16 md:py-24">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
            The Great Commission Benchmark
          </h1>
          <p className="mt-6 text-xl text-muted-foreground">
            Which AI models can actually help you make disciples?
          </p>
          <p className="mt-4 text-lg text-muted-foreground">
            We test AI for real missionary work—evangelism, apologetics, discipleship tools, and
            more. Not just knowledge, but obedience to the Great Commission.
          </p>
          {stats && (
            <div className="mt-8 flex items-center justify-center gap-4 text-sm text-muted-foreground">
              <span>
                {stats.total_models || 0} models tested
              </span>
              <span>•</span>
              <span>
                Last updated: {stats.last_updated ? new Date(stats.last_updated).toLocaleDateString() : "N/A"}
              </span>
            </div>
          )}
          <div className="mt-10 flex items-center justify-center gap-4">
            <Button asChild size="lg" className="bg-[--ga-red] hover:bg-[--ga-dark-red]">
              <Link href="/research">View Rankings ↓</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/about">Learn Why This Matters →</Link>
            </Button>
          </div>
        </div>
      </section>

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
      <section className="container py-12">
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
                "Go and make disciples of all nations..." — Matthew 28:19
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
            <CardTitle>Ready to Test a Model?</CardTitle>
            <CardDescription>
              Contribute to the benchmark by running a test on any AI model. Results are verified
              by moderators and added to the leaderboard.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="lg" className="bg-[--ga-red] hover:bg-[--ga-dark-red]">
              <Link href="/tests/new">Run a Test →</Link>
            </Button>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
