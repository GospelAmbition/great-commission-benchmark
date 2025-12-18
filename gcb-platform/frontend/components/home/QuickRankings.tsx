"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

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

export function QuickRankings({ rankings }: QuickRankingsProps) {
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Rank</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Provider</TableHead>
            <TableHead className="text-right">Score</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rankings.map((ranking) => (
            <TableRow key={ranking.model_id}>
              <TableCell className="font-medium">{ranking.rank}</TableCell>
              <TableCell>
                <Link
                  href={`/research/models/${ranking.model_id}`}
                  className="hover:underline font-medium"
                >
                  {ranking.model_name}
                </Link>
              </TableCell>
              <TableCell>
                <Badge variant="secondary">{ranking.provider}</Badge>
              </TableCell>
              <TableCell className="text-right font-semibold">
                {ranking.score.toFixed(1)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="text-center">
        <Button asChild variant="outline">
          <Link href="/research">View Full Leaderboard in Research →</Link>
        </Button>
      </div>
    </div>
  );
}
