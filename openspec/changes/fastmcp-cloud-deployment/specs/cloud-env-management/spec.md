## ADDED Requirements

### Requirement: Secure credential injection

The system SHALL support secure environment variable injection via Horizon UI without storing credentials in code or configuration files.

#### Scenario: Environment variables set in Horizon UI

- **WHEN** deploying MCP server to Horizon
- **THEN** five required variables SHALL be configurable: `GONG_API_KEY`, `GONG_API_SECRET`, `GONG_API_BASE_URL`, `ANTHROPIC_API_KEY`, `DATABASE_URL`
- **AND** values SHALL be stored encrypted in Horizon's secret management system
- **AND** no credential values SHALL appear in logs or error messages

#### Scenario: Runtime variable injection

- **WHEN** MCP server starts in cloud environment
- **THEN** all configured environment variables SHALL be injected before server initialization
- **AND** variables SHALL be accessible via `os.environ` in Python
- **AND** `config.py` Settings class SHALL load variables from environment

### Requirement: Environment variable validation

The system SHALL validate that all required environment variables are present and correctly formatted at server startup.

#### Scenario: Missing required variable

- **WHEN** MCP server starts with missing `GONG_API_KEY`
- **THEN** server SHALL fail to start with clear error message: "Missing required environment variable: GONG_API_KEY"
- **AND** error SHALL be visible in Horizon deployment logs
- **AND** server status SHALL be "Failed" in Horizon UI

#### Scenario: Invalid variable format

- **WHEN** `DATABASE_URL` is set but missing `?sslmode=require` suffix
- **THEN** server SHALL fail to start with error: "DATABASE_URL must include sslmode=require for Neon"
- **AND** error SHALL include example of correct format
- **AND** server SHALL not attempt database connection with invalid URL

### Requirement: Production credential security

No production credentials SHALL be committed to version control or included in deployment artifacts.

#### Scenario: Configuration file security audit

- **WHEN** reviewing `fastmcp.toml` and `.fastmcp/config.json`
- **THEN** files SHALL contain only placeholder variable names like `${GONG_API_KEY}`
- **AND** no actual credential values SHALL be present in any committed file
- **AND** `.env` file SHALL remain in `.gitignore`

#### Scenario: Deployment artifact inspection

- **WHEN** inspecting deployed server in Horizon
- **THEN** environment variables SHALL be marked as "secret" type
- **AND** variable values SHALL be masked in UI (showing only `***`)
- **AND** variable values SHALL not be included in exported configuration or logs
