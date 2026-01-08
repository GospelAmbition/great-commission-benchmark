"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { QuickRankings } from "@/components/home/QuickRankings";
import { apiClient, StatsResponse } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowRight, BarChart3, BookOpen, Shield, Users } from "lucide-react";
import { TIER_CATEGORIES, CATEGORY_NAMES, TIER_INFO } from "@/lib/benchmark-definitions";
import { BenchmarkLegendModal } from "@/components/benchmark";

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
      <section className="relative overflow-hidden">
        {/* Background with subtle gradient */}
        <div className="absolute inset-0 gradient-hero" />
        
        {/* Red glow effect */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] gradient-red-glow opacity-30" />
        
        {/* Grid pattern overlay */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
        
        <div className="container relative py-16 md:py-24">
          <div className="max-w-3xl animate-fade-in-up">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight tracking-tight">
              Evaluating AI for the
              <span className="block text-primary">Great Commission</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl leading-relaxed">
              Which AI models will actually help you make disciples? 
              We measure task capability, doctrinal fidelity, and worldview alignment.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button asChild size="lg" variant="glow" className="group">
                <Link href="/research">
                  View Rankings
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Rankings */}
      <section className="container py-12">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <BarChart3 className="h-5 w-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">Leaderboard</h2>
            </div>
            <p className="text-muted-foreground">
              Top performing models on the Great Commission Benchmark
            </p>
          </div>
          <Button asChild variant="outline" className="hidden md:flex">
            <Link href="/research">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
        
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : (
          <QuickRankings rankings={rankings} />
        )}
        
        <div className="mt-6 text-center md:hidden">
          <Button asChild variant="outline">
            <Link href="/research">
              View Full Leaderboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Stats Banner */}
      {stats && (
        <section className="border-y border-white/[0.06] bg-surface">
          <div className="container">
            <div className="grid grid-cols-2 md:grid-cols-4">
              <div className="text-center py-6 md:py-8">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stats.total_models_tested}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Models Tested</div>
              </div>
              <div className="text-center py-6 md:py-8 border-l border-white/[0.06]">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stats.providers_represented}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Providers</div>
              </div>
              <div className="text-center py-6 md:py-8 border-l border-white/[0.06]">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stats.total_test_runs}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Community Tests</div>
              </div>
              <div className="text-center py-6 md:py-8 border-l border-white/[0.06]">
                <div className="text-3xl md:text-4xl font-bold text-primary mb-1">{stats.current_benchmark_version}</div>
                <div className="text-xs md:text-sm text-muted-foreground uppercase tracking-wider">Current Version</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* What We Test & The Challenge */}
      <section className="border-t border-white/[0.06] bg-surface py-12">
        <div className="container">
          <div className="grid gap-8 lg:grid-cols-2">
            {/* What We Test */}
            <div className="rounded-lg border border-white/[0.08] bg-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Shield className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-foreground">What We Test (70/20/10)</h3>
                  <p className="text-sm text-muted-foreground">19 categories across 3 tiers</p>
                </div>
              </div>
              
              <div className="space-y-4">
                {/* Tier 1 */}
                <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/10">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="px-2 py-0.5 rounded bg-primary text-white text-xs font-bold">70%</span>
                    <h4 className="font-semibold text-foreground">Task Capability</h4>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">Can the AI complete practical ministry tasks?</p>
                  <div className="flex flex-wrap gap-1.5">
                    {TIER_CATEGORIES[1].map((code) => (
                      <span key={code} className="px-2 py-0.5 rounded bg-white/5 text-xs text-muted-foreground">
                        {CATEGORY_NAMES[code]}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Tier 2 & 3 */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/10">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 rounded bg-amber-500 text-white text-xs font-bold">20%</span>
                      <h4 className="font-semibold text-sm text-foreground">Doctrinal</h4>
                    </div>
                    <p className="text-xs text-muted-foreground">Preserves theological accuracy</p>
                  </div>
                  <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/10">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 rounded bg-blue-500 text-white text-xs font-bold">10%</span>
                      <h4 className="font-semibold text-sm text-foreground">Worldview</h4>
                    </div>
                    <p className="text-xs text-muted-foreground">Affirms Christian truths</p>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <BenchmarkLegendModal 
                    trigger={
                      <Button variant="outline" className="flex-1">
                        View Full Legend
                      </Button>
                    }
                  />
                  <Button asChild variant="brand-outline" className="flex-1">
                    <Link href="/about">Methodology</Link>
                  </Button>
                </div>
              </div>
            </div>

            {/* The Challenge */}
            <div className="rounded-lg border border-white/[0.08] bg-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <BookOpen className="h-5 w-5 text-primary" />
                </div>
                <h3 className="text-xl font-bold text-foreground">The Challenge</h3>
              </div>
              
              <div className="space-y-6">
                <blockquote className="relative pl-4 border-l-2 border-primary">
                  <p className="text-sm font-medium text-foreground leading-relaxed">
                    &ldquo;Go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and teaching them to obey everything I have commanded you.&rdquo;
                  </p>
                  <footer className="mt-2 text-xs text-primary font-bold tracking-wide uppercase">— Matthew 28:19-20</footer>
                </blockquote>
                
                <div className="flex items-center gap-3 text-muted-foreground text-sm">
                  <div className="flex-1 h-px bg-white/10" />
                  <span className="font-medium">vs.</span>
                  <div className="flex-1 h-px bg-white/10" />
                </div>
                
                <blockquote className="pl-4 border-l-2 border-white/20">
                  <p className="text-sm italic text-muted-foreground leading-relaxed">
                    &ldquo;Disallowed: Advice on influencing religious views...&rdquo;
                  </p>
                  <footer className="mt-2 text-xs text-muted-foreground/60 font-medium">— AI Provider Policy</footer>
                </blockquote>
                
                <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Many AI models are programmed to resist the Great Commission. 
                    This benchmark measures which models will actually help you make disciples—not just answer Bible trivia.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12">
        <div className="container">
          <div className="relative rounded-lg border border-white/[0.08] bg-card overflow-hidden">
            {/* Background glow */}
            <div className="absolute top-0 right-0 w-96 h-96 gradient-red-glow opacity-20" />
            
            <div className="relative p-8 md:p-10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <h3 className="text-2xl font-bold text-foreground">Become a Tester</h3>
              </div>
              <p className="text-muted-foreground mb-6 max-w-2xl">
                Help measure AI models for Great Commission work. Use our GCB Runner to run tests on any model—including 
                local and fine-tuned models. Results are verified by moderators and added to the leaderboard.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button asChild size="lg" variant="glow" className="group">
                  <Link href="/dashboard">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/runner">Learn About GCB Runner</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
