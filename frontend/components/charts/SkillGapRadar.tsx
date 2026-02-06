'use client';

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { CHART_COLORS } from '@/lib/colors';

export interface SkillGapRadarData {
  skill: string;
  actual: number;
  target: number;
  teamAverage?: number;
}

export interface SkillGapRadarProps {
  /** Array of skill gap data with actual, target, and optional team average scores */
  data: SkillGapRadarData[];
  /** Compare against team average or top performers */
  compareType?: 'team' | 'topPerformers' | 'target';
  /** Optional height in pixels (default: 350) */
  height?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * SkillGapRadar Component
 *
 * Displays a radar chart showing skill/dimension gaps.
 * Compares actual performance against target goals and optionally against team averages.
 * Useful for identifying skill development areas.
 */
export function SkillGapRadar({
  data,
  compareType = 'target',
  height = 350,
  className = '',
}: SkillGapRadarProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center border rounded-lg bg-gray-50 ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 text-sm">No skill gap data available</p>
      </div>
    );
  }

  // Custom tooltip for better readability
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{data.skill}</p>
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

  // Determine which comparison series to show
  const shouldShowTeam = compareType === 'team' && data.some(d => d.teamAverage !== undefined);
  const shouldShowTarget = compareType !== 'team';

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={data} margin={{ top: 30, right: 120, bottom: 30, left: 120 }}>
          <PolarGrid stroke="#e5e7eb" strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="skill"
            tick={{ fontSize: 11 }}
            stroke="#6b7280"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 11 }}
            stroke="#6b7280"
          />

          {/* Actual performance */}
          <Radar
            name="Actual Performance"
            dataKey="actual"
            stroke={CHART_COLORS[0]}
            fill={CHART_COLORS[0]}
            fillOpacity={0.6}
            isAnimationActive={true}
          />

          {/* Target or Team Average comparison */}
          {shouldShowTarget && (
            <Radar
              name="Target Performance"
              dataKey="target"
              stroke={CHART_COLORS[1]}
              fill={CHART_COLORS[1]}
              fillOpacity={0.2}
              strokeDasharray="5 5"
              isAnimationActive={true}
            />
          )}

          {shouldShowTeam && (
            <Radar
              name="Team Average"
              dataKey="teamAverage"
              stroke={CHART_COLORS[2]}
              fill={CHART_COLORS[2]}
              fillOpacity={0.2}
              strokeDasharray="5 5"
              isAnimationActive={true}
            />
          )}

          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            verticalAlign="bottom"
            height={36}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
