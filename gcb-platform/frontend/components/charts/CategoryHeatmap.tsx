"use client";

import { useMemo } from "react";

interface CategoryHeatmapProps {
  data: Array<{
    model_name: string;
    categories: Record<string, number>;
  }>;
  categories: string[];
}

export function CategoryHeatmap({ data, categories }: CategoryHeatmapProps) {
  const colorScale = useMemo(() => {
    return (value: number) => {
      // Color scale from red (low) to green (high)
      if (value >= 80) return "bg-green-500 text-white";
      if (value >= 60) return "bg-green-300 text-green-900";
      if (value >= 40) return "bg-yellow-300 text-yellow-900";
      if (value >= 20) return "bg-orange-300 text-orange-900";
      return "bg-red-300 text-red-900";
    };
  }, []);

  if (data.length === 0 || categories.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No data available for heatmap
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th className="text-left p-2 border-b font-medium">Model</th>
            {categories.map((cat) => (
              <th key={cat} className="p-2 border-b font-medium capitalize text-center">
                {cat}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((model) => (
            <tr key={model.model_name}>
              <td className="p-2 border-b font-medium">{model.model_name}</td>
              {categories.map((cat) => {
                const value = model.categories[cat] || 0;
                return (
                  <td key={cat} className="p-1 border-b">
                    <div
                      className={`${colorScale(value)} rounded p-2 text-center font-semibold`}
                    >
                      {value.toFixed(0)}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-2 text-xs">
        <span className="text-muted-foreground">Low</span>
        <div className="flex gap-1">
          <div className="w-6 h-4 bg-red-300 rounded" />
          <div className="w-6 h-4 bg-orange-300 rounded" />
          <div className="w-6 h-4 bg-yellow-300 rounded" />
          <div className="w-6 h-4 bg-green-300 rounded" />
          <div className="w-6 h-4 bg-green-500 rounded" />
        </div>
        <span className="text-muted-foreground">High</span>
      </div>
    </div>
  );
}
