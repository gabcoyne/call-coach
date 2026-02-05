"use client";

import { TeamInsight } from "@/types/coaching";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, Users } from "lucide-react";

interface TeamInsightCardProps {
  insight: TeamInsight;
}

export function TeamInsightCard({ insight }: TeamInsightCardProps) {
  const getTrendIcon = () => {
    switch (insight.trend) {
      case 'up':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      case 'stable':
        return <Minus className="h-5 w-5 text-gray-600" />;
    }
  };

  const getTrendColor = () => {
    switch (insight.trend) {
      case 'up':
        return 'text-green-600 bg-green-50';
      case 'down':
        return 'text-red-600 bg-red-50';
      case 'stable':
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getTypeLabel = () => {
    switch (insight.type) {
      case 'trend':
        return 'Team Trend';
      case 'comparison':
        return 'Team Comparison';
      case 'achievement':
        return 'Team Achievement';
    }
  };

  return (
    <Card className="border-l-4 border-l-prefect-purple-500 hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="secondary" className="text-xs">
                {getTypeLabel()}
              </Badge>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Users className="h-3 w-3" />
                <span>{insight.team_size} reps</span>
              </div>
            </div>
            <CardTitle className="text-base">{insight.title}</CardTitle>
          </div>
          <div className={`p-2 rounded-lg ${getTrendColor()}`}>
            {getTrendIcon()}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">{insight.description}</p>

        <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
          <div>
            <p className="text-xs text-muted-foreground">{insight.metric}</p>
            <p className="text-2xl font-bold text-foreground">{insight.value}</p>
          </div>
          {insight.change !== 0 && (
            <div className={`flex items-center gap-1 ${
              insight.change > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {insight.change > 0 ? (
                <TrendingUp className="h-4 w-4" />
              ) : (
                <TrendingDown className="h-4 w-4" />
              )}
              <span className="text-sm font-semibold">
                {Math.abs(insight.change)}%
              </span>
            </div>
          )}
        </div>

        <div className="text-xs text-muted-foreground">
          Period: {insight.period}
        </div>
      </CardContent>
    </Card>
  );
}
