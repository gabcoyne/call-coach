/**
 * Loading State Utilities for SWR
 *
 * Provides reusable loading state patterns and skeleton loaders.
 */

import { useState, useEffect, useCallback } from "react";

/**
 * Loading state types
 */
export type LoadingState = "idle" | "loading" | "success" | "error";

/**
 * Options for loading state hook
 */
export interface UseLoadingStateOptions {
  /**
   * Initial loading state
   */
  initialState?: LoadingState;

  /**
   * Callback when loading starts
   */
  onLoadingStart?: () => void;

  /**
   * Callback when loading completes successfully
   */
  onLoadingSuccess?: () => void;

  /**
   * Callback when loading fails
   */
  onLoadingError?: () => void;

  /**
   * Minimum loading time in milliseconds (prevents flash of loading state)
   */
  minLoadingTime?: number;
}

/**
 * Return type for loading state hook
 */
export interface UseLoadingStateReturn {
  /**
   * Current loading state
   */
  loadingState: LoadingState;

  /**
   * Whether currently loading
   */
  isLoading: boolean;

  /**
   * Whether loading completed successfully
   */
  isSuccess: boolean;

  /**
   * Whether loading failed
   */
  isError: boolean;

  /**
   * Whether in idle state
   */
  isIdle: boolean;

  /**
   * Set loading state to loading
   */
  startLoading: () => void;

  /**
   * Set loading state to success
   */
  setSuccess: () => void;

  /**
   * Set loading state to error
   */
  setError: () => void;

  /**
   * Reset to idle state
   */
  reset: () => void;
}

/**
 * Hook for managing loading state with lifecycle callbacks
 *
 * @param options - Loading state options
 * @returns Loading state and handlers
 *
 * @example
 * ```tsx
 * function CallAnalysisView({ callId }: { callId: string }) {
 *   const { data, error, isValidating } = useCallAnalysis(callId);
 *   const { isLoading, isSuccess } = useLoadingState({
 *     initialState: isValidating ? 'loading' : 'idle',
 *     onLoadingSuccess: () => {
 *       console.log('Analysis loaded successfully');
 *     },
 *   });
 *
 *   useEffect(() => {
 *     if (data) setSuccess();
 *     if (error) setError();
 *   }, [data, error]);
 *
 *   if (isLoading) return <LoadingSpinner />;
 *   if (isSuccess) return <AnalysisContent data={data} />;
 *
 *   return null;
 * }
 * ```
 */
export function useLoadingState(
  options: UseLoadingStateOptions = {}
): UseLoadingStateReturn {
  const {
    initialState = "idle",
    onLoadingStart,
    onLoadingSuccess,
    onLoadingError,
    minLoadingTime = 0,
  } = options;

  const [loadingState, setLoadingState] = useState<LoadingState>(initialState);
  const [loadingStartTime, setLoadingStartTime] = useState<number | null>(null);

  // Execute callbacks when loading state changes
  useEffect(() => {
    switch (loadingState) {
      case "loading":
        onLoadingStart?.();
        break;
      case "success":
        onLoadingSuccess?.();
        break;
      case "error":
        onLoadingError?.();
        break;
    }
  }, [loadingState, onLoadingStart, onLoadingSuccess, onLoadingError]);

  const startLoading = useCallback(() => {
    setLoadingState("loading");
    setLoadingStartTime(Date.now());
  }, []);

  const setSuccess = useCallback(() => {
    const finishLoading = () => setLoadingState("success");

    if (minLoadingTime > 0 && loadingStartTime) {
      const elapsed = Date.now() - loadingStartTime;
      const remaining = minLoadingTime - elapsed;

      if (remaining > 0) {
        setTimeout(finishLoading, remaining);
        return;
      }
    }

    finishLoading();
  }, [minLoadingTime, loadingStartTime]);

  const setError = useCallback(() => {
    setLoadingState("error");
  }, []);

  const reset = useCallback(() => {
    setLoadingState("idle");
    setLoadingStartTime(null);
  }, []);

  return {
    loadingState,
    isLoading: loadingState === "loading",
    isSuccess: loadingState === "success",
    isError: loadingState === "error",
    isIdle: loadingState === "idle",
    startLoading,
    setSuccess,
    setError,
    reset,
  };
}

/**
 * Hook for managing multiple loading states
 * Useful when loading data from multiple sources
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   const { data: insights, isLoading: insightsLoading } = useRepInsights(email);
 *   const { data: calls, isLoading: callsLoading } = useSearchCalls(filters);
 *
 *   const { isAnyLoading, isAllLoading, loadingCount } = useMultipleLoadingStates({
 *     insights: insightsLoading,
 *     calls: callsLoading,
 *   });
 *
 *   if (isAllLoading) return <LoadingSpinner />;
 *   if (isAnyLoading) return <PartialLoader count={loadingCount} />;
 *
 *   return <DashboardContent insights={insights} calls={calls} />;
 * }
 * ```
 */
