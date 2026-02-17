# Call Coach Backend Development Guide

FastMCP server for AI-powered sales call coaching. This guide covers local development, testing, and deployment.

## Coaching Framework: Five Wins

All coaching analysis uses the **Five Wins** framework - a unified approach that replaces methodology-specific rubrics (SPICED, Challenger, Sandler, MEDDIC).

### The Five Wins

| Win            | Weight | Exit Criteria                                        |
| -------------- | ------ | ---------------------------------------------------- |
| **Business**   | 35%    | Budget and resources allocated to evaluate/implement |
| **Technical**  | 25%    | "Vendor of choice" from technical evaluators         |
| **Security**   | 15%    | InfoSec/Architecture formal approval                 |
| **Commercial** | 15%    | Exec sponsor approval on scope and commercials       |
| **Legal**      | 10%    | Contract signed                                      |

### Key Principles

- **No methodology jargon** in coaching output (no SPICED, Challenger, etc.)
- **One actionable recommendation** per call
- **Feedback tied to specific call moments** with timestamps
- **Call type determines primary win focus** (discovery→Business, demo→Technical, etc.)

### Configuration

- Feature flag: `USE_FIVE_WINS_UNIFIED` (default: `True`)
- Rubric: `analysis/rubrics/five_wins_unified.py`
- Models: `analysis/models/five_wins.py`
- Prompts: `analysis/prompts/five_wins_prompt.py`

## Development Rules

### CRITICAL: Never skip tests of any kind

- **NO SKIPPING**: Never use `SKIP=jest-quick`, `SKIP=pytest-quick`, or any
  other mechanism to skip tests during commits
- **ALL TESTS MUST PASS**: If tests fail, fix them - don't skip them
- **FIX THE ROOT CAUSE**: When tests fail, fix the underlying issue, not just
  the test
- **PRE-EXISTING FAILURES**: If tests were failing before your changes, fix
  them as part of your work
- **TEST INFRASTRUCTURE**: If test infrastructure is broken (mocks, setup,
  etc.), fix it properly
- **NO EXCEPTIONS**: This rule applies to all test types: unit tests,
  integration tests, E2E tests, linting, type checking

Tests are the safety net that prevents bugs from reaching production.
Skipping them is never acceptable.

## Quick Start

Get the backend running locally in under 5 minutes.

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Access to Neon Postgres database
- Anthropic API key

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
   # Required: ANTHROPIC_API_KEY, DATABASE_URL
   ```

3. **Start the REST API server** (Required for frontend):

   ```bash
   # Terminal 1: Start REST API server
   uv run python api/rest_server.py

   # You should see:
   # INFO: Started server process [xxxxx]
   # INFO: Application startup complete
   # INFO: Uvicorn running on http://0.0.0.0:8000
   ```

4. **Verify health check**:

   ```bash
   curl http://localhost:8000/health
   # {"status":"ok","service":"call-coaching-api","tools":5}
   ```

### Optional: MCP Server for Claude Desktop

If you want to use the tools directly from Claude Desktop (not required for web app):

```bash
# Terminal 2: Start MCP server (stdio protocol)
uv run python -m coaching_mcp.server --dev

# You should see:
# ============================================================
# Starting Call Coaching MCP Server
# 🏗️  Dev mode: skipping expensive validations
# ============================================================
#
# 🔍 Running pre-flight validation checks...
# ✓ All required environment variables present
# ✓ Database connection successful (dev mode - schema not validated)
# ✓ Anthropic API key validated
#
# ✅ All validation checks passed!
# ============================================================
# 🚀 MCP server ready - 5 tools registered
# ============================================================
```

## Architecture

### Two-Tier Backend Architecture

The application has two backend components:

```
Frontend (Next.js :3000)
    ↓ HTTP POST
REST API Server (:8000)     ← api/rest_server.py
    ↓ Function Calls
MCP Server (stdio)          ← coaching_mcp/server.py
    ↓ SQL Queries
