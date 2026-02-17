/**
 * Generated Types Index
 *
 * Re-exports generated types from the OpenAPI schema for convenient importing.
 * This file serves as the single entry point for all generated API types.
 *
 * Usage:
 *   import type { AnalyzeCallRequest, components } from '@/types/generated';
 *
 * To regenerate types:
 *   npm run generate:types
 */

export * from "./api";

// Re-export commonly used types for convenience
export type {
  // Request types (generated from Pydantic models)
  AnalyzeCallRequest,
  RepInsightsRequest,
  SearchCallsRequest,
  AnalyzeOpportunityRequest,
  LearningInsightsRequest,
  CoachingFeedRequest,

  // Path and operation types for typed fetch
  paths,
  operations,
  components,
} from "./api";
