/**
 * Rep Insights API Route
 *
 * POST /api/coaching/rep-insights
 *
 * Performance trends and coaching history for a specific sales rep.
 */

import { NextRequest, NextResponse } from 'next/server';
import { mcpClient } from '@/lib/mcp-client';
import { repInsightsRequestSchema } from '@/types/coaching';
import { withAuth, apiError, canAccessRepData } from '@/lib/auth-middleware';
import { checkRateLimit, rateLimitHeaders } from '@/lib/rate-limit';
import { logRequest, logResponse, logError } from '@/lib/api-logger';

export const POST = withAuth(async (req: NextRequest, authContext) => {
  const startTime = Date.now();

  try {
    // Log request
    logRequest(req, authContext.userId);

    // Check rate limit
    const rateLimit = checkRateLimit(authContext.userId, '/api/coaching/rep-insights');
    if (!rateLimit.allowed) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        {
          status: 429,
          headers: rateLimitHeaders(rateLimit.limit, rateLimit.remaining, rateLimit.reset),
        }
      );
    }

    // Parse and validate request body
    const body = await req.json();
    const validationResult = repInsightsRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return apiError(
        'Invalid request parameters',
        400,
        validationResult.error.format()
      );
    }

    const params = validationResult.data;

    // RBAC check: Verify user can access this rep's data
    if (!canAccessRepData(authContext, params.rep_email)) {
      return apiError(
        'Forbidden: You can only access your own insights',
        403
      );
    }

    // Call MCP backend
    const result = await mcpClient.getRepInsights(params);

    // Log successful response
    const duration = Date.now() - startTime;
    const response = NextResponse.json(result, {
      headers: rateLimitHeaders(rateLimit.limit, rateLimit.remaining, rateLimit.reset),
    });

    logResponse(req, response, authContext.userId, duration, {
      rep_email: params.rep_email,
      time_period: params.time_period,
      calls_analyzed: result.rep_info.calls_analyzed,
    });

    return response;
  } catch (error) {
    logError(req, error, authContext.userId);

    if (error instanceof Error) {
      return apiError(error.message, 500);
    }

    return apiError('Internal server error', 500);
  }
});