Database (Neon PostgreSQL)
```

**Why two servers?**

- **REST API Server**: Bridges HTTP ↔ MCP tools for the Next.js frontend
- **MCP Server**: FastMCP stdio server for Claude Desktop integration
- Frontend requires HTTP, MCP uses stdio protocol
- REST API adds middleware (rate limiting, compression, auth)

### Project Structure

```
call-coach/
├── api/
│   ├── rest_server.py           # FastAPI HTTP bridge (port 8000)
│   ├── v1/                      # Versioned API routes
│   │   ├── calls.py             # Call CRUD endpoints
│   │   ├── opportunities.py     # Opportunity endpoints
│   │   ├── sync.py              # BigQuery sync trigger endpoint
│   │   └── tools.py             # MCP tool endpoints
│   └── middleware/              # Rate limiting, compression
├── analysis/
│   ├── engine.py                # Core analysis engine
│   ├── rubrics/
│   │   └── five_wins_unified.py # Five Wins rubric definitions
│   ├── models/
│   │   └── five_wins.py         # Pydantic models for coaching output
│   ├── prompts/
│   │   └── five_wins_prompt.py  # LLM prompts for Five Wins analysis
│   ├── consolidation/           # Post-processing (narrative, action selection)
│   └── ab_testing.py            # A/B test infrastructure
├── coaching_mcp/
│   ├── server.py                # FastMCP stdio server
│   ├── shared/
│   │   └── config.py            # Environment configuration
│   └── tools/
│       ├── analyze_call.py      # Call analysis tool
│       ├── get_rep_insights.py  # Rep performance tool
│       └── search_calls.py      # Call search tool
├── scripts/
│   ├── sync_bigquery_data.py    # BigQuery → Postgres sync
│   └── migrate_to_five_wins.py  # Five Wins migration CLI
├── db/
│   ├── connection.py            # Database connection pool
│   ├── queries.py               # SQL queries
│   └── models.py                # Pydantic models
└── frontend/
    ├── app/
    │   ├── api/cron/            # Vercel cron handlers
    │   │   └── bigquery-sync/   # Scheduled data sync
    │   └── ...                  # Next.js 14 app router pages
    ├── components/coaching/
    │   ├── NarrativeSummary.tsx     # Call narrative display
    │   ├── PrimaryActionCard.tsx    # Single action recommendation
    │   └── FiveWinsScoreCard.tsx    # Win progress visualization
    └── lib/
        └── mcp-client.ts        # HTTP client for REST API
```

### Tools Overview

| Tool                    | Purpose                                           | Key Features                                                |
| ----------------------- | ------------------------------------------------- | ----------------------------------------------------------- |
| `analyze_call`          | Deep-dive coaching analysis of a specific call    | Five Wins scoring, narrative summary, single primary action |
| `get_rep_insights`      | Performance trends and coaching history for a rep | Score trends, skill gaps, improvement tracking              |
| `search_calls`          | Find calls matching specific criteria             | Complex filters, date ranges, objection types               |
| `get_coaching_feed`     | Coaching highlights across team                   | Recent insights, win progress, team patterns                |
| `get_learning_insights` | Learning recommendations for reps                 | Personalized skill development, resource suggestions        |

### Database Schema

The backend uses Neon Postgres with the following key tables:

- **calls**: Call metadata (ID, title, date, participants)
- **speakers**: Speaker information and roles
- **transcripts**: Call transcripts with timestamps
- **coaching_sessions**: Analysis results and coaching feedback
- **coaching_dimensions**: Dimension-specific scores and insights
- **opportunities**: Salesforce opportunities (synced from BigQuery)
- **sync_status**: Tracks last sync timestamp for incremental updates
- **ab_test_results**: A/B test metrics for pipeline comparison

### Integration Flows

**Web Application Flow:**

```
Frontend → HTTP POST → REST API → MCP Tools → Database/APIs
```

**Claude Desktop Flow:**

```
Claude Desktop → MCP Protocol (stdio) → MCP Server → Database/APIs
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

- Only validates basic database connection (no table schema check)
- Faster startup (~2 seconds vs ~5 seconds)
- Use for rapid iteration on tool logic

**Production Mode** (`uv run mcp-server`):

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
   grep -E "^(ANTHROPIC_API_KEY|DATABASE_URL)" .env
   ```

3. Ensure no trailing spaces or quotes around values
4. Test loading manually:

   ```bash
   uv run python -c "from coaching_mcp.shared import settings; print(settings.anthropic_api_key[:10])"
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
   - <https://console.anthropic.com/settings/usage>

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

