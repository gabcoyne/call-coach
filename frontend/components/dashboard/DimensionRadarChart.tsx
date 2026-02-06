"use client";

import { Card } from "@/components/ui/card";
import { ScoreTrends } from "@/types/coaching";
// Optimized imports: import only specific components from recharts
import { RadarChart } from "recharts/lib/chart/RadarChart";
import { Radar } from "recharts/lib/polar/Radar";
import { PolarGrid } from "recharts/lib/polar/PolarGrid";
import { PolarAngleAxis } from "recharts/lib/polar/PolarAngleAxis";
import { PolarRadiusAxis } from "recharts/lib/polar/PolarRadiusAxis";
import { ResponsiveContainer } from "recharts/lib/component/ResponsiveContainer";
import { Legend } from "recharts/lib/component/Legend";
import { Tooltip } from "recharts/lib/component/Tooltip";

interface DimensionRadarChartProps {
  scoreTrends: ScoreTrends;
  teamAverages?: Record<string, number>;
  showTeamAverage?: boolean;
}

const DIMENSION_LABELS = {
  product_knowledge: "Product Knowledge",
  discovery: "Discovery",
  objection_handling: "Objection Handling",
  engagement: "Engagement",
};

export function DimensionRadarChart({
  scoreTrends,
  teamAverages,
  showTeamAverage = false,
}: DimensionRadarChartProps) {
  // Calculate average scores for each dimension
  const dimensions = Object.keys(scoreTrends).filter((d) => d !== "overall");

  if (dimensions.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Dimension Score Distribution</h3>
        <p className="text-sm text-muted-foreground">No dimension data available</p>
      </Card>
    );
  }

  const chartData = dimensions.map((dimension) => {
    const scores = scoreTrends[dimension]?.scores || [];
    const validScores = scores.filter((s): s is number => s !== null && s !== undefined);
    const avgScore =
      validScores.length > 0
        ? Math.round(validScores.reduce((a, b) => a + b, 0) / validScores.length)
        : 0;

    const dataPoint: any = {
      dimension: DIMENSION_LABELS[dimension as keyof typeof DIMENSION_LABELS] || dimension,
      repScore: avgScore,
    };

    if (showTeamAverage && teamAverages && teamAverages[dimension]) {
      dataPoint.teamAverage = teamAverages[dimension];
    }

    return dataPoint;
  });

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Dimension Score Distribution</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="dimension" tick={{ fill: "#64748b", fontSize: 12 }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 12 }} />
          <Radar
            name="Rep Score"
            dataKey="repScore"
            stroke="#2563eb"
            fill="#2563eb"
            fillOpacity={0.6}
          />
          {showTeamAverage && teamAverages && (
            <Radar
              name="Team Average"
              dataKey="teamAverage"
              stroke="#16a34a"
              fill="#16a34a"
              fillOpacity={0.3}
            />
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "14px" }} />
        </RadarChart>
      </ResponsiveContainer>
    </Card>
  );
}
