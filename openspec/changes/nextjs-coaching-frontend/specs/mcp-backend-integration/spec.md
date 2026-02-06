## ADDED Requirements

### Requirement: REST API Bridge Architecture

The integration SHALL implement Next.js API routes that proxy MCP tool calls to FastMCP backend using @modelcontextprotocol/sdk.

#### Scenario: API route structure

- **WHEN** frontend needs to call MCP backend
- **THEN** system provides API routes at `/app/api/coaching/[tool]` that accept HTTP requests and proxy to MCP protocol

#### Scenario: MCP SDK client initialization

- **WHEN** API route receives request
- **THEN** system initializes MCP SDK client with stdio or SSE transport to connect to FastMCP server

#### Scenario: Server-side credential management

- **WHEN** API route connects to MCP backend
- **THEN** system uses server-side environment variables for MCP credentials, never exposing them to browser

### Requirement: Analyze Call Endpoint

The integration SHALL provide `/api/coaching/analyze-call` endpoint that proxies to `analyze_call` MCP tool.

#### Scenario: Analyze call request

- **WHEN** frontend POST to `/api/coaching/analyze-call` with `{ callId, dimensions?, useCache?, includeTranscriptSnippets?, forceReanalysis? }`
- **THEN** system calls `analyze_call` MCP tool and returns comprehensive coaching analysis

#### Scenario: Handle analysis errors

- **WHEN** MCP tool returns error (call not found, analysis failed)
- **THEN** system returns appropriate HTTP status (404, 500) with error message

#### Scenario: Cache-aware requests

- **WHEN** frontend requests analysis with `useCache: true`
- **THEN** system passes cache flag to MCP tool to use cached analysis if available

### Requirement: Get Rep Insights Endpoint

The integration SHALL provide `/api/coaching/rep-insights` endpoint that proxies to `get_rep_insights` MCP tool.

#### Scenario: Rep insights request

- **WHEN** frontend GET to `/api/coaching/rep-insights?email=rep@prefect.io&timePeriod=last_30_days&productFilter=prefect`
- **THEN** system calls `get_rep_insights` MCP tool and returns performance trends, skill gaps, and coaching plan

#### Scenario: Time period validation

- **WHEN** frontend requests invalid time period
- **THEN** system returns 400 error with valid options (last_7_days, last_30_days, last_quarter, last_year, all_time)

#### Scenario: RBAC for rep insights

- **WHEN** rep user requests insights for different rep email
- **THEN** system returns 403 Forbidden (reps can only view own insights)

### Requirement: Search Calls Endpoint

The integration SHALL provide `/api/coaching/search-calls` endpoint that proxies to `search_calls` MCP tool.

#### Scenario: Search calls request

- **WHEN** frontend POST to `/api/coaching/search-calls` with filters `{ repEmail?, product?, callType?, dateRange?, minScore?, maxScore?, hasObjectionType?, topics?, limit? }`
- **THEN** system calls `search_calls` MCP tool and returns matching calls with metadata

#### Scenario: Pagination support

- **WHEN** frontend requests more than default limit
- **THEN** system passes limit parameter (max 100) to MCP tool

#### Scenario: Empty search results

- **WHEN** search filters match no calls
- **THEN** system returns empty array with 200 status (not error)

### Requirement: Error Handling and Retries

The integration SHALL implement robust error handling with exponential backoff retries for transient failures.

#### Scenario: Retry on timeout

- **WHEN** MCP backend times out (>30s)
- **THEN** system retries request up to 3 times with exponential backoff (1s, 2s, 4s)

#### Scenario: Circuit breaker on repeated failures

- **WHEN** MCP backend fails 5 consecutive requests
- **THEN** system opens circuit breaker and returns 503 Service Unavailable for 60 seconds before retrying

#### Scenario: Graceful degradation

- **WHEN** MCP backend is unavailable
- **THEN** system returns cached data if available with `X-Cache: STALE` header, otherwise 503 error

### Requirement: Request/Response Transformation

The integration SHALL transform between frontend TypeScript types and MCP tool schemas.

#### Scenario: TypeScript request validation

- **WHEN** frontend sends API request
- **THEN** system validates request body against TypeScript interface using Zod schemas

#### Scenario: MCP response typing

- **WHEN** MCP tool returns response
- **THEN** system transforms response to match frontend TypeScript types (CallAnalysis, RepInsights, SearchResults)

#### Scenario: Handle MCP schema changes

- **WHEN** MCP tool schema changes in backward-incompatible way
- **THEN** system detects version mismatch and returns 503 with upgrade required message

### Requirement: Authentication and Authorization

The integration SHALL enforce authentication and RBAC before proxying requests to MCP backend.

#### Scenario: Verify Clerk session

- **WHEN** API route receives request
- **THEN** system validates Clerk session token and extracts user identity

#### Scenario: Enforce manager-only endpoints

- **WHEN** non-manager user attempts to access manager-only endpoint
- **THEN** system returns 403 Forbidden with role requirement message

#### Scenario: Inject user context in MCP calls

- **WHEN** proxying request to MCP backend
- **THEN** system includes user email and role in request metadata for backend audit logging

### Requirement: Rate Limiting

The integration SHALL implement rate limiting to prevent abuse and protect MCP backend.

#### Scenario: Per-user rate limit

- **WHEN** user exceeds 100 requests per minute
- **THEN** system returns 429 Too Many Requests with Retry-After header

#### Scenario: Per-endpoint rate limit

- **WHEN** analyze_call endpoint receives >10 requests per minute from single user
- **THEN** system returns 429 error (analysis is expensive operation)

### Requirement: Observability and Logging

The integration SHALL log all MCP requests, responses, and errors for debugging and monitoring.

#### Scenario: Request logging

- **WHEN** API route receives request
- **THEN** system logs: timestamp, user email, endpoint, request params (excluding PII), status code, duration

#### Scenario: Error logging with context

- **WHEN** MCP call fails
- **THEN** system logs: error message, stack trace, MCP tool name, input params, user context

#### Scenario: Performance metrics

- **WHEN** API route completes
- **THEN** system records latency metric (p50, p95, p99) for endpoint monitoring
