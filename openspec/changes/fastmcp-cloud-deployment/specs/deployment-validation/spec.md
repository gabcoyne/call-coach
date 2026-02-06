## ADDED Requirements

### Requirement: Pre-deployment health checks

The system SHALL perform automated health checks before marking the MCP server as "Ready" in Horizon, validating connectivity to all external services.

#### Scenario: Database connectivity validation

- **WHEN** MCP server starts in cloud environment
- **THEN** it SHALL execute `SELECT 1` query against Neon database
- **AND** query SHALL complete within 5 seconds
- **AND** on failure, server SHALL log error: "Database connection failed: [specific error]"
- **AND** server SHALL not proceed to tool registration if database is unreachable

#### Scenario: Gong API authentication validation

- **WHEN** MCP server starts in cloud environment
- **THEN** it SHALL make test request to `GET /v2/calls` with minimal date range
- **AND** request SHALL use `GONG_API_KEY` and `GONG_API_SECRET` in Basic Auth
- **AND** request SHALL complete within 10 seconds
- **AND** on 401 error, server SHALL log: "Gong API authentication failed - verify GONG_API_KEY and GONG_API_SECRET"
- **AND** on network error, server SHALL log: "Gong API unreachable - verify GONG_API_BASE_URL"

#### Scenario: Anthropic API validation

- **WHEN** MCP server starts in cloud environment
- **THEN** it SHALL validate `ANTHROPIC_API_KEY` format (starts with `sk-ant-`)
- **AND** it MAY make lightweight API call to verify key is active
- **AND** on invalid format, server SHALL log: "ANTHROPIC_API_KEY has invalid format"
- **AND** validation SHALL complete within 5 seconds

### Requirement: Startup validation logging

The system SHALL provide clear, actionable logging during startup validation to aid debugging deployment issues.

#### Scenario: Successful validation logging

- **WHEN** all health checks pass
- **THEN** server SHALL log: "✓ Database connection successful"
- **AND** "✓ Gong API authentication successful"
- **AND** "✓ Anthropic API key validated"
- **AND** "✓ MCP server ready - 3 tools registered"
- **AND** Horizon SHALL mark server status as "Ready"

#### Scenario: Failed validation logging

- **WHEN** any health check fails
- **THEN** server SHALL log all attempted checks with pass/fail status
- **AND** failed check SHALL include specific error message and remediation hint
- **AND** server SHALL exit with non-zero status code
- **AND** Horizon SHALL mark server status as "Failed" with last error message visible

### Requirement: Fast startup time

The MCP server SHALL complete startup validation and be ready to handle tool invocations within 30 seconds of container start.

#### Scenario: Cold start performance

- **WHEN** FastMCP Cloud provisions new container for MCP server
- **THEN** server SHALL complete all health checks within 15 seconds
- **AND** Python imports and FastMCP initialization SHALL complete within 10 seconds
- **AND** tool registration SHALL complete within 5 seconds
- **AND** total startup time SHALL not exceed 30 seconds

#### Scenario: Startup timeout handling

- **WHEN** startup takes longer than 30 seconds
- **THEN** Horizon SHALL terminate the container
- **AND** server status SHALL be marked "Failed" with timeout error
- **AND** server SHALL be retried automatically up to 3 times
- **AND** developer SHALL be notified if all retries fail
