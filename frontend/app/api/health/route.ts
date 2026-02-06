/**
 * GET /api/health
 *
 * Comprehensive health check endpoint for monitoring application status.
 * Checks database connection, Redis connection, Claude API availability,
 * and returns detailed status for each dependency.
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  uptime: number;
  checks: {
    database: HealthCheck;
    redis: HealthCheck;
    claude_api: HealthCheck;
    backend_api: HealthCheck;
  };
  version: string;
  environment: string;
}

interface HealthCheck {
  status: "up" | "down" | "degraded";
  latency_ms: number;
  error?: string;
  timestamp: string;
}

// Track server start time
const serverStartTime = Date.now();

// Helper function to check database connection
async function checkDatabase(): Promise<HealthCheck> {
  const startTime = Date.now();
  try {
    const result = await query("SELECT 1 as test");
    const latency = Date.now() - startTime;

    if (result.rows.length === 0 || result.rows[0].test !== 1) {
      return {
        status: "down",
        latency_ms: latency,
        error: "Database query returned unexpected result",
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "up",
      latency_ms: latency,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    const latency = Date.now() - startTime;
    return {
      status: "down",
      latency_ms: latency,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString(),
    };
  }
}

// Helper function to check Redis connection
async function checkRedis(): Promise<HealthCheck> {
  const startTime = Date.now();
  try {
    // Try to connect to Redis if available
    const redisUrl = process.env.REDIS_URL;
    if (!redisUrl) {
      return {
        status: "degraded",
        latency_ms: 0,
        error: "Redis not configured",
        timestamp: new Date().toISOString(),
      };
    }

    // Note: For production, use an actual Redis client (ioredis, redis)
    // This is a placeholder check
    const response = await fetch(redisUrl, {
      method: "HEAD",
      timeout: 5000,
    }).catch(() => null);

    const latency = Date.now() - startTime;

    if (!response) {
      return {
        status: "down",
        latency_ms: latency,
        error: "Failed to connect to Redis",
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "up",
      latency_ms: latency,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    const latency = Date.now() - startTime;
    return {
      status: "degraded",
      latency_ms: latency,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString(),
    };
  }
}

// Helper function to check Claude API availability
async function checkClaudeAPI(): Promise<HealthCheck> {
  const startTime = Date.now();
  try {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return {
        status: "degraded",
        latency_ms: 0,
        error: "ANTHROPIC_API_KEY not configured",
        timestamp: new Date().toISOString(),
      };
    }

    // Call Claude API with a lightweight request
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-opus-4-5",
        max_tokens: 10,
        messages: [
          {
            role: "user",
            content: "ping",
          },
        ],
      }),
      signal: AbortSignal.timeout(5000),
    });

    const latency = Date.now() - startTime;

    if (response.status === 401 || response.status === 403) {
      return {
        status: "down",
        latency_ms: latency,
        error: "Claude API authentication failed",
        timestamp: new Date().toISOString(),
      };
    }

    if (!response.ok) {
      return {
        status: "degraded",
        latency_ms: latency,
        error: `Claude API returned ${response.status}`,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "up",
      latency_ms: latency,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    const latency = Date.now() - startTime;

    // Timeout is expected during health checks
    if (error instanceof Error && error.name === "AbortError") {
      return {
        status: "degraded",
        latency_ms: latency,
        error: "Claude API health check timed out",
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "degraded",
      latency_ms: latency,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString(),
    };
  }
}

// Helper function to check backend API
async function checkBackendAPI(): Promise<HealthCheck> {
  const startTime = Date.now();
  try {
    const backendUrl = process.env.COACHING_API_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(5000),
    });

    const latency = Date.now() - startTime;

    if (!response.ok) {
      return {
        status: "down",
        latency_ms: latency,
        error: `Backend API returned ${response.status}`,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "up",
      latency_ms: latency,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    const latency = Date.now() - startTime;
    return {
      status: "degraded",
      latency_ms: latency,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString(),
    };
  }
}

// Determine overall health status
function determineHealthStatus(checks: HealthStatus["checks"]): HealthStatus["status"] {
  const statuses = Object.values(checks).map((check) => check.status);

  // If any critical check is down, overall status is unhealthy
  const criticalChecks = ["database", "backend_api"];
  for (const critical of criticalChecks) {
    const key = critical as keyof typeof checks;
    if (checks[key].status === "down") {
      return "unhealthy";
    }
  }

  // If any check is down, status is degraded
  if (statuses.includes("down")) {
    return "degraded";
  }

  // If any check is degraded, status is degraded
  if (statuses.includes("degraded")) {
    return "degraded";
  }

  return "healthy";
}

export async function GET(request: NextRequest) {
  try {
    // Run all health checks in parallel
    const [database, redis, claude_api, backend_api] = await Promise.all([
      checkDatabase(),
      checkRedis(),
      checkClaudeAPI(),
      checkBackendAPI(),
    ]);

    const checks = {
      database,
      redis,
      claude_api,
      backend_api,
    };

    const status = determineHealthStatus(checks);
    const uptime = Date.now() - serverStartTime;

    const response: HealthStatus = {
      status,
      timestamp: new Date().toISOString(),
      uptime,
      checks,
      version: process.env.APP_VERSION || "unknown",
      environment: process.env.ENVIRONMENT || "unknown",
    };

    // Return appropriate status code
    const statusCode = status === "healthy" ? 200 : status === "degraded" ? 503 : 503;

    return NextResponse.json(response, { status: statusCode });
  } catch (error) {
    console.error("Health check failed:", error);
    return NextResponse.json(
      {
        status: "unhealthy" as const,
        timestamp: new Date().toISOString(),
        uptime: Date.now() - serverStartTime,
        checks: {
          database: { status: "down" as const, latency_ms: 0, timestamp: new Date().toISOString() },
          redis: { status: "down" as const, latency_ms: 0, timestamp: new Date().toISOString() },
          claude_api: {
            status: "down" as const,
            latency_ms: 0,
            timestamp: new Date().toISOString(),
          },
          backend_api: {
            status: "down" as const,
            latency_ms: 0,
            timestamp: new Date().toISOString(),
          },
        },
        version: process.env.APP_VERSION || "unknown",
        environment: process.env.ENVIRONMENT || "unknown",
      },
      { status: 503 }
    );
  }
}
