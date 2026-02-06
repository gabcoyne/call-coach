"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { SCORE_COLORS } from "@/lib/colors";

export interface ComparisonData {
  dimension: string;
  repScore: number;
  teamAverage: number;
}

export interface TeamComparisonChartProps {
  /** Array of dimension scores with rep and team averages */
  data: ComparisonData[];
  /** Optional height in pixels (default: 300) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * TeamComparisonChart Component
 *
 * Displays a bar chart comparing the rep's scores against team averages.
 * Helps identify where the rep is performing above or below their peers.
 */
export function TeamComparisonChart({
  data,
  height = 300,
  className = "",
}: TeamComparisonChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No comparison data available</p>
      </div>
    );
  }

  // Function to get bar color based on rep score vs team average
  const getBarColor = (repScore: number, teamAverage: number) => {
    const difference = repScore - teamAverage;
    if (difference >= 5) return SCORE_COLORS.HIGH; // Performing above average
    if (difference <= -5) return SCORE_COLORS.LOW; // Performing below average
    return SCORE_COLORS.MEDIUM; // Performing close to average
  };

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="dimension"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            angle={-45}
            textAnchor="end"
            height={80}
          />
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
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          <Bar
            dataKey="repScore"
            fill={SCORE_COLORS.HIGH}
            name="Your Score"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="teamAverage"
            fill={SCORE_COLORS.MEDIUM}
            name="Team Average"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
