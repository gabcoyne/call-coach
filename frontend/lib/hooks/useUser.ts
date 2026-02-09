"use client";

import { useCurrentUser, type CurrentUser } from "./use-current-user";

export interface UseUserReturn {
  currentUser: CurrentUser | null;
  isManager: boolean;
  loading: boolean;
  error: any;
}

/**
 * Hook for accessing current user information with role-based access checks.
 *
 * Wraps useCurrentUser to provide a simplified interface for checking manager access.
 */
export function useUser(): UseUserReturn {
  const { data, isLoading, error } = useCurrentUser();

  return {
    currentUser: data ?? null,
    isManager: data?.role === "manager" || data?.role === "admin",
    loading: isLoading,
    error,
  };
}
