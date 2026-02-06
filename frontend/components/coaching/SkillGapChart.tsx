'use client';

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { CHART_COLORS } from '@/lib/colors';

export interface SkillGapData {
  area: string;
  current: number;
  target: number;
}

export interface SkillGapChartProps {
  /** Array of skill gap data with current and target scores */
  data: SkillGapData[];
  /** Optional height in pixels (default: 350) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * SkillGapChart Component
 *
 * Displays a radar chart comparing current vs target scores across different skill areas.
 * Provides visual representation of gaps and areas for improvement.
 */
export function SkillGapChart({
  data,
  height = 350,
  className = '',
}: SkillGapChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No skill gap data available</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={data} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="area"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <Radar
            name="Current Score"
            dataKey="current"
            stroke={CHART_COLORS[0]}
            fill={CHART_COLORS[0]}
            fillOpacity={0.6}
          />
          <Radar
            name="Target Score"
            dataKey="target"
            stroke={CHART_COLORS[1]}
            fill={CHART_COLORS[1]}
            fillOpacity={0.3}
            strokeDasharray="5 5"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontSize: '12px',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
