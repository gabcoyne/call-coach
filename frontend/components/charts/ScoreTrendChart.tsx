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
  Area,
  AreaChart,
} from "recharts";
import { CHART_COLORS } from "@/lib/colors";

export interface ScoreTrendDataPoint {
  /** Date label for x-axis (e.g., "2026-01-15") */
  date: string;
  /** Overall score for this date */
  overall?: number;
  /** Week-over-week score (if applicable) */
  weekOverWeek?: number;
  /** Dynamic key-value pairs for each dimension score */
  [dimension: string]: string | number | undefined;
}

export interface ScoreTrendChartProps {
  /** Array of data points with date and dimension scores */
  data: ScoreTrendDataPoint[];
  /** Array of dimension names to plot (keys in data objects) */
  dimensions?: string[];
  /** Show area chart instead of line chart */
  showArea?: boolean;
  /** Enable week-over-week comparison visualization */
  showWeekOverWeek?: boolean;
  /** Optional height in pixels (default: 350) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * ScoreTrendChart Component
 *
 * Advanced line/area chart for tracking score trends over time.
 * Supports multiple dimensions on the same chart with visual distinction.
 * Can highlight week-over-week comparisons and improvements/declines.
 */
export function ScoreTrendChart({
  data,
  dimensions = [],
  showArea = false,
  showWeekOverWeek = false,
  height = 350,
  className = "",
}: ScoreTrendChartProps) {
  // If no data, show placeholder
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg bg-gray-50 ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No trend data available</p>
      </div>
    );
  }

  // Filter out any undefined dimensions and add overall if not present
  const displayDimensions = dimensions.filter((d) => d !== "date");
  const hasOverall = data.some((d) => d.overall !== undefined);

  // Custom tooltip to show detailed information
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{data.date}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Determine which chart type to render
  if (showArea && displayDimensions.length <= 1) {
    return (
      <div className={className}>
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS[0]} stopOpacity={0.8} />
                <stop offset="95%" stopColor={CHART_COLORS[0]} stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#6b7280" />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              label={{ value: "Score", angle: -90, position: "insideLeft" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey={displayDimensions[0] || "overall"}
              stroke={CHART_COLORS[0]}
              fillOpacity={1}
              fill="url(#colorScore)"
              name={
                displayDimensions[0]?.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) ||
                "Score"
              }
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#6b7280" />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            label={{ value: "Score", angle: -90, position: "insideLeft" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: "12px" }} iconType="line" />

          {/* Overall score line if available */}
          {hasOverall && (
            <Line
              type="monotone"
              dataKey="overall"
              stroke={CHART_COLORS[0]}
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 7 }}
              name="Overall Score"
            />
          )}

          {/* Individual dimension lines */}
          {displayDimensions.map((dimension, index) => (
            <Line
              key={dimension}
              type="monotone"
              dataKey={dimension}
              stroke={CHART_COLORS[(index + 1) % CHART_COLORS.length]}
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
