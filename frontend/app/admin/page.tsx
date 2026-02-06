"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
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
import {
  Activity,
  Users,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  ArrowRight,
} from "lucide-react";

interface SystemMetrics {
  apiResponseTime: number;
  errorRate: number;
  uptime: number;
}

interface UsageStats {
  callsAnalyzed: number;
  activeUsers: number;
  apiCallsToday: number;
  totalApiCalls: number;
}

interface CostTracking {
  tokensUsedToday: number;
  estimatedCostToday: number;
  tokensUsedMonth: number;
  estimatedCostMonth: number;
}

interface ActivityItem {
  id: string;
  timestamp: string;
  type: "call_analyzed" | "user_login" | "api_call" | "system_event";
  description: string;
}

const COLORS = ["#f472b6", "#fb923c", "#facc15", "#86efac", "#60a5fa"];

export default function AdminDashboardPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [costs, setCosts] = useState<CostTracking | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authorization
  const isManager = user?.publicMetadata?.role === "manager";

  useEffect(() => {
    if (!isLoaded) return;

    if (!isManager) {
      router.push("/403?message=Admin access required");
      return;
    }

    fetchDashboardData();
  }, [isLoaded, isManager, router]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/admin/metrics");
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/403?message=Admin access required");
          return;
        }
        throw new Error("Failed to fetch metrics");
      }

      const data = await response.json();

      setMetrics(data.metrics);
      setUsage(data.usage);
      setCosts(data.costs);
      setActivity(data.activity);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded || loading) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">Loading system metrics...</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-100 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
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
          <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            System health, usage metrics, and cost tracking
          </p>
        </div>
        <Button
          onClick={fetchDashboardData}
          variant="outline"
          size="sm"
          className="gap-2"
        >
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

      {/* Key Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* API Response Time */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Response Time</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.apiResponseTime?.toFixed(0) ?? "N/A"}ms
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Average response time
            </p>
          </CardContent>
        </Card>

        {/* Error Rate */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.errorRate?.toFixed(2) ?? "N/A"}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Last 24 hours
            </p>
          </CardContent>
        </Card>

        {/* Uptime */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uptime</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.uptime?.toFixed(2) ?? "N/A"}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              This month
            </p>
          </CardContent>
        </Card>

        {/* Active Users */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage?.activeUsers ?? "N/A"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              This month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Statistics Section */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Calls Analyzed */}
        <Card>
          <CardHeader>
            <CardTitle>Calls Analyzed</CardTitle>
            <CardDescription>
              Total calls processed this month
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {usage?.callsAnalyzed ?? 0}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              API calls today: {usage?.apiCallsToday ?? 0}
            </p>
          </CardContent>
        </Card>

        {/* Cost Tracking */}
        <Card>
          <CardHeader>
            <CardTitle>Claude API Cost</CardTitle>
            <CardDescription>
              Estimated token usage and costs
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Today</p>
                <p className="text-lg font-semibold">
                  ${costs?.estimatedCostToday?.toFixed(2) ?? "0.00"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {costs?.tokensUsedToday?.toLocaleString() ?? 0} tokens
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">This Month</p>
                <p className="text-lg font-semibold">
                  ${costs?.estimatedCostMonth?.toFixed(2) ?? "0.00"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {costs?.tokensUsedMonth?.toLocaleString() ?? 0} tokens
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest system events from the past 24 hours
            </CardDescription>
          </div>
          <Button asChild variant="ghost" size="sm" className="gap-2">
            <a href="/admin/analytics">
              View More
              <ArrowRight className="h-4 w-4" />
            </a>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activity.length > 0 ? (
              activity.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className="flex items-start gap-4 pb-4 border-b last:border-b-0 last:pb-0"
                >
                  <div className="mt-1">
                    <div
                      className={`h-2 w-2 rounded-full ${
                        item.type === "call_analyzed"
                          ? "bg-blue-500"
                          : item.type === "user_login"
                            ? "bg-green-500"
                            : item.type === "api_call"
                              ? "bg-yellow-500"
                              : "bg-gray-500"
                      }`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {item.description}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No recent activity
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Admin Links */}
      <div className="grid gap-4 md:grid-cols-3">
        <Button asChild variant="outline" className="h-auto flex flex-col items-start p-4">
          <a href="/admin/users">
            <Users className="h-5 w-5 mb-2" />
            <span className="font-semibold">User Management</span>
            <span className="text-xs text-muted-foreground mt-1">
              Manage roles and permissions
            </span>
          </a>
        </Button>

        <Button asChild variant="outline" className="h-auto flex flex-col items-start p-4">
          <a href="/admin/analytics">
            <TrendingUp className="h-5 w-5 mb-2" />
            <span className="font-semibold">Analytics</span>
            <span className="text-xs text-muted-foreground mt-1">
              Performance metrics & insights
            </span>
          </a>
        </Button>

        <Button asChild variant="outline" className="h-auto flex flex-col items-start p-4">
          <a href="/admin/system">
            <Activity className="h-5 w-5 mb-2" />
            <span className="font-semibold">System Health</span>
            <span className="text-xs text-muted-foreground mt-1">
              Database & cache status
            </span>
          </a>
        </Button>
      </div>
    </div>
  );
}
