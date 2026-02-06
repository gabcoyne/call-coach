/**
 * Vercel Cron Job: Daily Gong Sync
 *
 * Runs daily at 6am UTC to sync opportunities, calls, and emails from Gong.
 *
 * Schedule: 0 6 * * * (configured in vercel.json)
 * Max Duration: 300s (5 minutes)
 *
 * Authentication:
 * - Vercel Cron requests include Authorization header with CRON_SECRET
 * - Manual testing: POST to /api/cron/daily-sync with Authorization: Bearer <CRON_SECRET>
 */

import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

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

  // Vercel Cron sends: Authorization: Bearer <CRON_SECRET>
  if (authHeader === `Bearer ${cronSecret}`) {
    return true;
  }

  console.error("Unauthorized cron request - invalid or missing Authorization header");
  return false;
}

/**
 * Execute Python sync script using uv
 */
async function runSync(): Promise<{ status: string; output?: string; error?: string }> {
  const projectRoot = path.resolve(process.cwd(), "..");
  const scriptPath = "flows.daily_gong_sync";

  try {
    console.log("Starting daily Gong sync...");
    console.log(`Project root: ${projectRoot}`);

    // Execute Python script with uv
    // uv is installed in the Vercel build environment via pyproject.toml
    const { stdout, stderr } = await execAsync(
      `cd "${projectRoot}" && uv run python -m ${scriptPath}`,
      {
        timeout: 280000, // 280s timeout (20s buffer from function limit)
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer for large logs
        env: {
          ...process.env,
          // Ensure Python can find modules
          PYTHONPATH: projectRoot,
        },
      }
    );

    console.log("Sync completed successfully");
    console.log("STDOUT:", stdout);
    if (stderr) {
      console.warn("STDERR:", stderr);
    }

    return {
      status: "success",
      output: stdout,
    };
  } catch (error: any) {
    console.error("Sync failed:", error);

    return {
      status: "failed",
      error: error.message || "Unknown error",
      output: error.stdout || "",
    };
  }
}

/**
 * POST /api/cron/daily-sync
 *
 * Executes daily Gong synchronization.
 */
export async function POST(request: NextRequest) {
  // Verify authorization
  if (!isAuthorized(request)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const startTime = new Date().toISOString();
  console.log(`[${startTime}] Daily sync cron job triggered`);

  try {
    // Run sync
    const result = await runSync();

    const endTime = new Date().toISOString();
    const response = {
      job: "daily-gong-sync",
      startTime,
      endTime,
      ...result,
    };

    if (result.status === "success") {
      console.log(`[${endTime}] Daily sync completed successfully`);
      return NextResponse.json(response, { status: 200 });
    } else {
      console.error(`[${endTime}] Daily sync failed`);

      // Still return 200 to Vercel Cron (job executed, even if sync failed)
      // Log the error for monitoring
      return NextResponse.json(response, { status: 200 });
    }
  } catch (error: any) {
    const endTime = new Date().toISOString();
    console.error(`[${endTime}] Daily sync error:`, error);

    // Return 500 for unexpected errors
    return NextResponse.json(
      {
        job: "daily-gong-sync",
        startTime,
        endTime,
        status: "error",
        error: error.message || "Internal server error",
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/cron/daily-sync
 *
 * Returns cron job configuration and status.
 * Useful for health checks and verification.
 */
export async function GET(request: NextRequest) {
  // Don't require auth for GET - just returns config
  return NextResponse.json({
    job: "daily-gong-sync",
    schedule: "0 6 * * *",
    description: "Syncs opportunities, calls, and emails from Gong API",
    configured: !!process.env.CRON_SECRET,
    nextRun: "Daily at 6:00 AM UTC",
  });
}

// Export runtime config for Vercel
export const runtime = "nodejs";
export const maxDuration = 300; // 5 minutes
