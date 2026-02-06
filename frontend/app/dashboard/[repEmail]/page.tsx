"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useRepInsights } from "@/lib/hooks/use-rep-insights";
import { ScoreCard } from "@/components/coaching/ScoreCard";
import { TrendChart, TrendDataPoint } from "@/components/coaching/TrendChart";
import { SkillGapChart, SkillGapData } from "@/components/coaching/SkillGapChart";
import { TeamComparisonChart, ComparisonData } from "@/components/coaching/TeamComparisonChart";
import { DimensionBreakdownChart, DimensionData } from "@/components/coaching/DimensionBreakdownChart";
import { RecentActivityFeed, ActivityItem } from "@/components/coaching/RecentActivityFeed";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, TrendingUp, TrendingDown, Calendar, Phone } from "lucide-react";
import { getScoreColor } from "@/lib/colors";
import Link from "next/link";

// Time range options
type TimeRange = 'last_7_days' | 'last_30_days' | 'last_90_days' | 'all_time';

const TIME_RANGE_OPTIONS = [
  { value: 'last_7_days' as TimeRange, label: 'Last 7 Days' },
  { value: 'last_30_days' as TimeRange, label: 'Last 30 Days' },
  { value: 'last_90_days' as TimeRange, label: 'Last 90 Days' },
  { value: 'all_time' as TimeRange, label: 'All Time' },
] as const;

interface DashboardPageProps {
  params: {
    repEmail: string;
  };
}

