/**
 * Prefetching utilities for critical data
 * Helps improve perceived performance by loading data before user navigation
 */

import { cache } from "react";
import { buildApiUrl } from "./swr-config";

/**
 * Prefetch call analysis data
 * Can be called server-side or client-side to warm the cache
 */
export const prefetchCallAnalysis = cache(async (callId: string) => {
  const url = buildApiUrl("/api/coaching/analyze-call", {
    call_id: callId,
    use_cache: "true",
    include_transcript_snippets: "true",
  });

  try {
    const response = await fetch(url, {
      next: {
        revalidate: 300, // Cache for 5 minutes
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to prefetch call analysis: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Prefetch error:", error);
    return null;
  }
});

/**
 * Prefetch rep insights data
 * Useful for dashboard pages
 */
export const prefetchRepInsights = cache(
  async (repEmail: string, timePeriod: string = "last_30_days") => {
    const url = buildApiUrl("/api/coaching/rep-insights", {
      rep_email: repEmail,
      time_period: timePeriod,
    });

    try {
      const response = await fetch(url, {
        next: {
          revalidate: 300, // Cache for 5 minutes
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to prefetch rep insights: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Prefetch error:", error);
      return null;
    }
  }
);

/**
 * Client-side prefetch helper for Link hover/focus
 * Triggers SWR to fetch data before navigation
 */
export function usePrefetchOnHover() {
  return {
    prefetchCall: (callId: string) => {
      // In browser, trigger SWR fetch via creating a temporary fetch
      if (typeof window !== "undefined") {
        const url = buildApiUrl("/api/coaching/analyze-call", {
          call_id: callId,
          use_cache: "true",
        });
        // Don't await - fire and forget
        fetch(url).catch(() => {
          // Silently fail prefetch
        });
      }
    },
    prefetchDashboard: (repEmail: string) => {
      if (typeof window !== "undefined") {
        const url = buildApiUrl("/api/coaching/rep-insights", {
          rep_email: repEmail,
          time_period: "last_30_days",
        });
        fetch(url).catch(() => {
          // Silently fail prefetch
        });
      }
    },
  };
}
