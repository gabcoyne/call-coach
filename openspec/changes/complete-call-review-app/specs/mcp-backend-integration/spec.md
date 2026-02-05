## ADDED Requirements

### Requirement: API client for analyze_call tool
The system SHALL provide a frontend API client that calls the MCP backend's analyze_call tool.

#### Scenario: Analyze call request
- **WHEN** the frontend calls analyzeCall(callId) API method
- **THEN** the system sends POST request to /api/calls/[callId]/analyze with call ID

#### Scenario: Analysis response
- **WHEN** the analyze_call tool returns coaching results
- **THEN** the API client parses and returns structured coaching data

#### Scenario: Analysis error
- **WHEN** the analyze_call tool returns an error
- **THEN** the API client throws an error with the backend error message

### Requirement: API client for get_rep_insights tool
The system SHALL provide a frontend API client that calls the MCP backend's get_rep_insights tool.

#### Scenario: Get rep insights request
- **WHEN** the frontend calls getRepInsights(email, timeRange) API method
- **THEN** the system sends GET request to /api/reps/[email]/insights with time range query params

#### Scenario: Insights response
- **WHEN** the get_rep_insights tool returns performance data
- **THEN** the API client parses and returns structured insights including trends, metrics, and recent calls

#### Scenario: Rep not found
- **WHEN** the get_rep_insights tool cannot find the specified rep
- **THEN** the API client throws a 404 error

### Requirement: API client for search_calls tool
The system SHALL provide a frontend API client that calls the MCP backend's search_calls tool.

#### Scenario: Search calls request
- **WHEN** the frontend calls searchCalls(filters) API method
- **THEN** the system sends POST request to /api/calls/search with filter parameters

#### Scenario: Search response
- **WHEN** the search_calls tool returns matching calls
- **THEN** the API client parses and returns array of call summaries with metadata

#### Scenario: Empty results
- **WHEN** the search_calls tool finds no matching calls
- **THEN** the API client returns empty array

### Requirement: Backend URL configuration
The system SHALL use NEXT_PUBLIC_MCP_BACKEND_URL environment variable for backend API base URL.

#### Scenario: Local development
- **WHEN** NEXT_PUBLIC_MCP_BACKEND_URL is set to http://localhost:8000
- **THEN** the API client sends requests to http://localhost:8000/api/*

#### Scenario: Production deployment
- **WHEN** NEXT_PUBLIC_MCP_BACKEND_URL is set to https://mcp.prefect.io
- **THEN** the API client sends requests to https://mcp.prefect.io/api/*

### Requirement: Request authentication
The system SHALL include Clerk authentication token in all API requests to backend.

#### Scenario: Authenticated request
- **WHEN** an authenticated user makes an API call
- **THEN** the API client includes Authorization: Bearer <clerk-token> header

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated user attempts an API call
- **THEN** the API client throws authentication error

### Requirement: Request timeout handling
The system SHALL implement 30-second timeout for all backend API requests.

#### Scenario: Request completes within timeout
- **WHEN** backend responds within 30 seconds
- **THEN** the API client returns the response

#### Scenario: Request exceeds timeout
- **WHEN** backend does not respond within 30 seconds
- **THEN** the API client aborts the request and throws timeout error

### Requirement: Retry logic for transient errors
The system SHALL retry failed requests up to 2 times for 5xx server errors.

#### Scenario: Transient error recovers
- **WHEN** first request fails with 500 error but retry succeeds
- **THEN** the API client returns the successful response

#### Scenario: Persistent error
- **WHEN** all retry attempts fail with 5xx errors
- **THEN** the API client throws the final error

### Requirement: Error response parsing
The system SHALL parse backend error responses and throw typed errors.

#### Scenario: Backend returns error object
- **WHEN** backend returns JSON error with status code and message
- **THEN** the API client throws Error with parsed message

#### Scenario: Network error
- **WHEN** request fails due to network issue
- **THEN** the API client throws "Network error" message

### Requirement: TypeScript type safety
The system SHALL use TypeScript interfaces for all API request and response types.

#### Scenario: API method call with types
- **WHEN** developer calls analyzeCall(callId)
- **THEN** TypeScript validates callId is string and return type is CoachingAnalysis

#### Scenario: Type error at compile time
- **WHEN** developer passes wrong type to API method
- **THEN** TypeScript compiler shows error before runtime
