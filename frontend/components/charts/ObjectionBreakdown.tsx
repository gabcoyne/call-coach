"use client";

import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { CHART_COLORS, SCORE_COLORS } from "@/lib/colors";
import { useState } from "react";

export interface ObjectionType {
  name: string;
  count: number;
  successRate?: number; // 0-100
  avgScore?: number;
}

export interface ObjectionBreakdownProps {
  /** Array of objection types with counts and success rates */
  data: ObjectionType[];
  /** Show bar chart breakdown instead of pie */
  showDetails?: boolean;
  /** Optional height in pixels (default: 350) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * ObjectionBreakdown Component
 *
 * Displays a pie chart of objection types encountered in calls.
 * Can toggle to a detailed bar chart showing success rate per objection type.
 * Helps identify which objections are most common and which are handled best.
 */
export function ObjectionBreakdown({
  data,
  showDetails = false,
  height = 350,
  className = "",
}: ObjectionBreakdownProps) {
  const [viewMode, setViewMode] = useState<"pie" | "details">(showDetails ? "details" : "pie");

  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg bg-gray-50 ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No objection data available</p>
      </div>
    );
  }

  // Calculate total objections
  const totalObjections = data.reduce((sum, d) => sum + d.count, 0);

  // Custom tooltip for pie chart
  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const entry = payload[0];
      const dataPoint = entry.payload;
      const percentage = Math.round((dataPoint.count / totalObjections) * 100);

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{dataPoint.name}</p>
          <p className="text-sm text-gray-600">Count: {dataPoint.count}</p>
          <p className="text-sm text-gray-600">Percentage: {percentage}%</p>
          {dataPoint.successRate !== undefined && (
            <p className="text-sm text-gray-600">Success Rate: {dataPoint.successRate}%</p>
          )}
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const CustomBarTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{dataPoint.name}</p>
          <p className="text-sm text-gray-600">Times Encountered: {dataPoint.count}</p>
          {dataPoint.successRate !== undefined && (
            <p className="text-sm text-green-600">Success Rate: {dataPoint.successRate}%</p>
          )}
          {dataPoint.avgScore !== undefined && (
            <p className="text-sm text-blue-600">Avg Score: {dataPoint.avgScore}</p>
          )}
        </div>
      );
    }
    return null;
  };

  // Pie chart view
  if (viewMode === "pie") {
    return (
      <div className={className}>
        <div className="flex justify-end mb-4 gap-2">
          <button
            onClick={() => setViewMode("pie")}
            className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
              viewMode === "pie"
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Distribution
          </button>
          <button
            onClick={() => setViewMode("details")}
            className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
              viewMode === "details"
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Details
          </button>
        </div>

        <ResponsiveContainer width="100%" height={height}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, count }) => {
                const percentage = Math.round((count / totalObjections) * 100);
                return `${name} (${percentage}%)`;
              }}
              outerRadius={120}
              fill="#8884d8"
              dataKey="count"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomPieTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Details bar chart view (success rate per objection)
  const detailsData = data.filter((d) => d.successRate !== undefined);

  if (detailsData.length === 0) {
    return (
      <div className={className}>
        <div className="flex justify-end mb-4 gap-2">
          <button
            onClick={() => setViewMode("pie")}
            className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
              viewMode === "pie"
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Distribution
          </button>
          <button
            onClick={() => setViewMode("details")}
            className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
              viewMode === "details"
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Details
          </button>
        </div>

        <div
          className="flex items-center justify-center border rounded-lg bg-gray-50"
          style={{ height }}
        >
          <p className="text-gray-500 text-sm">
            No success rate data available. Switch to Distribution view.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex justify-end mb-4 gap-2">
        <button
          onClick={() => setViewMode("pie")}
          className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
            viewMode === "pie"
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          Distribution
        </button>
        <button
          onClick={() => setViewMode("details")}
          className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
            viewMode === "details"
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          Details
        </button>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={detailsData} margin={{ top: 5, right: 30, left: 0, bottom: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11 }}
            stroke="#6b7280"
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis
            yAxisId="left"
            domain={[0, "auto"]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            label={{ value: "Count", angle: -90, position: "insideLeft" }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            label={{ value: "Success Rate %", angle: 90, position: "insideRight" }}
          />
          <Tooltip content={<CustomBarTooltip />} />
          <Legend wrapperStyle={{ fontSize: "12px" }} />

          {/* Count bars */}
          <Bar
            yAxisId="left"
            dataKey="count"
            fill={CHART_COLORS[0]}
            name="Times Encountered"
            radius={[6, 6, 0, 0]}
          />

          {/* Success rate bars */}
          <Bar
            yAxisId="right"
            dataKey="successRate"
            fill={SCORE_COLORS.HIGH}
            name="Success Rate (%)"
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