| Aspect          | Local Development                 | Horizon Deployment                  |
| --------------- | --------------------------------- | ----------------------------------- |
| Environment     | `.env` file in project root       | Environment variables in Horizon UI |
| Startup command | `uv run mcp-server-dev`           | Automated by Horizon                |
| Validation      | Relaxed (use `--dev` flag)        | Full validation required            |
| Database        | Neon cloud (shared)               | Neon cloud (same instance)          |
| Logs            | Terminal output                   | Horizon logs viewer                 |
| Debugging       | IDE breakpoints, print statements | Structured logging only             |

### Deploying to Horizon

1. **Prepare environment variables** for Horizon UI:

   ```
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
   - Args: `["run", "mcp-server"]` # NOT mcp-server-dev
   - Working Directory: `/app`

4. **Monitor deployment**:
   - Check Horizon logs for "MCP server ready - 5 tools registered"
   - Verify health endpoint: `curl https://<horizon-url>/health`

### Deploying Frontend to Vercel

The Next.js frontend is deployed to Vercel with cron jobs for data sync.

1. **Required environment variables** in Vercel dashboard (Settings > Environment Variables):

   ```
   # Database
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

   # Clerk Auth
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
   CLERK_SECRET_KEY=sk_live_...

   # Backend API
   NEXT_PUBLIC_MCP_BACKEND_URL=https://your-backend-url

   # Claude API (for insights)
   ANTHROPIC_API_KEY=sk-ant-api03-...

   # Cron authentication
   CRON_SECRET=<random-secure-token>

   # BigQuery (for data sync)
   BIGQUERY_PROJECT_ID=your-project
   BIGQUERY_CREDENTIALS={"type":"service_account",...}
   ```

2. **Cron job configuration** (in `vercel.json`):

   ```json
   {
     "crons": [
       {
         "path": "/api/cron/daily-sync",
         "schedule": "0 6 * * *"
       }
     ]
   }
   ```

3. **Deploy**:

   - Connect repo to Vercel project
   - Set environment variables in Vercel dashboard
   - Cron jobs run automatically on Vercel Pro/Enterprise plans

4. **Test cron locally** (requires `vercel login`):

   ```bash
   cd frontend && vercel dev
   curl http://localhost:3000/api/cron/daily-sync
   ```

### Environment Variables Reference

**Required:**

| Variable            | Description                       | Example                                                      |
| ------------------- | --------------------------------- | ------------------------------------------------------------ |
| `ANTHROPIC_API_KEY` | Claude API key                    | `sk-ant-api03-...`                                           |
| `DATABASE_URL`      | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` |

**Optional:**

| Variable                | Description                     | Default |
| ----------------------- | ------------------------------- | ------- |
| `LOG_LEVEL`             | Logging verbosity               | `INFO`  |
| `ENABLE_CACHING`        | Enable intelligent caching      | `true`  |
| `CACHE_TTL_DAYS`        | Cache expiration in days        | `90`    |
| `SKIP_VALIDATION`       | Skip all startup validation     | `false` |
| `USE_FIVE_WINS_UNIFIED` | Use Five Wins coaching pipeline | `true`  |
| `CRON_SECRET`           | Auth token for Vercel cron jobs | -       |

### Getting API Keys

1. **Anthropic API Key**:

   - Go to: <https://console.anthropic.com/settings/keys>
   - Create new API key
   - Copy key (starts with `sk-ant-`)

2. **Neon Database URL**:
   - Go to: <https://console.neon.tech>
   - Navigate to your project
   - Copy connection string from dashboard
   - Ensure it includes `?sslmode=require`

## Full-Stack Testing

How to run the complete application stack locally for integration testing.

### Three-Terminal Setup

**Terminal 1: REST API Server** (Required)

```bash
cd /Users/gcoyne/src/prefect/call-coach

# Start REST API server on port 8000
uv run python api/rest_server.py

# Wait for: "INFO: Uvicorn running on http://0.0.0.0:8000"
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

