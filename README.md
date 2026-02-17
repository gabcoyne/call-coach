# Call Coaching Agent for Prefect Sales Teams

[![codecov](https://codecov.io/gh/gabcoyne/call-coach/branch/main/graph/badge.svg)](https://codecov.io/gh/gabcoyne/call-coach)
[![Backend Tests](https://github.com/gabcoyne/call-coach/actions/workflows/test-backend.yml/badge.svg)](https://github.com/gabcoyne/call-coach/actions/workflows/test-backend.yml)
[![Frontend Tests](https://github.com/gabcoyne/call-coach/actions/workflows/test-frontend.yml/badge.svg)](https://github.com/gabcoyne/call-coach/actions/workflows/test-frontend.yml)

AI-powered sales coaching system that analyzes call transcripts for SEs, AEs, and CSMs across Prefect and Horizon products.

## Architecture

- **FastMCP Server**: On-demand coaching tools via MCP protocol
- **DLT Pipeline**: Syncs call data from BigQuery (Fivetran-sourced Gong data) to Neon Postgres
- **Claude API**: AI-powered call analysis and coaching generation
- **Neon Postgres**: Coaching data, metrics, and knowledge base

## Data Pipeline

Call data flows from Gong through the following path:

```
Gong → Fivetran → BigQuery → DLT Pipeline → Neon Postgres
```

The DLT pipeline runs hourly (via cron) and syncs:

- **Calls**: Call metadata, transcripts, and speaker information
- **Emails**: Email threads with sender/recipient data
- **Opportunities**: Salesforce opportunity data with call linkages

**Data freshness**: ~1 hour lag from Gong to available in application.

### Running the DLT Sync

```bash
# Run sync manually
uv run python -m flows.dlt_sync_flow

# Schedule via cron (hourly)
0 * * * * cd /path/to/call-coach && uv run python -m flows.dlt_sync_flow >> /var/log/dlt-sync.log 2>&1
```

## Key Features

- **Intelligent Caching**: 60-80% cost reduction through transcript hashing and rubric versioning
- **Parallel Analysis**: 4x faster processing with concurrent dimension analysis
- **Long Call Support**: Sliding window chunking for 60+ minute calls
- **Trend Analysis**: Performance tracking across reps and time periods
- **Comprehensive Testing**: 70%+ code coverage with unit, integration, and E2E tests

## Project Structure

```
call-coach/
├── db/                 # Database schema and migrations
├── dlt_pipeline/       # DLT sources for BigQuery to Postgres sync
├── analysis/           # Claude-powered coaching analysis engine
├── knowledge/          # Coaching rubrics and product documentation
├── coaching_mcp/       # FastMCP server and tools
├── flows/              # Data sync flows
├── reports/            # Report generation and templates
└── tests/              # Test suite
```

## Prerequisites

- **Python 3.11+**: Required for FastMCP backend server
- **uv**: Modern Python package manager ([installation guide](https://github.com/astral-sh/uv))
- **Neon Postgres Database**: Cloud PostgreSQL instance with SSL ([Neon Console](https://console.neon.tech))
- **Node.js 18+**: For Next.js frontend (if doing full-stack development)

## Setup

1. **Install uv** (Python package manager):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - ANTHROPIC_API_KEY (from Anthropic Console)
   # - DATABASE_URL (from Neon dashboard, must include ?sslmode=require)
   ```

3. **Initialize database** (first time only):

   ```bash
   psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
   ```

4. **Load knowledge base** (first time only):

   ```bash
   uv run python -m knowledge.loader
   ```

5. **Run DLT sync** (populates data from BigQuery):

   ```bash
   uv run python -m flows.dlt_sync_flow
   ```

6. **Start the REST API server** (for frontend integration):

   ```bash
   # Start REST API at http://localhost:8000
   ./scripts/start-rest-api.sh

   # Or manually with uvicorn
   uv run uvicorn api.rest_server:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Start the Next.js frontend** (optional):

   ```bash
   cd frontend
   npm install
   npm run dev
   # Frontend available at http://localhost:3000
   ```

8. **Run FastMCP server** (for Claude Desktop MCP integration):

   ```bash
   # Development mode (recommended for local dev)
   uv run mcp-server-dev

   # Or production mode with full validation
   uv run mcp-server
   ```

## Cloud Deployment (FastMCP + Prefect Horizon)

The MCP server can be deployed to **FastMCP Cloud** via **Prefect Horizon** for team-wide access without local setup.

### Horizon Prerequisites

- Prefect Horizon workspace: `https://horizon.prefect.io/prefect-george/servers`
- FastMCP API key: `fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc`
- All environment variables from `.env` file

### Deployment Steps

1. **Run pre-deployment validation**:

   ```bash
   ./.fastmcp/deploy.sh
   ```

   This verifies dependencies, configuration files, and local server initialization.

2. **Navigate to Horizon MCP Servers**:

   - Go to: <https://horizon.prefect.io/prefect-george/servers>
   - Click "Create New MCP Server"

3. **Configure server settings**:

   - **Name**: `call-coach`
   - **Runtime**: Python 3.11
   - **Command**: `uv`
   - **Args**: `["run", "python", "coaching_mcp/server.py"]`
   - **Working Directory**: `/app`

4. **Set environment variables** (mark as secrets):

   ```
   ANTHROPIC_API_KEY=sk-ant-your_key_here
   DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require
   ```

5. **Upload project files**:

   - Option A: Connect GitHub repository
   - Option B: Upload project directory (zip entire `call-coach/` folder)

6. **Deploy**:

   - Click "Deploy" button
   - Wait for status to show "Ready" (should complete within 30 seconds)
   - Check logs for validation success messages:

     ```
     ✓ All required environment variables present
     ✓ Database connection successful
     ✓ Anthropic API key validated
     ✓ MCP server ready - 5 tools registered
     ```

### Required Environment Variables

| Variable            | Description         | Example                            |
| ------------------- | ------------------- | ---------------------------------- |
| `ANTHROPIC_API_KEY` | Claude API key      | `sk-ant-api03-...`                 |
| `DATABASE_URL`      | Neon PostgreSQL URL | `postgresql://...?sslmode=require` |

**Optional Variables:**

- `LOG_LEVEL`: Logging verbosity (default: `INFO`)
- `SLACK_WEBHOOK_URL`: For sync failure notifications

### Testing Deployment

Once deployed, test via Claude Desktop:

```
Test 1 - Analyze a call:
> Can you analyze call 1464927526043145564?

Test 2 - Get rep insights:
> Show me performance insights for sarah.jones@prefect.io over the last quarter

Test 3 - Search calls:
> Find all discovery calls from last month with pricing objections where the rep scored below 70
```

### Performance Characteristics

- **Cold start**: 5-10 seconds (first invocation after idle)
- **Warm start**: <2 seconds (subsequent invocations)
- **Validation time**: 2-3 seconds (database + Anthropic checks)
- **Concurrent users**: Supports 5-20 simultaneous tool invocations (Neon connection pool)

### Troubleshooting

#### Database Connection Timeout

**Symptom**: `✗ Database connection failed`

**Solutions**:

1. Verify `DATABASE_URL` includes `?sslmode=require` suffix
2. Check Neon dashboard for connection pool limits (5-20 max)
3. Confirm IP allowlist in Neon includes Horizon/FastMCP Cloud IPs
4. Test locally: `psql $DATABASE_URL -c "SELECT 1"`

#### Cold Start Latency >30s

**Symptom**: Server status shows "Failed" with timeout error

**Solutions**:

1. Check if large dependencies (tiktoken models) are causing slow imports
2. Review Horizon logs for specific bottleneck during startup
3. Consider pre-warming with Horizon warmup configuration
4. Verify all validation checks complete within 15 seconds

#### Tools Not Appearing in Claude Desktop

**Symptom**: MCP tools not visible in Claude Desktop

**Solutions**:

1. Restart Claude Desktop completely
2. Verify Horizon server status is "Ready" (not "Failed" or "Deploying")
3. Check Horizon logs for tool registration success
4. Confirm FastMCP API key is valid and not expired

### Credential Rotation

To rotate Anthropic API key:

1. Generate new key at: <https://console.anthropic.com/settings/keys>
2. Update in Horizon UI: Navigate to server settings → Edit environment variables
3. Redeploy server

**Recommended rotation schedule**: Quarterly (every 90 days)

### Monitoring

**Horizon Logs**:

- View real-time logs in Horizon UI
- Look for validation success messages on startup
- Monitor for repeated errors

**Neon Dashboard**:

- Track connection pool usage (target: <50% utilization)
- Monitor query latency (target: <100ms for simple queries)
- Alert if connections exceed 15/20 limit

**Anthropic Usage Dashboard**:

- Track daily token usage and costs
- Expected: $10-15/day with cache hit rate of 60-80%
- Alert if daily cost exceeds $25 (possible cache invalidation issue)

## Usage

### On-Demand Coaching (MCP Tools)

Use with Claude Desktop (local or cloud-deployed):

```
"Analyze call abc-123 and focus on discovery quality"
"Show me Sarah's performance trends this month"
"Compare calls xyz-456 and xyz-789 for objection handling"
```

## Local Development

### Quick Start

Get the MCP backend server running locally in 3 steps:

1. **Install uv** (Python package manager):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Setup environment**:

   ```bash
   # Ensure .env exists in project root with required credentials
   # Required: ANTHROPIC_API_KEY, DATABASE_URL
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the server**:

   ```bash
   # Development mode (fast startup, relaxed validation)
   uv run mcp-server-dev

   # You should see:
   # 🚀 MCP server ready - 5 tools registered
   # Server running on http://localhost:8000
   ```

For detailed backend development guide, see [CLAUDE.md](CLAUDE.md).

### Full Stack Development (Backend + Frontend)

**Terminal 1 - MCP Backend Server**:

```bash
# Ensure you're in the project root
cd /Users/gcoyne/src/prefect/call-coach

# Run the FastMCP server on port 8000
uv run python coaching_mcp/server.py

# You should see:
# ✓ Database connection successful
# ✓ Anthropic API key validated
# 🚀 MCP server ready - 5 tools registered
# Server running on http://localhost:8000
```

**Terminal 2 - Next.js Frontend**:

```bash
# Navigate to frontend directory
cd /Users/gcoyne/src/prefect/call-coach/frontend

# Install dependencies (first time only)
npm install

# Start development server on port 3000
npm run dev

# You should see:
# ▲ Next.js 15.1.6
# - Local:    http://localhost:3000
# ✓ Ready in 1.5s
```

**Terminal 3 - Watch Tests (Optional)**:

```bash
cd /Users/gcoyne/src/prefect/call-coach/frontend
npm run test:watch
```

### Environment Setup

**Backend** (`.env` in project root):

```bash
# Required for MCP backend
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require
```

**Frontend** (`frontend/.env.local`):

```bash
# Required for Next.js frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000

# Optional - Clerk URLs (defaults shown)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### Development Workflow

1. **Backend changes**: Edit files in `coaching_mcp/`, `analysis/`, or `db/`

   - Server auto-reloads on file changes (if using uvicorn with --reload)
   - Test with: `pytest tests/`

2. **Frontend changes**: Edit files in `frontend/app/`, `frontend/components/`, or `frontend/lib/`

   - Next.js hot-reloads automatically
   - Test with: `npm run test`

3. **Database changes**:

   ```bash
   # Apply migration
   psql $DATABASE_URL -f db/migrations/00X_migration_name.sql

   # Verify
   psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
   ```

4. **Test full flow**:
   - Open browser: <http://localhost:3000>
   - Sign in with Clerk (create test user first)
   - Navigate to Dashboard, Search, or Feed
   - Backend API calls go to <http://localhost:8000>

### Common Development Tasks

**Run Python tests**:

```bash
pytest tests/ -v
```

**Run frontend tests**:

```bash
cd frontend
npm run test:coverage
```

**Analyze bundle size**:

```bash
cd frontend
npm run analyze
```

**Check Python dependencies**:

```bash
uv tree
```

**Update frontend dependencies**:

```bash
cd frontend
npm outdated
npm update
```

**Format code**:

```bash
# Python (if black/ruff configured)
black coaching_mcp/ analysis/ db/

# Frontend
cd frontend
npm run lint
```

### Local Troubleshooting

**Backend won't start**:

- Check `.env` has all required variables
- Verify database connection: `psql $DATABASE_URL -c "SELECT 1"`
- Review logs for specific error

**Frontend won't start**:

- Check `frontend/.env.local` exists with Clerk keys
- Run `npm install` to ensure dependencies are installed
- Clear Next.js cache: `rm -rf frontend/.next`
- Check port 3000 isn't already in use: `lsof -ti:3000`

**API calls failing** (Frontend → Backend):

- Verify backend is running on <http://localhost:8000>
- Check `NEXT_PUBLIC_MCP_BACKEND_URL` in `frontend/.env.local`
- Open browser DevTools Network tab, check request/response
- Review CORS settings if needed

**Database connection issues**:

- Confirm Neon database is running
- Check DATABASE_URL includes `?sslmode=require`
- Verify IP allowlist in Neon dashboard
- Test connection: `psql $DATABASE_URL`

**DLT sync issues**:

- Check BigQuery credentials are configured
- Verify DLT state directory (`.dlt/`) has write permissions
- If state is corrupted, delete `.dlt/state.json` to force full refresh
- Check logs for specific BigQuery or Postgres errors

## Testing

The project uses a comprehensive test suite with unit, integration, and end-to-end tests for both backend (Python) and frontend (TypeScript/React). We follow test-driven development (TDD) practices.

### Running Tests

**Backend tests:**

```bash
# Run all backend tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Frontend tests:**

```bash
cd frontend

# Run all frontend tests
npm test

# Run with coverage
npm run test:coverage
open coverage/lcov-report/index.html  # View coverage report

# Run in watch mode (re-runs on file changes)
npm run test:watch
```

### Test Organization

**Backend structure:**

```
tests/
├── unit/              # Fast, isolated tests
│   ├── analysis/      # Analysis engine tests
│   ├── api/           # API endpoint tests
│   ├── cache/         # Caching tests
│   └── mcp/           # MCP tools tests
├── integration/       # Component interaction tests
├── e2e/               # End-to-end workflow tests
├── performance/       # Load and performance tests
└── conftest.py        # Shared fixtures
```

**Frontend structure:**

```
frontend/
├── __tests__/                    # Top-level tests
├── components/ui/__tests__/      # Component tests
├── lib/__tests__/                # Utility tests
├── lib/hooks/__tests__/          # React hooks tests
└── app/api/*/__tests__/          # API route tests
```

### Coverage Targets

The project enforces minimum coverage thresholds:

**Backend:** 85% minimum coverage
**Frontend:** 75% minimum coverage

Coverage reports are generated automatically and block CI if thresholds aren't met.

### Pre-commit Hooks

Tests run automatically before commits via pre-commit hooks.

**Manual pre-commit run:**

```bash
pre-commit run --all-files
```

### CI/CD Pipeline

Tests run automatically on:

- Every push to `main` or `develop` branches
- Every pull request
- Manual workflow dispatch

**Required Checks**:

- Backend: Lint, type check, unit tests (70% coverage)
- Frontend: Lint, unit tests (70% coverage), build check
- Both must pass before merge

### Coverage Reports

View coverage reports:

- **Codecov Dashboard**: <https://codecov.io/gh/gabcoyne/call-coach>
- **Local HTML Report**: `pytest --cov --cov-report=html` then open `htmlcov/index.html`
- **Frontend Coverage**: `npm run test:coverage` then open `frontend/coverage/lcov-report/index.html`

**Coverage Targets**:

- Backend: 70% minimum (target: 80%)
- Frontend: 70% minimum (target: 75%)

## Cost Optimization

- **Baseline**: ~$1,787/month (100 calls/week, no optimization)
- **Optimized**: ~$317/month (82% reduction)
- **Per call**: $3.17 (vs. $17.87 baseline)

Key optimizations:

1. Intelligent caching (60-80% cache hit rate)
2. Prompt caching (50% input token reduction)
3. Parallel execution (4x faster, same cost)

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [MCP Tools Reference](docs/MCP_TOOLS.md)
- [Coaching Rubrics](docs/COACHING_RUBRICS.md)

## License

Proprietary - Prefect Technologies, Inc.
