"use client";

import useSWR from "swr";
import type { RepInsightsRequest, RepInsightsResponse, APIErrorResponse } from "@/types/coaching";
import { buildApiUrl, SWRError } from "../swr-config";

/**
 * Options for useRepInsights hook
 */
export interface UseRepInsightsOptions {
  time_period?: RepInsightsRequest["time_period"];
  product_filter?: RepInsightsRequest["product_filter"];
  enabled?: boolean;
  refreshInterval?: number;
}

/**
 * Return type for useRepInsights hook
 */
export interface UseRepInsightsReturn {
  data?: RepInsightsResponse;
  error?: SWRError;
  isLoading: boolean;
  isValidating: boolean;
  mutate: () => Promise<RepInsightsResponse | undefined>;
}

/**
 * Custom SWR hook for fetching rep performance insights
 *
 * @param repEmail - The email address of the rep
 * @param options - Optional configuration for the insights request
 * @returns Rep insights data with loading/error states
 *
 * @example
 * ```tsx
 * function RepDashboard({ repEmail }: { repEmail: string }) {
 *   const { data, error, isLoading } = useRepInsights(repEmail, {
 *     time_period: 'last_30_days',
 *     product_filter: 'prefect',
 *   });
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (!data) return null;
 *
 *   return (
 *     <div>
 *       <h2>{data.rep_info.name}</h2>
 *       <p>Calls Analyzed: {data.rep_info.calls_analyzed}</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useRepInsights(
  repEmail: string | null | undefined,
  options: UseRepInsightsOptions = {}
): UseRepInsightsReturn {
  const { time_period = "last_30_days", product_filter, enabled = true, refreshInterval } = options;

  // Build API URL with query parameters
  // Note: convert null to undefined since buildApiUrl doesn't accept null
  const url =
    repEmail && enabled
      ? buildApiUrl("/api/coaching/rep-insights", {
          rep_email: repEmail,
          time_period,
          product_filter: product_filter ?? undefined,
        })
      : null;

  const { data, error, isValidating, mutate } = useSWR<RepInsightsResponse, SWRError>(url, {
    revalidateOnFocus: true,
    keepPreviousData: true,
    refreshInterval,
    dedupingInterval: 5000,
  });

  return {
    data,
    error,
    isLoading: !data && !error && enabled,
    isValidating,
    mutate,
  };
}

/**
 * Hook to fetch insights for multiple reps (manager view)
 *
 * @param repEmails - Array of rep email addresses
 * @param options - Optional configuration for the insights request
 * @returns Map of rep email to insights data
 *
 * @example
 * ```tsx
 * function TeamDashboard({ repEmails }: { repEmails: string[] }) {
 *   const { data, error, isLoading } = useMultipleRepInsights(repEmails, {
 *     time_period: 'last_30_days',
 *   });
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>Error loading team data</div>;
 *
 *   return (
 *     <div>
 *       {Object.entries(data).map(([email, insights]) => (
 *         <RepCard key={email} insights={insights} />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useMultipleRepInsights(
  repEmails: string[],
  options: Omit<UseRepInsightsOptions, "enabled"> = {}
) {
  const { time_period = "last_30_days", product_filter, refreshInterval } = options;

  // Create keys for all reps
  // Note: convert null to undefined since buildApiUrl doesn't accept null
  const keys = repEmails.map((email) =>
    buildApiUrl("/api/coaching/rep-insights", {
      rep_email: email,
      time_period,
      product_filter: product_filter ?? undefined,
    })
  );

  // Use SWR with multiple keys
  const results = useSWR<RepInsightsResponse[], SWRError>(
    repEmails.length > 0 ? keys : null,
    async (urls: string[]) => {
      const responses = await Promise.all(
        urls.map((url) =>
          fetch(url, {
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
          })
        )
      );

      // Check for errors
      for (const response of responses) {
        if (!response.ok) {
          const error: any = new Error("Failed to fetch rep insights");
          error.status = response.status;

          try {
            const errorData: APIErrorResponse = await response.json();
            error.info = errorData;
            error.message = errorData.error || errorData.message || error.message;
          } catch {
            // If error response is not JSON, use default message
          }

          throw error;
        }
      }

      // Parse all responses
      return Promise.all(responses.map((r) => r.json()));
    },
    {
      revalidateOnFocus: true,
      keepPreviousData: true,
      refreshInterval,
      dedupingInterval: 5000,
    }
  );

  // Convert array to map keyed by email
  const dataMap =
    results.data?.reduce(
      (acc, insights, index) => {
        acc[repEmails[index]] = insights;
        return acc;
      },
      {} as Record<string, RepInsightsResponse>
    ) || {};

  return {
    data: dataMap,
    error: results.error,
    isLoading: !results.data && !results.error && repEmails.length > 0,
    isValidating: results.isValidating,
    mutate: results.mutate,
  };
}
