"use client";

import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";
import { CHART_COLORS } from "@/lib/colors";

export interface DimensionData {
  name: string;
  value: number; // Weight or percentage
  score?: number; // Optional: current score for the dimension
}

export interface DimensionBreakdownChartProps {
  /** Array of dimension data with weights/percentages */
  data: DimensionData[];
  /** Optional height in pixels (default: 300) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
  /** Optional title for the chart */
  title?: string;
}

/**
 * DimensionBreakdownChart Component
 *
 * Displays a pie chart showing the breakdown of dimension weights or percentages.
 * Useful for understanding how different coaching dimensions contribute to overall performance.
 */
export function DimensionBreakdownChart({
  data,
  height = 300,
  className = "",
  title,
}: DimensionBreakdownChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No dimension data available</p>
      </div>
    );
  }

  // Custom label renderer to show percentage
  const renderLabel = (entry: { value: number; percent?: number }) => {
    const percent = entry.percent ? (entry.percent * 100).toFixed(0) : "0";
    return `${percent}%`;
  };

  return (
    <div className={className}>
      {title && <p className="text-sm font-medium text-gray-700 mb-2">{title}</p>}
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
              fontSize: "12px",
            }}
            formatter={(value: number, name: string, props: any) => {
              const total = data.reduce((sum, item) => sum + item.value, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return [`${percentage}%`, props.payload.name];
            }}
          />
          <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: "12px" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
