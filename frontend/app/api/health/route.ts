/**
 * GET /api/health
 *
 * Simple health check endpoint for container startup probes.
 * This endpoint returns quickly with minimal dependencies
 * to ensure the container can pass health checks.
 */
import { NextResponse } from "next/server";

// Track server start time
const serverStartTime = Date.now();

export async function GET() {
  // Simple health check - just return OK
  // More detailed health checks can be done via a separate /api/health/detailed endpoint
  return NextResponse.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime_ms: Date.now() - serverStartTime,
    version: process.env.APP_VERSION || "1.0.0",
  });
}

// Force this route to be dynamic (not statically generated)
export const dynamic = "force-dynamic";
