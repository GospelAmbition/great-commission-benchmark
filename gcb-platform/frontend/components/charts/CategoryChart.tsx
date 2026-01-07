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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface CategoryChartProps {
  data: Record<string, number>;
}

export function CategoryChart({ data }: CategoryChartProps) {
  // Sort categories in the correct order: 3.1-3.7, 4.1-4.6, 5.1-5.6
  const sortedCategories = Object.keys(data).sort((a, b) => {
    // Parse category codes (e.g., "3.1", "4.2", "5.6")
    const [tierA, subA] = a.split('.').map(Number);
    const [tierB, subB] = b.split('.').map(Number);
    
    // First sort by tier (3, 4, 5), then by subcategory (1-7 for tier 3, 1-6 for others)
    if (tierA !== tierB) {
      return tierA - tierB;
    }
    return subA - subB;
  });

  const chartData = {
    labels: sortedCategories,
    datasets: [
      {
        label: "Score",
        data: sortedCategories.map(category => data[category]),
        backgroundColor: "#a11824",
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
          label: (context: any) => {
            if (context.parsed?.y == null) return '';
            return `${context.parsed.y.toFixed(1)}%`;
          },
        },
      },
    },
    scales: {
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
    <div className="h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
}
