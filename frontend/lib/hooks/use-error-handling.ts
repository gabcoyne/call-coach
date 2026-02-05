/**
 * Error Handling Utilities for SWR
 *
 * Provides reusable error handling patterns and error boundary integration.
 */

import { useState, useEffect, useCallback } from "react";
import { SWRError, getErrorMessage, isAuthError, isNotFoundError, isServerError } from "../swr-config";

/**
 * Options for error handling hook
 */
export interface UseErrorHandlingOptions {
  /**
   * Callback when an error occurs
   */
  onError?: (error: SWRError) => void;

  /**
   * Callback when an auth error occurs (401/403)
   */
  onAuthError?: (error: SWRError) => void;

  /**
   * Callback when a not found error occurs (404)
   */
  onNotFoundError?: (error: SWRError) => void;

  /**
   * Callback when a server error occurs (5xx)
   */
  onServerError?: (error: SWRError) => void;

  /**
   * Whether to automatically clear errors after a timeout
   */
  autoClear?: boolean;

  /**
   * Timeout in milliseconds to auto-clear errors (default: 5000)
   */
  autoClearTimeout?: number;
}

/**
 * Return type for error handling hook
 */
export interface UseErrorHandlingReturn {
  /**
   * The formatted error message
   */
  errorMessage: string | null;

  /**
   * The raw error object
   */
  error: SWRError | null;

  /**
   * Whether there is an error
   */
  hasError: boolean;

  /**
   * Whether the error is an auth error (401/403)
   */
  isAuthError: boolean;

  /**
   * Whether the error is a not found error (404)
   */
  isNotFoundError: boolean;

  /**
   * Whether the error is a server error (5xx)
   */
  isServerError: boolean;

  /**
   * Clear the error state
   */
  clearError: () => void;

  /**
   * Set a new error
   */
  setError: (error: SWRError | null) => void;
}

/**
 * Hook for managing error state with automatic error type detection
 *
 * @param swrError - The error from SWR hook
 * @param options - Error handling options
 * @returns Error state and handlers
 *
 * @example
 * ```tsx
 * function CallAnalysisView({ callId }: { callId: string }) {
 *   const { data, error: swrError } = useCallAnalysis(callId);
 *   const { errorMessage, isAuthError, clearError } = useErrorHandling(swrError, {
 *     onAuthError: () => {
 *       // Redirect to login
 *       window.location.href = '/sign-in';
 *     },
 *     autoClear: true,
 *   });
 *
 *   if (isAuthError) {
 *     return <div>Please sign in to view this analysis.</div>;
 *   }
 *
 *   if (errorMessage) {
 *     return (
 *       <div className="error-banner">
 *         {errorMessage}
 *         <button onClick={clearError}>Dismiss</button>
 *       </div>
 *     );
 *   }
 *
 *   return <div>{data && <AnalysisContent data={data} />}</div>;
 * }
 * ```
 */
export function useErrorHandling(
  swrError: SWRError | undefined,
  options: UseErrorHandlingOptions = {}
): UseErrorHandlingReturn {
  const {
    onError,
    onAuthError,
    onNotFoundError,
    onServerError,
    autoClear = false,
    autoClearTimeout = 5000,
  } = options;

  const [error, setError] = useState<SWRError | null>(swrError || null);

  // Update error when SWR error changes
  useEffect(() => {
    if (swrError) {
      setError(swrError);
    }
  }, [swrError]);

  // Execute error callbacks
  useEffect(() => {
    if (!error) return;

    onError?.(error);

    if (isAuthError(error)) {
      onAuthError?.(error);
    } else if (isNotFoundError(error)) {
      onNotFoundError?.(error);
    } else if (isServerError(error)) {
      onServerError?.(error);
    }
  }, [error, onError, onAuthError, onNotFoundError, onServerError]);

  // Auto-clear error after timeout
  useEffect(() => {
    if (!error || !autoClear) return;

    const timer = setTimeout(() => {
      setError(null);
    }, autoClearTimeout);

    return () => clearTimeout(timer);
  }, [error, autoClear, autoClearTimeout]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    errorMessage: error ? getErrorMessage(error) : null,
    error,
    hasError: error !== null,
    isAuthError: error ? isAuthError(error) : false,
    isNotFoundError: error ? isNotFoundError(error) : false,
    isServerError: error ? isServerError(error) : false,
    clearError,
    setError,
  };
}

/**
 * Hook for managing retry logic with exponential backoff
 *
 * @example
 * ```tsx
 * function CallAnalysisView({ callId }: { callId: string }) {
 *   const { data, error, mutate } = useCallAnalysis(callId);
 *   const { retry, isRetrying, retryCount, canRetry } = useRetry({
 *     maxRetries: 3,
 *     onRetry: mutate,
 *   });
 *
 *   if (error) {
 *     return (
 *       <div>
 *         <p>Error loading analysis: {error.message}</p>
 *         {canRetry && (
 *           <button onClick={retry} disabled={isRetrying}>
 *             {isRetrying ? 'Retrying...' : `Retry (${retryCount}/3)`}
 *           </button>
 *         )}
 *       </div>
 *     );
 *   }
 *
 *   return <div>{data && <AnalysisContent data={data} />}</div>;
 * }
 * ```
 */
export function useRetry(options: {
  maxRetries?: number;
  onRetry: () => Promise<any>;
  baseDelay?: number;
}) {
  const { maxRetries = 3, onRetry, baseDelay = 1000 } = options;
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const retry = useCallback(async () => {
    if (retryCount >= maxRetries) return;

    setIsRetrying(true);

    // Exponential backoff
    const delay = baseDelay * Math.pow(2, retryCount);
    await new Promise((resolve) => setTimeout(resolve, delay));

    try {
      await onRetry();
      setRetryCount(0);
    } catch (error) {
      setRetryCount((count) => count + 1);
    } finally {
      setIsRetrying(false);
    }
  }, [retryCount, maxRetries, onRetry, baseDelay]);

  const reset = useCallback(() => {
    setRetryCount(0);
    setIsRetrying(false);
  }, []);

  return {
    retry,
    reset,
    isRetrying,
    retryCount,
    canRetry: retryCount < maxRetries,
  };
}

/**
 * Hook for displaying user-friendly error messages
 */
export function useErrorMessage(error: SWRError | undefined): string | null {
  if (!error) return null;

  // Custom error messages based on status code
  switch (error.status) {
    case 400:
      return "Invalid request. Please check your input and try again.";
    case 401:
      return "You need to sign in to access this content.";
    case 403:
      return "You don't have permission to access this content.";
    case 404:
      return "The requested resource was not found.";
    case 429:
      return "Too many requests. Please wait a moment and try again.";
    case 500:
      return "A server error occurred. Our team has been notified.";
    case 503:
      return "Service temporarily unavailable. Please try again later.";
    default:
      return getErrorMessage(error);
  }
}
