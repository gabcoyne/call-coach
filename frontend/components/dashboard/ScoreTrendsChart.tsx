"use client";

import { Card } from "@/components/ui/card";
import { ScoreTrends } from "@/types/coaching";
// Optimized imports: import only specific components from recharts
import { LineChart } from "recharts/lib/chart/LineChart";
import { Line } from "recharts/lib/cartesian/Line";
import { XAxis } from "recharts/lib/cartesian/XAxis";
import { YAxis } from "recharts/lib/cartesian/YAxis";
import { CartesianGrid } from "recharts/lib/cartesian/CartesianGrid";
import { Tooltip } from "recharts/lib/component/Tooltip";
import { Legend } from "recharts/lib/component/Legend";
import { ResponsiveContainer } from "recharts/lib/component/ResponsiveContainer";

interface ScoreTrendsChartProps {
  scoreTrends: ScoreTrends;
  showTeamAverage?: boolean;
}

const DIMENSION_COLORS = {
  product_knowledge: '#2563eb', // blue
  discovery: '#16a34a', // green
  objection_handling: '#ea580c', // orange
  engagement: '#9333ea', // purple
  overall: '#0f172a', // dark
};

const DIMENSION_LABELS = {
  product_knowledge: 'Product Knowledge',
  discovery: 'Discovery',
  objection_handling: 'Objection Handling',
  engagement: 'Engagement',
  overall: 'Overall',
};

export function ScoreTrendsChart({ scoreTrends, showTeamAverage = false }: ScoreTrendsChartProps) {
  // Transform data for Recharts
  const dimensions = Object.keys(scoreTrends).filter(d => d !== 'overall');

  if (dimensions.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Score Trends</h3>
        <p className="text-sm text-muted-foreground">No trend data available</p>
      </Card>
    );
  }

  // Get the longest date array to use as base
  const baseDimension = dimensions[0];
  const dates = scoreTrends[baseDimension]?.dates || [];

  // Transform into array of objects for Recharts
  const chartData = dates.map((date, index) => {
    const dataPoint: any = { date };

    dimensions.forEach(dimension => {
      const scores = scoreTrends[dimension]?.scores || [];
      dataPoint[dimension] = scores[index] ?? null;
    });

    return dataPoint;
  });

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(date);
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Score Trends Over Time</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            domain={[0, 100]}
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            labelFormatter={formatDate}
            formatter={(value: any) => [`${value}`, '']}
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            formatter={(value) => DIMENSION_LABELS[value as keyof typeof DIMENSION_LABELS] || value}
          />
          {dimensions.map((dimension) => (
            <Line
              key={dimension}
              type="monotone"
              dataKey={dimension}
              name={DIMENSION_LABELS[dimension as keyof typeof DIMENSION_LABELS] || dimension}
              stroke={DIMENSION_COLORS[dimension as keyof typeof DIMENSION_COLORS] || '#000000'}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
