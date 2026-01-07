"use client";

import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface RadarChartProps {
  data: Array<{
    label: string;
    scores: Record<string, number>;
  }>;
  categories: string[];
}

export function RadarChart({ data, categories }: RadarChartProps) {
  const colors = ["#a11824", "#e84545", "#7a1219"];

  const chartData = {
    labels: categories,
    datasets: data.map((item, index) => ({
      label: item.label,
      data: categories.map((cat) => item.scores[cat] || 0),
      borderColor: colors[index % colors.length],
      backgroundColor: `${colors[index % colors.length]}33`,
      pointBackgroundColor: colors[index % colors.length],
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: {
        filter: (tooltipItem: any) => tooltipItem.raw != null,
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
        },
      },
    },
  };

  return (
    <div className="h-96">
      <Radar data={chartData} options={options} />
    </div>
  );
}
