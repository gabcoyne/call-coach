'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { SCORE_COLORS } from '@/lib/colors';

export interface TeamComparisonData {
  dimension: string;
  repScore: number;
  teamAverage: number;
  percentile?: number;
}

export interface TeamComparisonBarProps {
  /** Array of dimension comparison data */
  data: TeamComparisonData[];
  /** Show percentile ranking */
  showPercentile?: boolean;
  /** Filter by role (e.g., "AEs only") */
  roleFilter?: string;
  /** Optional height in pixels (default: 350) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * TeamComparisonBar Component
 *
 * Displays a bar chart comparing individual rep performance against team averages.
 * Highlights where rep is above/below team performance and shows percentile ranking.
 * Useful for benchmarking and identifying competitive positions.
 */
export function TeamComparisonBar({
  data,
  showPercentile = false,
  roleFilter,
  height = 350,
  className = '',
}: TeamComparisonBarProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg bg-gray-50 ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No comparison data available</p>
      </div>
    );
  }

  // Calculate average team performance across all dimensions
  const avgTeamScore = data.length > 0
    ? Math.round(data.reduce((sum, d) => sum + d.teamAverage, 0) / data.length)
    : 0;

  // Function to determine bar color based on rep vs team
  const getBarColor = (repScore: number, teamAverage: number) => {
    const diff = repScore - teamAverage;
    if (diff > 5) return SCORE_COLORS.HIGH;
    if (diff < -5) return SCORE_COLORS.LOW;
    return SCORE_COLORS.MEDIUM;
  };

  // Custom tooltip with percentile information
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      const diff = dataPoint.repScore - dataPoint.teamAverage;
      const diffLabel = diff > 0 ? `+${diff}` : `${diff}`;

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{dataPoint.dimension}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}
            </p>
          ))}
          <p className="text-sm text-gray-600 mt-1">
            Difference: <span className={diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-600'}>{diffLabel}</span>
          </p>
          {showPercentile && dataPoint.percentile !== undefined && (
            <p className="text-sm text-blue-600 mt-1">Percentile: {dataPoint.percentile}th</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="dimension"
            tick={{ fontSize: 11 }}
            stroke="#6b7280"
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            label={{ value: 'Score', angle: -90, position: 'insideLeft' }}
          />
          {/* Reference line for team average */}
          <ReferenceLine
            y={avgTeamScore}
            stroke="#6b7280"
            strokeDasharray="5 5"
            label={{
              value: `Team Avg: ${avgTeamScore}`,
              position: 'right',
              fill: '#6b7280',
              fontSize: 11,
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: '12px' }} />

          {/* Rep score bars */}
          <Bar
            dataKey="repScore"
            fill={SCORE_COLORS.HIGH}
            name="Your Score"
            radius={[6, 6, 0, 0]}
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBarColor(entry.repScore, entry.teamAverage)}
              />
            ))}
          </Bar>

          {/* Team average bars */}
          <Bar
            dataKey="teamAverage"
            fill={SCORE_COLORS.MEDIUM}
            name="Team Average"
            radius={[6, 6, 0, 0]}
            opacity={0.6}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Summary stats below chart */}
      {roleFilter && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600">
            Comparing {roleFilter} • Team average across all dimensions: <span className="font-semibold">{avgTeamScore}</span>
          </p>
        </div>
      )}
    </div>
  );
}
