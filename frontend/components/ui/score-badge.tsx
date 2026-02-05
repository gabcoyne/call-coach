import * as React from "react";
import { Badge } from "./badge";
import { cn } from "@/lib/utils";

interface ScoreBadgeProps {
  score: number;
  maxScore?: number;
  className?: string;
  showPercentage?: boolean;
}

export function ScoreBadge({
  score,
  maxScore = 100,
  className,
  showPercentage = true,
}: ScoreBadgeProps) {
  const percentage = (score / maxScore) * 100;

  // Determine color based on score percentage
  const getVariant = (percent: number) => {
    if (percent >= 90) return "success";
    if (percent >= 75) return "info";
    if (percent >= 60) return "warning";
    return "destructive";
  };

  const variant = getVariant(percentage);
  const displayValue = showPercentage
    ? `${Math.round(percentage)}%`
    : `${score}/${maxScore}`;

  return (
    <Badge variant={variant} className={cn("font-semibold", className)}>
      {displayValue}
    </Badge>
  );
}

interface DimensionScoreCardProps {
  dimension: string;
  score: number;
  maxScore?: number;
  description?: string;
  className?: string;
}

export function DimensionScoreCard({
  dimension,
  score,
  maxScore = 100,
  description,
  className,
}: DimensionScoreCardProps) {
  const percentage = (score / maxScore) * 100;

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-4 space-y-2",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <h4 className="font-semibold">{dimension}</h4>
        <ScoreBadge score={score} maxScore={maxScore} />
      </div>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
        <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full transition-all duration-300",
              percentage >= 90 && "bg-green-500",
              percentage >= 75 && percentage < 90 && "bg-prefect-blue-500",
              percentage >= 60 && percentage < 75 && "bg-prefect-sunrise1",
              percentage < 60 && "bg-red-500"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