export default function RepDashboardPage({ params }: DashboardPageProps) {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [timeRange, setTimeRange] = useState<TimeRange>('last_30_days');

  // Decode the email from URL
  const repEmail = decodeURIComponent(params.repEmail);

  // Check if current user is a manager
  const isManager = user?.publicMetadata?.role === 'manager';
  const currentUserEmail = user?.emailAddresses[0]?.emailAddress;

  // Check authorization: managers can view anyone, reps can only view themselves
  const canViewData = isManager || currentUserEmail === repEmail;

  // Fetch insights using the hook
  const { data: insights, isLoading, error } = useRepInsights(
    canViewData ? repEmail : null,
    { time_period: timeRange }
  );

  useEffect(() => {
    if (isLoaded && !canViewData) {
      // Return 403 for reps trying to view other reps' data
      if (currentUserEmail && currentUserEmail !== repEmail) {
        router.push(`/dashboard/${encodeURIComponent(currentUserEmail)}`);
      } else {
        router.push('/sign-in');
      }
    }
  }, [isLoaded, canViewData, currentUserEmail, repEmail, router]);

  // Calculate average dimension scores
  const calculateAverageDimensionScores = () => {
    if (!insights?.score_trends) return [];

    return Object.entries(insights.score_trends)
      .filter(([key]) => key !== 'overall')
      .map(([dimension, data]) => {
        const scores = data.scores.filter((s): s is number => s !== null);
        const avgScore = scores.length > 0
          ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
          : 0;

        return {
          dimension,
          avgScore,
          displayName: dimension.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        };
      })
      .sort((a, b) => b.avgScore - a.avgScore);
  };

  // Calculate overall average score
  const calculateOverallScore = () => {
    if (!insights?.score_trends.overall?.scores) return null;
    const scores = insights.score_trends.overall.scores.filter((s): s is number => s !== null);
    if (scores.length === 0) return null;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  // Prepare trend data for chart
  const prepareTrendData = (): { data: TrendDataPoint[], dimensions: string[] } => {
    if (!insights?.score_trends) return { data: [], dimensions: [] };

    const dimensions = Object.keys(insights.score_trends).filter(k => k !== 'overall');
    const dates = insights.score_trends.overall?.dates || [];

    const data: TrendDataPoint[] = dates.map((date, index) => {
      const point: TrendDataPoint = { date };

      dimensions.forEach((dimension) => {
        const score = insights.score_trends[dimension]?.scores[index];
        point[dimension] = score !== null ? score : 0;
      });

      return point;
    });

    return { data, dimensions };
  };

  // Get recent calls (top 10)
  const getRecentCalls = () => {
    if (!insights?.score_trends.overall?.dates) return [];

    const calls = insights.score_trends.overall.dates
      .map((date, index) => ({
        call_id: `call-${index}`,
        date,
        call_type: 'Sales Call',
        overall_score: insights.score_trends.overall?.scores[index] ?? null,
      }))
      .reverse()
      .slice(0, 10);

    return calls;
  };

  if (!isLoaded) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="h-8 bg-gray-200 rounded w-1/3 animate-pulse" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-6">
                <div className="h-6 bg-gray-200 rounded w-1/2 mb-4" />
                <div className="h-10 bg-gray-100 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!canViewData) {
    return null; // Will redirect in useEffect
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 bg-gray-200 rounded w-1/3 animate-pulse" />
          <div className="h-10 bg-gray-200 rounded w-40 animate-pulse" />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-6 space-y-3">
                <div className="h-4 bg-gray-200 rounded w-1/2" />
                <div className="h-8 bg-gray-100 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="animate-pulse">
          <CardContent className="pt-6">
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-4" />
            <div className="h-64 bg-gray-100 rounded" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Rep Dashboard</h1>
            <p className="text-muted-foreground mt-1">{repEmail}</p>
          </div>
        </div>

        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-800">Error Loading Dashboard</CardTitle>
            <CardDescription className="text-red-600">
              {error.message || 'Failed to load rep insights'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              onClick={() => window.location.reload()}
              className="gap-2"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Rep Dashboard</h1>
            <p className="text-muted-foreground mt-1">{repEmail}</p>
          </div>
        </div>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center">
              No insights available for this rep. Make sure calls have been analyzed.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const totalCalls = insights.rep_info.calls_analyzed;
  const overallScore = calculateOverallScore();
  const dimensionScores = calculateAverageDimensionScores();
  const { data: trendData, dimensions } = prepareTrendData();
  const recentCalls = getRecentCalls();
  const hasEnoughData = totalCalls >= 3;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header with Back Button and Time Range Filter */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {insights.rep_info.name}
            </h1>
            <p className="text-muted-foreground mt-1">{repEmail}</p>
          </div>
        </div>

        {/* Time Range Filter */}
        <Select value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TIME_RANGE_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Performance Overview Section */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Performance Overview</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {overallScore !== null ? (
            <ScoreCard
              score={overallScore}
              title="Overall Average Score"
              subtitle={`Based on ${totalCalls} call${totalCalls !== 1 ? 's' : ''}`}
            />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-gray-500">No score data available</p>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Calls</p>
                  <p className="text-3xl font-bold mt-2">{totalCalls}</p>
                </div>
                <Phone className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {insights.rep_info.date_range.period}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Date Range</p>
                  <p className="text-sm font-semibold mt-2">
                    {new Date(insights.rep_info.date_range.start).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-500">to</p>
                  <p className="text-sm font-semibold">
                    {new Date(insights.rep_info.date_range.end).toLocaleDateString()}
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Performance Trend Charts */}
      {hasEnoughData ? (
        <div>
          <h2 className="text-xl font-semibold mb-4">Performance Trends</h2>
          <Card>
            <CardHeader>
              <CardTitle>Score Trends Over Time</CardTitle>
              <CardDescription>
                Track performance across different coaching dimensions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TrendChart
                data={trendData}
                dimensions={dimensions}
                height={350}
              />
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-800 text-center">
              Not enough data to display trends. At least 3 analyzed calls are required.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Aggregated Metrics - Average Dimension Scores */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Dimension Breakdown</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {dimensionScores.map((dim) => (
            <ScoreCard
              key={dim.dimension}
              score={dim.avgScore}
              title={dim.displayName}
            />
          ))}
        </div>
      </div>

      {/* Recent Calls List */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Calls</h2>
        <Card>
          <CardContent className="pt-6">
            {recentCalls.length > 0 ? (
              <div className="space-y-3">
                {recentCalls.map((call, index) => {
                  const scoreColor = call.overall_score ? getScoreColor(call.overall_score) : null;

                  return (
                    <div
                      key={call.call_id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="text-sm text-gray-500">#{index + 1}</div>
                        <div>
                          <p className="text-sm font-medium">{call.call_type}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(call.date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {call.overall_score !== null ? (
                          <div
                            className="px-3 py-1 rounded-full text-sm font-semibold"
                            style={{
                              backgroundColor: scoreColor?.bg,
                              color: scoreColor?.text,
                            }}
                          >
                            {call.overall_score}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">N/A</span>
                        )}
                        <Link
                          href={`/calls/${call.call_id}`}
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          View Details
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center">No calls available</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
