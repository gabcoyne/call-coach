## 1. Fix Environment File Loading

- [x] 1.1 Add `find_project_root()` function to `coaching_mcp/shared/config.py` that walks up from `__file__` looking for `.git` or `pyproject.toml`
- [x] 1.2 Add fallback logic that returns 3 levels up if project root not found
- [x] 1.3 Update `Settings` class to use absolute path to `.env` file: `env_file=str(PROJECT_ROOT / ".env")`
- [x] 1.4 Test that env loading works: `uv run python -c "from coaching_mcp.shared import settings; print(settings.gong_api_key[:10])"`
- [x] 1.5 Verify server can load all required environment variables from project root `.env`

## 2. Add Development Mode Flag

- [x] 2.1 Add `argparse` to `coaching_mcp/server.py` with `--dev` flag argument
- [x] 2.2 Update `_validate_gong_api()` to skip Gong API connectivity check when `dev_mode=True`
- [x] 2.3 Create `_validate_database_connection_only()` function that only tests basic connectivity without table checks
- [x] 2.4 Update validation logic to call relaxed validation in dev mode
- [x] 2.5 Add logging: "🏗️  Dev mode: skipping expensive validations" when --dev flag is used
- [x] 2.6 Test server starts in dev mode: `uv run python -m coaching_mcp.server --dev`
- [x] 2.7 Test server still does full validation without --dev flag

## 3. Create uv Script Entries

- [x] 3.1 Add `[project.scripts]` section to `pyproject.toml` if not present
- [x] 3.2 Add `mcp-server` entry pointing to `coaching_mcp.server:main`
- [x] 3.3 Create `main_dev()` wrapper function in `coaching_mcp/server.py` that sets dev=True
- [x] 3.4 Add `mcp-server-dev` entry pointing to `coaching_mcp.server:main_dev`
- [x] 3.5 Test `uv run mcp-server-dev` starts server in development mode
- [x] 3.6 Test `uv run mcp-server` starts server in production mode

## 4. Add Health Check Endpoint

- [x] 4.1 Add `/health` GET endpoint to FastMCP server that returns JSON status
- [x] 4.2 Implement health check to return `{"status": "ok", "tools": 3}` when server is ready
- [x] 4.3 Implement health check to return `{"status": "starting"}` with 503 status code during initialization
- [x] 4.4 Test health check endpoint: `curl http://localhost:8000/health`

## 5. Create CLAUDE.md Documentation

- [x] 5.1 Create `CLAUDE.md` at project root
- [x] 5.2 Write Quick Start section with 5-minute setup guide (install uv, clone, copy .env, run server)
- [x] 5.3 Write Architecture section documenting FastMCP structure, tools, database schema
- [x] 5.4 Write Development Workflow section with Edit → Test → Debug cycle and how to add new tools
- [x] 5.5 Write Testing section covering unit tests, integration tests, manual tool testing
- [x] 5.6 Write Troubleshooting section with common errors and solutions (missing env vars, database issues, port conflicts)
- [x] 5.7 Write Deployment section explaining differences between local and Horizon deployment
- [x] 5.8 Add Full-Stack Testing section showing how to run frontend + backend + database together

## 6. Update Frontend Configuration

- [x] 6.1 Add `NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000` to `frontend/.env.local`
- [x] 6.2 Add `NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000` to `frontend/.env.example`
- [x] 6.3 Update `frontend/lib/mcp-client.ts` to read backend URL from `process.env.NEXT_PUBLIC_MCP_BACKEND_URL` with fallback to localhost:8000
- [x] 6.4 Test that frontend can connect to local backend

## 7. Update README

- [x] 7.1 Add "Local Development" section to root `README.md`
- [x] 7.2 Write 3-step quick start in README (install, setup, run)
- [x] 7.3 Add link to CLAUDE.md for detailed backend development guide
- [x] 7.4 Update prerequisites section to mention uv, Python 3.11+, and Neon database

## 8. Create Helper Scripts

- [x] 8.1 Create `scripts/check-backend.sh` that curls health endpoint and reports status
- [x] 8.2 Make check-backend.sh executable: `chmod +x scripts/check-backend.sh`
- [x] 8.3 Add comment header to script explaining usage
- [x] 8.4 Test script: `./scripts/check-backend.sh`

## 9. Integration Testing

- [x] 9.1 Start backend in dev mode: `uv run mcp-server-dev`
- [x] 9.2 Verify backend logs show "🚀 MCP server ready - 3 tools registered"
- [x] 9.3 Start frontend in separate terminal: `cd frontend && npm run dev`
- [x] 9.4 Open browser to http://localhost:3000 and verify no MCP backend errors
- [x] 9.5 Test call analysis page tries to load data from backend (expect no data but no connection errors)
- [x] 9.6 Check frontend Network tab shows requests to http://localhost:8000
- [x] 9.7 Verify health check endpoint accessible: `curl http://localhost:8000/health`

## 10. Documentation Verification

- [x] 10.1 Follow Quick Start in CLAUDE.md from scratch and verify it works
- [x] 10.2 Verify all troubleshooting scenarios are documented
- [x] 10.3 Verify environment variables are fully documented with examples
- [x] 10.4 Check that README Local Development section is clear and concise
