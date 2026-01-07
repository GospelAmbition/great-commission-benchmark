"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { QuickRankings } from "@/components/home/QuickRankings";
import { apiClient, StatsResponse } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowRight, BarChart3, BookOpen, Shield, Users } from "lucide-react";

export default function Home() {
  const [rankings, setRankings] = useState<any[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
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
      {/* Hero Section */}
      <section 
        className="relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
      >
        {/* Decorative background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white/20 rounded-full -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-white/10 rounded-full translate-x-1/3 translate-y-1/3" />
        </div>
        
        <div className="container relative py-12 md:py-16">
          <div className="max-w-3xl">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
              Evaluating AI for the
              <span className="block text-white/90">Great Commission</span>
            </h1>
            <p className="text-lg md:text-xl text-white/80 mb-6 max-w-2xl">
              Which AI models will actually help you make disciples? 
              We measure task capability, doctrinal fidelity, and worldview alignment.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button asChild size="lg" className="bg-white text-red-700 hover:bg-slate-100 font-semibold shadow-lg">
                <Link href="/research">
                  View Rankings
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild size="lg" className="border-2 border-white/40 bg-transparent text-white hover:bg-white/10 hover:border-white/60">
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Banner */}
      {stats && (
        <section className="bg-info py-6">
          <div className="container">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center py-3">
                <div className="text-2xl md:text-3xl font-bold text-info-foreground">{stats.total_models_tested}</div>
                <div className="text-xs md:text-sm text-info-muted">Models Tested</div>
              </div>
              <div className="text-center py-3 border-l border-info-border">
                <div className="text-2xl md:text-3xl font-bold text-info-foreground">{stats.providers_represented}</div>
                <div className="text-xs md:text-sm text-info-muted">Providers</div>
              </div>
              <div className="text-center py-3 border-l border-info-border">
                <div className="text-2xl md:text-3xl font-bold text-info-foreground">{stats.total_test_runs}</div>
                <div className="text-xs md:text-sm text-info-muted">Community Tests</div>
              </div>
              <div className="text-center py-3 border-l border-info-border">
                <div className="text-2xl md:text-3xl font-bold text-info-foreground">{stats.current_benchmark_version}</div>
                <div className="text-xs md:text-sm text-info-muted">Current Version</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Quick Rankings */}
      <section className="container py-8">
        <Card className="overflow-hidden pt-0">
          <CardHeader className="bg-red-50 border-b border-red-100 py-4 rounded-t-xl">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-red-700" />
              <CardTitle className="text-slate-900">Quick Rankings (Top 10)</CardTitle>
            </div>
            <CardDescription className="text-slate-600">
              See how models compare across the benchmark
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : (
              <QuickRankings rankings={rankings} />
            )}
          </CardContent>
        </Card>
      </section>

      {/* What We Test & The Challenge */}
      <section className="bg-slate-50 py-8">
        <div className="container">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* What We Test */}
            <Card className="h-full bg-white">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-slate-900">What We Test (70/20/10)</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 rounded-lg bg-red-50 border border-red-100">
                  <h3 className="font-semibold text-base text-slate-900 mb-1 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-8 h-5 rounded bg-red-700 text-white text-xs font-bold">70%</span>
                    TASK CAPABILITY
                  </h3>
                  <p className="text-slate-600 text-sm mb-2">Can it do the work?</p>
                  <ul className="grid grid-cols-2 gap-1 text-xs text-slate-600">
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Evangelism & outreach</li>
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Apologetics & defense</li>
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Discipleship tools</li>
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Missiological research</li>
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Prayer resources</li>
                    <li className="flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-700" />Scripture processing</li>
                  </ul>
                </div>
                <div className="flex gap-3">
                  <div className="flex-1 p-3 rounded-lg">
                    <h3 className="font-semibold text-sm text-slate-900 mb-1 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-8 h-5 rounded bg-slate-800 text-white text-xs font-bold">20%</span>
                      DOCTRINAL
                    </h3>
                    <p className="text-slate-600 text-xs">
                      Theologically accurate and faithful?
                    </p>
                  </div>
                  <div className="flex-1 p-3 rounded-lg">
                    <h3 className="font-semibold text-sm text-slate-900 mb-1 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-8 h-5 rounded bg-slate-500 text-white text-xs font-bold">10%</span>
                      WORLDVIEW
                    </h3>
                    <p className="text-slate-600 text-xs">
                      Affirms Christian truth claims?
                    </p>
                  </div>
                </div>
                <Button asChild variant="brand-outline" className="w-full">
                  <Link href="/about">Learn About Methodology →</Link>
                </Button>
              </CardContent>
            </Card>

            {/* The Challenge */}
            <Card className="h-full bg-white">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-slate-900">The Challenge</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <blockquote className="relative pl-4 border-l-4 border-red-700">
                  <p className="text-sm font-semibold text-slate-900 leading-relaxed">
                    &ldquo;Go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and teaching them to obey everything I have commanded you.&rdquo;
                  </p>
                  <footer className="mt-2 text-xs text-red-700 font-bold tracking-wide uppercase">— Matthew 28:19-20</footer>
                </blockquote>
                
                <div className="flex items-center gap-2 text-slate-400 text-sm">
                  <div className="flex-1 h-px bg-slate-200" />
                  <span className="font-medium">vs.</span>
                  <div className="flex-1 h-px bg-slate-200" />
                </div>
                
                <blockquote className="pl-4 border-l-4 border-slate-300">
                  <p className="text-sm italic text-slate-500 leading-relaxed">
                    &ldquo;Disallowed: Advice on influencing religious views...&rdquo;
                  </p>
                  <footer className="mt-2 text-xs text-slate-400 font-medium">— AI Provider Policy</footer>
                </blockquote>
                
                <div className="p-3 rounded-lg border border-slate-200 bg-white">
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Many AI models are programmed to resist the Great Commission. 
                    This benchmark measures which models will actually help you make disciples—not just answer Bible trivia.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-8">
        <div className="container">
          <Card 
            className="border-0 text-white overflow-hidden relative"
            style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
          >
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full translate-x-1/3 -translate-y-1/3" />
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full -translate-x-1/2 translate-y-1/2" />
            
            <CardHeader className="relative">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-white/80" />
                <CardTitle className="text-white text-xl">Become a Tester</CardTitle>
              </div>
              <CardDescription className="text-white/80 text-base">
                Help measure AI models for Great Commission work. Use our GCB Runner to run tests on any model—including 
                local and fine-tuned models. Results are verified by moderators and added to the leaderboard.
              </CardDescription>
            </CardHeader>
            <CardContent className="relative flex flex-wrap gap-3">
              <Button asChild size="lg" className="bg-white text-red-700 hover:bg-slate-100 font-semibold shadow-lg">
                <Link href="/dashboard">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild size="lg" className="border-2 border-white/40 bg-transparent text-white hover:bg-white/10 hover:border-white/60">
                <Link href="/runner">Learn About GCB Runner</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