# Optional: Start MCP server for Claude Desktop integration
uv run python -m coaching_mcp.server --dev
```

### Frontend-Backend Connection

The frontend connects to the REST API server via the `NEXT_PUBLIC_MCP_BACKEND_URL` environment variable:

**Configure in `frontend/.env.local`**:

```bash
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
```

**Verify connection**:

1. Open browser to <http://localhost:3000>
2. Open DevTools Network tab
3. Navigate to any page that uses coaching tools
4. Verify requests go to `http://localhost:8000/tools/...`

**Example API Request**:

```bash
# Test REST API directly
curl http://localhost:8000/tools/get_rep_insights \
  -H "Content-Type: application/json" \
  -d '{"rep_email": "george@prefect.io", "time_period": "last_30_days"}'
```

### Common Integration Issues

**Frontend shows "MCP backend request failed" or connection errors**:

- **Check REST API is running**: `curl http://localhost:8000/health`
- **Verify correct server**: You need `api/rest_server.py`, NOT `coaching_mcp/server.py`
- **Check `.env` file exists**: Must be in project root with DATABASE_URL, API keys
- **Verify port**: REST API should be on port 8000

**"Missing required environment variables" error on startup**:

- Ensure `.env` file is in `/Users/gcoyne/src/prefect/call-coach/` (project root)
- Check all required variables are set: `ANTHROPIC_API_KEY`, `DATABASE_URL`
- Test loading: `uv run python -c "from coaching_mcp.shared import settings; print('OK')"`

**API calls return 404**:

- Verify endpoint exists in `api/rest_server.py` or `api/v1/`
- Check REST API logs for request handling
- Ensure you're calling `/tools/*` endpoints not `/mcp/*`

**Database connection errors**:

- Verify `DATABASE_URL` includes `?sslmode=require` for Neon
- Test connection: `psql $DATABASE_URL -c "SELECT 1"`
- Use dev mode to skip schema validation: `uv run python -m coaching_mcp.server --dev`

**Slow response times or empty data**:

- Database might be empty - check if calls/coaching sessions exist
- Enable caching for repeated analyses
- Check database query performance in logs

## Performance Tips

### Faster Development Cycle

1. **Use dev mode** to skip expensive validations:

   ```bash
   uv run mcp-server-dev  # 2s startup vs 5s
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

## Data Sync

### BigQuery to Postgres Sync

Data from Salesforce (opportunities) and Gong (calls) flows through Fivetran to BigQuery, then is synced to Neon Postgres via DLT.

**Automatic sync (Vercel Cron):**

- Schedule: Every 6 hours (`0 */6 * * *`)
- Endpoint: `POST /api/cron/bigquery-sync`
- Config: `frontend/vercel.json`

**Manual sync:**

```bash
# Incremental sync (only new/modified records)
uv run python scripts/sync_bigquery_data.py

# Full sync (re-sync all records)
uv run python scripts/sync_bigquery_data.py --full-sync

# Sync only opportunities
uv run python scripts/sync_bigquery_data.py --opportunities-only

# Sync only calls
uv run python scripts/sync_bigquery_data.py --calls-only
```

**Via REST API:**

```bash
# Trigger sync from backend
curl -X POST http://localhost:8000/api/v1/sync/bigquery \
  -H "Content-Type: application/json" \
  -d '{"full_sync": false, "sync_opportunities": true, "sync_calls": true}'

# Check sync status
curl http://localhost:8000/api/v1/sync/status
```

### Data Sources

| Entity        | BigQuery Table              | Sync Frequency |
| ------------- | --------------------------- | -------------- |
| Opportunities | `salesforce_ft.opportunity` | Every 6 hours  |
| Calls         | `gongio_ft.call`            | Every 1 hour   |

## Five Wins Migration

To enable/disable the Five Wins pipeline:

```bash
# Enable Five Wins (default)
uv run python scripts/migrate_to_five_wins.py enable

# Rollback to legacy pipeline
uv run python scripts/migrate_to_five_wins.py rollback

# Validate pipeline before deployment
uv run python scripts/migrate_to_five_wins.py validate
```

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [DLT Documentation](https://dlthub.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com)
- [Neon Postgres Docs](https://neon.tech/docs)

## Support

For questions or issues:

1. Check Troubleshooting section above
2. Review logs for specific error messages
3. Test with minimal examples to isolate the issue
4. Contact the platform team with reproduction steps
