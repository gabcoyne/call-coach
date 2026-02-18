/**
 * Authentication Middleware for API Routes
 *
 * Provides session verification and RBAC enforcement using IAP headers.
 * Supports dev mode bypass with BYPASS_AUTH=true.
 */

import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";

/**
 * User role types
 */
export type UserRole = "manager" | "rep";

/**
 * Authenticated user context
 */
export interface AuthContext {
  userId: string;
  email: string;
  role: UserRole;
  name: string | null;
}

/**
 * Dev mode bypass check
 */
const bypassAuth = process.env.NODE_ENV === "development" && process.env.BYPASS_AUTH === "true";

/**
 * Mock user for dev mode
 */
const DEV_AUTH_CONTEXT: AuthContext = {
  userId: "dev_user_george",
  email: "george@prefect.io",
  role: "manager",
  name: "George Coyne",
};

/**
 * Manager emails - users with manager role
 * In production, this could come from a database or config
 */
const MANAGER_EMAILS = new Set([
  "george@prefect.io",
  "gcoyne@prefect.io",
  // Add other managers here
]);

/**
 * Determine user role based on email
 */
function getRoleFromEmail(email: string): UserRole {
  if (MANAGER_EMAILS.has(email.toLowerCase())) {
    return "manager";
  }
  return "rep";
}

/**
 * Extract name from email (fallback when we don't have full name)
 */
function getNameFromEmail(email: string): string {
  const localPart = email.split("@")[0];
  // Convert "george.coyne" or "gcoyne" to "George Coyne" or "Gcoyne"
  return localPart
    .split(/[._]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

/**
 * Get auth context from IAP headers
 *
 * @throws {Error} If user is not authenticated
 */
export async function getAuthContext(): Promise<AuthContext> {
  // Dev mode bypass
  if (bypassAuth) {
    return DEV_AUTH_CONTEXT;
  }

  const headersList = await headers();

  // IAP headers (normalized by middleware or direct from IAP)
  let email = headersList.get("x-iap-user-email");
  let userId = headersList.get("x-iap-user-id");

  // Fallback to raw IAP headers
  if (!email) {
    const rawEmail = headersList.get("x-goog-authenticated-user-email");
    if (rawEmail) {
      email = rawEmail.replace("accounts.google.com:", "");
    }
  }

  if (!userId) {
    const rawUserId = headersList.get("x-goog-authenticated-user-id");
    if (rawUserId) {
      userId = rawUserId.replace("accounts.google.com:", "");
    }
  }

  if (!email) {
    throw new Error("Unauthorized: No IAP authentication");
  }

  const role = getRoleFromEmail(email);
  const name = getNameFromEmail(email);

  return {
    userId: userId || email,
    email,
    role,
    name,
  };
}

/**
 * Check if user has required role
 */
export function hasRole(context: AuthContext, allowedRoles: UserRole[]): boolean {
  return allowedRoles.includes(context.role);
}

/**
 * Check if user can access rep data (managers can access all, reps only their own)
 */
export function canAccessRepData(context: AuthContext, repEmail: string): boolean {
  if (context.role === "manager") {
    return true;
  }
  return context.email.toLowerCase() === repEmail.toLowerCase();
}

/**
 * API Error Response Helper
 */
export function apiError(message: string, status: number = 400, details?: unknown): NextResponse {
  return NextResponse.json(
    {
      error: message,
      details,
    },
    { status }
  );
}

/**
 * Middleware wrapper for authenticated API routes
 */
export function withAuth(
  handler: (req: NextRequest, context: AuthContext) => Promise<NextResponse>,
  options: { allowedRoles?: UserRole[] } = {}
) {
  return async (req: NextRequest): Promise<NextResponse> => {
    try {
      // Verify session and get user context
      const authContext = await getAuthContext();

      // Check role if specified
      if (options.allowedRoles && !hasRole(authContext, options.allowedRoles)) {
        return apiError(
          `Forbidden: Requires one of roles: ${options.allowedRoles.join(", ")}`,
          403
        );
      }

      // Call the actual handler
      return await handler(req, authContext);
    } catch (error) {
      if (error instanceof Error && error.message.startsWith("Unauthorized")) {
        return apiError(error.message, 401);
      }

      console.error("Auth middleware error:", error);
      return apiError("Internal server error", 500, error);
    }
  };
}

// Alias for backward compatibility
export const withAuthMiddleware = withAuth;
