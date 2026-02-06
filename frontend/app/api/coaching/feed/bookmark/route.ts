import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { withAuthMiddleware } from "@/lib/auth-middleware";
import { withRateLimit } from "@/lib/rate-limit";
import { logApiRequest, logApiResponse, logApiError } from "@/lib/api-logger";
import { getCurrentUserEmail } from "@/lib/auth";

const bookmarkSchema = z.object({
  item_id: z.string().min(1, "Item ID is required"),
});

async function handlePost(req: NextRequest) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();

  try {
    const body = await req.json();
    const validatedData = bookmarkSchema.parse(body);
    const userEmail = await getCurrentUserEmail();

    logApiRequest(requestId, "POST", "/api/coaching/feed/bookmark", validatedData);

    // Call MCP backend to bookmark item
    const mcpBackendUrl = process.env.MCP_BACKEND_URL || "http://localhost:8000";
    const mcpResponse = await fetch(`${mcpBackendUrl}/coaching/feed/bookmark`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...validatedData,
        user_email: userEmail,
      }),
    });

    if (!mcpResponse.ok) {
      const errorText = await mcpResponse.text();
      throw new Error(`MCP backend error: ${mcpResponse.status} ${errorText}`);
    }

    const data = await mcpResponse.json();
    const duration = Date.now() - startTime;
    logApiResponse(requestId, 200, data, duration);

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    const duration = Date.now() - startTime;

    if (error instanceof z.ZodError) {
      logApiError(requestId, error, 400, duration);
      return NextResponse.json(
        {
          error: "Validation Error",
          message: "Invalid request body",
          details: error.errors,
        },
        { status: 400 }
      );
    }

    logApiError(requestId, error, 500, duration);
    return NextResponse.json(
      {
        error: "Internal Server Error",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export const POST = withRateLimit(withAuthMiddleware(handlePost), 60, "bookmark");
