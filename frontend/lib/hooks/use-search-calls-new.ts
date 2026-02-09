'use client';

import { useState, useEffect, useCallback } from 'react';
import useSWR from 'swr';
import { useAuth } from '@clerk/nextjs';
import { debounce } from 'lodash';
import { mcpClient, SearchCallsResponse } from '@/lib/mcp-client';

export interface SearchFilters {
  rep_email?: string;
  product?: string;
  call_type?: string;
  date_range?: { start: string; end: string };
  min_score?: number;
  max_score?: number;
  has_objection_type?: string;
  /** Keyword search - will be debounced */
  keyword?: string;
  topics?: string[];
  limit?: number;
}

/**
 * useSearchCalls Hook
 *
 * Searches for calls with filters using SWR.
 * Automatically debounces keyword search input with 300ms delay.
 * Requires authentication via Clerk.
 *
 * @param filters - Search filters
 * @returns SWR response with search results, loading, and error states
 *
 * @example
 * const [filters, setFilters] = useState<SearchFilters>({
 *   min_score: 70,
 *   keyword: 'pricing'
 * });
 * const { data, error, isLoading } = useSearchCalls(filters);
 */
export function useSearchCalls(filters: SearchFilters | null) {
  const { getToken, userId } = useAuth();
  const [debouncedKeyword, setDebouncedKeyword] = useState(filters?.keyword);

  // Debounce keyword changes with 300ms delay
  const updateKeyword = useCallback(
    debounce((keyword: string | undefined) => {
      setDebouncedKeyword(keyword);
    }, 300),
    []
  );

  // Update debounced keyword when filters change
  useEffect(() => {
    updateKeyword(filters?.keyword);
  }, [filters?.keyword, updateKeyword]);

  // Create SWR key with debounced keyword
  const filtersWithDebouncedKeyword = filters
    ? { ...filters, keyword: debouncedKeyword }
    : null;

  const swrKey = filtersWithDebouncedKeyword
    ? ['search-calls', JSON.stringify(filtersWithDebouncedKeyword)]
    : null;

  return useSWR<SearchCallsResponse>(
    swrKey,
    async () => {
      if (!filtersWithDebouncedKeyword) {
        throw new Error('Search filters are required');
      }

      if (!userId) {
        throw new Error('Authentication required');
      }

      // Get Clerk auth token
      const token = await getToken();

      return mcpClient.searchCalls(
        filtersWithDebouncedKeyword,
        token || undefined
      );
    },
    {
      // Revalidate every 5 minutes
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
