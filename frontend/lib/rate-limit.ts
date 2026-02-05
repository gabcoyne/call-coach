/**
 * Rate Limiting for API Routes
 *
 * Simple in-memory rate limiter with per-user and per-endpoint tracking.
 * For production, consider using Redis or a dedicated rate limiting service.
 */

interface RateLimitConfig {
  maxRequests: number;
  windowMs: number;
}

interface RateLimitEntry {
  count: number;
  resetAt: number;
}

/**
 * In-memory store for rate limit tracking
 * Key format: `{userId}:{endpoint}`
 */
const rateLimitStore = new Map<string, RateLimitEntry>();

/**
 * Clean up expired entries periodically
 */
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetAt < now) {
      rateLimitStore.delete(key);
    }
  }
}, 60000); // Clean up every minute

/**
 * Rate limit configurations by endpoint
 */
const RATE_LIMIT_CONFIGS: Record<string, RateLimitConfig> = {
  '/api/coaching/analyze-call': {
    maxRequests: 10,
    windowMs: 60000, // 10 requests per minute
  },
  '/api/coaching/rep-insights': {
    maxRequests: 20,
    windowMs: 60000, // 20 requests per minute
  },
  '/api/coaching/search-calls': {
    maxRequests: 30,
    windowMs: 60000, // 30 requests per minute
  },
};

/**
 * Default rate limit for unspecified endpoints
 */
const DEFAULT_RATE_LIMIT: RateLimitConfig = {
  maxRequests: 60,
  windowMs: 60000, // 60 requests per minute
};

/**
 * Check if a request is rate limited
 *
 * @param userId - User identifier
 * @param endpoint - API endpoint path
 * @returns Object with allowed status and rate limit info
 */
export function checkRateLimit(
  userId: string,
  endpoint: string
): {
  allowed: boolean;
  limit: number;
  remaining: number;
  reset: number;
} {
  const config = RATE_LIMIT_CONFIGS[endpoint] || DEFAULT_RATE_LIMIT;
  const key = `${userId}:${endpoint}`;
  const now = Date.now();

  // Get or create entry
  let entry = rateLimitStore.get(key);

  // Reset if window has expired
  if (!entry || entry.resetAt < now) {
    entry = {
      count: 0,
      resetAt: now + config.windowMs,
    };
    rateLimitStore.set(key, entry);
  }

  // Increment count
  entry.count++;

  // Check if limit exceeded
  const allowed = entry.count <= config.maxRequests;
  const remaining = Math.max(0, config.maxRequests - entry.count);

  return {
    allowed,
    limit: config.maxRequests,
    remaining,
    reset: entry.resetAt,
  };
}

/**
 * Rate limit headers for HTTP response
 */
export function rateLimitHeaders(
  limit: number,
  remaining: number,
  reset: number
): Record<string, string> {
  return {
    'X-RateLimit-Limit': limit.toString(),
    'X-RateLimit-Remaining': remaining.toString(),
    'X-RateLimit-Reset': reset.toString(),
  };
}
