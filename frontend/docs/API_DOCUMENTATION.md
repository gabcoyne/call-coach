# API Documentation

Complete API reference for the Gong Call Coaching frontend API endpoints.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [POST /api/coaching/analyze-call](#post-apicoachinganalyze-call)
  - [POST /api/coaching/rep-insights](#post-apicoachingrep-insights)
  - [POST /api/coaching/search-calls](#post-apicoachingsearch-calls)
- [Type Definitions](#type-definitions)

## Overview

The frontend provides REST API endpoints that serve as a bridge to the FastMCP backend server. All endpoints:

- Use POST method with JSON request bodies
- Require Clerk authentication
- Enforce role-based access control (RBAC)
- Include rate limiting
- Return JSON responses
- Support request/response logging

**Base URL**: `http://localhost:3000` (development) or your deployed domain

**Content-Type**: `application/json`

## Authentication

All API endpoints require authentication via Clerk. The authentication is handled automatically by the `withAuth` middleware.

### Request Headers

Clerk automatically includes authentication cookies when making requests from the Next.js app. No additional headers are required when using the built-in SWR hooks.

### Authorization

Access control is enforced at two levels:

1. **Authentication**: User must be signed in (enforced by middleware)
2. **Authorization**: User must have permission to access the requested resource (enforced by RBAC)

**Roles**:
- `manager`: Can access all reps' data and team insights
- `rep`: Can only access their own data

## Rate Limiting

Rate limits are enforced per user and per endpoint to prevent abuse.

**Default Limits**:
- `analyze-call`: 60 requests per hour per user
- `rep-insights`: 120 requests per hour per user
- `search-calls`: 180 requests per hour per user

**Rate Limit Headers** (included in all responses):
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1707180000
```

**Rate Limit Exceeded Response** (HTTP 429):
```json
{
  "error": "Rate limit exceeded"
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Brief error message",
  "message": "Detailed error description (optional)",
  "details": {
    "field": ["validation error details"]
  }
}
```

### HTTP Status Codes

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions (RBAC failure)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server or backend error

### Common Error Scenarios

**Authentication Required**:
```json
{
  "error": "Unauthorized",
  "message": "You must be signed in to access this resource"
}
```

**RBAC Forbidden**:
```json
{
  "error": "Forbidden: You can only access your own insights"
}
```

**Validation Error**:
```json
{
  "error": "Invalid request parameters",
  "details": {
    "rep_email": ["Invalid email address"],
    "time_period": ["Invalid enum value. Expected 'last_7_days' | 'last_30_days' | ..."]
  }
}
```

## Endpoints

### POST /api/coaching/analyze-call

Analyze a specific Gong call and return coaching insights across multiple dimensions.

#### Request Body

```typescript
{
  call_id: string;                    // Required: Gong call ID
  dimensions?: string[];              // Optional: Specific dimensions to analyze
  use_cache?: boolean;                // Optional: Use cached analysis (default: true)
  include_transcript_snippets?: boolean;  // Optional: Include transcript examples (default: true)
  force_reanalysis?: boolean;         // Optional: Force fresh analysis (default: false)
}
```

**Validation Rules**:
- `call_id`: Required, non-empty string
- `dimensions`: Optional array of valid dimension names
- Booleans default to `true` for cache and snippets, `false` for force

**Valid Dimensions**:
- `product_knowledge`
- `discovery`
- `objection_handling`
- `engagement`

#### Example Request

```json
{
  "call_id": "8123456789012345678",
  "dimensions": ["product_knowledge", "discovery"],
  "use_cache": true,
  "include_transcript_snippets": true
}
```

#### Response (HTTP 200)

```typescript
{
  call_metadata: {
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
  };
  rep_analyzed: {
    name: string;
    email: string | null;
    role: string | null;
  } | null;
  scores: {
    product_knowledge?: number | null;  // 0-100
    discovery?: number | null;          // 0-100
    objection_handling?: number | null; // 0-100
    engagement?: number | null;         // 0-100
    overall: number;                    // 0-100
  };
  strengths: string[];                  // Key strengths identified
  areas_for_improvement: string[];      // Areas needing improvement
  specific_examples: {
    good: string[];                     // Positive examples from transcript
    needs_work: string[];               // Examples needing improvement
  } | null;
  action_items: string[];               // Concrete action items for rep
  dimension_details: {
    [dimension: string]: {
      score: number | null;
      strengths?: string[];
      areas_for_improvement?: string[];
      specific_examples?: {
        good: string[];
        needs_work: string[];
      };
      action_items?: string[];
      error?: string;
    };
  };
  comparison_to_average: Array<{
    metric: string;
    rep_score: number;
    team_average: number;
    difference: number;
    percentile: number;
    sample_size: number;
  }>;
}
```

#### Authorization

- **Managers**: Can analyze any call
- **Reps**: Can only analyze calls where they are the primary rep
- Verified by checking `rep_analyzed.email` against authenticated user

#### Example Usage with SWR

```typescript
import { useCallAnalysis } from '@/lib/hooks/use-call-analysis';

function CallViewer({ callId }: { callId: string }) {
  const { data, error, isLoading } = useCallAnalysis(callId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>Overall Score: {data.scores.overall}</div>;
}
```

---

### POST /api/coaching/rep-insights

Get performance trends and coaching history for a specific sales rep over a time period.

#### Request Body

```typescript
{
  rep_email: string;      // Required: Rep's email address
  time_period?: string;   // Optional: Time period for analysis (default: 'last_30_days')
  product_filter?: string; // Optional: Filter by product (default: both)
}
```

**Validation Rules**:
- `rep_email`: Required, valid email format
- `time_period`: Optional enum value
- `product_filter`: Optional enum value

**Valid Time Periods**:
- `last_7_days`
- `last_30_days`
- `last_quarter`
- `last_year`
- `all_time`

**Valid Product Filters**:
- `prefect`
- `horizon`
- `both`

#### Example Request

```json
{
  "rep_email": "john.doe@prefect.io",
  "time_period": "last_30_days",
  "product_filter": "both"
}
```

#### Response (HTTP 200)

```typescript
{
  rep_info: {
    name: string;
    email: string;
    role: string;
    calls_analyzed: number;
    date_range: {
      start: string;        // ISO 8601 date
      end: string;          // ISO 8601 date
      period: string;
    };
    product_filter: string | null;
  };
  score_trends: {
    [dimension: string]: {
      dates: string[];      // Array of ISO dates
      scores: number[];     // Corresponding scores (0-100)
      call_counts: number[]; // Number of calls per date
    };
  };
  skill_gaps: Array<{
    area: string;
    current_score: number;
    target_score: number;
    gap: number;
    sample_size: number;
    priority: 'high' | 'medium' | 'low';
  }>;
  improvement_areas: Array<{
    area: string;
    recent_score: number;
    older_score: number;
    change: number;
    trend: 'improving' | 'declining' | 'stable';
  }>;
  recent_wins: string[];    // Notable achievements
  coaching_plan: string;    // Personalized coaching recommendations
}
```

#### Authorization

- **Managers**: Can request insights for any rep
- **Reps**: Can only request their own insights (verified by email match)

#### Example Usage with SWR

```typescript
import { useRepInsights } from '@/lib/hooks/use-rep-insights';

function RepDashboard({ repEmail }: { repEmail: string }) {
  const { data, error, isLoading } = useRepInsights(
    repEmail,
    'last_30_days',
    'both'
  );

  if (isLoading) return <div>Loading insights...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>{data.rep_info.name}</h2>
      <p>Calls analyzed: {data.rep_info.calls_analyzed}</p>
    </div>
  );
}
```

---

### POST /api/coaching/search-calls

Search for calls matching specific criteria with advanced filtering and sorting.

#### Request Body

```typescript
{
  rep_email?: string;               // Optional: Filter by rep email
  product?: string;                 // Optional: Filter by product
  call_type?: string;               // Optional: Filter by call type
  date_range?: {
    start: string;                  // ISO 8601 datetime
    end: string;                    // ISO 8601 datetime
  };
  min_score?: number;               // Optional: Minimum overall score (0-100)
  max_score?: number;               // Optional: Maximum overall score (0-100)
  has_objection_type?: string;      // Optional: Filter by objection type
  topics?: string[];                // Optional: Filter by topics/keywords
  limit?: number;                   // Optional: Max results (default: 20, max: 100)
}
```

**Validation Rules**:
- All fields are optional
- Dates must be valid ISO 8601 datetime strings
- Scores must be integers between 0-100
- Limit must be between 1-100

**Valid Products**:
- `prefect`
- `horizon`
- `both`

**Valid Call Types**:
- `discovery`
- `demo`
- `technical_deep_dive`
- `negotiation`

**Valid Objection Types**:
- `pricing`
- `timing`
- `technical`
- `competitor`

#### Example Request

```json
{
  "rep_email": "john.doe@prefect.io",
  "product": "prefect",
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "min_score": 70,
  "call_type": "discovery",
  "limit": 20
}
```

#### Response (HTTP 200)

```typescript
Array<{
  call_id: string;
  title: string;
  date: string | null;          // ISO 8601 date
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  overall_score: number | null; // 0-100
  customer_names: string[];
  prefect_reps: string[];
}>
```

#### Authorization

- **Managers**: Can search all calls
- **Reps**: Automatically filtered to only their calls (even if no `rep_email` specified)

#### Example Usage with SWR

```typescript
import { useSearchCalls } from '@/lib/hooks/use-search-calls';

function CallSearch() {
  const { data, error, isLoading, mutate } = useSearchCalls({
    product: 'prefect',
    min_score: 70,
    call_type: 'discovery',
    limit: 20
  });

  if (isLoading) return <div>Searching...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.map(call => (
        <div key={call.call_id}>
          <h3>{call.title}</h3>
          <p>Score: {call.overall_score}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Type Definitions

### Complete TypeScript Types

All request and response types are defined in `types/coaching.ts` with Zod validation schemas.

```typescript
// Import types
import type {
  AnalyzeCallRequest,
  AnalyzeCallResponse,
  RepInsightsRequest,
  RepInsightsResponse,
  SearchCallsRequest,
  SearchCallsResponse,
} from '@/types/coaching';

// Import validation schemas
import {
  analyzeCallRequestSchema,
  repInsightsRequestSchema,
  searchCallsRequestSchema,
} from '@/types/coaching';
```

### Runtime Validation

All requests are validated using Zod schemas:

```typescript
// Example: Validate analyze-call request
const validationResult = analyzeCallRequestSchema.safeParse(requestBody);

if (!validationResult.success) {
  // Returns 400 with validation errors
  return apiError(
    'Invalid request parameters',
    400,
    validationResult.error.format()
  );
}

const params = validationResult.data; // Type-safe validated data
```

## Testing

### Local Testing

See [API_TESTING.md](../API_TESTING.md) for comprehensive testing guide with curl examples.

### Using Thunder Client or Postman

1. Start the Next.js dev server: `npm run dev`
2. Sign in to the application in a browser
3. Copy the Clerk session cookie from browser DevTools
4. Add cookie to API client requests

### Example curl Request

```bash
# Analyze a call
curl -X POST http://localhost:3000/api/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -H "Cookie: __session=your_clerk_session_cookie" \
  -d '{
    "call_id": "8123456789012345678",
    "dimensions": ["product_knowledge"],
    "use_cache": true
  }'
```

## Best Practices

### Client-Side Usage

1. **Use SWR hooks**: Don't make direct fetch calls; use provided hooks
2. **Handle loading states**: Always show loading UI while fetching
3. **Handle errors gracefully**: Display user-friendly error messages
4. **Implement retry logic**: SWR handles retries automatically
5. **Use optimistic updates**: Update UI immediately, revalidate in background

### Performance

1. **Enable caching**: Use `use_cache: true` for analyze-call when possible
2. **Limit result sets**: Use appropriate `limit` values for search-calls
3. **Debounce search inputs**: Prevent excessive API calls on user input
4. **Prefetch data**: Use `<Link prefetch>` for navigation

### Security

1. **Never bypass RBAC**: Don't manipulate requests to access unauthorized data
2. **Validate on server**: Client validation is UX only; server enforces rules
3. **Don't expose sensitive data**: Check what data is included in responses
4. **Respect rate limits**: Implement client-side throttling if needed

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common API issues and solutions.

## Additional Resources

- [Clerk Session Management](https://clerk.com/docs/backend-requests/handling/nodejs)
- [Next.js API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [Zod Validation](https://zod.dev)
- [SWR Documentation](https://swr.vercel.app)
