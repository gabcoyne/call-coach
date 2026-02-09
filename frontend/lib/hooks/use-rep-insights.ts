'use client';

import useSWR from 'swr';
import { useAuth } from '@clerk/nextjs';
import { mcpClient, RepInsightsResponse } from '@/lib/mcp-client';

export interface UseRepInsightsOptions {
  /** Time period for insights (e.g., "last_7_days", "last_30_days", "last_90_days", "all_time") */
  time_period?: string;
  /** Product filter (optional) */
  product_filter?: string;
}

/**
 * useRepInsights Hook
 *
 * Fetches performance insights for a sales rep using SWR.
 * Automatically enforces role-based access: reps can only fetch their own data.
 * Requires authentication via Clerk.
 *
 * @param email - The rep's email address
 * @param options - Optional time period and product filter
 * @returns SWR response with insights data, loading, and error states
 *
 * @example
 * const { data, error, isLoading } = useRepInsights('sarah.jones@prefect.io', {
 *   time_period: 'last_30_days'
 * });
 */
export function useRepInsights(
  email: string | null | undefined,
  options: UseRepInsightsOptions = {}
) {
  const { getToken, userId } = useAuth();

  const swrKey = email
    ? ['rep-insights', email, JSON.stringify(options)]
    : null;

  return useSWR<RepInsightsResponse>(
    swrKey,
    async () => {
      if (!email) {
        throw new Error('Rep email is required');
      }

      if (!userId) {
        throw new Error('Authentication required');
      }

      // Get Clerk auth token
      const token = await getToken();

      // Note: Role-based access check happens on backend
      // Reps can only access their own data (enforced by backend using token)
      // Managers can access any rep's data

      return mcpClient.getRepInsights(
        {
          rep_email: email,
          ...options,
        },
        token || undefined
      );
    },
    {
      // Revalidate every 5 minutes (performance data is relatively static)
      refreshInterval: 5 * 60 * 1000,
      // Don't revalidate on focus
      revalidateOnFocus: false,
      // Retry on error with exponential backoff
      errorRetryCount: 3,
      errorRetryInterval: 1000,
      // Keep previous data while revalidating
      keepPreviousData: true,
    }
  );
}
