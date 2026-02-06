"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, AlertTriangle, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface QualityIssue {
  type: string;
  severity: "high" | "medium" | "low";
  message: string;
  metric: number;
  affected_count: number;
}

interface DimensionStat {
  dimension: string;
  total_feedback: number;
  accuracy_rate: number;
  helpfulness_rate: number;
}

interface FeedbackStatsData {
  overall_stats: {
    total_feedback: number;
    accurate_count: number;
    inaccurate_count: number;
    missing_context_count: number;
    helpful_count: number;
    not_helpful_count: number;
    accuracy_rate: number;
    helpfulness_rate: number;
  };
  dimension_stats: DimensionStat[];
  quality_issues: QualityIssue[];
  time_period: string;
}

interface FeedbackStatsProps {
  dimension?: string;
  timePeriod?: "last_7_days" | "last_30_days" | "last_90_days" | "all_time";
  repEmail?: string;
}

export function FeedbackStats({
  dimension,
  timePeriod = "last_30_days",
  repEmail,
}: FeedbackStatsProps) {
  const [stats, setStats] = useState<FeedbackStatsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const params = new URLSearchParams();
        if (dimension) params.append("dimension", dimension);
        params.append("time_period", timePeriod);
        if (repEmail) params.append("rep_email", repEmail);

        const response = await fetch(`/api/coaching-sessions/feedback-stats?${params}`);

        if (!response.ok) {
          throw new Error("Failed to fetch feedback stats");
        }

        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching feedback stats:", err);
        setError(err instanceof Error ? err.message : "Failed to load statistics");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [dimension, timePeriod, repEmail]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Coaching Quality Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">Loading statistics...</div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Coaching Quality Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-600">{error}</div>
        </CardContent>
      </Card>
    );
  }

  const { overall_stats, dimension_stats, quality_issues } = stats;

  if (overall_stats.total_feedback === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Coaching Quality Metrics</CardTitle>
          <CardDescription>No feedback data available yet</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Feedback will appear here once coaching sessions are reviewed
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Overall Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Accuracy Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold">{overall_stats.accuracy_rate?.toFixed(0)}%</div>
              <div className="text-xs text-muted-foreground">
                <div className="font-semibold text-green-600">
                  {overall_stats.accurate_count} accurate
                </div>
                <div className="font-semibold text-red-600">
                  {overall_stats.inaccurate_count} inaccurate
                </div>
              </div>
            </div>
            {(overall_stats.accuracy_rate || 0) >= 90 && (
              <Badge className="mt-3 bg-green-600">Target Met</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Helpfulness Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold">
                {overall_stats.helpfulness_rate?.toFixed(0)}%
              </div>
              <div className="text-xs text-muted-foreground">
                <div className="font-semibold text-green-600">
                  {overall_stats.helpful_count} helpful
                </div>
                <div className="font-semibold text-red-600">
                  {overall_stats.not_helpful_count} not helpful
                </div>
              </div>
            </div>
            {(overall_stats.helpfulness_rate || 0) >= 80 && (
              <Badge className="mt-3 bg-green-600">Target Met</Badge>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quality Issues */}
      {quality_issues.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              {quality_issues.some((i) => i.severity === "high") ? (
                <AlertCircle className="h-4 w-4 text-red-600" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
              )}
              Quality Issues Detected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {quality_issues.map((issue, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "rounded-lg p-3 text-sm",
                    issue.severity === "high"
                      ? "bg-red-100 text-red-900"
                      : "bg-yellow-100 text-yellow-900"
                  )}
                >
                  <div className="font-semibold">{issue.message}</div>
                  <div className="text-xs mt-1">
                    Affecting {issue.affected_count} feedback entries
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dimension-Specific Stats */}
      {dimension_stats.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">By Coaching Dimension</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dimension_stats.map((d) => (
                <div key={d.dimension} className="rounded-lg border p-3 space-y-2">
                  <div className="font-semibold capitalize">{d.dimension.replace(/_/g, " ")}</div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Accuracy</div>
                      <div className="text-lg font-semibold">{d.accuracy_rate?.toFixed(0)}%</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Helpfulness</div>
                      <div className="text-lg font-semibold">{d.helpfulness_rate?.toFixed(0)}%</div>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {d.total_feedback} feedback entries
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Summary */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Summary</CardTitle>
        </CardHeader>
        <CardContent className="text-sm">
          <div className="space-y-2 text-blue-900">
            <div>
              Total feedback entries: <strong>{overall_stats.total_feedback}</strong>
            </div>
            <div>
              Missing context mentions: <strong>{overall_stats.missing_context_count}</strong>
            </div>
            <div className="pt-2 text-xs">Data from {stats.time_period.replace(/_/g, " ")}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
