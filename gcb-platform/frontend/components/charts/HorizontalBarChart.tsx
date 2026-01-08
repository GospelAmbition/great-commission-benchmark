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

// Register Chart.js components once
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Color scheme for the Great Commission Benchmark charts.
 * Uses brand colors with decreasing opacity for visual hierarchy.
 */
export const GA_CHART_COLORS = {
  backgrounds: [
    "rgba(161, 24, 36, 0.9)",    // ga-red
    "rgba(232, 69, 69, 0.8)",    // ga-light-red
    "rgba(122, 18, 25, 0.7)",    // ga-dark-red
    "rgba(161, 24, 36, 0.6)",
    "rgba(232, 69, 69, 0.5)",
  ],
  borders: [
    "#a11824",
    "#e84545",
    "#7a1219",
    "#a11824",
    "#e84545",
  ],
  primary: "#a11824",
};

/**
 * Generate gradient opacity colors based on index (rank-based styling)
 */
export function generateGradientColors(count: number): { backgrounds: string[]; borders: string[] } {
  const backgrounds: string[] = [];
  const borders: string[] = [];
  
  for (let i = 0; i < count; i++) {
    const opacity = Math.max(0.9 - i * 0.06, 0.4);
    backgrounds.push(`rgba(161, 24, 36, ${opacity})`);
    borders.push(GA_CHART_COLORS.primary);
  }
  
  return { backgrounds, borders };
}

export interface HorizontalBarChartProps {
  /** Labels for each bar (Y-axis) */
  labels: string[];
  /** Data values for each bar */
  values: number[];
  /** Optional background colors per bar (defaults to GA brand colors) */
  backgroundColors?: string[];
  /** Optional border colors per bar (defaults to GA brand colors) */
  borderColors?: string[];
  /** Chart title (optional) */
  title?: string;
  /** Chart height (default: "h-64") */
  height?: string;
  /** Maximum value for X-axis (default: 100) */
  maxValue?: number;
  /** X-axis tick suffix (default: "%") */
  tickSuffix?: string;
  /** Custom tooltip label formatter */
  tooltipLabelCallback?: (context: { raw: number; dataIndex: number }) => string | string[];
  /** Custom tooltip title formatter */
  tooltipTitleCallback?: (context: { dataIndex: number }[]) => string;
  /** Click handler for bar elements */
  onBarClick?: (index: number) => void;
  /** Whether to show pointer cursor on hover when clickable */
  clickable?: boolean;
  /** Custom className for the container */
  className?: string;
}

export function HorizontalBarChart({
  labels,
  values,
  backgroundColors,
  borderColors,
  title,
  height = "h-64",
  maxValue = 100,
  tickSuffix = "%",
  tooltipLabelCallback,
  tooltipTitleCallback,
  onBarClick,
  clickable = false,
  className,
}: HorizontalBarChartProps) {
  // Use provided colors or default to cycling brand colors
  const backgrounds = backgroundColors ?? values.map((_, i) => GA_CHART_COLORS.backgrounds[i % GA_CHART_COLORS.backgrounds.length]);
  const borders = borderColors ?? values.map((_, i) => GA_CHART_COLORS.borders[i % GA_CHART_COLORS.borders.length]);

  const chartData: ChartData<"bar"> = {
    labels,
    datasets: [
      {
        label: "Score",
        data: values,
        backgroundColor: backgrounds,
        borderColor: borders,
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    onClick: onBarClick
      ? (_event, elements) => {
          if (elements.length > 0) {
            onBarClick(elements[0].index);
          }
        }
      : undefined,
    plugins: {
      legend: {
        display: false,
      },
      title: title
        ? {
            display: true,
            text: title,
            font: {
              size: 14,
              weight: "bold",
            },
          }
        : { display: false },
      tooltip: {
        filter: (tooltipItem) => tooltipItem.raw != null,
        callbacks: {
          title: tooltipTitleCallback
            ? (context) => tooltipTitleCallback(context.map(c => ({ dataIndex: c.dataIndex })))
            : undefined,
          label: tooltipLabelCallback
            ? (context) => tooltipLabelCallback({ raw: context.raw as number, dataIndex: context.dataIndex })
            : (context) => `Score: ${(context.raw as number).toFixed(1)}`,
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: maxValue,
        grid: {
          display: true,
          color: "rgba(0, 0, 0, 0.05)",
        },
        ticks: {
          callback: (value) => `${value}${tickSuffix}`,
        },
      },
      y: {
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
    onHover: clickable
      ? (event, elements) => {
          const canvas = (event.native?.target as HTMLCanvasElement | undefined);
          if (canvas) {
            canvas.style.cursor = elements.length > 0 ? "pointer" : "default";
          }
        }
      : undefined,
  };

  return (
    <div className={className ?? height}>
      <Bar data={chartData} options={options} />
    </div>
  );
}
