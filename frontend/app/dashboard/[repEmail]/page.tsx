"use client";

import { use, useState, useEffect } from "react";
import { useUser } from "@/lib/hooks/use-auth";
import { useRouter } from "next/navigation";
import { useRepInsights } from "@/lib/hooks";
import { useCurrentUser } from "@/lib/hooks/use-current-user";
import { isManager, canViewRep } from "@/lib/rbac";
import { ScoreCard } from "@/components/coaching/ScoreCard";
import { TrendChart, TrendDataPoint } from "@/components/coaching/TrendChart";
import { SkillGapChart, SkillGapData } from "@/components/coaching/SkillGapChart";
import { TeamComparisonChart, ComparisonData } from "@/components/coaching/TeamComparisonChart";
import {
  DimensionBreakdownChart,
  DimensionData,
} from "@/components/coaching/DimensionBreakdownChart";
import { RecentActivityFeed, ActivityItem } from "@/components/coaching/RecentActivityFeed";
import { FeedbackStats } from "@/components/coaching/FeedbackStats";
import {
  ScoreTrendChart,
  SkillGapRadar,
  TeamComparisonBar,
  ActivityTimeline,
  ObjectionBreakdown,
} from "@/components/charts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, TrendingUp, TrendingDown, Calendar, Phone } from "lucide-react";
import { getScoreColor } from "@/lib/colors";
import Link from "next/link";

// Time range options
type TimeRange = "last_7_days" | "last_30_days" | "last_90_days" | "all_time";

const TIME_RANGE_OPTIONS = [
  { value: "last_7_days" as TimeRange, label: "Last 7 Days" },
  { value: "last_30_days" as TimeRange, label: "Last 30 Days" },
  { value: "last_90_days" as TimeRange, label: "Last 90 Days" },
  { value: "all_time" as TimeRange, label: "All Time" },
] as const;

interface DashboardPageProps {
  params: Promise<{
    repEmail: string;
  }>;
}

// Mock data for team average comparison - in production this would come from the backend
const MOCK_TEAM_AVERAGES: Record<string, number> = {
  "Qualification Skills": 72,
  "Discovery & Diagnosis": 68,
  "Value Communication": 75,
  "Objection Handling": 70,
  "Deal Advancement": 73,
  "Relationship Building": 76,
};

