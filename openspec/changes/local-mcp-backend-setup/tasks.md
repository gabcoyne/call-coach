## 1. Fix Environment File Loading

- [ ] 1.1 Add `find_project_root()` function to `coaching_mcp/shared/config.py` that walks up from `__file__` looking for `.git` or `pyproject.toml`
- [ ] 1.2 Add fallback logic that returns 3 levels up if project root not found
- [ ] 1.3 Update `Settings` class to use absolute path to `.env` file: `env_file=str(PROJECT_ROOT / ".env")`
- [ ] 1.4 Test that env loading works: `uv run python -c "from coaching_mcp.shared import settings; print(settings.gong_api_key[:10])"`
- [ ] 1.5 Verify server can load all required environment variables from project root `.env`

## 2. Add Development Mode Flag

- [ ] 2.1 Add `argparse` to `coaching_mcp/server.py` with `--dev` flag argument
- [ ] 2.2 Update `_validate_gong_api()` to skip Gong API connectivity check when `dev_mode=True`
- [ ] 2.3 Create `_validate_database_connection_only()` function that only tests basic connectivity without table checks
- [ ] 2.4 Update validation logic to call relaxed validation in dev mode
- [ ] 2.5 Add logging: "🏗️  Dev mode: skipping expensive validations" when --dev flag is used
- [ ] 2.6 Test server starts in dev mode: `uv run python -m coaching_mcp.server --dev`
- [ ] 2.7 Test server still does full validation without --dev flag

## 3. Create uv Script Entries

- [ ] 3.1 Add `[project.scripts]` section to `pyproject.toml` if not present
- [ ] 3.2 Add `mcp-server` entry pointing to `coaching_mcp.server:main`
- [ ] 3.3 Create `main_dev()` wrapper function in `coaching_mcp/server.py` that sets dev=True
- [ ] 3.4 Add `mcp-server-dev` entry pointing to `coaching_mcp.server:main_dev`
- [ ] 3.5 Test `uv run mcp-server-dev` starts server in development mode
- [ ] 3.6 Test `uv run mcp-server` starts server in production mode

## 4. Add Health Check Endpoint

- [ ] 4.1 Add `/health` GET endpoint to FastMCP server that returns JSON status
- [ ] 4.2 Implement health check to return `{"status": "ok", "tools": 3}` when server is ready
- [ ] 4.3 Implement health check to return `{"status": "starting"}` with 503 status code during initialization
- [ ] 4.4 Test health check endpoint: `curl http://localhost:8000/health`

## 5. Create CLAUDE.md Documentation

- [ ] 5.1 Create `CLAUDE.md` at project root
- [ ] 5.2 Write Quick Start section with 5-minute setup guide (install uv, clone, copy .env, run server)
- [ ] 5.3 Write Architecture section documenting FastMCP structure, tools, database schema
- [ ] 5.4 Write Development Workflow section with Edit → Test → Debug cycle and how to add new tools
- [ ] 5.5 Write Testing section covering unit tests, integration tests, manual tool testing
- [ ] 5.6 Write Troubleshooting section with common errors and solutions (missing env vars, database issues, port conflicts)
- [ ] 5.7 Write Deployment section explaining differences between local and Horizon deployment
- [ ] 5.8 Add Full-Stack Testing section showing how to run frontend + backend + database together

## 6. Update Frontend Configuration

- [ ] 6.1 Add `NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000` to `frontend/.env.local`
- [ ] 6.2 Add `NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000` to `frontend/.env.example`
- [ ] 6.3 Update `frontend/lib/mcp-client.ts` to read backend URL from `process.env.NEXT_PUBLIC_MCP_BACKEND_URL` with fallback to localhost:8000
- [ ] 6.4 Test that frontend can connect to local backend

## 7. Update README

- [ ] 7.1 Add "Local Development" section to root `README.md`
- [ ] 7.2 Write 3-step quick start in README (install, setup, run)
- [ ] 7.3 Add link to CLAUDE.md for detailed backend development guide
- [ ] 7.4 Update prerequisites section to mention uv, Python 3.11+, and Neon database

## 8. Create Helper Scripts

- [ ] 8.1 Create `scripts/check-backend.sh` that curls health endpoint and reports status
- [ ] 8.2 Make check-backend.sh executable: `chmod +x scripts/check-backend.sh`
- [ ] 8.3 Add comment header to script explaining usage
- [ ] 8.4 Test script: `./scripts/check-backend.sh`

## 9. Integration Testing

- [ ] 9.1 Start backend in dev mode: `uv run mcp-server-dev`
- [ ] 9.2 Verify backend logs show "🚀 MCP server ready - 3 tools registered"
- [ ] 9.3 Start frontend in separate terminal: `cd frontend && npm run dev`
- [ ] 9.4 Open browser to http://localhost:3000 and verify no MCP backend errors
- [ ] 9.5 Test call analysis page tries to load data from backend (expect no data but no connection errors)
- [ ] 9.6 Check frontend Network tab shows requests to http://localhost:8000
- [ ] 9.7 Verify health check endpoint accessible: `curl http://localhost:8000/health`

## 10. Documentation Verification

- [ ] 10.1 Follow Quick Start in CLAUDE.md from scratch and verify it works
- [ ] 10.2 Verify all troubleshooting scenarios are documented
- [ ] 10.3 Verify environment variables are fully documented with examples
- [ ] 10.4 Check that README Local Development section is clear and concise
