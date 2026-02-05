## 1. FastMCP Cloud Configuration Files

- [x] 1.1 Create `fastmcp.toml` with project metadata, server command, and environment variable placeholders
- [x] 1.2 Create `.fastmcp/config.json` with tool metadata, dependencies, and environment variable requirements
- [x] 1.3 Update `pyproject.toml` to pin exact dependency versions for cloud deployment (fastmcp==0.3.0, anthropic==0.40.0, psycopg2-binary==2.9.9, httpx==0.27.2)
- [x] 1.4 Verify all three MCP tools are properly documented in `.fastmcp/config.json` with descriptions and parameters

## 2. Startup Validation

- [x] 2.1 Add `_validate_environment()` function in `mcp/server.py` to check all required env vars are present
- [x] 2.2 Add `_validate_database_connection()` function to test Neon connectivity with `SELECT 1` query
- [x] 2.3 Add `_validate_gong_api()` function to test Gong API authentication with minimal `GET /v2/calls` request
- [x] 2.4 Add `_validate_anthropic_api()` function to check `ANTHROPIC_API_KEY` format (starts with `sk-ant-`)
- [x] 2.5 Add startup logging with clear success/failure messages for each validation step
- [x] 2.6 Implement fail-fast behavior: exit with non-zero status if any validation fails

## 3. Deployment Script

- [x] 3.1 Create `.fastmcp/deploy.sh` executable script with deployment instructions
- [x] 3.2 Add pre-deployment checks: verify `uv sync` succeeds and MCP server initializes locally
- [x] 3.3 Document manual Horizon deployment steps in deploy script (create server, set env vars, upload files)
- [x] 3.4 Add post-deployment test commands: `analyze_call("1464927526043145564")`, `get_rep_insights("email")`, `search_calls()`

## 4. Documentation

- [x] 4.1 Add "Cloud Deployment" section to `README.md` with Prefect Horizon integration steps
- [x] 4.2 Document all required environment variables with descriptions and example values
- [x] 4.3 Add troubleshooting section for common deployment failures (401 auth errors, database connection timeout, cold start latency)
- [x] 4.4 Document credential rotation process for Gong and Anthropic API keys
- [x] 4.5 Add expected performance characteristics (cold start 10-15s, warm start <2s)

## 5. Testing

- [x] 5.0 Write comprehensive unit tests for all validation functions (TDD)
- [x] 5.1 Run test suite - all validation tests should pass
- [ ] 5.2 Test local MCP server startup with validation enabled (all checks should pass)
- [ ] 5.3 Test with missing env var to verify fail-fast behavior and error messaging
- [ ] 5.4 Test with invalid `DATABASE_URL` (missing `?sslmode=require`) to verify validation catches it
- [ ] 5.5 Test with invalid Gong credentials to verify 401 error is caught during startup
- [ ] 5.6 Deploy to Horizon staging environment (if available) and verify tools work via Claude Desktop

## 6. Production Deployment

- [ ] 6.1 Navigate to `https://horizon.prefect.io/prefect-george/servers` and create new MCP server
- [ ] 6.2 Configure server: name=`gong-call-coach`, runtime=Python 3.11, command=`uv run python mcp/server.py`
- [ ] 6.3 Set all required environment variables in Horizon UI (copy from local `.env`)
- [ ] 6.4 Upload project files or connect GitHub repository
- [ ] 6.5 Deploy and verify server reaches "Ready" status within 30 seconds
- [ ] 6.6 Test all three MCP tools via Claude Desktop with production data
- [ ] 6.7 Monitor Neon dashboard for connection pool usage during initial testing

## 7. Monitoring & Verification

- [ ] 7.1 Check Horizon logs for successful validation messages during deployment
- [ ] 7.2 Verify no credential values appear in logs or error messages
- [ ] 7.3 Test concurrent tool invocations from multiple Claude Desktop instances
- [ ] 7.4 Verify cache layer works correctly (SHA256 transcript hash + rubric version)
- [ ] 7.5 Document observed cold start latency and add to README if >15s
