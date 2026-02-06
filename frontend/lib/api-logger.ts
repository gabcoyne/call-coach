/**
 * API Request/Response Logger
 *
 * Provides structured logging for API routes with request/response details.
 */

import { NextRequest, NextResponse } from 'next/server';

/**
 * Log levels
 */
type LogLevel = 'info' | 'warn' | 'error';

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
    case 'error':
      console.error(formatted);
      break;
    case 'warn':
      console.warn(formatted);
      break;
    default:
      console.log(formatted);
  }
}

/**
 * Create log entry
 */
function createLogEntry(
  level: LogLevel,
  message: string,
  data: Partial<LogEntry>
): LogEntry {
  return {
    timestamp: new Date().toISOString(),
    level,
    message,
    endpoint: data.endpoint || '',
    method: data.method || '',
    ...data,
  };
}

/**
 * Log API request
 */
export function logRequest(
  req: NextRequest,
  userId?: string,
  metadata?: Record<string, unknown>
): void {
  const entry = createLogEntry('info', 'API request received', {
    endpoint: req.nextUrl.pathname,
    method: req.method,
    userId,
    metadata: {
      searchParams: Object.fromEntries(req.nextUrl.searchParams),
      ...metadata,
    },
  });

  writeLog(entry);
}

/**
 * Log API response
 */
export function logResponse(
  req: NextRequest,
  res: NextResponse,
  userId?: string,
  duration?: number,
  metadata?: Record<string, unknown>
): void {
  const statusCode = res.status;
  const level: LogLevel = statusCode >= 500 ? 'error' : statusCode >= 400 ? 'warn' : 'info';

  const entry = createLogEntry(level, 'API response sent', {
    endpoint: req.nextUrl.pathname,
    method: req.method,
    userId,
    statusCode,
    duration,
    metadata,
  });

  writeLog(entry);
}

/**
 * Log API error
 */
export function logError(
  req: NextRequest,
  error: unknown,
  userId?: string,
  metadata?: Record<string, unknown>
): void {
  const errorMessage = error instanceof Error ? error.message : String(error);
  const errorStack = error instanceof Error ? error.stack : undefined;

  const entry = createLogEntry('error', 'API error occurred', {
    endpoint: req.nextUrl.pathname,
    method: req.method,
    userId,
    error: errorMessage,
    metadata: {
      stack: errorStack,
      ...metadata,
    },
  });

  writeLog(entry);
}

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
    logRequest(req, userId);

    try {
      // Execute handler
      const response = await handler(req, ...args);
      const duration = Date.now() - startTime;

      // Log response
      logResponse(req, response, userId, duration);

      return response;
    } catch (error) {
      // Log error
      logError(req, error, userId);
      throw error;
    }
  }) as T;
}

// Aliases for backward compatibility
export const logApiRequest = logRequest;
export const logApiResponse = logResponse;
export const logApiError = logError;
