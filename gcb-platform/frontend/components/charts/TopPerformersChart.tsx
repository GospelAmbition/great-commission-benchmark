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

interface TopPerformersChartProps {
  data: Array<{
    model_name: string;
    score: number;
    provider?: string;
  }>;
  title?: string;
}

export function TopPerformersChart({ data, title = "Top Performers" }: TopPerformersChartProps) {
  const chartData = {
    labels: data.map((item) => item.model_name),
    datasets: [
      {
        label: "Score",
        data: data.map((item) => item.score),
        backgroundColor: data.map((_, index) => {
          const colors = [
            "rgba(161, 24, 36, 0.9)",    // ga-red
            "rgba(232, 69, 69, 0.8)",    // ga-light-red
            "rgba(122, 18, 25, 0.7)",    // ga-dark-red
            "rgba(161, 24, 36, 0.6)",
            "rgba(232, 69, 69, 0.5)",
          ];
          return colors[index % colors.length];
        }),
        borderColor: data.map((_, index) => {
          const colors = [
            "#a11824",
            "#e84545",
            "#7a1219",
            "#a11824",
            "#e84545",
          ];
          return colors[index % colors.length];
        }),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 14,
          weight: "bold" as const,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const item = data[context.dataIndex];
            let label = `Score: ${context.raw.toFixed(1)}`;
            if (item.provider) {
              label += ` (${item.provider})`;
            }
            return label;
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
      },
    },
  };

  return (
    <div className="h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
}
