/**
 * MCP Backend Client
 *
 * HTTP client wrapper for communicating with the FastMCP backend server.
 * The backend exposes coaching tools as an MCP server that we interact with via HTTP.
 */

const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || 'http://localhost:8000';

/**
 * Base error class for MCP client errors
 */
export class MCPClientError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: unknown
  ) {
    super(message);
    this.name = 'MCPClientError';
  }
}

/**
 * Retry configuration for exponential backoff
 */
interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelayMs: 1000,
  maxDelayMs: 10000,
  backoffMultiplier: 2,
};

/**
 * Sleep helper for retry delays
 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Calculate delay for exponential backoff
 */
function calculateBackoffDelay(
  attempt: number,
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): number {
  const delay = config.initialDelayMs * Math.pow(config.backoffMultiplier, attempt);
  return Math.min(delay, config.maxDelayMs);
}

/**
 * Check if an error is retryable (network errors, 5xx, rate limits)
 */
function isRetryableError(error: unknown): boolean {
  if (error instanceof MCPClientError) {
    const status = error.statusCode;
    // Retry on server errors (5xx) and rate limits (429)
    return !status || status >= 500 || status === 429;
  }
  // Retry on network errors
  return true;
}

/**
 * Make HTTP request with retry logic
 */
async function fetchWithRetry<T>(
  url: string,
  options: RequestInit = {},
  retryConfig: RetryConfig = DEFAULT_RETRY_CONFIG
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Handle non-OK responses
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage: string;

        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.error || errorJson.message || errorText;
        } catch {
          errorMessage = errorText || `HTTP ${response.status} error`;
        }

        throw new MCPClientError(
          errorMessage,
          response.status
        );
      }

      // Parse and return successful response
      return await response.json();

    } catch (error) {
      lastError = error;

      // Don't retry if this is the last attempt or error is not retryable
      if (attempt === retryConfig.maxRetries || !isRetryableError(error)) {
        break;
      }

      // Wait before retrying
      const delay = calculateBackoffDelay(attempt, retryConfig);
      console.warn(
        `MCP request failed (attempt ${attempt + 1}/${retryConfig.maxRetries + 1}), ` +
        `retrying in ${delay}ms:`,
        error
      );
      await sleep(delay);
    }
  }

  // All retries exhausted
  throw lastError instanceof MCPClientError
    ? lastError
    : new MCPClientError(
        'MCP backend request failed after retries',
        undefined,
        lastError
      );
}

/**
 * MCP Backend Client
 *
 * Provides methods to call the FastMCP backend tools.
 */
export class MCPClient {
  private baseUrl: string;
  private retryConfig: RetryConfig;

  constructor(
    baseUrl: string = MCP_BACKEND_URL,
    retryConfig: Partial<RetryConfig> = {}
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
  }

  /**
   * Call a tool on the MCP backend
   */
  private async callTool<T>(
    toolName: string,
    params: Record<string, unknown>
  ): Promise<T> {
    const url = `${this.baseUrl}/tools/${toolName}`;

    return fetchWithRetry<T>(
      url,
      {
        method: 'POST',
        body: JSON.stringify(params),
      },
      this.retryConfig
    );
  }

  /**
   * Analyze a specific call with coaching insights
   */
  async analyzeCall(params: {
    call_id: string;
    dimensions?: string[];
    use_cache?: boolean;
    include_transcript_snippets?: boolean;
    force_reanalysis?: boolean;
  }): Promise<AnalyzeCallResponse> {
    return this.callTool<AnalyzeCallResponse>('analyze_call', params);
  }

  /**
   * Get performance insights for a sales rep
   */
  async getRepInsights(params: {
    rep_email: string;
    time_period?: string;
    product_filter?: string;
  }): Promise<RepInsightsResponse> {
    return this.callTool<RepInsightsResponse>('get_rep_insights', params);
  }

  /**
   * Search for calls matching criteria
   */
  async searchCalls(params: {
    rep_email?: string;
    product?: string;
    call_type?: string;
    date_range?: { start: string; end: string };
    min_score?: number;
    max_score?: number;
    has_objection_type?: string;
    topics?: string[];
    limit?: number;
  }): Promise<SearchCallsResponse> {
    return this.callTool<SearchCallsResponse>('search_calls', params);
  }
}

/**
 * TypeScript interfaces for API responses
 * These match the MCP backend tool return types
 */

export interface CallMetadata {
  id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  participants: Array<{
    name: string;
    email: string;
    role: string;
    is_internal: boolean;
    talk_time_seconds: number;
  }>;
}

export interface RepAnalyzed {
  name: string;
  email: string | null;
  role: string | null;
}

export interface Scores {
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

export interface AnalyzeCallResponse {
  call_metadata: CallMetadata;
  rep_analyzed: RepAnalyzed | null;
  scores: Scores;
  strengths: string[];
  areas_for_improvement: string[];
  specific_examples: SpecificExamples | null;
  action_items: string[];
  dimension_details: Record<string, unknown>;
  comparison_to_average: ComparisonToAverage[];
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

export interface ScoreTrends {
  [dimension: string]: {
    dates: string[];
    scores: number[];
    call_counts: number[];
  };
}

export interface SkillGap {
  area: string;
  current_score: number;
  target_score: number;
  gap: number;
  sample_size: number;
  priority: 'high' | 'medium' | 'low';
}

export interface ImprovementArea {
  area: string;
  recent_score: number;
  older_score: number;
  change: number;
  trend: 'improving' | 'declining' | 'stable';
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
 * Create a singleton instance for use in API routes
 */
export const mcpClient = new MCPClient();
