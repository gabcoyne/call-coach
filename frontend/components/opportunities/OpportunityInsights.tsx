"use client";

/**
 * OpportunityInsights Component
 *
 * Displays AI-generated coaching insights for an opportunity using the analyze_opportunity MCP tool.
 * Shows recurring themes, objection patterns, relationship trends, and recommendations.
 */
import { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Lightbulb,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  TrendingUp,
  MessageSquare,
  Target,
  AlertTriangle,
} from "lucide-react";

interface OpportunityInsights {
  themes: string[];
  objections: {
    objection: string;
    frequency: number;
    status: string;
  }[];
  relationship_strength: {
    score: number;
    trend: string;
    notes: string;
  };
  recommendations: string[];
}

interface InsightsResponse {
  insights: OpportunityInsights;
  generated_at: string;
}

async function fetcher(url: string): Promise<InsightsResponse> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch insights");
  }
  return response.json();
}

interface OpportunityInsightsProps {
  opportunityId: string;
}

export function OpportunityInsights({ opportunityId }: OpportunityInsightsProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [shouldFetch, setShouldFetch] = useState(false);

  // Only fetch when user expands for the first time
  const { data, error, isLoading } = useSWR<InsightsResponse>(
    shouldFetch || isExpanded ? `/api/opportunities/${opportunityId}/insights` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 3600000, // Cache for 1 hour
    }
  );

  const toggleExpanded = () => {
    if (!isExpanded && !shouldFetch) {
      setShouldFetch(true);
    }
    setIsExpanded(!isExpanded);
  };

  const getRelationshipColor = (score: number) => {
    if (score >= 70) return "success";
    if (score >= 40) return "warning";
    return "destructive";
  };

  return (
    <Card className="border-2 border-prefect-pink/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <div className="p-2 rounded-full bg-prefect-pink/10">
              <Lightbulb className="h-5 w-5 text-prefect-pink" />
            </div>
            AI Coaching Insights
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={toggleExpanded} className="ml-2">
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
        <p className="text-sm text-muted-foreground pl-12">
          Holistic analysis across all calls and emails
        </p>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0 border-t">
          {isLoading ? (
            <InsightsSkeleton />
          ) : error ? (
            <div className="flex items-center gap-2 text-destructive pt-4">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Failed to load insights. Please try again.</span>
            </div>
          ) : data ? (
            <div className="space-y-6 pt-4">
              {/* Recurring Themes */}
              {data.insights.themes && data.insights.themes.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <MessageSquare className="h-4 w-4 text-prefect-pink" />
                    <h3 className="font-semibold">Recurring Themes</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {data.insights.themes.map((theme, i) => (
                      <Badge key={i} variant="prefect">
                        {theme}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Objection Patterns */}
              {data.insights.objections && data.insights.objections.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <h3 className="font-semibold">Objection Patterns</h3>
                  </div>
                  <div className="space-y-2">
                    {data.insights.objections.map((obj, i) => (
                      <div
                        key={i}
                        className="flex items-start justify-between p-3 rounded-lg bg-muted/50"
                      >
                        <div className="flex-1">
                          <div className="font-medium text-sm">{obj.objection}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Mentioned {obj.frequency} time
                            {obj.frequency !== 1 ? "s" : ""}
                          </div>
                        </div>
                        <Badge
                          variant={
                            obj.status === "resolved"
                              ? "success"
                              : obj.status === "partially_resolved"
                                ? "warning"
                                : "outline"
                          }
                        >
                          {obj.status.replace("_", " ")}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Relationship Strength */}
              {data.insights.relationship_strength && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <h3 className="font-semibold">Relationship Strength</h3>
                  </div>
                  <div className="p-4 rounded-lg bg-muted/50">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium">Score</span>
                      <Badge
                        variant={getRelationshipColor(data.insights.relationship_strength.score)}
                        className="text-base px-3"
                      >
                        {data.insights.relationship_strength.score}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium">Trend</span>
                      <Badge variant="outline">{data.insights.relationship_strength.trend}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {data.insights.relationship_strength.notes}
                    </p>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {data.insights.recommendations && data.insights.recommendations.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="h-4 w-4 text-blue-500" />
                    <h3 className="font-semibold">Coaching Recommendations</h3>
                  </div>
                  <div className="space-y-2">
                    {data.insights.recommendations.map((recommendation, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20"
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-semibold">
                            {i + 1}
                          </div>
                        </div>
                        <p className="text-sm text-foreground flex-1">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Generated timestamp */}
              <div className="text-xs text-muted-foreground pt-4 border-t">
                Generated:{" "}
                {new Date(data.generated_at).toLocaleString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </div>
            </div>
          ) : null}
        </CardContent>
      )}
    </Card>
  );
}

function InsightsSkeleton() {
  return (
    <div className="space-y-6 pt-4">
      <div>
        <Skeleton className="h-5 w-32 mb-3" />
        <div className="flex gap-2">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-6 w-28" />
        </div>
      </div>
      <div>
        <Skeleton className="h-5 w-32 mb-3" />
        <Skeleton className="h-20 w-full" />
      </div>
      <div>
        <Skeleton className="h-5 w-32 mb-3" />
        <Skeleton className="h-24 w-full" />
      </div>
    </div>
  );
}
