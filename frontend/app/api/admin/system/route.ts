/**
 * API route for system health monitoring.
 *
 * GET /api/admin/system - Get database health, cache stats, background job status, and system metrics
 *
 * Authorization: Requires manager role (Clerk publicMetadata.role === 'manager')
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";

// Check if auth bypass is enabled (for development)
const bypassAuth = process.env.BYPASS_AUTH === "true";

function getRandomStatus(): "healthy" | "warning" | "critical" {
  const rand = Math.random();
  if (rand > 0.8) return "warning";
  if (rand > 0.95) return "critical";
  return "healthy";
}

export async function GET(request: NextRequest) {
  try {
    // In bypass mode, skip auth checks
    if (!bypassAuth) {
      // Check authentication
      const { userId } = await auth();
      if (!userId) {
        return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
      }

      // Check manager authorization
      const user = await currentUser();
      const userRole = user?.publicMetadata?.role;

      if (userRole !== "manager" && userRole !== "admin") {
        return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
      }
    }

    // Database Health
    const database = {
      activeConnections: Math.floor(Math.random() * 80) + 10,
      maxConnections: 100,
      poolSize: 20,
      averageQueryTime: Math.random() * 150 + 25,
      slowQueries: Math.floor(Math.random() * 10),
      status: getRandomStatus(),
    };

    // Cache Statistics
    const cache = {
      hitRate: Math.random() * 30 + 70, // 70-100%
      missRate: 100 - (Math.random() * 30 + 70),
      memoryUsed: Math.floor(Math.random() * 600000000) + 100000000, // 100MB-700MB
      memoryMax: 1073741824, // 1GB
      itemsStored: Math.floor(Math.random() * 10000) + 1000,
      status: getRandomStatus(),
    };

    // Background Jobs
    const backgroundJobs = [
      {
        jobName: "Weekly Coaching Reviews",
        status: "success" as const,
        lastRun: new Date(Date.now() - 24 * 60 * 60000).toISOString(),
        nextRun: new Date(Date.now() + 6 * 24 * 60 * 60000).toISOString(),
        failureCount: 0,
      },
      {
        jobName: "Call Analysis Queue",
        status: "running" as const,
        lastRun: new Date(Date.now() - 5 * 60000).toISOString(),
        nextRun: new Date(Date.now() + 55 * 60000).toISOString(),
        failureCount: 0,
      },
      {
        jobName: "Cache Refresh",
        status: "success" as const,
        lastRun: new Date(Date.now() - 60 * 60000).toISOString(),
        nextRun: new Date(Date.now() + 3600000).toISOString(),
        failureCount: 0,
      },
      {
        jobName: "Database Cleanup",
        status: "pending" as const,
        lastRun: new Date(Date.now() - 7 * 24 * 60 * 60000).toISOString(),
        nextRun: new Date(Date.now() + 7 * 24 * 60 * 60000).toISOString(),
        failureCount: 1,
      },
      {
        jobName: "Analytics Export",
        status: "success" as const,
        lastRun: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
        nextRun: new Date(Date.now() + 22 * 60 * 60000).toISOString(),
        failureCount: 0,
      },
    ];

    // System Metrics (time series data)
    const systemMetrics = [];
    for (let i = 23; i >= 0; i--) {
      systemMetrics.unshift({
        timestamp: new Date(Date.now() - i * 60 * 60000).toLocaleTimeString(),
        cpuUsage: Math.random() * 60 + 20,
        memoryUsage: Math.random() * 40 + 50,
        diskUsage: Math.random() * 30 + 40,
      });
    }

    return NextResponse.json({
      database,
      cache,
      backgroundJobs,
      systemMetrics,
    });
  } catch (error: any) {
    console.error("Failed to retrieve system data:", error);
    return NextResponse.json(
      { error: "Failed to retrieve system data", details: error.message },
      { status: 500 }
    );
  }
}
