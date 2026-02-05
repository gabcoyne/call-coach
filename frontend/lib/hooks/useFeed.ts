/**
 * Feed Hooks
 *
 * SWR hooks for fetching and managing coaching insights feed data
 */

import useSWR from 'swr';
import useSWRInfinite from 'swr/infinite';
import { buildApiUrl } from '@/lib/swr-config';
import { FeedResponse, FeedRequest } from '@/types/coaching';

export interface UseFeedOptions {
  type_filter?: 'all' | 'call_analysis' | 'team_insight' | 'highlight' | 'milestone';
  time_filter?: 'today' | 'this_week' | 'this_month' | 'custom';
  start_date?: string;
  end_date?: string;
  include_dismissed?: boolean;
  limit?: number;
}

export interface UseFeedReturn {
  data?: FeedResponse;
  error?: Error;
  isLoading: boolean;
  isValidating: boolean;
  mutate: () => void;
}

/**
 * Hook to fetch feed data
 */
export function useFeed(options: UseFeedOptions = {}): UseFeedReturn {
  const params: Record<string, string | number | boolean | undefined> = {
    type_filter: options.type_filter,
    time_filter: options.time_filter,
    start_date: options.start_date,
    end_date: options.end_date,
    include_dismissed: options.include_dismissed,
    limit: options.limit || 20,
    offset: 0,
  };

  const url = buildApiUrl('/api/coaching/feed', params);

  const { data, error, isValidating, mutate } = useSWR<FeedResponse>(url, {
    revalidateOnFocus: true,
    refreshInterval: 60000, // Auto-refresh every 60 seconds
  });

  return {
    data,
    error,
    isLoading: !data && !error,
    isValidating,
    mutate,
  };
}

/**
 * Hook for infinite scrolling feed
 */
export interface UseInfiniteFeedReturn {
  data?: FeedResponse[];
  error?: Error;
  size: number;
  setSize: (size: number | ((size: number) => number)) => void;
  isLoading: boolean;
  isLoadingMore: boolean;
  isEmpty: boolean;
  isReachingEnd: boolean;
  mutate: () => void;
}

export function useInfiniteFeed(
  options: UseFeedOptions = {}
): UseInfiniteFeedReturn {
  const limit = options.limit || 20;

  const getKey = (pageIndex: number, previousPageData: FeedResponse | null) => {
    // Reached the end
    if (previousPageData && !previousPageData.has_more) return null;

    const params: Record<string, string | number | boolean | undefined> = {
      type_filter: options.type_filter,
      time_filter: options.time_filter,
      start_date: options.start_date,
      end_date: options.end_date,
      include_dismissed: options.include_dismissed,
      limit,
      offset: pageIndex * limit,
    };

    return buildApiUrl('/api/coaching/feed', params);
  };

  const { data, error, size, setSize, isValidating, mutate } = useSWRInfinite<FeedResponse>(
    getKey,
    {
      revalidateFirstPage: true,
      revalidateAll: false,
      refreshInterval: 60000, // Auto-refresh every 60 seconds
    }
  );

  const isLoading = !data && !error;
  const isLoadingMore =
    isLoading || (size > 0 && data && typeof data[size - 1] === 'undefined');
  const isEmpty = data?.[0]?.items.length === 0;
  const isReachingEnd =
    isEmpty || (data && data[data.length - 1]?.has_more === false);

  return {
    data,
    error,
    size,
    setSize,
    isLoading,
    isLoadingMore: !!isLoadingMore,
    isEmpty,
    isReachingEnd: !!isReachingEnd,
    mutate,
  };
}

/**
 * Hook to manage feed item actions (bookmark, dismiss)
 */
export interface UseFeedActionsReturn {
  bookmarkItem: (itemId: string) => Promise<void>;
  dismissItem: (itemId: string) => Promise<void>;
  shareItem: (itemId: string) => Promise<string>;
  isProcessing: boolean;
}

export function useFeedActions(): UseFeedActionsReturn {
  const [isProcessing, setIsProcessing] = useState(false);

  const bookmarkItem = async (itemId: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/coaching/feed/bookmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId }),
      });

      if (!response.ok) {
        throw new Error('Failed to bookmark item');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const dismissItem = async (itemId: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/coaching/feed/dismiss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId }),
      });

      if (!response.ok) {
        throw new Error('Failed to dismiss item');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const shareItem = async (itemId: string): Promise<string> => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/coaching/feed/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate share link');
      }

      const data = await response.json();
      return data.share_url;
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    bookmarkItem,
    dismissItem,
    shareItem,
    isProcessing,
  };
}

// Import useState from react
import { useState } from 'react';
