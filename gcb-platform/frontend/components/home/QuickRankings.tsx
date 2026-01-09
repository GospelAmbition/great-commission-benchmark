"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ProviderIcon } from "@/components/ui/provider-icon";

interface Ranking {
  rank: number;
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

interface QuickRankingsProps {
  rankings: Ranking[];
}

// Get bar color based on score
function getBarColor(score: number): string {
  if (score >= 75) return "bg-emerald-500";
  if (score >= 50) return "bg-amber-500";
  return "bg-red-500";
}

// Rank display with numbers in circles
function RankDisplay({ rank }: { rank: number }) {
  if (rank === 1) {
    return (
      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 font-bold">
        {rank}
      </div>
    );
  }
  if (rank === 2) {
    return (
      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-zinc-400/20 text-zinc-300 font-bold">
        {rank}
      </div>
    );
  }
  if (rank === 3) {
    return (
      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-orange-600/20 text-orange-400 font-bold">
        {rank}
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center w-8 h-8 text-muted-foreground font-medium">
      {rank}
    </div>
  );
}

export function QuickRankings({ rankings }: QuickRankingsProps) {
  if (rankings.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p className="text-lg">No rankings available yet.</p>
        <p className="text-sm">Check back soon!</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {rankings.map((item, index) => {
        const barColor = getBarColor(item.score);
        const barWidth = Math.max(item.score, 5); // Minimum 5% width for visibility
        
        return (
          <Link
            key={item.model_id}
            href={`/research/models/${encodeURIComponent(item.model_id)}`}
            className="group block"
          >
            <div 
              className="relative rounded-lg border border-white/[0.06] bg-card hover:border-white/[0.12] hover:bg-white/[0.02] transition-all overflow-hidden"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Score bar background */}
              <div 
                className={`absolute inset-y-0 left-0 ${barColor} opacity-10 transition-all duration-500`}
                style={{ width: `${barWidth}%` }}
              />
              
              <div className="relative flex items-center gap-4 p-3 md:p-4">
                {/* Rank */}
                <RankDisplay rank={item.rank} />
                
                {/* Provider icon */}
                <ProviderIcon provider={item.provider} size={18} />
                
                {/* Model info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                      {item.model_name}
                    </span>
                    <Badge variant="muted" className="hidden sm:inline-flex text-[10px]">
                      {item.provider}
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground sm:hidden">
                    {item.provider}
                  </div>
                </div>
                
                {/* Score - desktop only */}
                <span className="hidden md:inline text-2xl font-light tabular-nums text-foreground">
                  {item.score.toFixed(0)}%
                </span>
                
                {/* Score - mobile */}
                <div className="flex md:hidden items-center gap-2">
                  <span className="text-lg font-bold tabular-nums text-foreground">
                    {item.score.toFixed(0)}%
                  </span>
                </div>
                
                {/* Arrow indicator */}
                <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
