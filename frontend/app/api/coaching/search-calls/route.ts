/**
 * Search Calls API Route
 *
 * POST /api/coaching/search-calls
 *
 * Find calls matching specific criteria with filtering and sorting.
 */

import { NextRequest, NextResponse } from 'next/server';
import { mcpClient } from '@/lib/mcp-client';
import { searchCallsRequestSchema } from '@/types/coaching';
import { withAuth, apiError, canAccessRepData } from '@/lib/auth-middleware';
import { checkRateLimit, rateLimitHeaders } from '@/lib/rate-limit';
import { logRequest, logResponse, logError } from '@/lib/api-logger';

export const POST = withAuth(async (req: NextRequest, authContext) => {
  const startTime = Date.now();

  try {
    // Log request
    logRequest(req, authContext.userId);

    // Check rate limit
    const rateLimit = checkRateLimit(authContext.userId, '/api/coaching/search-calls');
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
    const validationResult = searchCallsRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return apiError(
        'Invalid request parameters',
        400,
        validationResult.error.format()
      );
    }

    const params = validationResult.data;

    // RBAC check: If searching by rep email, verify access
    // Reps can only search their own calls, managers can search all
    if (params.rep_email) {
      if (!canAccessRepData(authContext, params.rep_email)) {
        return apiError(
          'Forbidden: You can only search your own calls',
          403
        );
      }
    } else {
      // If no rep_email specified and user is a rep, default to their email
      if (authContext.role === 'rep') {
        params.rep_email = authContext.email;
      }
    }

    // Call MCP backend
    const result = await mcpClient.searchCalls(params);

    // Log successful response
    const duration = Date.now() - startTime;
    const response = NextResponse.json(result, {
      headers: rateLimitHeaders(rateLimit.limit, rateLimit.remaining, rateLimit.reset),
    });

    logResponse(req, response, authContext.userId, duration, {
      filters: params,
      results_count: result.length,
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
