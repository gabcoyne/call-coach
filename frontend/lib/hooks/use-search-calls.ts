/**
 * SWR Hook for Call Search
 *
 * Provides reactive data fetching for searching calls with filters.
 * Includes optimistic updates for better UX.
 */

import useSWR from "swr";
import useSWRMutation from "swr/mutation";
import {
  SearchCallsRequest,
  SearchCallsResponse,
  APIErrorResponse,
} from "@/types/coaching";
import { SWRError } from "../swr-config";

/**
 * Fetcher for search calls API
 */
async function searchCallsFetcher(
  url: string,
  filters: SearchCallsRequest
): Promise<SearchCallsResponse> {
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(filters),
  });

  if (!response.ok) {
    const error: any = new Error("Failed to search calls");
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
 * Options for useSearchCalls hook
 */
export interface UseSearchCallsOptions {
  refreshInterval?: number;
  revalidateOnFocus?: boolean;
  enabled?: boolean;
}

/**
 * Return type for useSearchCalls hook
 */
export interface UseSearchCallsReturn {
  data?: SearchCallsResponse;
  error?: SWRError;
  isLoading: boolean;
  isValidating: boolean;
  mutate: (
    data?: SearchCallsResponse | Promise<SearchCallsResponse>,
    opts?: { revalidate?: boolean }
  ) => Promise<SearchCallsResponse | undefined>;
}

/**
 * Hook to search calls with filters
 *
 * @param filters - Search filters (SearchCallsRequest)
 * @param options - SWR configuration options
 * @returns SWR response with search results
 *
 * @example
 * ```tsx
 * function CallSearchResults() {
 *   const [filters, setFilters] = useState<SearchCallsRequest>({
 *     min_score: 70,
 *     limit: 20,
 *   });
 *
 *   const { data, error, isLoading } = useSearchCalls(filters);
 *
 *   if (isLoading) return <div>Searching...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *
 *   return (
 *     <div>
 *       {data?.map((call) => (
 *         <CallCard key={call.call_id} call={call} />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSearchCalls(
  filters: SearchCallsRequest | null,
  options: UseSearchCallsOptions = {}
): UseSearchCallsReturn {
  const {
    refreshInterval,
    revalidateOnFocus = false,
    enabled = true,
  } = options;

  // Create a stable key from filters
  const key =
    filters && enabled ? ["/api/coaching/search-calls", filters] : null;

  const { data, error, isLoading, isValidating, mutate } = useSWR<
    SearchCallsResponse,
    SWRError
  >(
    key,
    ([url, filters]) => searchCallsFetcher(url, filters),
    {
      revalidateOnFocus,
      refreshInterval,
      keepPreviousData: true,
      shouldRetryOnError: (error) => {
        // Only retry on server errors (5xx)
        return error.status !== undefined && error.status >= 500;
      },
    }
  );

  return {
    data,
    error,
    isLoading: !data && !error && enabled,
    isValidating,
    mutate,
  };
}

/**
 * Options for useSearchCallsMutation hook
 */
export interface UseSearchCallsMutationOptions {
  onSuccess?: (data: SearchCallsResponse) => void;
  onError?: (error: SWRError) => void;
}

/**
 * Return type for useSearchCallsMutation hook
 */
export interface UseSearchCallsMutationReturn {
  trigger: (filters: SearchCallsRequest) => Promise<SearchCallsResponse>;
  isMutating: boolean;
  error?: SWRError;
  data?: SearchCallsResponse;
  reset: () => void;
}

/**
 * Custom SWR mutation hook for searching calls on-demand
 * Useful for implementing search forms with manual submit
 *
 * @param options - Optional callbacks for success/error
 * @returns Mutation trigger function with loading/error states
 *
 * @example
 * ```tsx
 * function CallSearchForm() {
 *   const { trigger, isMutating, data } = useSearchCallsMutation({
 *     onSuccess: (results) => {
 *       console.log('Found', results.length, 'calls');
 *     },
 *   });
 *
 *   const handleSubmit = async (filters: SearchCallsRequest) => {
 *     await trigger(filters);
 *   };
 *
 *   return (
 *     <div>
 *       <SearchForm onSubmit={handleSubmit} disabled={isMutating} />
 *       {data && <SearchResults results={data} />}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSearchCallsMutation(
  options: UseSearchCallsMutationOptions = {}
): UseSearchCallsMutationReturn {
  const { onSuccess, onError } = options;

  async function searchCalls(
    url: string,
    { arg }: { arg: SearchCallsRequest }
  ): Promise<SearchCallsResponse> {
    return searchCallsFetcher(url, arg);
  }

  const { trigger, isMutating, error, data, reset } = useSWRMutation<
    SearchCallsResponse,
    SWRError,
    "/api/coaching/search-calls",
    SearchCallsRequest
  >("/api/coaching/search-calls", searchCalls, {
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
