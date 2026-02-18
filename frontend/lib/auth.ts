"use server";

import { headers } from "next/headers";
import { UserRole } from "./auth-utils";

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
 * Dev mode bypass check
 */
const bypassAuth = process.env.NODE_ENV === "development" && process.env.BYPASS_AUTH === "true";

/**
 * Get IAP email from headers
 */
async function getIAPEmail(): Promise<string | null> {
  if (bypassAuth) {
    return "george@prefect.io";
  }

  const headersList = await headers();

  // Try normalized header first
  let email = headersList.get("x-iap-user-email");

  // Fallback to raw IAP header
  if (!email) {
    const rawEmail = headersList.get("x-goog-authenticated-user-email");
    if (rawEmail) {
      email = rawEmail.replace("accounts.google.com:", "");
    }
  }

  return email;
}

/**
 * Get the current user's role based on email
 */
export async function getCurrentUserRole(): Promise<UserRole | null> {
  const email = await getIAPEmail();

  if (!email) {
    return null;
  }

  if (MANAGER_EMAILS.has(email.toLowerCase())) {
    return UserRole.MANAGER;
  }

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
  return getIAPEmail();
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
  const email = await getIAPEmail();
  const role = await getCurrentUserRole();

  const headersList = await headers();
  let userId = headersList.get("x-iap-user-id");
  if (!userId) {
    const rawUserId = headersList.get("x-goog-authenticated-user-id");
    if (rawUserId) {
      userId = rawUserId.replace("accounts.google.com:", "");
    }
  }

  return {
    userId: userId || email,
    sessionId: null, // IAP doesn't provide session IDs like Clerk
    user: email ? { email } : null,
    role,
    email,
  };
}
