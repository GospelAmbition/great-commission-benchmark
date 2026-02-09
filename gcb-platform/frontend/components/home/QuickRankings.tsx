"use client";

import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { Button } from "@/components/ui/button";

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
  if (score >= 80) return "bg-emerald-500";
  if (score >= 61) return "bg-blue-500";
  if (score >= 40) return "bg-amber-500";
  return "bg-red-500";
}

// Capitalize a string (e.g., "x-ai" -> "X-AI", "grok-code-fast-1" -> "Grok-Code-Fast-1")
function capitalizeString(str: string): string {
  return str
    .split(/[-_\/]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('-');
}

// Extract model name without provider prefix
function extractModelName(modelName: string, provider: string): string {
  const prefix = `${provider}/`;
  if (modelName.toLowerCase().startsWith(prefix.toLowerCase())) {
    return modelName.slice(prefix.length);
  }
  return modelName;
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

// Single ranking row (reused for top 5 and bottom 5)
function RankingRow({ item, index }: { item: Ranking; index: number }) {
  const barColor = getBarColor(item.score);
  const barWidth = Math.max(item.score, 5);
  return (
    <Link
      key={item.model_id}
      href={`/leaderboard/models/${encodeURIComponent(item.model_id)}`}
      className="group block"
    >
      <div
        className="relative rounded-lg border border-white/[0.06] bg-card hover:border-white/[0.12] hover:bg-white/[0.02] transition-all overflow-hidden"
        style={{ animationDelay: `${index * 50}ms` }}
      >
        <div
          className={`absolute inset-y-0 left-0 ${barColor} opacity-10 transition-all duration-500`}
          style={{ width: `${barWidth}%` }}
        />
        <div className="relative flex items-center gap-4 p-3 md:p-4">
          <RankDisplay rank={item.rank} />
          <ProviderIcon provider={item.provider} size={18} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                {capitalizeString(item.provider)} | {capitalizeString(extractModelName(item.model_name, item.provider))}
              </span>
            </div>
          </div>
          <span className="hidden md:inline text-2xl font-light tabular-nums text-foreground">
            {item.score.toFixed(0)}%
          </span>
          <div className="flex md:hidden items-center gap-2">
            <span className="text-lg font-bold tabular-nums text-foreground">
              {item.score.toFixed(0)}%
            </span>
          </div>
          <ChevronRight className="h-4 w-4 text-muted-foreground opacity-60 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
        </div>
      </div>
    </Link>
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

  const top5 = rankings.slice(0, 5);
  const bottom5 = rankings.slice(5, 10);

  return (
    <div className="space-y-2">
      {/* Top 5 */}
      {top5.map((item, index) => (
        <RankingRow key={item.model_id} item={item} index={index} />
      ))}

      {/* Bottom 5 (ranks 6–10) */}
      {bottom5.length > 0 &&
        bottom5.map((item, index) => (
          <RankingRow key={item.model_id} item={item} index={5 + index} />
        ))}

      {/* View Full Leaderboard at bottom of list */}
      <div className="py-8 md:py-10 flex justify-center">
        <Button asChild size="lg" className="text-base px-8">
          <Link href="/leaderboard">
            View Full Leaderboard
            <ChevronRight className="ml-2 h-5 w-5" />
          </Link>
        </Button>
      </div>
    </div>
  );
}
