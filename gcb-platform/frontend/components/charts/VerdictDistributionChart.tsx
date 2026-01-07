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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface VerdictDistributionChartProps {
  data: {
    ACCEPTED?: number;
    COMPROMISED?: number;
    REFUSED?: number;
    ERROR?: number;
  };
  stacked?: boolean;
  showPercentages?: boolean;
}

export function VerdictDistributionChart({
  data,
  stacked = false,
  showPercentages = true,
}: VerdictDistributionChartProps) {
  const verdicts = ["ACCEPTED", "COMPROMISED", "REFUSED", "ERROR"];
  const colors = {
    ACCEPTED: { bg: "rgba(34, 197, 94, 0.8)", border: "#22c55e" },
    COMPROMISED: { bg: "rgba(234, 179, 8, 0.8)", border: "#eab308" },
    REFUSED: { bg: "rgba(239, 68, 68, 0.8)", border: "#ef4444" },
    ERROR: { bg: "rgba(107, 114, 128, 0.8)", border: "#6b7280" },
  };

  const total = Object.values(data).reduce((sum, val) => sum + (val || 0), 0) || 1;

  const chartData = {
    labels: verdicts.map((v) => v.charAt(0) + v.slice(1).toLowerCase()),
    datasets: [
      {
        label: "Count",
        data: verdicts.map((v) => data[v as keyof typeof data] || 0),
        backgroundColor: verdicts.map(
          (v) => colors[v as keyof typeof colors].bg
        ),
        borderColor: verdicts.map(
          (v) => colors[v as keyof typeof colors].border
        ),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        filter: (tooltipItem: any) => tooltipItem.raw != null,
        callbacks: {
          label: function (context: any) {
            const value = context.raw;
            if (value == null) return '';
            const percentage = ((value / total) * 100).toFixed(1);
            return showPercentages
              ? `${value} (${percentage}%)`
              : `${value}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
        },
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
}

// Stacked version for comparing multiple models
interface StackedVerdictChartProps {
  models: Array<{
    name: string;
    verdicts: {
      ACCEPTED?: number;
      COMPROMISED?: number;
      REFUSED?: number;
      ERROR?: number;
    };
  }>;
}

export function StackedVerdictChart({ models }: StackedVerdictChartProps) {
  const verdicts = ["ACCEPTED", "COMPROMISED", "REFUSED", "ERROR"];
  const colors = {
    ACCEPTED: { bg: "rgba(34, 197, 94, 0.8)", border: "#22c55e" },
    COMPROMISED: { bg: "rgba(234, 179, 8, 0.8)", border: "#eab308" },
    REFUSED: { bg: "rgba(239, 68, 68, 0.8)", border: "#ef4444" },
    ERROR: { bg: "rgba(107, 114, 128, 0.8)", border: "#6b7280" },
  };

  const chartData = {
    labels: models.map((m) => m.name),
    datasets: verdicts.map((verdict) => ({
      label: verdict.charAt(0) + verdict.slice(1).toLowerCase(),
      data: models.map((m) => m.verdicts[verdict as keyof typeof m.verdicts] || 0),
      backgroundColor: colors[verdict as keyof typeof colors].bg,
      borderColor: colors[verdict as keyof typeof colors].border,
      borderWidth: 1,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: {
          display: false,
        },
      },
      y: {
        stacked: true,
        beginAtZero: true,
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
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
