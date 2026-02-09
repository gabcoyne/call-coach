# Call Analysis Display Spec

## ADDED Requirements

### Requirement: Call analysis data SHALL load successfully

The system SHALL fetch and display call analysis data when a manager navigates to a call detail page.

#### Scenario: Valid call ID loads analysis data

- **WHEN** manager navigates to /calls/[callId] with valid call ID
- **THEN** page SHALL fetch analysis data from /api/coaching/analyze-call
- **THEN** analysis data SHALL be displayed within 5 seconds
- **THEN** skeleton loaders SHALL be replaced with actual content

#### Scenario: Cached analysis data loads immediately

- **WHEN** manager returns to a previously viewed call detail page
- **THEN** cached analysis data SHALL be displayed immediately
- **THEN** background revalidation SHALL occur without blocking UI

### Requirement: Loading states SHALL provide clear feedback

The system SHALL display appropriate loading states during data fetching to inform users of progress.

#### Scenario: Initial load shows skeleton loaders

- **WHEN** call detail page loads for the first time
- **THEN** skeleton loaders SHALL be displayed for each analysis section
- **THEN** skeleton layout SHALL match the structure of actual content

#### Scenario: Revalidation shows subtle loading indicator

- **WHEN** cached data is being revalidated in background
- **THEN** existing content SHALL remain visible
- **THEN** subtle loading indicator SHALL show revalidation in progress

### Requirement: Error states SHALL be actionable

The system SHALL display clear error messages with recovery actions when data fetching fails.

#### Scenario: Network error shows retry option

- **WHEN** API request fails due to network error
- **THEN** error message SHALL explain the issue (e.g., "Unable to connect to server")
- **THEN** "Retry" button SHALL be provided to retry the request
- **THEN** skeleton loaders SHALL be replaced with error state

#### Scenario: Authentication error redirects to login

- **WHEN** API request fails with 401 Unauthorized
- **THEN** user SHALL be redirected to login page
- **THEN** original URL SHALL be preserved for post-login redirect

#### Scenario: Invalid call ID shows not found error

- **WHEN** API request fails with 404 Not Found
- **THEN** error message SHALL indicate call does not exist
- **THEN** link to calls list SHALL be provided

#### Scenario: Authorization error shows access denied

- **WHEN** API request fails with 403 Forbidden
- **THEN** error message SHALL indicate insufficient permissions
- **THEN** explanation SHALL reference RBAC rules (manager can only see their team's calls)

### Requirement: Authentication SHALL work across SSR and client boundaries

The system SHALL maintain authentication context from server-side rendering through client-side data fetching.

#### Scenario: Server component passes authenticated context

- **WHEN** call detail page server component renders
- **THEN** user authentication state SHALL be verified
- **THEN** authenticated user context SHALL be available to client components

#### Scenario: Client-side SWR fetch includes credentials

- **WHEN** SWR hook fetches data from API route
- **THEN** request SHALL include credentials (cookies) automatically
- **THEN** authentication SHALL be validated by API route withAuth middleware

#### Scenario: Authentication persists across page navigation

- **WHEN** user navigates between call detail pages
- **THEN** authentication state SHALL persist without re-login
- **THEN** API requests SHALL continue to be authenticated

### Requirement: Database queries SHALL handle Gong call ID format

The system SHALL correctly handle Gong's numeric string call IDs in database queries.

#### Scenario: Numeric call ID queries coaching sessions

- **WHEN** API route queries coaching_sessions table with Gong call ID
- **THEN** query SHALL not attempt to cast numeric string to UUID
- **THEN** query SHALL use appropriate column type (TEXT or BIGINT)
- **THEN** results SHALL be returned without type errors

#### Scenario: Call metadata query uses correct ID format

- **WHEN** fetching call metadata from calls table
- **THEN** gong_call_id column SHALL store numeric string from Gong API
- **THEN** queries SHALL match on gong_call_id not internal UUID

### Requirement: Error logging SHALL capture debugging context

The system SHALL log errors with sufficient context to diagnose and fix issues.

#### Scenario: API error logged with request context

- **WHEN** API route handler encounters error
- **THEN** error SHALL be logged with request URL, method, user ID, and parameters
- **THEN** error stack trace SHALL be included
- **THEN** log entry SHALL include timestamp and severity

#### Scenario: Frontend error logged with component context

- **WHEN** React component encounters error
- **THEN** error SHALL be logged with component name, props, and state
- **THEN** SWR hook state (data, error, isLoading) SHALL be logged
- **THEN** user SHALL see graceful error UI, not crash

#### Scenario: Authentication error logged with full context

- **WHEN** authentication validation fails
- **THEN** log SHALL include authentication method (Clerk), user session state, and request headers
- **THEN** log SHALL indicate whether issue is SSR or client-side
