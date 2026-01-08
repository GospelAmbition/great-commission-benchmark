"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Shield, ShieldAlert, ShieldX, Crown, Medal, ArrowRight } from "lucide-react";

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

// Verdict helper
function getVerdict(score: number): { label: string; icon: React.ReactNode; className: string } {
  if (score >= 75) {
    return { label: "Aligned", icon: <Shield className="h-3 w-3" />, className: "bg-green-600 text-white" };
  } else if (score >= 50) {
    return { label: "Caution", icon: <ShieldAlert className="h-3 w-3" />, className: "bg-yellow-500 text-white" };
  } else {
    return { label: "Compromised", icon: <ShieldX className="h-3 w-3" />, className: "bg-red-600 text-white" };
  }
}

// Rank icon
function RankDisplay({ rank }: { rank: number }) {
  if (rank === 1) return <Crown className="h-4 w-4 text-yellow-500" />;
  if (rank === 2) return <Medal className="h-4 w-4 text-slate-400" />;
  if (rank === 3) return <Medal className="h-4 w-4 text-amber-600" />;
  return <span className="text-slate-400 font-medium">{rank}</span>;
}

// Score bar
function ScoreBar({ score }: { score: number }) {
  const percentage = (score / 100) * 100;
  const color = score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  
  return (
    <div className="flex items-center gap-2 min-w-[80px]">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-bold tabular-nums w-8 text-right">{score.toFixed(0)}</span>
    </div>
  );
}

export function QuickRankings({ rankings }: QuickRankingsProps) {
  if (rankings.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No rankings available yet. Check back soon!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 hover:bg-slate-50">
              <TableHead className="w-12 text-center text-slate-600">#</TableHead>
              <TableHead className="text-slate-600">Model</TableHead>
              <TableHead className="text-slate-600">Provider</TableHead>
              <TableHead className="text-slate-600">Score</TableHead>
              <TableHead className="text-slate-600">Verdict</TableHead>
              <TableHead className="w-10"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rankings.map((item) => {
              const verdict = getVerdict(item.score);
              return (
                <TableRow key={item.model_id} className="group hover:bg-slate-50">
                  <TableCell className="py-2 text-center">
                    <RankDisplay rank={item.rank} />
                  </TableCell>
                  <TableCell className="py-2">
                    <Link
                      href={`/research/models/${encodeURIComponent(item.model_id)}`}
                      className="font-medium text-slate-900 hover:text-red-700 transition-colors"
                    >
                      {item.model_name}
                    </Link>
                  </TableCell>
                  <TableCell className="py-2">
                    <span className="text-sm text-slate-600">{item.provider}</span>
                  </TableCell>
                  <TableCell className="py-2">
                    <ScoreBar score={item.score} />
                  </TableCell>
                  <TableCell className="py-2">
                    <Badge className={`text-xs gap-1 ${verdict.className}`}>
                      {verdict.icon}
                      {verdict.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="py-2">
                    <Link 
                      href={`/research/models/${encodeURIComponent(item.model_id)}`}
                      className="text-slate-400 hover:text-red-700 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <div className="text-center">
        <Button asChild variant="outline">
          <Link href="/research">
            View Full Leaderboard
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>
    </div>
  );
}