export default function RepDashboardPage({ params }: DashboardPageProps) {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [timeRange, setTimeRange] = useState<TimeRange>("last_30_days");

  // Unwrap params Promise and decode email
  const { repEmail: rawRepEmail } = use(params);
  const repEmail = decodeURIComponent(rawRepEmail);

  // Get current user from backend
  const { data: currentUser, isLoading: isLoadingUser, error: userError } = useCurrentUser();

  // Check authorization: managers can view anyone, reps can only view themselves
  const canViewData = currentUser ? canViewRep(currentUser, repEmail) : false;

  // Fetch insights using the hook - only fetch if authorized
  const {
    data: insights,
    isLoading,
    error,
  } = useRepInsights(canViewData ? repEmail : null, { time_period: timeRange });

  // Handle authorization redirects
  useEffect(() => {
    if (!isLoaded || isLoadingUser) return;

    if (!currentUser) {
      router.push("/sign-in");
      return;
    }

    if (!canViewData) {
      // Reps trying to view other reps' data get redirected to their own dashboard
      if (currentUser.email !== repEmail) {
        router.push(`/dashboard/${encodeURIComponent(currentUser.email)}`);
      }
    }
  }, [isLoaded, isLoadingUser, canViewData, currentUser, repEmail, router]);

  // Calculate average dimension scores
  const calculateAverageDimensionScores = () => {
    if (!insights?.score_trends) return [];

    return Object.entries(insights.score_trends)
      .filter(([key]) => key !== "overall")
      .map(([dimension, data]) => {
        const scores = data.scores.filter((s): s is number => s !== null);
        const avgScore =
          scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;

        return {
          dimension,
          avgScore,
          displayName: dimension.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
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
  const prepareTrendData = (): { data: TrendDataPoint[]; dimensions: string[] } => {
    if (!insights?.score_trends) return { data: [], dimensions: [] };

    const dimensions = Object.keys(insights.score_trends).filter((k) => k !== "overall");
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
  const getRecentCalls = (): ActivityItem[] => {
    if (!insights?.score_trends.overall?.dates) return [];

    const calls = insights.score_trends.overall.dates
      .map((date, index) => ({
        call_id: `call-${index}`,
        date,
        call_type: "Sales Call",
        overall_score: insights.score_trends.overall?.scores[index] ?? null,
      }))
      .reverse()
      .slice(0, 10);

    return calls;
  };

  // Prepare skill gap data for radar chart
  const prepareSkillGapData = (): SkillGapData[] => {
    if (!insights?.skill_gaps) return [];

    return insights.skill_gaps.map((gap) => ({
      area: gap.area.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      current: gap.current_score,
      target: gap.target_score,
    }));
  };

  // Prepare team comparison data
  const prepareTeamComparisonData = (): ComparisonData[] => {
    const dimensionScores = calculateAverageDimensionScores();
    return dimensionScores.map((dim) => ({
      dimension: dim.displayName,
      repScore: dim.avgScore,
      teamAverage: MOCK_TEAM_AVERAGES[dim.displayName] || 75,
    }));
  };

  // Prepare dimension breakdown data (weights)
  const prepareDimensionBreakdownData = (): DimensionData[] => {
    const dimensionScores = calculateAverageDimensionScores();
    if (dimensionScores.length === 0) return [];

    // Weight each dimension by 1 for equal weighting, or could be customized
    return dimensionScores.map((dim) => ({
      name: dim.displayName,
      value: dim.avgScore, // Using score as value for visualization
      score: dim.avgScore,
    }));
  };

  // Prepare data for advanced score trend chart
  const prepareAdvancedTrendData = () => {
    if (!insights?.score_trends) return [];
    const dates = insights.score_trends.overall?.dates || [];

    return dates.map((date, index) => {
      const point: any = { date };

      // Add overall score
      if (insights.score_trends.overall?.scores[index] !== undefined) {
        point.overall = insights.score_trends.overall.scores[index];
      }

      // Add top dimension scores
      Object.keys(insights.score_trends)
        .filter((k) => k !== "overall")
        .slice(0, 3)
        .forEach((dimension) => {
          const score = insights.score_trends[dimension]?.scores[index];
          if (score !== undefined) {
            point[dimension] = score;
          }
        });

      return point;
    });
  };

  // Prepare data for skill gap radar chart (comparing to team average)
  const prepareSkillGapRadarData = () => {
    if (!insights?.skill_gaps) return [];

    return insights.skill_gaps.map((gap) => ({
      skill: gap.area.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      actual: gap.current_score,
      target: gap.target_score,
      teamAverage:
        MOCK_TEAM_AVERAGES[gap.area.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())] ||
        gap.target_score,
    }));
  };

  // Prepare data for team comparison bar chart with percentiles
  const prepareTeamComparisonBarData = () => {
    const dimensionScores = calculateAverageDimensionScores();
    return dimensionScores.map((dim, index) => ({
      dimension: dim.displayName,
      repScore: dim.avgScore,
      teamAverage: MOCK_TEAM_AVERAGES[dim.displayName] || 75,
      percentile: 50 + Math.floor(Math.random() * 50), // Mock percentile (would come from backend)
    }));
  };

  // Prepare activity timeline data (mock data for now)
  const prepareActivityTimelineData = () => {
    if (!insights?.score_trends.overall?.dates) return [];

    const dates = insights.score_trends.overall.dates;
    return dates.map((date) => ({
      date,
      count: Math.floor(Math.random() * 5) + 1, // Mock call count per day
      isHighActivity: Math.random() > 0.7,
    }));
  };

  // Prepare objection breakdown data (mock for now - would need backend support)
  const prepareObjectionBreakdownData = () => {
    return [
      { name: "Budget Concerns", count: 12, successRate: 65, avgScore: 72 },
      { name: "Timeline Issues", count: 8, successRate: 78, avgScore: 81 },
      { name: "Product Fit", count: 6, successRate: 55, avgScore: 68 },
      { name: "Competitor Comparison", count: 5, successRate: 72, avgScore: 75 },
      { name: "Implementation Risk", count: 3, successRate: 85, avgScore: 88 },
    ];
  };

  if (!isLoaded || isLoadingUser) {
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
          <Button variant="ghost" onClick={() => router.back()} className="gap-2">
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
              {error.message || "Failed to load rep insights"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => window.location.reload()} className="gap-2">
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
          <Button variant="ghost" onClick={() => router.back()} className="gap-2">
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

  const skillGapData = prepareSkillGapData();
  const teamComparisonData = prepareTeamComparisonData();
  const dimensionBreakdownData = prepareDimensionBreakdownData();

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header with Back Button and Time Range Filter */}
      <div className="flex items-center justify-between border-b pb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.back()} className="gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">{insights.rep_info.name}</h1>
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
      <section>
        <h2 className="text-2xl font-bold mb-4">Performance Overview</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {overallScore !== null ? (
            <ScoreCard
              score={overallScore}
              title="Overall Average Score"
              subtitle={`Based on ${totalCalls} call${totalCalls !== 1 ? "s" : ""}`}
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
              <p className="text-xs text-gray-500 mt-2">{insights.rep_info.date_range.period}</p>
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
      </section>

      {/* Score Trends Over Time - Line Chart */}
      {hasEnoughData ? (
        <section>
          <h2 className="text-2xl font-bold mb-4">Score Trends Over Time</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Performance Trajectory</CardTitle>
              <CardDescription>
                Track your progress across different coaching dimensions over the selected time
                period
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TrendChart data={trendData} dimensions={dimensions} height={350} />
            </CardContent>
          </Card>
        </section>
      ) : (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-800 text-center">
              Not enough data to display trends. At least 3 analyzed calls are required.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Skill Gaps - Radar Chart */}
      {skillGapData.length > 0 ? (
        <section>
          <h2 className="text-2xl font-bold mb-4">Skill Gap Analysis</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Current vs Target Performance</CardTitle>
              <CardDescription>
                Radar chart showing your current scores compared to target goals across key skill
                areas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SkillGapChart data={skillGapData} height={350} />
            </CardContent>
          </Card>
        </section>
      ) : null}

      {/* Team Comparison - Bar Chart */}
      {hasEnoughData && teamComparisonData.length > 0 ? (
        <section>
          <h2 className="text-2xl font-bold mb-4">Team Performance Comparison</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>You vs Team Average</CardTitle>
              <CardDescription>
                See how your scores compare to team averages across dimensions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TeamComparisonChart data={teamComparisonData} height={320} />
            </CardContent>
          </Card>
        </section>
      ) : null}

      {/* Dimension Breakdown - Pie Chart */}
      {dimensionBreakdownData.length > 0 ? (
        <section>
          <h2 className="text-2xl font-bold mb-4">Dimension Breakdown</h2>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Pie Chart */}
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle>Score Distribution</CardTitle>
                <CardDescription>
                  Visual breakdown of your average scores across all coaching dimensions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DimensionBreakdownChart data={dimensionBreakdownData} height={300} />
              </CardContent>
            </Card>

            {/* Dimension Score Cards */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Dimension Details</h3>
              <div className="grid gap-3 grid-cols-1">
                {dimensionScores.map((dim) => (
                  <ScoreCard key={dim.dimension} score={dim.avgScore} title={dim.displayName} />
                ))}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      {/* Advanced Score Trends Chart */}
      {hasEnoughData && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Performance Trends (Enhanced)</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Score Progress Over Time</CardTitle>
              <CardDescription>
                Track your overall performance and top dimension scores across the selected time
                period
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScoreTrendChart
                data={prepareAdvancedTrendData()}
                dimensions={Object.keys(insights.score_trends)
                  .filter((k) => k !== "overall")
                  .slice(0, 3)}
                height={350}
                showArea={false}
              />
            </CardContent>
          </Card>
        </section>
      )}

      {/* Skill Gap Radar Chart */}
      {prepareSkillGapRadarData().length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Skill Gap Analysis (Radar View)</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Your Skills vs Team Average</CardTitle>
              <CardDescription>
                Compare your actual performance against team averages and target goals across all
                dimensions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SkillGapRadar data={prepareSkillGapRadarData()} compareType="team" height={350} />
            </CardContent>
          </Card>
        </section>
      )}

      {/* Team Comparison Bar Chart (Enhanced) */}
      {hasEnoughData && prepareTeamComparisonBarData().length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Competitive Positioning</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>You vs Team Benchmarks</CardTitle>
              <CardDescription>
                See where you rank compared to your team across all coaching dimensions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TeamComparisonBar
                data={prepareTeamComparisonBarData()}
                showPercentile={true}
                height={350}
              />
            </CardContent>
          </Card>
        </section>
      )}

      {/* Activity Timeline */}
      {prepareActivityTimelineData().length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Activity Timeline</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Call Activity Heatmap</CardTitle>
              <CardDescription>
                Visualize your call and coaching session frequency throughout the time period
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <ActivityTimeline data={prepareActivityTimelineData()} metric="calls" />
            </CardContent>
          </Card>
        </section>
      )}

      {/* Objection Breakdown */}
      {prepareObjectionBreakdownData().length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Objection Handling Analysis</h2>
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle>Objection Types & Success Rates</CardTitle>
              <CardDescription>
                Analyze the most common objections you encounter and how successfully you handle
                each type
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ObjectionBreakdown
                data={prepareObjectionBreakdownData()}
                showDetails={false}
                height={350}
              />
            </CardContent>
          </Card>
        </section>
      )}

      {/* Recent Activity Feed */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
        <RecentActivityFeed activities={recentCalls} limit={10} />
      </section>

      {/* Coaching Quality Metrics */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Coaching Quality Metrics</h2>
        <FeedbackStats
          repEmail={repEmail}
          timePeriod={timeRange as "last_7_days" | "last_30_days" | "last_90_days" | "all_time"}
        />
      </section>
    </div>
  );
}
