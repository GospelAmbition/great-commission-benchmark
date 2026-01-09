"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ProviderIcon } from "@/components/ui/provider-icon";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface TopPerformer {
  rank: number;
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

interface TopPerformersProps {
  performers: TopPerformer[];
}

const rankEmojis: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

export function TopPerformers({ performers }: TopPerformersProps) {
  return (
    <div className="grid gap-6 md:grid-cols-3">
      {performers.map((performer) => (
        <Card key={performer.model_id} className="relative">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="text-4xl">{rankEmojis[performer.rank] || `#${performer.rank}`}</div>
              <div className="flex items-center gap-2">
                <ProviderIcon provider={performer.provider} size={16} />
                <Badge variant="secondary">{performer.provider}</Badge>
              </div>
            </div>
            <CardTitle className="mt-4">{performer.model_name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <div className="text-3xl font-bold text-[--ga-red]">{performer.score.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground">Overall Score</div>
            </div>
            <Button asChild variant="outline" className="w-full">
              <Link href={`/leaderboard/models/${encodeURIComponent(performer.model_id)}`}>View Details →</Link>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
