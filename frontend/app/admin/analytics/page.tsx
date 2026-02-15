"use client";

import { useState, useEffect } from "react";
import { useUser } from "@/lib/hooks/use-auth";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { AlertCircle, RefreshCw, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CoachingDimension {
  dimension: string;
  score: number;
  count: number;
}

interface TopPerformer {
  name: string;
  email: string;
  avgScore: number;
  callsAnalyzed: number;
  rank: number;
}

interface SkillGap {
  skill: string;
  averageScore: number;
  targetScore: number;
  gap: number;
  teamMembers: number;
}

interface AnalyticsData {
  coachingDimensions: CoachingDimension[];
  topPerformers: TopPerformer[];
  skillGaps: SkillGap[];
}

const COLORS = ["#f472b6", "#fb923c", "#facc15", "#86efac", "#60a5fa", "#a78bfa"];

export default function AdminAnalyticsPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authorization - support both manager and admin roles
  const userRole = (user?.publicMetadata as { role?: string } | undefined)?.role;
  const isManager = userRole === "manager" || userRole === "admin";

  useEffect(() => {
    if (!isLoaded) return;

    if (!isManager) {
      router.push("/403?message=Admin access required");
      return;
    }

    fetchAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isManager]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/admin/analytics");
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/403?message=Admin access required");
          return;
        }
        throw new Error("Failed to fetch analytics");
      }

      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      console.error("Error fetching analytics:", err);
      setError(err instanceof Error ? err.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded || loading) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground mt-1">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (!isManager) {
    return null;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Team performance insights and skill gap analysis
          </p>
        </div>
        <Button onClick={fetchAnalytics} variant="outline" size="sm" className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Coaching Dimensions Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Coaching Dimensions</CardTitle>
          <CardDescription>Score distribution across all coaching dimensions</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data?.coachingDimensions || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="dimension" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" fill="#8884d8" />
              <Bar dataKey="count" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Performers Leaderboard */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            Top Performers
          </CardTitle>
          <CardDescription>
            Sales representatives with highest average coaching scores
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(data?.topPerformers || []).length > 0 ? (
              (data?.topPerformers || []).map((performer, index) => (
                <div
                  key={performer.email}
                  className="flex items-center gap-4 p-3 rounded-lg border hover:bg-gray-50"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-prefect-pink to-prefect-sunrise1 flex items-center justify-center">
                    <span className="text-sm font-bold text-white">{performer.rank}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">{performer.name}</p>
                    <p className="text-xs text-muted-foreground">{performer.email}</p>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <div className="text-lg font-bold text-foreground">
                      {performer.avgScore.toFixed(1)}
                    </div>
                    <p className="text-xs text-muted-foreground">{performer.callsAnalyzed} calls</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No performer data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Skill Gap Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Skill Gap Analysis</CardTitle>
          <CardDescription>Areas where team performance lags behind targets</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(data?.skillGaps || []).length > 0 ? (
              (data?.skillGaps || []).map((skill) => (
                <div key={skill.skill} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-foreground">{skill.skill}</p>
                      <p className="text-xs text-muted-foreground">
                        {skill.teamMembers} team members
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-foreground">
                        Gap: {skill.gap.toFixed(1)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Avg: {skill.averageScore.toFixed(1)} / Target:{" "}
                        {skill.targetScore.toFixed(1)}
                      </p>
                    </div>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-red-500 rounded-full transition-all"
                      style={{
                        width: `${Math.min((skill.averageScore / skill.targetScore) * 100, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No skill gap data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Coaching Dimension Pie Chart */}
      {(data?.coachingDimensions || []).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Dimension Score Distribution</CardTitle>
            <CardDescription>Percentage breakdown of dimensions</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data?.coachingDimensions || []}
                  dataKey="score"
                  nameKey="dimension"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {(data?.coachingDimensions || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
