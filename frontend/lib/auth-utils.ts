/**
 * Client-side auth utilities for role-based access control
 *
 * These utilities work with Clerk's publicMetadata.role field on the client side.
 * For server-side auth checks, use lib/auth.ts instead.
 */

import type { UserResource } from "@clerk/types";

/**
 * User roles for the coaching application
 */
export enum UserRole {
  MANAGER = "manager",
  REP = "rep",
}

/**
 * Extract user role from Clerk user object
 * Role is stored in publicMetadata.role
 *
 * @param user - Clerk user object from useUser() hook
 * @returns UserRole enum value
 */
export function getUserRole(user: UserResource | null | undefined): UserRole {
  if (!user?.publicMetadata?.role) {
    return UserRole.REP; // Default to rep if no role is set
  }

  const role = user.publicMetadata.role as string;

  if (role === UserRole.MANAGER) {
    return UserRole.MANAGER;
  }

  return UserRole.REP;
}

/**
 * Check if the user is a manager
 *
 * @param user - Clerk user object from useUser() hook
 * @returns true if user is a manager
 *
 * @example
 * const { user } = useUser();
 * const canViewAllReps = isManager(user);
 */
export function isManager(user: UserResource | null | undefined): boolean {
  return getUserRole(user) === UserRole.MANAGER;
}

/**
 * Check if the user is a rep
 *
 * @param user - Clerk user object from useUser() hook
 * @returns true if user is a rep
 */
export function isRep(user: UserResource | null | undefined): boolean {
  return getUserRole(user) === UserRole.REP;
}

/**
 * Get user's email address
 *
 * @param user - Clerk user object from useUser() hook
 * @returns email address or null if not available
 */
export function getUserEmail(user: UserResource | null | undefined): string | null {
  return user?.emailAddresses[0]?.emailAddress ?? null;
}

/**
 * Check if the user can view a specific rep's data
 * Managers can view all data, reps can only view their own
 *
 * @param user - Clerk user object from useUser() hook
 * @param repEmail - Email of the rep whose data is being accessed
 * @returns true if user has access to view the rep's data
 *
 * @example
 * const { user } = useUser();
 * const canView = canViewRepData(user, 'sarah.jones@prefect.io');
 */
export function canViewRepData(
  user: UserResource | null | undefined,
  repEmail: string
): boolean {
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
 * @param user - Clerk user object from useUser() hook
 * @returns true if user has manager access
 *
 * @example
 * const { user } = useUser();
 *
 * {hasManagerAccess(user) && (
 *   <ManagerOnlyFeature />
 * )}
 */
export function hasManagerAccess(user: UserResource | null | undefined): boolean {
  return isManager(user);
}

/**
 * Get a user-friendly role display name
 *
 * @param user - Clerk user object from useUser() hook
 * @returns "Manager" or "Sales Rep"
 */
export function getRoleDisplayName(user: UserResource | null | undefined): string {
  return isManager(user) ? "Manager" : "Sales Rep";
}
