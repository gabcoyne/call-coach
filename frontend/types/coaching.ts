/**
 * TypeScript Types and Zod Schemas for Coaching API
 *
 * This file contains:
 * - Zod schemas for runtime validation (Request types)
 * - Response types (not auto-generated from backend)
 *
 * Request types are re-exported from @/types/generated for convenience.
 * Response types remain here because FastAPI endpoints return dict[str, Any].
 *
 * To regenerate request types: npm run generate:types
 */

import { z } from "zod";
import type { FiveWinsEvaluation, SupplementaryFrameworks } from "./rubric";

// Re-export generated request types for backward compatibility
export type {
  AnalyzeCallRequest,
  RepInsightsRequest,
  SearchCallsRequest,
  AnalyzeOpportunityRequest,
  LearningInsightsRequest,
  CoachingFeedRequest,
} from "./generated";

/**
 * Zod Schemas for Request Validation
 *
 * These schemas provide runtime validation for API requests.
 * The inferred types match the generated types from OpenAPI.
 */

// Analyze Call Request Schema (runtime validation)
export const analyzeCallRequestSchema = z.object({
  call_id: z.string().min(1, "Call ID is required"),
  dimensions: z
    .array(z.enum(["product_knowledge", "discovery", "objection_handling", "engagement"]))
    .optional(),
  use_cache: z.boolean().optional().default(true),
  include_transcript_snippets: z.boolean().optional().default(true),
  force_reanalysis: z.boolean().optional().default(false),
});

// Rep Insights Request Schema (runtime validation)
export const repInsightsRequestSchema = z.object({
  rep_email: z.string().email("Valid email address required"),
  time_period: z
    .enum(["last_7_days", "last_30_days", "last_quarter", "last_year", "all_time"])
    .optional()
    .default("last_30_days"),
  product_filter: z.enum(["prefect", "horizon", "both"]).optional(),
});

// Search Calls Request Schema (runtime validation)
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
  role: string; // Display role: "Internal" or "External"
  business_role: string | null; // Business role: "ae", "se", "csm", "support", or null
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
  start_time_ms: number;
  text: string;
}

export interface KeyMoment {
  timestamp: number;
  moment_type: "strength" | "improvement";
  summary: string;
  dimension: string;
}

export interface ThematicInsight {
  strengths: string[];
  improvements: string[];
  count: number;
  priority: number;
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

  /**
   * Five Wins Evaluation - Primary coaching framework
   * Evaluates Business, Technical, Security, Commercial, and Legal wins
   */
  five_wins_evaluation?: FiveWinsEvaluation;

  /**
   * Supplementary Frameworks - Additional coaching insights
   * SPICED, Challenger, Sandler frameworks from dimension-specific analysis
   */
  supplementary_frameworks?: SupplementaryFrameworks;

  /**
   * Thematic Insights - Insights grouped by theme instead of dimension
   * Reduces overwhelming granularity by organizing around common themes
   */
  thematic_insights?: Record<string, ThematicInsight>;

  /**
   * Key Moments - Top 10 most impactful moments from the call
   * Concise timestamps with summaries, replacing verbose specific examples
   */
  key_moments?: KeyMoment[];

  /**
   * Filtered Action Items - Concrete, actionable next steps only
   * Filtered to remove vague recommendations like "build repository"
   */
  action_items_filtered?: string[];

  /**
   * Narrative Summary - 2-3 sentence coaching summary (Five Wins Unified)
   * Replaces verbose lists with concise, actionable narrative
   */
  narrative?: string;

  /**
   * Wins Addressed - Map of win name to what was accomplished
   * Part of Five Wins Unified output
   */
  wins_addressed?: Record<string, string>;

  /**
   * Wins Missed - Map of win name to what needs work
   * Part of Five Wins Unified output
   */
  wins_missed?: Record<string, string>;

  /**
   * Primary Action - The ONE most important action for the rep
   * Part of Five Wins Unified output
   */
  primary_action?: PrimaryAction;
}

/**
 * Primary Action - The single most important next step for the rep
 */
export interface PrimaryAction {
  /** Which win this action relates to */
  win: "business" | "technical" | "security" | "commercial" | "legal";

  /** Specific, actionable instruction */
  action: string;

  /** Why this matters, linked to call context */
  context: string;

  /** Call moment that makes this action important */
  related_moment?: CallMoment | null;
}

/**
 * Call Moment - A specific moment in the call to reference
 */
export interface CallMoment {
  /** Timestamp in seconds from call start */
  timestamp_seconds: number;

  /** Who was speaking */
  speaker: string;

  /** Brief summary of what happened */
  summary: string;
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