export function useMultipleLoadingStates(states: Record<string, boolean>) {
  const loadingStates = Object.values(states);
  const loadingCount = loadingStates.filter(Boolean).length;

  return {
    isAnyLoading: loadingCount > 0,
    isAllLoading: loadingCount === loadingStates.length,
    loadingCount,
    loadingKeys: Object.keys(states).filter((key) => states[key]),
  };
}

/**
 * Hook for debouncing loading state
 * Prevents flickering by delaying the loading indicator
 *
 * @param isLoading - The loading state to debounce
 * @param delay - Delay in milliseconds (default: 200)
 * @returns Debounced loading state
 *
 * @example
 * ```tsx
 * function SearchResults({ query }: { query: string }) {
 *   const { data, isValidating } = useSearchCalls({ query });
 *   const debouncedLoading = useDebouncedLoading(isValidating, 300);
 *
 *   // Only show loading spinner after 300ms
 *   if (debouncedLoading) return <LoadingSpinner />;
 *
 *   return <ResultsList results={data} />;
 * }
 * ```
 */
export function useDebouncedLoading(isLoading: boolean, delay: number = 200): boolean {
  const [debouncedLoading, setDebouncedLoading] = useState(false);

  useEffect(() => {
    if (isLoading) {
      // Show loading state after delay
      const timer = setTimeout(() => {
        setDebouncedLoading(true);
      }, delay);

      return () => clearTimeout(timer);
    } else {
      // Hide loading state immediately
      setDebouncedLoading(false);
    }
  }, [isLoading, delay]);

  return debouncedLoading;
}

/**
 * Hook for progressive loading feedback
 * Shows different messages based on loading duration
 *
 * @example
 * ```tsx
 * function AnalysisLoader() {
 *   const { data, isLoading } = useCallAnalysis(callId);
 *   const loadingMessage = useProgressiveLoading(isLoading, {
 *     initial: 'Loading analysis...',
 *     medium: 'This is taking longer than usual...',
 *     long: 'Almost there...',
 *   });
 *
 *   if (isLoading) return <LoadingSpinner message={loadingMessage} />;
 *
 *   return <AnalysisContent data={data} />;
 * }
 * ```
 */
export function useProgressiveLoading(
  isLoading: boolean,
  messages: {
    initial: string;
    medium?: string;
    long?: string;
  },
  thresholds: {
    medium?: number;
    long?: number;
  } = {}
): string {
  const { medium = 3000, long = 8000 } = thresholds;
  const [message, setMessage] = useState(messages.initial);

  useEffect(() => {
    if (!isLoading) {
      setMessage(messages.initial);
      return;
    }

    setMessage(messages.initial);

    const timers: NodeJS.Timeout[] = [];

    if (messages.medium) {
      timers.push(
        setTimeout(() => {
          setMessage(messages.medium!);
        }, medium)
      );
    }

    if (messages.long) {
      timers.push(
        setTimeout(() => {
          setMessage(messages.long!);
        }, long)
      );
    }

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [isLoading, messages, medium, long]);

  return message;
}

/**
 * Hook for tracking data freshness
 * Useful for showing "last updated" timestamps
 *
 * @example
 * ```tsx
 * function RepDashboard({ email }: { email: string }) {
 *   const { data, mutate } = useRepInsights(email);
 *   const { lastUpdated, isStale, refresh } = useDataFreshness({
 *     onRefresh: mutate,
 *     staleTime: 60000, // 1 minute
 *   });
 *
 *   return (
 *     <div>
 *       <p>Last updated: {lastUpdated?.toLocaleTimeString()}</p>
 *       {isStale && <button onClick={refresh}>Refresh</button>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useDataFreshness(options: {
  onRefresh: () => Promise<any>;
  staleTime?: number;
}) {
  const { onRefresh, staleTime = 60000 } = options;
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isStale, setIsStale] = useState(false);

  useEffect(() => {
    setLastUpdated(new Date());
  }, []);

  useEffect(() => {
    if (!lastUpdated || !staleTime) return;

    const timer = setTimeout(() => {
      setIsStale(true);
    }, staleTime);

    return () => clearTimeout(timer);
  }, [lastUpdated, staleTime]);

  const refresh = useCallback(async () => {
    await onRefresh();
    setLastUpdated(new Date());
    setIsStale(false);
  }, [onRefresh]);

  return {
    lastUpdated,
    isStale,
    refresh,
  };
}
