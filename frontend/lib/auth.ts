import { auth, currentUser } from "@clerk/nextjs/server";

/**
 * User roles for the coaching application
 */
export enum UserRole {
  MANAGER = "manager",
  REP = "rep",
}

/**
 * Get the current user's role from Clerk metadata
 * Role is stored in publicMetadata.role
 */
export async function getCurrentUserRole(): Promise<UserRole | null> {
  const user = await currentUser();

  if (!user) {
    return null;
  }

  const role = user.publicMetadata?.role as string | undefined;

  if (role === UserRole.MANAGER || role === UserRole.REP) {
    return role as UserRole;
  }

  // Default to rep if no role is set
  return UserRole.REP;
}

/**
 * Check if the current user is a manager
 */
export async function isManager(): Promise<boolean> {
  const role = await getCurrentUserRole();
  return role === UserRole.MANAGER;
}

/**
 * Check if the current user is a rep
 */
export async function isRep(): Promise<boolean> {
  const role = await getCurrentUserRole();
  return role === UserRole.REP;
}

/**
 * Get the current user's email
 */
export async function getCurrentUserEmail(): Promise<string | null> {
  const user = await currentUser();
  return user?.emailAddresses[0]?.emailAddress ?? null;
}

/**
 * Check if the current user can view a specific rep's data
 * Managers can view all data, reps can only view their own
 */
export async function canViewRepData(repEmail: string): Promise<boolean> {
  const userRole = await getCurrentUserRole();
  const userEmail = await getCurrentUserEmail();

  if (!userEmail) {
    return false;
  }

  // Managers can view all rep data
  if (userRole === UserRole.MANAGER) {
    return true;
  }

  // Reps can only view their own data
  return userEmail.toLowerCase() === repEmail.toLowerCase();
}

/**
 * Enforce manager-only access
 * Throws an error if the user is not a manager
 */
export async function requireManager(): Promise<void> {
  const role = await getCurrentUserRole();

  if (role !== UserRole.MANAGER) {
    throw new Error("Unauthorized: Manager access required");
  }
}

/**
 * Get user session information
 */
export async function getUserSession() {
  const { userId, sessionId } = await auth();
  const user = await currentUser();

  return {
    userId,
    sessionId,
    user,
    role: await getCurrentUserRole(),
    email: await getCurrentUserEmail(),
  };
}

/**
 * Type guard for checking if metadata contains a valid role
 */
export function hasValidRole(metadata: unknown): metadata is { role: UserRole } {
  if (typeof metadata !== "object" || metadata === null) {
    return false;
  }

  const obj = metadata as Record<string, unknown>;
  return (
    typeof obj.role === "string" &&
    (obj.role === UserRole.MANAGER || obj.role === UserRole.REP)
  );
}
