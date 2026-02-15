"use client";

import { useState, useEffect } from "react";
import { useUser } from "@/lib/hooks/use-auth";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Database,
  Zap,
  Clock,
  RefreshCw,
} from "lucide-react";

interface DatabaseHealth {
  activeConnections: number;
  maxConnections: number;
  poolSize: number;
  averageQueryTime: number;
  slowQueries: number;
  status: "healthy" | "warning" | "critical";
}

interface CacheStats {
  hitRate: number;
  missRate: number;
  memoryUsed: number;
  memoryMax: number;
  itemsStored: number;
  status: "healthy" | "warning" | "critical";
}

interface BackgroundJobStatus {
  jobName: string;
  status: "running" | "success" | "failed" | "pending";
  lastRun: string;
  nextRun: string;
  failureCount: number;
}

interface SystemData {
  database: DatabaseHealth;
  cache: CacheStats;
  backgroundJobs: BackgroundJobStatus[];
  systemMetrics: Array<{
    timestamp: string;
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
  }>;
}

function getStatusIcon(status: "healthy" | "warning" | "critical") {
  switch (status) {
    case "healthy":
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case "warning":
      return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    case "critical":
      return <AlertCircle className="h-5 w-5 text-red-500" />;
  }
}

function getStatusColor(status: "healthy" | "warning" | "critical") {
  switch (status) {
    case "healthy":
      return "bg-green-50 border-green-200";
    case "warning":
      return "bg-yellow-50 border-yellow-200";
    case "critical":
      return "bg-red-50 border-red-200";
  }
}

export default function AdminSystemPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [data, setData] = useState<SystemData | null>(null);
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

    fetchSystemData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isManager]);

  const fetchSystemData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/admin/system");
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/403?message=Admin access required");
          return;
        }
        throw new Error("Failed to fetch system data");
      }

      const systemData = await response.json();
      setData(systemData);
    } catch (err) {
      console.error("Error fetching system data:", err);
      setError(err instanceof Error ? err.message : "Failed to load system data");
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded || loading) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">System Health</h1>
          <p className="text-muted-foreground mt-1">Loading system data...</p>
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
          <h1 className="text-3xl font-bold text-foreground">System Health</h1>
          <p className="text-muted-foreground mt-1">Database, cache, and background job status</p>
        </div>
        <Button onClick={fetchSystemData} variant="outline" size="sm" className="gap-2">
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

      {/* Database Health */}
      {data?.database && (
        <Card className={`border ${getStatusColor(data.database.status)}`}>
          <CardHeader className="flex flex-row items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5 text-muted-foreground" />
              <div>
                <CardTitle>Database Health</CardTitle>
                <CardDescription>Connection pool and query performance</CardDescription>
              </div>
            </div>
            {getStatusIcon(data.database.status)}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Active Connections</p>
                <p className="text-2xl font-bold">
                  {data.database.activeConnections} / {data.database.maxConnections}
                </p>
                <div className="w-full h-2 bg-gray-200 rounded-full mt-2 overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all"
                    style={{
                      width: `${
                        (data.database.activeConnections / data.database.maxConnections) * 100
                      }%`,
                    }}
                  />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pool Size</p>
                <p className="text-2xl font-bold">{data.database.poolSize}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Query Time</p>
                <p className="text-2xl font-bold">{data.database.averageQueryTime.toFixed(0)}ms</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Slow Queries</p>
                <p className="text-2xl font-bold">{data.database.slowQueries}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cache Statistics */}
      {data?.cache && (
        <Card className={`border ${getStatusColor(data.cache.status)}`}>
          <CardHeader className="flex flex-row items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className="h-5 w-5 text-muted-foreground" />
              <div>
                <CardTitle>Cache Statistics</CardTitle>
                <CardDescription>Hit/miss rates and memory usage</CardDescription>
              </div>
            </div>
            {getStatusIcon(data.cache.status)}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Hit Rate</p>
                <p className="text-2xl font-bold">{data.cache.hitRate.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Miss Rate</p>
                <p className="text-2xl font-bold">{data.cache.missRate.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Memory Used</p>
                <p className="text-2xl font-bold">
                  {(data.cache.memoryUsed / 1024 / 1024).toFixed(0)}MB
                </p>
                <div className="w-full h-2 bg-gray-200 rounded-full mt-2 overflow-hidden">
                  <div
                    className="h-full bg-purple-500 rounded-full transition-all"
                    style={{
                      width: `${(data.cache.memoryUsed / data.cache.memoryMax) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Items Stored</p>
                <p className="text-2xl font-bold">{data.cache.itemsStored}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Background Jobs Status */}
      {data?.backgroundJobs && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Background Jobs
            </CardTitle>
            <CardDescription>Status and execution history of background tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.backgroundJobs.length > 0 ? (
                data.backgroundJobs.map((job) => (
                  <div
                    key={job.jobName}
                    className="flex items-start gap-4 p-3 rounded-lg border hover:bg-gray-50"
                  >
                    <div className="mt-1">
                      {job.status === "running" && (
                        <div className="h-3 w-3 rounded-full bg-blue-500 animate-pulse" />
                      )}
                      {job.status === "success" && (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                      {job.status === "failed" && <AlertCircle className="h-5 w-5 text-red-500" />}
                      {job.status === "pending" && (
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground">{job.jobName}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Status: <span className="font-semibold">{job.status}</span>
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Last run: {new Date(job.lastRun).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Next run: {new Date(job.nextRun).toLocaleString()}
                      </p>
                      {job.failureCount > 0 && (
                        <p className="text-xs text-red-600 mt-1">
                          Failed {job.failureCount} time(s)
                        </p>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No background jobs configured
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Metrics Chart */}
      {data?.systemMetrics && data.systemMetrics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>System Metrics Over Time</CardTitle>
            <CardDescription>CPU, memory, and disk usage trends</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.systemMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpuUsage" stroke="#8884d8" name="CPU %" />
                <Line type="monotone" dataKey="memoryUsage" stroke="#82ca9d" name="Memory %" />
                <Line type="monotone" dataKey="diskUsage" stroke="#ffc658" name="Disk %" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
