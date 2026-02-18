/**
 * Client-side auth utilities for role-based access control
 *
 * These utilities work with IAP authentication and the auth context.
 * For server-side auth checks, use lib/auth.ts instead.
 */

import type { AuthUser } from "@/lib/auth-context";

/**
 * User roles for the coaching application
 */
export enum UserRole {
  MANAGER = "manager",
  REP = "rep",
}

/**
 * Extract user role from auth user object
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns UserRole enum value
 */
export function getUserRole(user: AuthUser | null | undefined): UserRole {
  if (!user?.role) {
    return UserRole.REP; // Default to rep if no role is set
  }

  if (user.role === UserRole.MANAGER) {
    return UserRole.MANAGER;
  }

  return UserRole.REP;
}

/**
 * Check if the user is a manager
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns true if user is a manager
 *
 * @example
 * const { user } = useAuthContext();
 * const canViewAllReps = isManager(user);
 */
export function isManager(user: AuthUser | null | undefined): boolean {
  return getUserRole(user) === UserRole.MANAGER;
}

/**
 * Check if the user is a rep
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns true if user is a rep
 */
export function isRep(user: AuthUser | null | undefined): boolean {
  return getUserRole(user) === UserRole.REP;
}

/**
 * Get user's email address
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns email address or null if not available
 */
export function getUserEmail(user: AuthUser | null | undefined): string | null {
  return user?.email ?? null;
}

/**
 * Check if the user can view a specific rep's data
 * Managers can view all data, reps can only view their own
 *
 * @param user - Auth user object from useAuthContext() hook
 * @param repEmail - Email of the rep whose data is being accessed
 * @returns true if user has access to view the rep's data
 *
 * @example
 * const { user } = useAuthContext();
 * const canView = canViewRepData(user, 'sarah.jones@prefect.io');
 */
export function canViewRepData(user: AuthUser | null | undefined, repEmail: string): boolean {
  if (!user) {
    return false;
  }

  // Managers can view all rep data
  if (isManager(user)) {
    return true;
  }

  // Reps can only view their own data
  const userEmail = getUserEmail(user);
  if (!userEmail) {
    return false;
  }

  return userEmail.toLowerCase() === repEmail.toLowerCase();
}

/**
 * Check if the user has manager-only features access
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns true if user has manager access
 *
 * @example
 * const { user } = useAuthContext();
 *
 * {hasManagerAccess(user) && (
 *   <ManagerOnlyFeature />
 * )}
 */
export function hasManagerAccess(user: AuthUser | null | undefined): boolean {
  return isManager(user);
}

/**
 * Get a user-friendly role display name
 *
 * @param user - Auth user object from useAuthContext() hook
 * @returns "Manager" or "Sales Rep"
 */
export function getRoleDisplayName(user: AuthUser | null | undefined): string {
  return isManager(user) ? "Manager" : "Sales Rep";
}
