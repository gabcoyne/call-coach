// Call Analysis Hooks
export {
  useCallAnalysis,
  useCallAnalysisMutation,
  type UseCallAnalysisOptions,
  type UseCallAnalysisReturn,
  type UseCallAnalysisMutationOptions,
  type UseCallAnalysisMutationReturn,
} from "./useCallAnalysis";

// Rep Insights Hooks
export {
  useRepInsights,
  useMultipleRepInsights,
  type UseRepInsightsOptions,
  type UseRepInsightsReturn,
} from "./useRepInsights";

// Call Search Hooks
export {
  useSearchCalls,
  useSearchCallsMutation,
  type UseSearchCallsOptions,
  type UseSearchCallsReturn,
  type UseSearchCallsMutationOptions,
  type UseSearchCallsMutationReturn,
} from "./use-search-calls";

// Optimistic Update Hooks
export {
  useOptimistic,
  useOptimisticList,
  useOptimisticItem,
  type OptimisticUpdateOptions,
} from "./use-optimistic";

// Error Handling Hooks
export {
  useErrorHandling,
  useRetry,
  useErrorMessage,
  type UseErrorHandlingOptions,
  type UseErrorHandlingReturn,
} from "./use-error-handling";

// Loading State Hooks
export {
  useLoadingState,
  useMultipleLoadingStates,
  useDebouncedLoading,
  useProgressiveLoading,
  useDataFreshness,
  type LoadingState,
  type UseLoadingStateOptions,
  type UseLoadingStateReturn,
} from "./use-loading-state";
