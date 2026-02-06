/**
 * Analyze Call API Route
 *
 * POST /api/coaching/analyze-call
 *
 * Deep-dive analysis of a specific call with coaching insights.
 */

import { NextRequest, NextResponse } from "next/server";
import { mcpClient } from "@/lib/mcp-client";
import { analyzeCallRequestSchema } from "@/types/coaching";
import { withAuth, apiError, canAccessRepData } from "@/lib/auth-middleware";
import { checkRateLimit, rateLimitHeaders } from "@/lib/rate-limit";
import { logRequest, logResponse, logError } from "@/lib/api-logger";

export const POST = withAuth(async (req: NextRequest, authContext) => {
  const startTime = Date.now();

  try {
    // Log request
    logRequest(req, authContext.userId);

    // Check rate limit
    const rateLimit = checkRateLimit(authContext.userId, "/api/coaching/analyze-call");
    if (!rateLimit.allowed) {
      return NextResponse.json(
        { error: "Rate limit exceeded" },
        {
          status: 429,
          headers: rateLimitHeaders(rateLimit.limit, rateLimit.remaining, rateLimit.reset),
        }
      );
    }

    // Parse and validate request body
    const body = await req.json();
    const validationResult = analyzeCallRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return apiError("Invalid request parameters", 400, validationResult.error.format());
    }

    const params = validationResult.data;

    // Call MCP backend
    const result = await mcpClient.analyzeCall(params);

    // RBAC check: Verify user can access this rep's data
    // If rep_analyzed is present, check access
    if (result.rep_analyzed?.email) {
      if (!canAccessRepData(authContext, result.rep_analyzed.email)) {
        return apiError("Forbidden: You can only access your own call analyses", 403);
      }
    }

    // Log successful response
    const duration = Date.now() - startTime;
    const response = NextResponse.json(result, {
      headers: rateLimitHeaders(rateLimit.limit, rateLimit.remaining, rateLimit.reset),
    });

    logResponse(req, response, authContext.userId, duration, {
      call_id: params.call_id,
      overall_score: result.scores.overall,
    });

    return response;
  } catch (error) {
    logError(req, error, authContext.userId);

    if (error instanceof Error) {
      return apiError(error.message, 500);
    }

    return apiError("Internal server error", 500);
  }
});
