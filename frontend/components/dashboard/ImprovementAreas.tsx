"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ImprovementArea } from "@/types/coaching";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ImprovementAreasProps {
  improvementAreas: ImprovementArea[];
  recentWins: string[];
}

const TREND_CONFIG = {
  improving: {
    icon: TrendingUp,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Improving',
  },
  declining: {
    icon: TrendingDown,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Declining',
  },
  stable: {
    icon: Minus,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    label: 'Stable',
  },
};

export function ImprovementAreas({ improvementAreas, recentWins }: ImprovementAreasProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Improvement Areas */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Areas to Focus On</h3>
        {improvementAreas.length === 0 ? (
          <p className="text-sm text-muted-foreground">No improvement areas identified</p>
        ) : (
          <div className="space-y-3">
            {improvementAreas.map((area, index) => {
              const config = TREND_CONFIG[area.trend];
              const Icon = config.icon;

              return (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${config.bgColor} ${config.borderColor}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-sm">{area.area}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className={config.color}>
                          <Icon className="w-3 h-3 mr-1" />
                          {config.label}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {area.change > 0 ? '+' : ''}{area.change} points
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Recent</p>
                      <p className="text-lg font-semibold">{area.recent_score}</p>
                      <p className="text-xs text-muted-foreground">
                        was {area.older_score}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Recent Wins */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Wins</h3>
        {recentWins.length === 0 ? (
          <p className="text-sm text-muted-foreground">No recent wins recorded</p>
        ) : (
          <div className="space-y-3">
            {recentWins.map((win, index) => (
              <div
                key={index}
                className="p-3 rounded-lg bg-green-50 border border-green-200"
              >
                <div className="flex items-start gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700">{win}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
