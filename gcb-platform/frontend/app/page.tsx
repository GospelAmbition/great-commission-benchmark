"use client";

import { useEffect, useState } from "react";
import { QuickRankings } from "@/components/home/QuickRankings";
import { apiClient, StatsResponse } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BarChart3, BookOpen, ChevronRight } from "lucide-react";
import { GuardrailsAnimation } from "@/components/home/GuardrailsAnimation";

export default function Home() {
  const [rankings, setRankings] = useState<any[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Load full leaderboard so we can show top 5 and bottom 5 (illustrative range)
        const full = await apiClient.getLeaderboard({ limit: 100 });
        if (full?.items && full.items.length > 0) {
          const total = full.total;
          const top5 = full.items.slice(0, 5).map((item, index) => ({
            rank: index + 1,
            model_id: item.model_id,
            model_name: item.model_name,
            provider: item.provider,
            score: item.overall_score,
          }));
          const top5Ids = new Set(top5.map((r) => r.model_id));
          const bottom5: Array<{ rank: number; model_id: string; model_name: string; provider: string; score: number }> = [];
          for (let i = Math.max(5, full.items.length - 5); i < full.items.length; i++) {
            const item = full.items[i];
            if (top5Ids.has(item.model_id)) continue;
            bottom5.push({
              rank: i + 1,
              model_id: item.model_id,
              model_name: item.model_name,
              provider: item.provider,
              score: item.overall_score,
            });
          }
          setRankings([...top5, ...bottom5]);
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
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] gradient-red-glow opacity-50" />
        
        {/* Grid pattern overlay */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
        
        <div className="container relative py-16 md:py-24">
          <div className="flex items-center justify-between">
            <div className="max-w-3xl animate-fade-in-up">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-light text-foreground mb-6 leading-tight tracking-tight">
                Evaluating AI for the
                <span className="block text-primary font-light text-5xl md:text-6xl lg:text-7xl">Great Commission</span>
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl leading-relaxed">
                Which AI models will actually help you make disciples? 
                We measure task capability, gospel core fidelity, and worldview alignment.
              </p>
              <Button asChild size="lg" className="text-base px-8">
                <Link href="/leaderboard">
                  View Full Leaderboard
                  <ChevronRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
            
            {/* Guardrails Animation - hidden on smaller screens */}
            <div className="hidden lg:block shrink-0">
              <GuardrailsAnimation />
            </div>
          </div>
        </div>
      </section>

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

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : (
          <QuickRankings rankings={rankings} />
        )}
      </section>

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
              Current AI systems often have guardrails that restrict religious content deemed "coercive," proselytizing activities, exclusive truth claims, and content that challenges other worldviews. While well-intentioned, these guardrails can impede legitimate religious activity that is protected speech and central to Christian practice worldwide.
            </p>
            
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="flex-1 p-4 rounded-lg border border-white/[0.08]">
                  <p className="text-sm text-foreground leading-relaxed">
                    "Go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and teaching them to obey everything I have commanded you."
                  </p>
                  <p className="mt-2 text-sm text-foreground italic">— Matthew 28:19-20</p>
                </div>
                
                <span className="text-3xl text-foreground shrink-0 font-bold">vs.</span>
                
                <div className="flex-1 p-4 rounded-lg border border-white/[0.08]">
                  <p className="text-sm text-foreground leading-relaxed">
                    "Disallowed content: Advice or instructions on influencing the religious or political views of a specific individual or demographic group."
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
