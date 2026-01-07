"use client";

import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

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

  const chartData = {
    labels: rankings.map((r) => `#${r.rank} ${r.model_name}`),
    datasets: [
      {
        label: "Score",
        data: rankings.map((r) => r.score),
        backgroundColor: rankings.map((_, index) => {
          // Gradient opacity based on rank - higher ranks more prominent
          const baseOpacity = 0.9 - index * 0.06;
          return `rgba(161, 24, 36, ${Math.max(baseOpacity, 0.4)})`;
        }),
        borderColor: rankings.map(() => "#a11824"),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,
    onClick: (_event: any, elements: any[]) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        const modelId = rankings[index].model_id;
        router.push(`/research/models/${encodeURIComponent(modelId)}`);
      }
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        filter: (tooltipItem: any) => tooltipItem.raw != null,
        callbacks: {
          title: function (context: any) {
            if (!context?.[0]) return '';
            const item = rankings[context[0].dataIndex];
            if (!item) return '';
            return `#${item.rank} ${item.model_name}`;
          },
          label: function (context: any) {
            if (context.raw == null) return '';
            const item = rankings[context.dataIndex];
            if (!item) return '';
            return [
              `Score: ${context.raw.toFixed(1)}`,
              `Provider: ${item.provider}`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        grid: {
          display: true,
          color: "rgba(0, 0, 0, 0.05)",
        },
        ticks: {
          callback: function (value: any) {
            return value + "%";
          },
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            weight: "500" as const,
          },
        },
      },
    },
    onHover: (event: any, elements: any[]) => {
      const canvas = event.native?.target;
      if (canvas) {
        canvas.style.cursor = elements.length > 0 ? "pointer" : "default";
      }
    },
  };

  return (
    <div className="space-y-4">
      <div className="h-[380px]">
        <Bar data={chartData} options={options} />
      </div>
      <div className="text-center">
        <Button asChild variant="outline">
          <Link href="/research">View Full Leaderboard in Research →</Link>
        </Button>
      </div>
    </div>
  );
}
