## ADDED Requirements

### Requirement: Environment file loading from project root

The system SHALL load environment variables from `.env` file located in the project root directory, regardless of the module's location in the directory structure.

#### Scenario: Server starts with .env in project root

- **WHEN** `.env` file exists in project root with valid credentials
- **THEN** server successfully loads all environment variables (GONG_API_KEY, DATABASE_URL, ANTHROPIC_API_KEY)

#### Scenario: Server fails gracefully when .env missing

- **WHEN** `.env` file does not exist in project root
- **THEN** server displays clear error message indicating missing `.env` file and lists required variables

### Requirement: Development mode with relaxed validation

The system SHALL support a `--dev` command-line flag that enables development mode with relaxed validation for faster iteration.

#### Scenario: Server starts in dev mode with basic checks

- **WHEN** server is started with `--dev` flag
- **THEN** server skips expensive validation checks (Gong API connectivity, database table verification)
- **THEN** server only verifies database connection is available
- **THEN** server logs "Dev mode: skipping expensive validations" message

#### Scenario: Server starts in production mode with full checks

- **WHEN** server is started without `--dev` flag
- **THEN** server performs all validation checks including Gong API and database tables
- **THEN** server fails fast if any validation fails with clear error messages

### Requirement: uv-based execution scripts

The system SHALL provide `uv`-based execution methods through pyproject.toml scripts for easy invocation.

#### Scenario: Run server in dev mode via uv script

- **WHEN** developer runs `uv run mcp-server-dev`
- **THEN** server starts in development mode with --dev flag automatically applied

#### Scenario: Run server in production mode via uv script

- **WHEN** developer runs `uv run mcp-server`
- **THEN** server starts with full validation checks

### Requirement: Project root detection

The system SHALL automatically detect project root by searching for `.git` directory or `pyproject.toml` file in parent directories.

#### Scenario: Detect project root from nested module

- **WHEN** config is loaded from `coaching_mcp/shared/config.py`
- **THEN** system walks up directory tree to find project root
- **THEN** system uses detected root to construct absolute path to `.env`

#### Scenario: Fallback when git/pyproject not found

- **WHEN** neither `.git` nor `pyproject.toml` found in parent directories
- **THEN** system falls back to 3 levels up from config file location
- **THEN** system logs warning about fallback being used

### Requirement: Server startup validation logging

The system SHALL provide clear, structured logging during server startup showing validation progress.

#### Scenario: Successful startup shows all validation steps

- **WHEN** server starts successfully
- **THEN** logs show "✓ All required environment variables present"
- **THEN** logs show "✓ Database connection successful"
- **THEN** logs show "✓ Database schema validated" (production mode only)
- **THEN** logs show "🚀 MCP server ready - 3 tools registered"

#### Scenario: Failed startup shows specific error

- **WHEN** server startup fails due to missing DATABASE_URL
- **THEN** logs show "✗ Missing required environment variables: DATABASE_URL"
- **THEN** server exits with non-zero exit code
- **THEN** logs include suggestion to check `.env` file

### Requirement: Health check endpoint

The system SHALL expose a health check endpoint at `GET /health` that returns server status and available tools count.

#### Scenario: Health check returns ok status

- **WHEN** server is running normally
- **THEN** `GET /health` returns `{"status": "ok", "tools": 3}`
- **THEN** HTTP status code is 200

#### Scenario: Health check accessible during startup

- **WHEN** server is still initializing
- **THEN** `GET /health` returns `{"status": "starting"}`
- **THEN** HTTP status code is 503
