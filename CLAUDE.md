# Call Coach Backend Development Guide

FastMCP server for AI-powered sales call coaching. This guide covers local development, testing, and deployment.

## Quick Start

Get the backend server running locally in under 5 minutes.

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Access to Neon Postgres database
- API keys for Gong and Anthropic

### Setup Steps

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:
   ```bash
   cd /path/to/call-coach

   # Create .env file from example
   cp .env.example .env

   # Edit .env with your credentials
   # Required: GONG_API_KEY, GONG_API_SECRET, ANTHROPIC_API_KEY, DATABASE_URL
   ```

3. **Run the server**:
   ```bash
   # Development mode (fast startup, relaxed validation)
   uv run mcp-server-dev

   # You should see:
   # ============================================================
   # Starting Gong Call Coaching MCP Server
   # 🏗️  Dev mode: skipping expensive validations
   # ============================================================
   #
   # 🔍 Running pre-flight validation checks...
   # ✓ All required environment variables present
   # ✓ Database connection successful (dev mode - schema not validated)
   # ✓ Gong API validation skipped (dev mode)
   # ✓ Anthropic API key validated
   #
   # ✅ All validation checks passed!
   # ============================================================
   # 🚀 MCP server ready - 3 tools registered
   # ============================================================
   ```

4. **Verify health check**:
   ```bash
   curl http://localhost:8000/health
   # {"status":"ok","tools":3}
   ```

## Architecture

### FastMCP Server Structure

