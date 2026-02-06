## ADDED Requirements

### Requirement: FastMCP project configuration file

The system SHALL provide a `fastmcp.toml` configuration file that defines the MCP server project metadata, runtime command, and environment variable placeholders for FastMCP Cloud deployment.

#### Scenario: Valid fastmcp.toml structure

- **WHEN** FastMCP Cloud reads `fastmcp.toml`
- **THEN** it SHALL find `[project]` section with `name` and `version`
- **AND** it SHALL find `[server]` section with `command` and `args` array
- **AND** it SHALL find `[server.env]` section with placeholder-formatted environment variables

#### Scenario: Runtime command execution

- **WHEN** FastMCP Cloud starts the MCP server
- **THEN** it SHALL execute `uv run python mcp/server.py` as specified in `command` and `args`
- **AND** it SHALL use Python 3.11 or higher runtime

### Requirement: Cloud deployment metadata

The system SHALL provide a `.fastmcp/config.json` file that describes the MCP server capabilities, dependencies, and environment variable requirements for FastMCP Cloud UI.

#### Scenario: Tool metadata display

- **WHEN** FastMCP Cloud UI displays the server
- **THEN** it SHALL show three tools: `analyze_call`, `get_rep_insights`, `search_calls`
- **AND** each tool SHALL display its description and parameter names

#### Scenario: Dependency specification

- **WHEN** FastMCP Cloud builds the deployment environment
- **THEN** it SHALL install all dependencies listed in `config.json` with pinned versions
- **AND** it SHALL use Python 3.11 runtime as specified in `python_version` field

### Requirement: Environment variable documentation

The configuration files SHALL document all required and optional environment variables needed for MCP server operation.

#### Scenario: Required variables documented

- **WHEN** developer reviews deployment configuration
- **THEN** they SHALL find documentation of five required variables: `GONG_API_KEY`, `GONG_API_SECRET`, `GONG_API_BASE_URL`, `ANTHROPIC_API_KEY`, `DATABASE_URL`
- **AND** each variable SHALL have clear description of its purpose

#### Scenario: Optional variables documented

- **WHEN** developer reviews deployment configuration
- **THEN** they SHALL find documentation of optional variables: `GONG_WEBHOOK_SECRET`, `LOG_LEVEL`
- **AND** they SHALL understand which features require optional variables
