# Proposal

## Why

The FastMCP backend server cannot run locally for development because the Pydantic Settings configuration doesn't properly load the `.env` file in the project root, making full-stack local testing (frontend + backend + database) impossible. This blocks rapid iteration and forces developers to deploy to Horizon for every backend change, significantly slowing development velocity.

## What Changes

- Fix `.env` file loading in `coaching_mcp/shared/config.py` to properly load from project root
- Create `uv`-based runner scripts for local development (`run-mcp-server.sh`, `pyproject.toml` scripts)
- Add `--dev` mode flag that relaxes strict validation for local development
- Create comprehensive `CLAUDE.md` documentation for backend development workflow
- Add integration testing guide showing how to run frontend + backend + database locally
- Update existing `README.md` with local development quick-start section

## Capabilities

### New Capabilities

- `local-backend-runner`: Scripts, configuration, and tooling for running the FastMCP server locally using `uv`, including environment setup and hot-reload support
- `backend-development-docs`: Comprehensive CLAUDE.md with backend architecture, development workflow, testing procedures, and troubleshooting guide

### Modified Capabilities

<!-- No existing capabilities are being modified at the spec level -->

## Impact

**Affected Files:**

- `coaching_mcp/shared/config.py` - Fix env file path resolution
- `coaching_mcp/server.py` - Add dev mode flag and relaxed validation
- Root directory - New run scripts and CLAUDE.md
- `pyproject.toml` - Add uv script entries
- `README.md` - Add local development section

**Affected Systems:**

- Local development environment (Python 3.11+, uv, PostgreSQL)
- FastMCP server startup and configuration loading
- Frontend-backend integration (localhost:3000 ↔ localhost:8000)

**Dependencies:**

- Requires working Neon database connection (already configured)
- Requires valid API keys in `.env` (already present)
- Frontend expects MCP backend at `http://localhost:8000` (needs update to env var)

**Benefits:**

- Enables rapid local iteration without Horizon deployment
- Reduces development cycle time from ~5 minutes to <30 seconds
- Allows debugging with IDE breakpoints and local logs
- Makes it easier for new contributors to get started