The MCP backend is built with [FastMCP](https://github.com/jlowin/fastmcp), providing three on-demand coaching tools accessible via the Model Context Protocol.

```
coaching_mcp/
├── server.py           # FastMCP server and tool registration
├── shared/
│   └── config.py       # Pydantic Settings for environment configuration
└── tools/
    ├── analyze_call.py       # Deep-dive analysis of specific calls
    ├── get_rep_insights.py   # Performance trends for sales reps
    └── search_calls.py       # Search calls by filters
```

### Tools Overview

| Tool | Purpose | Key Features |
|------|---------|--------------|
| `analyze_call` | Deep-dive coaching analysis of a specific call | Multi-dimensional scoring, transcript snippets, actionable feedback |
| `get_rep_insights` | Performance trends and coaching history for a rep | Score trends, skill gaps, improvement tracking |
| `search_calls` | Find calls matching specific criteria | Complex filters, date ranges, objection types |

### Database Schema

The backend uses Neon Postgres with the following key tables:

- **calls**: Call metadata (Gong ID, title, date, participants)
- **speakers**: Speaker information and roles
- **transcripts**: Call transcripts with timestamps
- **coaching_sessions**: Analysis results and coaching feedback
- **coaching_dimensions**: Dimension-specific scores and insights

### Integration Flow

```
Claude Desktop → MCP Protocol → FastMCP Server → Tools
                                      ↓
                            Gong API ← → Neon Database ← → Anthropic API
```

## Development Workflow

### Edit → Test → Debug Cycle

1. **Make changes** to tool implementations in `coaching_mcp/tools/`:
   ```bash
   # Example: editing the analyze_call tool
   code coaching_mcp/tools/analyze_call.py
   ```

2. **Restart the server**:
   ```bash
   # Stop server (Ctrl+C)
   # Restart in dev mode
   uv run mcp-server-dev
   ```

3. **Test the change**:
   - Option A: Use via Claude Desktop (if MCP client configured)
   - Option B: Manual tool invocation (see Testing section)

### Adding New Tools

1. **Create tool module** in `coaching_mcp/tools/`:
   ```python
   # coaching_mcp/tools/my_new_tool.py
   from typing import Any

   def my_new_tool(param: str) -> dict[str, Any]:
       """
       Brief description of what this tool does.

       Args:
           param: Description of parameter

       Returns:
           Description of return value
       """
       # Implementation
       return {"result": "value"}
   ```

2. **Register in server.py**:
   ```python
   from coaching_mcp.tools.my_new_tool import my_new_tool

   @mcp.tool()
   def my_new_tool(param: str) -> dict[str, Any]:
       """Tool description for Claude."""
       return my_new_tool(param=param)
   ```

3. **Update health check tool count** if adding/removing tools:
   ```python
   # In server.py, update the health check response:
   return JSONResponse({"status": "ok", "tools": 4})  # Update count
   ```

### Development vs Production Mode

**Development Mode** (`uv run mcp-server-dev` or `--dev` flag):
- Skips Gong API connectivity check
- Only validates basic database connection (no table schema check)
- Faster startup (~2 seconds vs ~8 seconds)
- Use for rapid iteration on tool logic

**Production Mode** (`uv run mcp-server`):
- Full Gong API authentication check
- Complete database schema validation
- Stricter error handling
- Use before committing changes or deploying

## Testing

### Unit Tests

Run pytest tests for individual components:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_analyze_call.py -v

# Run with coverage
uv run pytest tests/ --cov=coaching_mcp --cov-report=html
```

### Integration Tests

Test with real database and APIs:

```bash
# Mark integration tests with @pytest.mark.integration
# Run integration tests only
uv run pytest tests/ -v -m integration

# Skip integration tests during rapid development
uv run pytest tests/ -v -m "not integration"
```

### Manual Tool Testing

Test individual tools without Claude Desktop:

```python
# Create a test script: test_manual.py
from coaching_mcp.tools.analyze_call import analyze_call_tool

result = analyze_call_tool(
    call_id="1464927526043145564",
    dimensions=["discovery"],
    use_cache=False
)

print(f"Discovery score: {result['scores']['discovery']}")
print(f"Strengths: {result['strengths']}")
```

Run it:
```bash
uv run python test_manual.py
```

### Testing via MCP Protocol

Use the `mcp` CLI tool to test MCP protocol directly:

```bash
# Install mcp CLI
npm install -g @modelcontextprotocol/cli

# List available tools
mcp list-tools http://localhost:8000

# Call a tool
mcp call-tool http://localhost:8000 analyze_call '{
  "call_id": "1464927526043145564",
  "dimensions": ["discovery"]
}'
```

## Troubleshooting

### Missing Environment Variables

**Symptom**: Server fails with "Missing required environment variables: ..."

**Solution**:
1. Verify `.env` file exists in project root (not in subdirectories)
2. Check file contains all required variables:
   ```bash
   grep -E "^(GONG_API_KEY|GONG_API_SECRET|ANTHROPIC_API_KEY|DATABASE_URL)" .env
   ```
3. Ensure no trailing spaces or quotes around values
4. Test loading manually:
   ```bash
   uv run python -c "from coaching_mcp.shared import settings; print(settings.gong_api_key[:10])"
   ```

### Database Connection Issues

**Symptom**: "Database connection failed" or timeout errors

**Solutions**:

1. **Verify sslmode=require for Neon**:
   ```bash
   # DATABASE_URL must include ?sslmode=require
   echo $DATABASE_URL
   # Should look like: postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require
   ```

2. **Test connection with psql**:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

3. **Check Neon dashboard**:
   - Verify database is not suspended
   - Check connection limits (5-20 concurrent connections)
   - Confirm IP allowlist includes your IP (if configured)

4. **Use dev mode to skip schema validation**:
   ```bash
   # If tables are missing but you want to test other features
   uv run mcp-server-dev
   ```

### Gong API Rate Limits

**Symptom**: 429 Too Many Requests errors during validation or tool calls

**Solutions**:

1. **Use development mode** to skip startup validation:
   ```bash
   uv run mcp-server-dev
   ```

2. **Check Gong API rate limits**:
   - Gong limits: 3 requests/second, 10,000 requests/day
   - Validation uses 1 request at startup
   - Each `analyze_call` uses 1-2 requests

3. **Enable caching** to reduce API calls:
   ```python
   # Tools use cache by default
   analyze_call(call_id="...", use_cache=True)  # Default
   ```

### Port Already in Use

**Symptom**: Server fails to start with "Address already in use" error

**Solutions**:

1. **Find process using port 8000**:
   ```bash
   lsof -ti:8000
   ```

2. **Kill existing process**:
   ```bash
   kill $(lsof -ti:8000)
   ```

3. **Or use a different port** (edit `coaching_mcp/shared/config.py`):
   ```python
   webhook_port: int = Field(default=8001, description="Webhook server port")
   ```

### Anthropic API Errors

**Symptom**: "Anthropic API key validation failed" or tool calls fail

**Solutions**:

1. **Verify API key format**:
   ```bash
   # Should start with sk-ant-
   echo $ANTHROPIC_API_KEY | cut -c1-7
   # Output: sk-ant-
   ```

2. **Test API key**:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   ```

3. **Check rate limits and quotas** in Anthropic Console:
   - https://console.anthropic.com/settings/usage

### Import Errors

**Symptom**: "ModuleNotFoundError" when starting server

**Solutions**:

1. **Reinstall dependencies**:
   ```bash
   uv sync --reinstall
   ```

2. **Verify package installation**:
   ```bash
   uv pip list | grep -E "(fastmcp|anthropic|psycopg2)"
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.11+
   ```

## Deployment

### Local Development vs Horizon Deployment

| Aspect | Local Development | Horizon Deployment |
|--------|------------------|-------------------|
| Environment | `.env` file in project root | Environment variables in Horizon UI |
| Startup command | `uv run mcp-server-dev` | Automated by Horizon |
| Validation | Relaxed (use `--dev` flag) | Full validation required |
| Database | Neon cloud (shared) | Neon cloud (same instance) |
| Logs | Terminal output | Horizon logs viewer |
| Debugging | IDE breakpoints, print statements | Structured logging only |

### Deploying to Horizon

1. **Prepare environment variables** for Horizon UI:
   ```
   GONG_API_KEY=<your_key>
   GONG_API_SECRET=<your_secret>
   GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
   ANTHROPIC_API_KEY=sk-ant-<your_key>
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
   ```

