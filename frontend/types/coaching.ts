/**
 * TypeScript Types and Zod Schemas for Coaching API
 *
 * Provides type-safe interfaces and runtime validation for all coaching API endpoints.
 */

import { z } from "zod";

/**
 * Zod Schemas for Request Validation
 */

// Analyze Call Request
export const analyzeCallRequestSchema = z.object({
  call_id: z.string().min(1, "Call ID is required"),
  dimensions: z
    .array(z.enum(["product_knowledge", "discovery", "objection_handling", "engagement"]))
    .optional(),
  use_cache: z.boolean().optional().default(true),
  include_transcript_snippets: z.boolean().optional().default(true),
  force_reanalysis: z.boolean().optional().default(false),
});

export type AnalyzeCallRequest = z.infer<typeof analyzeCallRequestSchema>;

// Rep Insights Request
export const repInsightsRequestSchema = z.object({
  rep_email: z.string().email("Valid email address required"),
  time_period: z
    .enum(["last_7_days", "last_30_days", "last_quarter", "last_year", "all_time"])
    .optional()
    .default("last_30_days"),
  product_filter: z.enum(["prefect", "horizon", "both"]).optional(),
});

export type RepInsightsRequest = z.infer<typeof repInsightsRequestSchema>;

// Search Calls Request
export const searchCallsRequestSchema = z.object({
  rep_email: z.string().email().optional(),
  product: z.enum(["prefect", "horizon", "both"]).optional(),
  call_type: z.enum(["discovery", "demo", "technical_deep_dive", "negotiation"]).optional(),
  date_range: z
    .object({
      start: z.string().datetime(),
      end: z.string().datetime(),
    })
    .optional(),
  min_score: z.number().int().min(0).max(100).optional(),
  max_score: z.number().int().min(0).max(100).optional(),
  has_objection_type: z.enum(["pricing", "timing", "technical", "competitor"]).optional(),
  topics: z.array(z.string()).optional(),
  limit: z.number().int().min(1).max(100).optional().default(20),
});

export type SearchCallsRequest = z.infer<typeof searchCallsRequestSchema>;

/**
 * TypeScript Types for API Responses
 */

export interface CallMetadata {
  id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  participants: CallParticipant[];
  gong_url?: string | null;
  recording_url?: string | null;
}

export interface CallParticipant {
  name: string;
  email: string;
  role: string;
  is_internal: boolean;
  talk_time_seconds: number;
}

export interface RepAnalyzed {
  name: string;
  email: string | null;
  role: string | null;
  evaluated_as_role?: "ae" | "se" | "csm"; // Role-specific rubric used for evaluation
}

export interface DimensionScores {
  product_knowledge?: number | null;
  discovery?: number | null;
  objection_handling?: number | null;
  engagement?: number | null;
  overall: number;
}

export interface SpecificExamples {
  good: string[];
  needs_work: string[];
}

export interface ComparisonToAverage {
  metric: string;
  rep_score: number;
  team_average: number;
  difference: number;
  percentile: number;
  sample_size: number;
}

export interface TranscriptSegment {
  speaker: string;
  timestamp_seconds: number;
  text: string;
}

export interface AnalyzeCallResponse {
  call_metadata: CallMetadata;
  rep_analyzed: RepAnalyzed | null;
  scores: DimensionScores;
  strengths: string[];
  areas_for_improvement: string[];
  specific_examples: SpecificExamples | null;
  action_items: string[];
  dimension_details: Record<string, DimensionAnalysis>;
  comparison_to_average: ComparisonToAverage[];
  transcript?: TranscriptSegment[] | null;
}

export interface DimensionAnalysis {
  score: number | null;
  strengths?: string[];
  areas_for_improvement?: string[];
  specific_examples?: SpecificExamples;
  action_items?: string[];
  error?: string;
}

export interface RepInfo {
  name: string;
  email: string;
  role: string;
  calls_analyzed: number;
  date_range: {
    start: string;
    end: string;
    period: string;
  };
  product_filter: string | null;
}

export interface ScoreTrendData {
  dates: string[];
  scores: number[];
  call_counts: number[];
}

export interface ScoreTrends {
  [dimension: string]: ScoreTrendData;
}

export interface SkillGap {
  area: string;
  current_score: number;
  target_score: number;
  gap: number;
  sample_size: number;
  priority: "high" | "medium" | "low";
}

