## ADDED Requirements

### Requirement: Prefect Horizon MCP server registration
The system SHALL be deployable to Prefect Horizon MCP server registry at `https://horizon.prefect.io/prefect-george/servers` with proper authentication and configuration.

#### Scenario: Server creation in Horizon UI
- **WHEN** deploying to Horizon
- **THEN** server SHALL be named `gong-call-coach`
- **AND** runtime SHALL be set to Python 3.11
- **AND** command SHALL be `uv run python mcp/server.py`
- **AND** working directory SHALL be `/app`

#### Scenario: Authentication with FastMCP Cloud
- **WHEN** Horizon connects to FastMCP Cloud
- **THEN** it SHALL use API key `fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc` for authentication
- **AND** authentication SHALL succeed before server is marked as "Ready"

### Requirement: Claude Desktop integration
The deployed MCP server SHALL be accessible via Claude Desktop through Horizon integration without requiring local setup.

#### Scenario: Tool discovery in Claude Desktop
- **WHEN** Claude Desktop connects to Horizon workspace
- **THEN** it SHALL discover three MCP tools: `analyze_call`, `get_rep_insights`, `search_calls`
- **AND** each tool SHALL include full parameter specifications and descriptions

#### Scenario: Tool invocation from Claude Desktop
- **WHEN** user invokes `analyze_call("1464927526043145564")` in Claude Desktop
- **THEN** request SHALL route through Horizon to cloud-deployed MCP server
- **AND** MCP server SHALL execute with production database credentials
- **AND** result SHALL return to Claude Desktop within 60 seconds

### Requirement: Multi-user access support
The deployed MCP server SHALL support concurrent access from multiple team members via their Claude Desktop instances.

#### Scenario: Concurrent tool invocations
- **WHEN** three users simultaneously invoke MCP tools
- **THEN** each request SHALL execute independently without conflicts
- **AND** database connection pool SHALL not be exhausted (5-20 connections available)
- **AND** each user SHALL receive their results without cross-contamination

#### Scenario: Session isolation
- **WHEN** multiple users access the same MCP server
- **THEN** each user's tool invocations SHALL be isolated
- **AND** cache hits SHALL be shared across users (transcript + rubric version hash)
- **AND** no user-specific state SHALL persist between tool calls