2. **Test with production validation** before deploying:
   ```bash
   # Must pass all checks
   uv run mcp-server
   ```

3. **Deploy via Horizon UI**:
   - Runtime: Python 3.11
   - Command: `uv`
   - Args: `["run", "mcp-server"]`  # NOT mcp-server-dev
   - Working Directory: `/app`

4. **Monitor deployment**:
   - Check Horizon logs for "MCP server ready - 3 tools registered"
   - Verify health endpoint: `curl https://<horizon-url>/health`

### Environment Variables Reference

**Required:**

| Variable | Description | Example |
|----------|-------------|---------|
| `GONG_API_KEY` | Gong access key | `UQ4SK2LPUPBCFN7Q...` |
| `GONG_API_SECRET` | Gong secret key (JWT) | `eyJhbGciOiJIUzI1NiJ9...` |
| `GONG_API_BASE_URL` | Tenant-specific Gong URL | `https://us-79647.api.gong.io/v2` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-api03-...` |
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` |

**Optional:**

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `ENABLE_CACHING` | Enable intelligent caching | `true` |
| `CACHE_TTL_DAYS` | Cache expiration in days | `90` |
| `SKIP_VALIDATION` | Skip all startup validation | `false` |

### Getting API Keys

1. **Gong API Keys**:
   - Go to: https://gong.app.gong.io/settings/api/authentication
   - Create new API key pair
   - Save both access key and secret key (JWT token)

2. **Anthropic API Key**:
   - Go to: https://console.anthropic.com/settings/keys
   - Create new API key
   - Copy key (starts with `sk-ant-`)

3. **Neon Database URL**:
   - Go to: https://console.neon.tech
   - Navigate to your project
   - Copy connection string from dashboard
   - Ensure it includes `?sslmode=require`

## Full-Stack Testing

How to run the complete application stack locally for integration testing.

### Three-Terminal Setup

**Terminal 1: Backend Server**
```bash
cd /Users/gcoyne/src/prefect/call-coach

# Start FastMCP server on port 8000
uv run mcp-server-dev

# Wait for: "🚀 MCP server ready - 3 tools registered"
```

**Terminal 2: Frontend Application**
```bash
cd /Users/gcoyne/src/prefect/call-coach/frontend

# Install dependencies (first time only)
npm install

# Start Next.js dev server on port 3000
npm run dev

# Wait for: "✓ Ready in 1.5s"
```

**Terminal 3: Testing/Development**
```bash
# Use this terminal for:
# - Running tests
# - Checking logs
# - Testing API endpoints
curl http://localhost:8000/health
```

### Frontend-Backend Connection

The frontend connects to the backend via the `NEXT_PUBLIC_MCP_BACKEND_URL` environment variable:

**Configure in `frontend/.env.local`**:
```bash
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
```

**Verify connection**:
1. Open browser to http://localhost:3000
2. Open DevTools Network tab
3. Navigate to any page that uses MCP tools
4. Verify requests go to `http://localhost:8000/...`

**Example API Request**:
```bash
# From frontend to backend
curl http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{"call_id": "1464927526043145564"}'
```

### Common Integration Issues

**Frontend shows "Backend not available"**:
- Check backend is running: `curl http://localhost:8000/health`
- Verify `NEXT_PUBLIC_MCP_BACKEND_URL` in `frontend/.env.local`
- Check browser console for CORS errors

**API calls return 404**:
- Verify endpoint path matches FastMCP routes
- Check backend logs for request handling
- Ensure MCP protocol is being used correctly

**Slow response times**:
- Use dev mode to skip expensive validations
- Enable caching for repeated analyses
- Check database query performance in logs

## Performance Tips

### Faster Development Cycle

1. **Use dev mode** to skip expensive validations:
   ```bash
   uv run mcp-server-dev  # 2s startup vs 8s
   ```

2. **Enable caching** to avoid re-analyzing same calls:
   ```python
   analyze_call(call_id="...", use_cache=True, force_reanalysis=False)
   ```

3. **Use minimal dimensions** during testing:
   ```python
   # Instead of analyzing all dimensions
   analyze_call(call_id="...", dimensions=["discovery"])
   ```

### Monitoring Performance

**Check startup time**:
```bash
time uv run mcp-server-dev
# Target: < 3 seconds in dev mode
```

**Check database query latency**:
```sql
-- In psql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Check API response times**:
```bash
# Time a tool call
time curl -X POST http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{"call_id": "1464927526043145564"}'
```

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Gong API Reference](https://gong.app.gong.io/settings/api/documentation)
- [Anthropic API Docs](https://docs.anthropic.com)
- [Neon Postgres Docs](https://neon.tech/docs)

## Support

For questions or issues:
1. Check Troubleshooting section above
2. Review logs for specific error messages
3. Test with minimal examples to isolate the issue
4. Contact the platform team with reproduction steps
