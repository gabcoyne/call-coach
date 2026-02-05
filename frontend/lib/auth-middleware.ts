/**
 * Authentication Middleware for API Routes
 *
 * Provides session verification and RBAC enforcement using Clerk.
 */

import { auth, currentUser } from '@clerk/nextjs/server';
import { NextRequest, NextResponse } from 'next/server';

/**
 * User role types
 */
export type UserRole = 'manager' | 'rep';

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
 * Verify Clerk session and extract user context
 *
 * @throws {Error} If user is not authenticated
 */
export async function getAuthContext(): Promise<AuthContext> {
  const { userId } = await auth();

  if (!userId) {
    throw new Error('Unauthorized: No valid session');
  }

  const user = await currentUser();

  if (!user) {
    throw new Error('Unauthorized: User not found');
  }

  // Get primary email
  const email = user.emailAddresses.find(
    (e) => e.id === user.primaryEmailAddressId
  )?.emailAddress;

  if (!email) {
    throw new Error('Unauthorized: No email address found');
  }

  // Extract role from Clerk metadata
  // In Clerk, you can store custom metadata in publicMetadata or privateMetadata
  const role = (user.publicMetadata?.role as UserRole) || 'rep';

  return {
    userId,
    email,
    role,
    name: user.fullName || user.firstName || null,
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
  if (context.role === 'manager') {
    return true;
  }
  return context.email === repEmail;
}

/**
 * API Error Response Helper
 */
export function apiError(
  message: string,
  status: number = 400,
  details?: unknown
): NextResponse {
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
          `Forbidden: Requires one of roles: ${options.allowedRoles.join(', ')}`,
          403
        );
      }

      // Call the actual handler
      return await handler(req, authContext);
    } catch (error) {
      if (error instanceof Error && error.message.startsWith('Unauthorized')) {
        return apiError(error.message, 401);
      }

      console.error('Auth middleware error:', error);
      return apiError('Internal server error', 500, error);
    }
  };
}
