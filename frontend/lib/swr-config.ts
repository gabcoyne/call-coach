/**
 * SWR Global Configuration
 *
 * Provides centralized configuration for SWR hooks including:
 * - Revalidation settings
 * - Error retry logic with exponential backoff
 * - Default fetcher with authentication
 * - Error handling utilities
 */

import { SWRConfiguration } from "swr";

/**
 * Default fetcher function with authentication
 * Uses Next.js API routes which handle Clerk session automatically
 */
async function fetcher<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    credentials: "include", // Include cookies for Clerk session
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error: any = new Error("An error occurred while fetching the data.");
    error.status = response.status;

    try {
      const errorData = await response.json();
      error.info = errorData;
      error.message = errorData.error || errorData.message || error.message;
    } catch {
      // If error response is not JSON, use default message
    }

    throw error;
  }

  return response.json();
}

/**
 * Global SWR configuration with optimized revalidation and retry settings
 */
export const swrConfig: SWRConfiguration = {
  // Default fetcher
  fetcher,

  // Revalidation settings
  revalidateOnFocus: true, // Revalidate when window regains focus
  revalidateOnReconnect: true, // Revalidate when network reconnects
  revalidateIfStale: true, // Revalidate if data is stale
  dedupingInterval: 2000, // Dedupe requests within 2 seconds

  // Focus revalidation settings
  focusThrottleInterval: 5000, // Throttle focus revalidation to every 5 seconds

  // Error retry configuration with exponential backoff
  shouldRetryOnError: true,
  errorRetryInterval: 5000, // Base retry interval of 5 seconds
  errorRetryCount: 3, // Maximum 3 retries

  // Custom error retry with exponential backoff
  onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
    // Don't retry on 404
    if (error.status === 404) return;

    // Don't retry on 401 (authentication error)
    if (error.status === 401) return;

    // Don't retry on 403 (authorization error)
    if (error.status === 403) return;

    // Max 3 retries
    if (retryCount >= 3) return;

    // Exponential backoff: 5s, 10s, 20s
    const timeout = 5000 * Math.pow(2, retryCount);

    setTimeout(() => revalidate({ retryCount }), timeout);
  },

  // Loading timeout (30 seconds)
  loadingTimeout: 30000,

  // Keep previous data while revalidating
  keepPreviousData: true,
};

/**
 * Utility function to build API URL with query parameters
 */
export function buildApiUrl(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined>
): string {
  // Use window.location.origin on client, fallback to relative URL on server
  const base = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";
  const url = new URL(endpoint, base);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return url.toString();
}

/**
 * Error handling utilities for SWR hooks
 */

export interface SWRError {
  status?: number;
  info?: any;
  message: string;
}

export function isSWRError(error: unknown): error is SWRError {
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof (error as any).message === "string"
  );
}

export function getErrorMessage(error: unknown): string {
  if (isSWRError(error)) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unknown error occurred";
}

export function isAuthError(error: unknown): boolean {
  if (isSWRError(error)) {
    return error.status === 401 || error.status === 403;
  }
  return false;
}

export function isNotFoundError(error: unknown): boolean {
  if (isSWRError(error)) {
    return error.status === 404;
  }
  return false;
}

export function isServerError(error: unknown): boolean {
  if (isSWRError(error)) {
    return error.status !== undefined && error.status >= 500;
  }
  return false;
}

/**
 * Loading state utilities
 */

export interface LoadingState<T> {
  data?: T;
  error?: SWRError;
  isLoading: boolean;
  isValidating: boolean;
}

export function isInitialLoading<T>(state: LoadingState<T>): boolean {
  return !state.data && !state.error && state.isLoading;
}

export function hasData<T>(state: LoadingState<T>): state is LoadingState<T> & { data: T } {
  return state.data !== undefined;
}

export function hasError<T>(
  state: LoadingState<T>
): state is LoadingState<T> & { error: SWRError } {
  return state.error !== undefined;
}
