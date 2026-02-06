"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SkillGap } from "@/types/coaching";
import { TrendingDown, AlertCircle } from "lucide-react";

interface SkillGapCardsProps {
  skillGaps: SkillGap[];
}

const PRIORITY_CONFIG = {
  high: {
    color: "bg-red-100 text-red-800 border-red-200",
    icon: AlertCircle,
    label: "High Priority",
  },
  medium: {
    color: "bg-yellow-100 text-yellow-800 border-yellow-200",
    icon: TrendingDown,
    label: "Medium Priority",
  },
  low: {
    color: "bg-blue-100 text-blue-800 border-blue-200",
    icon: TrendingDown,
    label: "Low Priority",
  },
};

export function SkillGapCards({ skillGaps }: SkillGapCardsProps) {
  if (skillGaps.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Skill Gaps</h3>
        <p className="text-sm text-muted-foreground">No skill gaps identified</p>
      </Card>
    );
  }

  // Sort by priority (high > medium > low) and then by gap size
  const sortedGaps = [...skillGaps].sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;
    return b.gap - a.gap;
  });

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Skill Gaps</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedGaps.map((gap, index) => {
          const config = PRIORITY_CONFIG[gap.priority];
          const Icon = config.icon;
          const progressPercentage = (gap.current_score / gap.target_score) * 100;

          return (
            <Card
              key={index}
              className="p-4 border-l-4"
              style={{ borderLeftColor: config.color.split(" ")[0].replace("bg-", "#") }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-medium text-sm">{gap.area}</h4>
                  <Badge variant="outline" className={`mt-1 ${config.color}`}>
                    <Icon className="w-3 h-3 mr-1" />
                    {config.label}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Current</span>
                  <span className="font-medium text-foreground">{gap.current_score}</span>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Target</span>
                  <span className="font-medium text-foreground">{gap.target_score}</span>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Gap</span>
                  <span className="font-medium text-red-600">{gap.gap}</span>
                </div>

                {/* Progress bar */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-prefect-blue h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 text-right">
                    {Math.round(progressPercentage)}% to target
                  </p>
                </div>

                <p className="text-xs text-muted-foreground mt-2">
                  Based on {gap.sample_size} call{gap.sample_size !== 1 ? "s" : ""}
                </p>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
