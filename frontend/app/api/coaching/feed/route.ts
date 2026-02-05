import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { withAuthMiddleware } from '@/lib/auth-middleware';
import { withRateLimit } from '@/lib/rate-limit';
import { logApiRequest, logApiResponse, logApiError } from '@/lib/api-logger';
import { feedRequestSchema, FeedResponse, FeedItem } from '@/types/coaching';
import { isManager } from '@/lib/auth';

/**
 * GET /api/coaching/feed
 *
 * Fetches coaching insights feed with optional filtering
 */
async function handleGet(req: NextRequest) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();

  try {
    // Parse query parameters
    const searchParams = req.nextUrl.searchParams;
    const params = {
      type_filter: searchParams.get('type_filter') || undefined,
      time_filter: searchParams.get('time_filter') || undefined,
      start_date: searchParams.get('start_date') || undefined,
      end_date: searchParams.get('end_date') || undefined,
      limit: searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 20,
      offset: searchParams.get('offset') ? parseInt(searchParams.get('offset')!) : 0,
      include_dismissed: searchParams.get('include_dismissed') === 'true',
    };

    // Validate request
    const validatedParams = feedRequestSchema.parse(params);

    // Log request
    logApiRequest(requestId, 'GET', '/api/coaching/feed', validatedParams);

    // Check if user is manager (for team insights)
    const userIsManager = await isManager();

    // Call MCP backend to get feed data
    const mcpBackendUrl = process.env.MCP_BACKEND_URL || 'http://localhost:8000';
    const mcpResponse = await fetch(`${mcpBackendUrl}/coaching/feed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...validatedParams,
        include_team_insights: userIsManager,
      }),
    });

    if (!mcpResponse.ok) {
      const errorText = await mcpResponse.text();
      throw new Error(`MCP backend error: ${mcpResponse.status} ${errorText}`);
    }

    const data: FeedResponse = await mcpResponse.json();

    // Filter team insights if not a manager
    if (!userIsManager) {
      data.team_insights = [];
    }

    // Log response
    const duration = Date.now() - startTime;
    logApiResponse(requestId, 200, data, duration);

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    const duration = Date.now() - startTime;

    if (error instanceof z.ZodError) {
      logApiError(requestId, error, 400, duration);
      return NextResponse.json(
        {
          error: 'Validation Error',
          message: 'Invalid request parameters',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    logApiError(requestId, error, 500, duration);
    return NextResponse.json(
      {
        error: 'Internal Server Error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// Apply middleware
export const GET = withRateLimit(
  withAuthMiddleware(handleGet),
  100, // Max 100 requests per minute
  'feed'
);
