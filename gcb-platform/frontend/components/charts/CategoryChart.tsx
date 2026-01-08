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
import { getCategoryName, sortCategories, getTierForCategory, TIER_INFO } from "@/lib/benchmark-definitions";
import { BenchmarkInlineLegend } from "@/components/benchmark";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface CategoryChartProps {
  data: Record<string, number>;
  /** Show inline legend below the chart */
  showLegend?: boolean;
}

export function CategoryChart({ data, showLegend = true }: CategoryChartProps) {
  // Sort categories in the correct order: 3.1-3.7, 4.1-4.6, 5.1-5.6
  const sortedCategories = sortCategories(Object.keys(data));

  // Color bars by tier
  const getBarColor = (category: string) => {
    const tier = getTierForCategory(category);
    if (tier === 1) return "#a11824"; // Red for Tier 1
    if (tier === 2) return "#334155"; // Slate-800 for Tier 2
    return "#64748b"; // Slate-500 for Tier 3
  };

  const chartData = {
    labels: sortedCategories,
    datasets: [
      {
        label: "Score",
        data: sortedCategories.map(category => data[category]),
        backgroundColor: sortedCategories.map(getBarColor),
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
          title: (context: any) => {
            const code = context[0]?.label;
            if (!code) return '';
            const name = getCategoryName(code);
            const tier = getTierForCategory(code);
            const tierName = TIER_INFO[tier]?.shortName || `Tier ${tier}`;
            return `${code} - ${name} (${tierName})`;
          },
          label: (context: any) => {
            if (context.parsed?.y == null) return '';
            return `Score: ${context.parsed.y.toFixed(1)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value: any) => `${value}%`,
        },
      },
    },
  };

  return (
    <div className="space-y-2">
      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>
      {showLegend && <BenchmarkInlineLegend className="mt-2 pt-2 border-t" />}
    </div>
  );
}
