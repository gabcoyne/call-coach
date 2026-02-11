# Specification

## ADDED Requirements

### Requirement: Analysis Engine Unit Tests

The system SHALL provide comprehensive unit tests for the analysis engine module covering prompt generation, Claude API integration, caching, and error handling.

#### Scenario: Prompt generation for each coaching dimension

- **WHEN** test calls `_generate_prompt_for_dimension()` with dimension and transcript
- **THEN** system returns formatted prompt with rubric, transcript, and instructions

#### Scenario: Claude API call with mocked response

- **WHEN** test calls `_run_claude_analysis()` with mocked Anthropic client
- **THEN** system returns parsed analysis without hitting real API

#### Scenario: Cache hit prevents API call

- **WHEN** test calls `get_or_create_coaching_session()` with existing cache key
- **THEN** system returns cached result without calling Claude API

#### Scenario: Cache miss triggers API call

- **WHEN** test calls `get_or_create_coaching_session()` with new cache key
- **THEN** system calls Claude API and stores result in cache

#### Scenario: Error handling for malformed Claude response

- **WHEN** Claude API returns invalid JSON
- **THEN** system raises `AnalysisError` with descriptive message

### Requirement: Cache Module Unit Tests

The system SHALL provide unit tests for Redis cache client and database cache fallback mechanisms.

#### Scenario: Redis available - successful cache operations

- **WHEN** Redis is available and test calls `get()`, `set()`, `invalidate()`
- **THEN** operations succeed with correct TTL and key patterns

#### Scenario: Redis unavailable - graceful degradation

- **WHEN** Redis is unavailable and test calls cache operations
- **THEN** operations return None/False without raising exceptions

#### Scenario: Cache key generation consistency

- **WHEN** test generates cache key for same transcript/dimension/rubric twice
- **THEN** both keys are identical (deterministic hashing)

#### Scenario: Cache invalidation by dimension

- **WHEN** test calls `invalidate_dimension()` after caching multiple sessions
- **THEN** only sessions for that dimension are invalidated

### Requirement: Database Module Unit Tests

The system SHALL provide unit tests for database connection pooling, query execution, and error handling.

#### Scenario: Connection pool initialization

- **WHEN** test initializes database connection with valid DSN
- **THEN** connection pool is created with configured min/max sizes

#### Scenario: Query execution with parameters

- **WHEN** test executes parameterized query with `fetch_one()`
- **THEN** results are returned with proper type conversion

#### Scenario: Transaction rollback on error

- **WHEN** test executes query that raises exception within transaction
- **THEN** transaction is rolled back and connection returned to pool

#### Scenario: Connection timeout handling

- **WHEN** test simulates connection timeout
- **THEN** system retries with exponential backoff up to max attempts

### Requirement: MCP Tools Unit Tests

The system SHALL provide unit tests for all FastMCP tool implementations (analyze_call, get_rep_insights, search_calls).

#### Scenario: analyze_call with valid parameters

- **WHEN** test calls `analyze_call_tool()` with valid call_id and dimensions
- **THEN** system returns structured analysis with scores and insights

#### Scenario: get_rep_insights with time period filtering

- **WHEN** test calls `get_rep_insights_tool()` with date range
- **THEN** system returns metrics only within specified period

#### Scenario: search_calls with complex filters

- **WHEN** test calls `search_calls_tool()` with multiple filter criteria
- **THEN** system returns calls matching ALL criteria (AND logic)

#### Scenario: Tool parameter validation

- **WHEN** test calls tool with invalid parameters
- **THEN** system raises validation error with specific field messages

### Requirement: Middleware Logic Unit Tests

The system SHALL provide unit tests for middleware logic (rate limiting, compression, auth) independent of FastAPI integration.

#### Scenario: Rate limit token bucket algorithm

- **WHEN** test simulates rapid requests exceeding limit
- **THEN** token bucket correctly blocks requests after threshold

#### Scenario: Rate limit refill over time

- **WHEN** test waits for refill period after exhausting tokens
- **THEN** new tokens are available according to refill rate

#### Scenario: Compression threshold decision

- **WHEN** test provides response smaller than threshold
- **THEN** compression is skipped to save CPU

#### Scenario: Auth context extraction from Clerk session

- **WHEN** test provides valid Clerk session data
- **THEN** system extracts user ID, email, and role correctly

### Requirement: Test Execution Speed

The system SHALL execute all backend unit tests in under 30 seconds on standard hardware.

#### Scenario: Parallel test execution

- **WHEN** test suite runs with pytest-xdist using 8 workers
- **THEN** total execution time is reduced by at least 4x vs serial

#### Scenario: Fast fixtures with minimal setup

- **WHEN** test uses function-scoped fixtures
- **THEN** fixture setup/teardown completes in <100ms

### Requirement: Test Isolation

The system SHALL ensure complete isolation between unit tests with no shared state.

#### Scenario: Database fixtures per test function

- **WHEN** two tests modify database state
- **THEN** second test sees clean database without first test's changes

#### Scenario: Mock reset between tests

- **WHEN** test mocks external API call
- **THEN** next test sees fresh mock without previous calls recorded

### Requirement: Test Coverage Reporting

The system SHALL generate coverage reports showing line and branch coverage for all backend modules.

#### Scenario: Coverage report includes all Python files

- **WHEN** test suite runs with `pytest-cov`
- **THEN** report includes all files in `analysis/`, `api/`, `coaching_mcp/`, `middleware/`

#### Scenario: Coverage fails below 85% threshold

- **WHEN** coverage drops below 85% for backend
- **THEN** pytest exits with failure code

#### Scenario: Coverage report shows uncovered lines

- **WHEN** test suite completes
- **THEN** report highlights specific line numbers without coverage
