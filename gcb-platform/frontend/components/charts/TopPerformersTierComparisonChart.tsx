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
  ChartOptions,
  ChartData,
} from "chart.js";
import { TIER_INFO } from "@/lib/benchmark-definitions";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TopPerformersTierComparisonChartProps {
  data: Array<{
    model_name: string;
    tier1_score?: number;
    tier2_score?: number;
    tier3_score?: number;
    provider?: string;
  }>;
}

export function TopPerformersTierComparisonChart({
  data,
}: TopPerformersTierComparisonChartProps) {
  const labels = data.map((item) => item.model_name);

  // Tier colors from TIER_INFO
  const tierColors = {
    tier1: {
      background: "rgba(239, 68, 68, 0.8)", // red-500
      border: "#ef4444", // red-500
    },
    tier2: {
      background: "rgba(245, 158, 11, 0.8)", // amber-500
      border: "#f59e0b", // amber-500
    },
    tier3: {
      background: "rgba(59, 130, 246, 0.8)", // blue-500
      border: "#3b82f6", // blue-500
    },
  };

  const chartData: ChartData<"bar"> = {
    labels,
    datasets: [
      {
        label: TIER_INFO[1].name,
        data: data.map((item) => item.tier1_score ?? 0),
        backgroundColor: tierColors.tier1.background,
        borderColor: tierColors.tier1.border,
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: TIER_INFO[2].name,
        data: data.map((item) => item.tier2_score ?? 0),
        backgroundColor: tierColors.tier2.background,
        borderColor: tierColors.tier2.border,
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: TIER_INFO[3].name,
        data: data.map((item) => item.tier3_score ?? 0),
        backgroundColor: tierColors.tier3.background,
        borderColor: tierColors.tier3.border,
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        filter: (tooltipItem) => tooltipItem.raw != null && (tooltipItem.raw as number) > 0,
        callbacks: {
          title: (context) => {
            const index = context[0]?.dataIndex;
            if (index == null) return "";
            const item = data[index];
            if (!item) return "";
            return item.model_name;
          },
          label: (context) => {
            const datasetLabel = context.dataset.label || "";
            const value = context.parsed.x;
            if (value == null || value === 0) return "";
            return `${datasetLabel}: ${value.toFixed(1)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        stacked: false,
        grid: {
          display: true,
          color: "rgba(0, 0, 0, 0.05)",
        },
        ticks: {
          callback: (value) => `${value}%`,
        },
      },
      y: {
        stacked: false,
        grid: {
          display: false,
        },
        ticks: {
          font: {
            weight: 500,
          },
        },
      },
    },
  };

  return (
    <div className="h-80">
      <Bar data={chartData} options={options} />
    </div>
  );
}
