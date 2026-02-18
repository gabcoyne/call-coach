/**
 * Auth hooks using IAP authentication
 *
 * These hooks provide a similar API to Clerk hooks but use IAP for authentication.
 */

import { useAuthContext, AuthUser } from "@/lib/auth-context";

/**
 * Mock user structure for compatibility with existing code
 */
function toUserObject(user: AuthUser | null) {
  if (!user) return null;

  return {
    id: user.id,
    firstName: user.name?.split(" ")[0] || null,
    lastName: user.name?.split(" ").slice(1).join(" ") || null,
    fullName: user.name,
    username: user.email.split("@")[0],
    primaryEmailAddress: { emailAddress: user.email },
    emailAddresses: [{ emailAddress: user.email }],
    publicMetadata: {
      role: user.role,
    },
    imageUrl: null,
    hasImage: false,
  };
}

/**
 * useUser hook - returns user info
 */
export function useUser() {
  const { user, isLoading, isAuthenticated } = useAuthContext();

  return {
    user: toUserObject(user),
    isLoaded: !isLoading,
    isSignedIn: isAuthenticated,
  };
}

/**
 * useAuth hook - returns auth state and methods
 */
export function useAuth() {
  const { user, isLoading, isAuthenticated, signOut } = useAuthContext();

  return {
    isLoaded: !isLoading,
    isSignedIn: isAuthenticated,
    userId: user?.id || null,
    sessionId: null,
    orgId: null,
    orgRole: null,
    orgSlug: null,
    signOut,
    getToken: async () => null, // IAP doesn't provide tokens to the client
  };
}
