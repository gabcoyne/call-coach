'use client';

import useSWR from 'swr';
import { mcpClient, AnalyzeCallResponse } from '@/lib/mcp-client';

export interface UseCallAnalysisOptions {
  /** Which dimensions to analyze (optional, analyzes all if not specified) */
  dimensions?: string[];
  /** Whether to use cached results (default: true) */
  use_cache?: boolean;
  /** Include transcript snippets in response (default: false) */
  include_transcript_snippets?: boolean;
  /** Force reanalysis even if cached (default: false) */
  force_reanalysis?: boolean;
}

/**
 * useCallAnalysis Hook
 *
 * Fetches coaching analysis for a specific call using SWR.
 * Automatically caches results and provides loading/error states.
 *
 * @param callId - The call ID to analyze
 * @param options - Optional analysis parameters
 * @returns SWR response with analysis data, loading, and error states
 *
 * @example
 * const { data, error, isLoading, mutate } = useCallAnalysis('call-123');
 */
export function useCallAnalysis(
  callId: string | null | undefined,
  options: UseCallAnalysisOptions = {}
) {
  const swrKey = callId
    ? ['call-analysis', callId, JSON.stringify(options)]
    : null;

  console.log('useCallAnalysis swrKey:', swrKey, 'callId:', callId);

  return useSWR<AnalyzeCallResponse>(
    swrKey,
    async () => {
      console.log('SWR fetcher called with callId:', callId);
      if (!callId) {
        throw new Error('Call ID is required');
      }

      console.log('Calling mcpClient.analyzeCall...');
      const result = await mcpClient.analyzeCall({
        call_id: callId,
        ...options,
      });
      console.log('mcpClient.analyzeCall returned:', result ? 'data received' : 'no data');
      return result;
    },
    {
      // Revalidate every 5 minutes (coaching data is relatively static)
      refreshInterval: 5 * 60 * 1000,
      // Don't revalidate on focus (user might be reading the analysis)
      revalidateOnFocus: false,
      // Retry on error with exponential backoff
      errorRetryCount: 3,
      errorRetryInterval: 1000,
      // Keep previous data while revalidating
      keepPreviousData: true,
      // Add onError handler to debug
      onError: (error) => {
        console.error('SWR error:', error);
      },
    }
  );
}
