/**
 * Auth hooks that support dev mode bypass
 *
 * When NEXT_PUBLIC_BYPASS_AUTH=true, returns a mock user instead of
 * requiring Clerk authentication. This allows local development without
 * needing to sign in.
 */

import { useUser as useClerkUser, useAuth as useClerkAuth } from "@clerk/nextjs";

/**
 * Mock user for development when BYPASS_AUTH is enabled
 */
const DEV_USER = {
  id: "dev_user_george",
  firstName: "George",
  lastName: "Coyne",
  fullName: "George Coyne",
  username: "gcoyne",
  primaryEmailAddress: { emailAddress: "george@prefect.io" },
  emailAddresses: [{ emailAddress: "george@prefect.io" }],
  publicMetadata: {
    role: "manager", // Can be "rep", "manager", or "admin"
    title: "Director of Engineering, GTM",
  },
  imageUrl: null,
  hasImage: false,
};

const bypassAuth = process.env.NEXT_PUBLIC_BYPASS_AUTH === "true";

/**
 * useUser hook that returns dev user when BYPASS_AUTH is enabled
 */
export function useUser() {
  const clerkUser = useClerkUser();

  if (bypassAuth) {
    return {
      user: DEV_USER as any,
      isLoaded: true,
      isSignedIn: true,
    };
  }

  return clerkUser;
}

/**
 * useAuth hook that returns mock auth when BYPASS_AUTH is enabled
 */
export function useAuth() {
  const clerkAuth = useClerkAuth();

  if (bypassAuth) {
    return {
      isLoaded: true,
      isSignedIn: true,
      userId: DEV_USER.id,
      sessionId: "dev_session",
      orgId: null,
      orgRole: null,
      orgSlug: null,
      signOut: async () => {},
      getToken: async () => "dev_token",
    };
  }

  return clerkAuth;
}