export interface ImprovementArea {
  area: string;
  recent_score: number;
  older_score: number;
  change: number;
  trend: "improving" | "declining" | "stable";
}

export interface RepInsightsResponse {
  rep_info: RepInfo;
  score_trends: ScoreTrends;
  skill_gaps: SkillGap[];
  improvement_areas: ImprovementArea[];
  recent_wins: string[];
  coaching_plan: string;
}

export interface CallSearchResult {
  call_id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  overall_score: number | null;
  customer_names: string[];
  prefect_reps: string[];
}

export type SearchCallsResponse = CallSearchResult[];

/**
 * Feed Types
 */

export type FeedItemType = "call_analysis" | "team_insight" | "highlight" | "milestone";
export type FeedTimeFilter = "today" | "this_week" | "this_month" | "custom";

export interface FeedItem {
  id: string;
  type: FeedItemType;
  timestamp: string;
  title: string;
  description: string;
  metadata: FeedItemMetadata;
  is_bookmarked?: boolean;
  is_dismissed?: boolean;
  is_new?: boolean;
}

export interface FeedItemMetadata {
  call_id?: string;
  call_title?: string;
  rep_email?: string;
  rep_name?: string;
  score?: number;
  dimension?: string;
  team_size?: number;
  team_average?: number;
  improvement_percentage?: number;
  milestone_type?: string;
  highlight_snippet?: string;
  action_items?: string[];
}

export interface TeamInsight {
  id: string;
  type: "trend" | "comparison" | "achievement";
  title: string;
  description: string;
  metric: string;
  value: number;
  change: number;
  trend: "up" | "down" | "stable";
  team_size: number;
  period: string;
}

export interface CoachingHighlight {
  id: string;
  call_id: string;
  call_title: string;
  rep_name: string;
  rep_email: string;
  timestamp: string;
  dimension: string;
  score: number;
  snippet: string;
  context: string;
  why_exemplary: string;
}

export const feedItemTypeFilterSchema = z.enum([
  "all",
  "call_analysis",
  "team_insight",
  "highlight",
  "milestone",
]);
export const feedTimeFilterSchema = z.enum(["today", "this_week", "this_month", "custom"]);

export const feedRequestSchema = z.object({
  type_filter: feedItemTypeFilterSchema.optional(),
  time_filter: feedTimeFilterSchema.optional(),
  start_date: z.string().datetime().optional(),
  end_date: z.string().datetime().optional(),
  limit: z.number().int().min(1).max(50).optional().default(20),
  offset: z.number().int().min(0).optional().default(0),
  include_dismissed: z.boolean().optional().default(false),
});

export type FeedRequest = z.infer<typeof feedRequestSchema>;

export interface FeedResponse {
  items: FeedItem[];
  team_insights: TeamInsight[];
  highlights: CoachingHighlight[];
  total_count: number;
  has_more: boolean;
  new_items_count: number;
}

/**
 * Feedback Types
 */
export type FeedbackType =
  | "accurate"
  | "inaccurate"
  | "missing_context"
  | "helpful"
  | "not_helpful";

export interface SubmitFeedbackRequest {
  feedback_type: FeedbackType;
  feedback_text?: string | null;
}

export interface CoachingFeedback {
  id: string;
  coaching_session_id: string;
  rep_id: string;
  feedback_type: FeedbackType;
  feedback_text: string | null;
  created_at: string;
}

export interface FeedbackStats {
  total_feedback: number;
  accurate_count: number;
  inaccurate_count: number;
  missing_context_count: number;
  helpful_count: number;
  not_helpful_count: number;
  accuracy_rate: number;
  helpfulness_rate: number;
}

export interface QualityIssue {
  type: string;
  severity: "high" | "medium" | "low";
  message: string;
  metric: number;
  affected_count: number;
}

export interface FeedbackStatsResponse {
  overall_stats: FeedbackStats;
  dimension_stats: Array<{
    dimension: string;
    total_feedback: number;
    accuracy_rate: number;
    helpfulness_rate: number;
  }>;
  quality_issues: QualityIssue[];
  time_period: string;
}

/**
 * Error Response
 */
export interface APIErrorResponse {
  error: string;
  message?: string;
  details?: unknown;
}
