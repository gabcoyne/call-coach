"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useRepInsights } from "@/lib/hooks/use-rep-insights";
import { ScoreCard } from "@/components/coaching/ScoreCard";
import { TrendChart, TrendDataPoint } from "@/components/coaching/TrendChart";
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
      <div className="container mx-auto p-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-2">No Data Available</h2>
          <p className="text-sm text-muted-foreground">
            No insights available for this rep. Make sure calls have been analyzed.
          </p>
        </Card>
      </div>
    );
  }

  // Mock call history - in production this would come from the API
  const callHistory = insights.score_trends.overall?.dates.map((date, index) => ({
    call_id: `call-${index}`,
    title: `Sales Call ${index + 1}`,
    date,
    duration_seconds: 1800 + Math.random() * 1800,
    call_type: ['discovery', 'demo', 'technical_deep_dive'][Math.floor(Math.random() * 3)],
    product: ['prefect', 'horizon'][Math.floor(Math.random() * 2)],
    overall_score: insights.score_trends.overall?.scores[index] ?? null,
  })) || [];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header with period selector */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>
        <TimePeriodSelector value={timePeriod} onChange={setTimePeriod} />
      </div>

      {/* Manager-only Rep Selector */}
      {isManager && (
        <Card className="p-4">
          <RepSelector
            reps={[
              { email: repEmail, name: insights.rep_info.name },
              // In production, this would be fetched from an API
            ]}
            selectedRepEmail={repEmail}
            onChange={(email) => router.push(`/dashboard/${encodeURIComponent(email)}`)}
            currentUserEmail={currentUserEmail}
          />
        </Card>
      )}

      {/* Dashboard Header */}
      <DashboardHeader
        repInfo={insights.rep_info}
        overallScore={calculateOverallScore()}
      />

      {/* Score Trends Chart */}
      <ScoreTrendsChart
        scoreTrends={insights.score_trends}
        showTeamAverage={isManager}
      />

      {/* Radar Chart */}
      <DimensionRadarChart
        scoreTrends={insights.score_trends}
        showTeamAverage={isManager}
      />

      {/* Skill Gaps */}
      <SkillGapCards skillGaps={insights.skill_gaps} />

      {/* Improvement Areas and Recent Wins */}
      <ImprovementAreas
        improvementAreas={insights.improvement_areas}
        recentWins={insights.recent_wins}
      />

      {/* Coaching Plan */}
      <CoachingPlanSection
        coachingPlan={insights.coaching_plan}
        onExport={handleExportPlan}
        onShare={handleSharePlan}
      />

      {/* Call History */}
      <CallHistoryTable
        calls={callHistory}
        onCallClick={handleCallClick}
      />
    </div>
  );
}
