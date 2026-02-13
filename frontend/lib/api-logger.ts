/**
 * API Request/Response Logger
 *
 * Provides structured logging for API routes with request/response details.
 * Supports two calling patterns:
 * 1. NextRequest-based: logApiRequest(req, userId?, metadata?)
 * 2. String-based: logApiRequest(requestId, method, endpoint, body?)
 */

import { NextRequest, NextResponse } from "next/server";

/**
 * Log levels
 */
type LogLevel = "info" | "warn" | "error";

/**
 * Log entry structure
 */
interface LogEntry {
  timestamp: string;
  level: LogLevel;
  endpoint: string;
  method: string;
  userId?: string;
  statusCode?: number;
  duration?: number;
  error?: string;
  message: string;
  metadata?: Record<string, unknown>;
}

/**
 * Format log entry as JSON
 */
function formatLog(entry: LogEntry): string {
  return JSON.stringify(entry);
}

/**
 * Log to console with appropriate level
 */
function writeLog(entry: LogEntry): void {
  const formatted = formatLog(entry);

  switch (entry.level) {
    case "error":
      console.error(formatted);
      break;
    case "warn":
      console.warn(formatted);
      break;
    default:
      console.log(formatted);
  }
}

/**
 * Create log entry
 */
function createLogEntry(level: LogLevel, message: string, data: Partial<LogEntry>): LogEntry {
  return {
    timestamp: new Date().toISOString(),
    level,
    message,
    endpoint: data.endpoint || "",
    method: data.method || "",
    ...data,
  };
}

/**
 * Log API request - overloaded for both calling patterns
 */
export function logApiRequest(
  reqOrRequestId: NextRequest | string,
  userIdOrMethod?: string,
  metadataOrEndpoint?: Record<string, unknown> | string,
  body?: unknown
): void {
  // Detect which calling pattern is being used
  if (typeof reqOrRequestId === "string") {
    // String-based pattern: (requestId, method, endpoint, body?)
    const entry = createLogEntry("info", "API request received", {
      endpoint: metadataOrEndpoint as string,
      method: userIdOrMethod || "",
      metadata: {
        requestId: reqOrRequestId,
        body,
      },
    });
    writeLog(entry);
  } else {
    // NextRequest-based pattern: (req, userId?, metadata?)
    const req = reqOrRequestId;
    const entry = createLogEntry("info", "API request received", {
      endpoint: req.nextUrl.pathname,
      method: req.method,
      userId: userIdOrMethod,
      metadata: {
        searchParams: Object.fromEntries(req.nextUrl.searchParams),
        ...(metadataOrEndpoint as Record<string, unknown>),
      },
    });
    writeLog(entry);
  }
}

/**
 * Log API response - overloaded for both calling patterns
 */
export function logApiResponse(
  reqOrRequestId: NextRequest | string,
  resOrStatusCode: NextResponse | number,
  userIdOrData?: string | unknown,
  durationOrDuration?: number,
  metadata?: Record<string, unknown>
): void {
  // Detect which calling pattern is being used
  if (typeof reqOrRequestId === "string") {
    // String-based pattern: (requestId, statusCode, data, duration)
    const statusCode = resOrStatusCode as number;
    const level: LogLevel = statusCode >= 500 ? "error" : statusCode >= 400 ? "warn" : "info";
    const entry = createLogEntry(level, "API response sent", {
      endpoint: "",
      method: "",
      statusCode,
      duration: durationOrDuration,
      metadata: {
        requestId: reqOrRequestId,
        responseSize: JSON.stringify(userIdOrData).length,
      },
    });
    writeLog(entry);
  } else {
    // NextRequest-based pattern: (req, res, userId?, duration?, metadata?)
    const req = reqOrRequestId;
    const res = resOrStatusCode as NextResponse;
    const statusCode = res.status;
    const level: LogLevel = statusCode >= 500 ? "error" : statusCode >= 400 ? "warn" : "info";

    const entry = createLogEntry(level, "API response sent", {
      endpoint: req.nextUrl.pathname,
      method: req.method,
      userId: userIdOrData as string,
      statusCode,
      duration: durationOrDuration,
      metadata,
    });
    writeLog(entry);
  }
}

/**
 * Log API error - overloaded for both calling patterns
 */
export function logApiError(
  reqOrRequestId: NextRequest | string,
  error: unknown,
  userIdOrStatusCode?: string | number,
  metadataOrDuration?: Record<string, unknown> | number
): void {
  const errorMessage = error instanceof Error ? error.message : String(error);
  const errorStack = error instanceof Error ? error.stack : undefined;

  // Detect which calling pattern is being used
  if (typeof reqOrRequestId === "string") {
    // String-based pattern: (requestId, error, statusCode, duration)
    const entry = createLogEntry("error", "API error occurred", {
      endpoint: "",
      method: "",
      statusCode: userIdOrStatusCode as number,
      duration: metadataOrDuration as number,
      error: errorMessage,
      metadata: {
        requestId: reqOrRequestId,
        stack: errorStack,
      },
    });
    writeLog(entry);
  } else {
    // NextRequest-based pattern: (req, error, userId?, metadata?)
    const req = reqOrRequestId;
    const entry = createLogEntry("error", "API error occurred", {
      endpoint: req.nextUrl.pathname,
      method: req.method,
      userId: userIdOrStatusCode as string,
      error: errorMessage,
      metadata: {
        stack: errorStack,
        ...(metadataOrDuration as Record<string, unknown>),
      },
    });
    writeLog(entry);
  }
}

// Legacy aliases
export const logRequest = logApiRequest;
export const logResponse = logApiResponse;
export const logError = logApiError;

/**
 * Middleware wrapper with logging
 */
export function withLogging<T extends (...args: any[]) => Promise<NextResponse>>(
  handler: T,
  getUserId?: (req: NextRequest) => string | undefined
): T {
  return (async (req: NextRequest, ...args: any[]) => {
    const startTime = Date.now();
    const userId = getUserId?.(req);

    // Log request
    logApiRequest(req, userId);

    try {
      // Execute handler
      const response = await handler(req, ...args);
      const duration = Date.now() - startTime;

      // Log response
      logApiResponse(req, response, userId, duration);

      return response;
    } catch (error) {
      // Log error
      logApiError(req, error, userId);
      throw error;
    }
  }) as T;
}
