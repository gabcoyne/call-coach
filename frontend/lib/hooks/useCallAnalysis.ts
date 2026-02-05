"use client";

import useSWR from "swr";
import useSWRMutation from "swr/mutation";
import type {
  AnalyzeCallRequest,
  AnalyzeCallResponse,
  APIErrorResponse,
} from "@/types/coaching";
import { buildApiUrl, SWRError } from "../swr-config";

/**
 * Options for useCallAnalysis hook
 */
export interface UseCallAnalysisOptions {
  dimensions?: AnalyzeCallRequest["dimensions"];
  use_cache?: boolean;
  include_transcript_snippets?: boolean;
  force_reanalysis?: boolean;
  enabled?: boolean;
}

/**
 * Return type for useCallAnalysis hook
 */
export interface UseCallAnalysisReturn {
  data?: AnalyzeCallResponse;
  error?: SWRError;
  isLoading: boolean;
  isValidating: boolean;
  mutate: () => Promise<AnalyzeCallResponse | undefined>;
}

/**
 * Custom SWR hook for fetching call analysis
 *
 * @param callId - The ID of the call to analyze
 * @param options - Optional configuration for the analysis request
 * @returns Call analysis data with loading/error states
 *
 * @example
 * ```tsx
 * function CallAnalysisView({ callId }: { callId: string }) {
 *   const { data, error, isLoading } = useCallAnalysis(callId);
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (!data) return null;
 *
 *   return <div>{data.scores.overall}</div>;
 * }
 * ```
 */
export function useCallAnalysis(
  callId: string | null | undefined,
  options: UseCallAnalysisOptions = {}
): UseCallAnalysisReturn {
  const {
    dimensions,
    use_cache = true,
    include_transcript_snippets = true,
    force_reanalysis = false,
    enabled = true,
  } = options;

  // Build API URL with query parameters
  const url =
    callId && enabled
      ? buildApiUrl("/api/coaching/analyze-call", {
          call_id: callId,
          dimensions: dimensions?.join(","),
          use_cache: String(use_cache),
          include_transcript_snippets: String(include_transcript_snippets),
          force_reanalysis: String(force_reanalysis),
        })
      : null;

  const { data, error, isValidating, mutate } = useSWR<
    AnalyzeCallResponse,
    SWRError
  >(url, {
    revalidateOnFocus: true,
    revalidateOnMount: force_reanalysis,
    keepPreviousData: true,
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
 * Options for useCallAnalysisMutation hook
 */
export interface UseCallAnalysisMutationOptions {
  onSuccess?: (data: AnalyzeCallResponse) => void;
  onError?: (error: SWRError) => void;
}

/**
 * Return type for useCallAnalysisMutation hook
 */
export interface UseCallAnalysisMutationReturn {
  trigger: (request: AnalyzeCallRequest) => Promise<AnalyzeCallResponse>;
  isMutating: boolean;
  error?: SWRError;
  data?: AnalyzeCallResponse;
  reset: () => void;
}

/**
 * Custom SWR mutation hook for triggering call analysis
 * Useful for on-demand analysis or re-analysis
 *
 * @param options - Optional callbacks for success/error
 * @returns Mutation trigger function with loading/error states
 *
 * @example
 * ```tsx
 * function AnalyzeCallButton({ callId }: { callId: string }) {
 *   const { trigger, isMutating } = useCallAnalysisMutation({
 *     onSuccess: (data) => console.log('Analysis complete:', data),
 *     onError: (error) => console.error('Analysis failed:', error),
 *   });
 *
 *   const handleAnalyze = async () => {
 *     await trigger({
 *       call_id: callId,
 *       force_reanalysis: true,
 *     });
 *   };
 *
 *   return (
 *     <button onClick={handleAnalyze} disabled={isMutating}>
 *       {isMutating ? 'Analyzing...' : 'Analyze Call'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useCallAnalysisMutation(
  options: UseCallAnalysisMutationOptions = {}
): UseCallAnalysisMutationReturn {
  const { onSuccess, onError } = options;

  async function analyzeCall(
    url: string,
    { arg }: { arg: AnalyzeCallRequest }
  ): Promise<AnalyzeCallResponse> {
    const response = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(arg),
    });

    if (!response.ok) {
      const error: any = new Error("Failed to analyze call");
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

    return response.json();
  }

  const { trigger, isMutating, error, data, reset } = useSWRMutation<
    AnalyzeCallResponse,
    SWRError,
    "/api/coaching/analyze-call",
    AnalyzeCallRequest
  >("/api/coaching/analyze-call", analyzeCall, {
    onSuccess,
    onError,
  });

  return {
    trigger,
    isMutating,
    error,
    data,
    reset,
  };
}
