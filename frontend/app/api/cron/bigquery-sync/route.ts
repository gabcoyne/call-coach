/**
 * Vercel Cron Job: BigQuery Data Sync
 *
 * Runs every 6 hours to sync opportunities and calls from BigQuery.
 *
 * Schedule: "0 *\/6 * * *" (configured in vercel.json)
 * Max Duration: 300s (5 minutes)
 */

import { NextRequest, NextResponse } from "next/server";

const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || "http://localhost:8000";

/**
 * Verify the request is from Vercel Cron or authenticated with CRON_SECRET
 */
function isAuthorized(request: NextRequest): boolean {
  const authHeader = request.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET;

  if (!cronSecret) {
    console.warn("CRON_SECRET not configured - cron job is unprotected!");
    return true; // Allow in development
  }

  if (authHeader === `Bearer ${cronSecret}`) {
    return true;
  }

  console.error("Unauthorized cron request");
  return false;
}

/**
 * POST /api/cron/bigquery-sync
 *
 * Triggers BigQuery sync via the backend API.
 */
export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const startTime = new Date().toISOString();
  console.log(`[${startTime}] BigQuery sync cron job triggered`);

  // Check for full-sync query param
  const url = new URL(request.url);
  const fullSync = url.searchParams.get("full") === "true";

  try {
    // Call backend sync endpoint
    const response = await fetch(`${MCP_BACKEND_URL}/api/v1/sync/bigquery`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_sync: fullSync,
        sync_opportunities: true,
        sync_calls: true,
      }),
    });

    const result = await response.json();
    const endTime = new Date().toISOString();

    console.log(`[${endTime}] BigQuery sync completed:`, result);

    return NextResponse.json(
      {
        job: "bigquery-sync",
        startTime,
        endTime,
        fullSync,
        ...result,
      },
      { status: response.ok ? 200 : 500 }
    );
  } catch (error: unknown) {
    const endTime = new Date().toISOString();
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error(`[${endTime}] BigQuery sync error:`, error);

    return NextResponse.json(
      {
        job: "bigquery-sync",
        startTime,
        endTime,
        status: "error",
        error: errorMessage,
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/cron/bigquery-sync
 *
 * Returns cron job configuration.
 */
export async function GET() {
  return NextResponse.json({
    job: "bigquery-sync",
    schedule: "0 */6 * * *",
    description: "Syncs opportunities and calls from BigQuery to Postgres",
    configured: !!process.env.CRON_SECRET,
    nextRun: "Every 6 hours at :00",
  });
}

export const runtime = "nodejs";
export const maxDuration = 300;
