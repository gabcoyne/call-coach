import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { ScoreBadge } from "@/components/ui/score-badge";
import { cn } from "@/lib/utils";

interface OverallScoreBadgeProps {
  score: number;
  previousScore?: number | null;
  className?: string;
}

export function OverallScoreBadge({ score, previousScore, className }: OverallScoreBadgeProps) {
  // Calculate trend
  let trend: "up" | "down" | "same" | null = null;
  let trendValue: number | null = null;

  if (previousScore !== null && previousScore !== undefined) {
    const diff = score - previousScore;
    trendValue = diff;

    if (Math.abs(diff) < 2) {
      trend = "same";
    } else if (diff > 0) {
      trend = "up";
    } else {
      trend = "down";
    }
  }

  return (
    <Card className={cn("", className)}>
      <CardContent className="p-6">
        <div className="flex flex-col items-center justify-center space-y-2">
          <p className="text-sm font-medium text-muted-foreground">Overall Score</p>
          <div className="flex items-center gap-2">
            <span className="text-5xl font-bold">{Math.round(score)}</span>
            <span className="text-2xl text-muted-foreground">/100</span>
          </div>
          <ScoreBadge score={score} className="text-base px-4 py-1" />

          {trend && trendValue !== null && (
            <div
              className={cn(
                "flex items-center gap-1 text-sm",
                trend === "up" && "text-green-600",
                trend === "down" && "text-red-600",
                trend === "same" && "text-muted-foreground"
              )}
            >
              {trend === "up" && <TrendingUp className="h-4 w-4" />}
              {trend === "down" && <TrendingDown className="h-4 w-4" />}
              {trend === "same" && <Minus className="h-4 w-4" />}
              <span>
                {trend === "up" && "+"}
                {trend === "same" ? "No change" : `${trendValue.toFixed(1)}`}
                {trend !== "same" && " from last call"}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
