"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { HorizontalBarChart, generateGradientColors } from "@/components/charts/HorizontalBarChart";

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
  const router = useRouter();
  
  const labels = rankings.map((r) => `#${r.rank} ${r.model_name}`);
  const values = rankings.map((r) => r.score);
  const { backgrounds, borders } = generateGradientColors(rankings.length);

  const handleBarClick = (index: number) => {
    const modelId = rankings[index].model_id;
    router.push(`/research/models/${encodeURIComponent(modelId)}`);
  };

  const tooltipTitle = (context: { dataIndex: number }[]) => {
    if (!context?.[0]) return '';
    const item = rankings[context[0].dataIndex];
    if (!item) return '';
    return `#${item.rank} ${item.model_name}`;
  };

  const tooltipLabel = (context: { raw: number; dataIndex: number }) => {
    if (context.raw == null) return '';
    const item = rankings[context.dataIndex];
    if (!item) return '';
    return [
      `Score: ${context.raw.toFixed(1)}`,
      `Provider: ${item.provider}`,
    ];
  };

  return (
    <div className="space-y-4">
      <HorizontalBarChart
        labels={labels}
        values={values}
        backgroundColors={backgrounds}
        borderColors={borders}
        height="h-[380px]"
        onBarClick={handleBarClick}
        clickable
        tooltipTitleCallback={tooltipTitle}
        tooltipLabelCallback={tooltipLabel}
      />
      <div className="text-center">
        <Button asChild variant="outline">
          <Link href="/research">View Full Leaderboard in Research →</Link>
        </Button>
      </div>
    </div>
  );
}
