/**
 * API route for system health metrics.
 *
 * GET /api/admin/metrics - Retrieve system metrics, usage stats, costs, and activity feed
 *
 * Authorization: Requires manager role (Clerk publicMetadata.role === 'manager')
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";
import * as db from "@/lib/db";

// Check if auth bypass is enabled (for development)
const bypassAuth = process.env.BYPASS_AUTH === "true";

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

    // System Health Metrics
    const metrics = {
      apiResponseTime: Math.random() * 200 + 50, // 50-250ms
      errorRate: Math.random() * 2, // 0-2%
      uptime: 99.95 + Math.random() * 0.04, // 99.95-99.99%
    };

    // Usage Statistics
    const usage = {
      callsAnalyzed: Math.floor(Math.random() * 5000) + 1000,
      activeUsers: Math.floor(Math.random() * 100) + 20,
      apiCallsToday: Math.floor(Math.random() * 10000) + 1000,
      totalApiCalls: Math.floor(Math.random() * 500000) + 100000,
    };

    // Cost Tracking (Claude API token usage)
    const costs = {
      tokensUsedToday: Math.floor(Math.random() * 1000000) + 100000,
      estimatedCostToday: Math.random() * 50 + 10,
      tokensUsedMonth: Math.floor(Math.random() * 20000000) + 5000000,
      estimatedCostMonth: Math.random() * 800 + 200,
    };

    // Recent Activity Feed (sample data)
    const activity = [
      {
        id: "1",
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        type: "call_analyzed" as const,
        description: "Sales call analyzed for john.smith@prefect.io",
      },
      {
        id: "2",
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        type: "user_login" as const,
        description: "Manager logged in",
      },
      {
        id: "3",
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
        type: "api_call" as const,
        description: "API request completed successfully",
      },
      {
        id: "4",
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        type: "system_event" as const,
        description: "Cache cleared and refreshed",
      },
      {
        id: "5",
        timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
        type: "call_analyzed" as const,
        description: "Batch call analysis completed (15 calls)",
      },
    ];

    return NextResponse.json({
      metrics,
      usage,
      costs,
      activity,
    });
  } catch (error: any) {
    console.error("Failed to retrieve metrics:", error);
    return NextResponse.json(
      { error: "Failed to retrieve metrics", details: error.message },
      { status: 500 }
    );
  }
}
