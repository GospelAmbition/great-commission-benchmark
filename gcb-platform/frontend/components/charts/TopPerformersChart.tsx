"use client";

import { HorizontalBarChart } from "@/components/charts/HorizontalBarChart";

interface TopPerformersChartProps {
  data: Array<{
    model_name: string;
    score: number;
    provider?: string;
  }>;
  title?: string;
}

export function TopPerformersChart({ data, title = "Top Performers" }: TopPerformersChartProps) {
  const labels = data.map((item) => item.model_name);
  const values = data.map((item) => item.score);

  const tooltipLabel = (context: { raw: number; dataIndex: number }) => {
    if (context.raw == null) return '';
    const item = data[context.dataIndex];
    if (!item) return '';
    let label = `Score: ${context.raw.toFixed(1)}`;
    if (item.provider) {
      label += ` (${item.provider})`;
    }
    return label;
  };

  return (
    <HorizontalBarChart
      labels={labels}
      values={values}
      title={title}
      height="h-64"
      tooltipLabelCallback={tooltipLabel}
    />
  );
}
