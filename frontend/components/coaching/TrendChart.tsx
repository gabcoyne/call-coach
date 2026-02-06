"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { CHART_COLORS } from "@/lib/colors";

export interface TrendDataPoint {
  /** Date label for x-axis (e.g., "2026-01-15") */
  date: string;
  /** Dynamic key-value pairs for each dimension score */
  [dimension: string]: string | number;
}

export interface TrendChartProps {
  /** Array of data points with date and dimension scores */
  data: TrendDataPoint[];
  /** Array of dimension names to plot (keys in data objects) */
  dimensions: string[];
  /** Optional height in pixels (default: 300) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * TrendChart Component
 *
 * Displays performance trends over time using Recharts LineChart.
 * Supports multiple dimension series with automatic color assignment and legend.
 * Responsive sizing adapts to container width.
 */
export function TrendChart({ data, dimensions, height = 300, className = "" }: TrendChartProps) {
  // If no data, show placeholder
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No trend data available</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#6b7280" />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            label={{ value: "Score", angle: -90, position: "insideLeft" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} iconType="line" />
          {dimensions.map((dimension, index) => (
            <Line
              key={dimension}
              type="monotone"
              dataKey={dimension}
              stroke={CHART_COLORS[index % CHART_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={dimension.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
