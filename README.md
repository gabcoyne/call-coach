# Gong Call Coaching Agent for Prefect Sales Teams

AI-powered sales coaching system that analyzes Gong calls for SEs, AEs, and CSMs across Prefect and Horizon products.

## Architecture

- **FastMCP Server**: On-demand coaching tools via MCP protocol
- **Prefect Flows on Horizon**: Webhook processing and scheduled batch reviews
- **Claude API**: AI-powered call analysis and coaching generation
- **Neon Postgres**: Coaching data, metrics, and knowledge base
- **Gong Integration**: Webhooks and API for call data

## Key Features

- **Intelligent Caching**: 60-80% cost reduction through transcript hashing and rubric versioning
- **Parallel Analysis**: 4x faster processing with concurrent dimension analysis
- **Long Call Support**: Sliding window chunking for 60+ minute calls
- **Real-time Ingestion**: Async webhook handling with <3s response time
- **Trend Analysis**: Performance tracking across reps and time periods

## Project Structure

```
call-coach/
├── db/                 # Database schema and migrations
├── gong/               # Gong API client and webhook handling
├── analysis/           # Claude-powered coaching analysis engine
├── knowledge/          # Coaching rubrics and product documentation
├── coaching_mcp/       # FastMCP server and tools
├── flows/              # Prefect flows for automation
├── reports/            # Report generation and templates
└── tests/              # Test suite
```

## Setup

1. **Install dependencies with uv**:
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize database**:
   ```bash
   psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
   ```

4. **Load knowledge base**:
   ```bash
   python -m knowledge.loader
   ```

5. **Run FastMCP server**:
   ```bash
   python coaching_mcp/server.py
   ```

6. **Deploy Prefect flows**:
   ```bash
   prefect deploy flows/process_new_call.py
   prefect deploy flows/weekly_review.py
   ```

## Cloud Deployment (FastMCP + Prefect Horizon)

The MCP server can be deployed to **FastMCP Cloud** via **Prefect Horizon** for team-wide access without local setup.

### Prerequisites

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
   - Go to: https://horizon.prefect.io/prefect-george/servers
   - Click "Create New MCP Server"

3. **Configure server settings**:
   - **Name**: `gong-call-coach`
   - **Runtime**: Python 3.11
   - **Command**: `uv`
   - **Args**: `["run", "python", "coaching_mcp/server.py"]`
   - **Working Directory**: `/app`

4. **Set environment variables** (mark as secrets):
   ```
   GONG_API_KEY=your_gong_access_key_here
   GONG_API_SECRET=your_gong_secret_key_jwt_here
   GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
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
     ✓ Gong API authentication successful
     ✓ Anthropic API key validated
     ✓ MCP server ready - 3 tools registered
     ```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GONG_API_KEY` | Gong access key | `UQ4SK2LPUPBCFN7Q...` |
| `GONG_API_SECRET` | Gong secret key (JWT) | `eyJhbGciOiJIUzI1NiJ9...` |
| `GONG_API_BASE_URL` | Tenant-specific URL | `https://us-79647.api.gong.io/v2` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-api03-...` |
| `DATABASE_URL` | Neon PostgreSQL URL | `postgresql://...?sslmode=require` |

**Optional Variables:**
- `GONG_WEBHOOK_SECRET`: For webhook signature verification
- `LOG_LEVEL`: Logging verbosity (default: `INFO`)

### Testing Deployment

Once deployed, test via Claude Desktop:

```
Test 1 - Analyze a call:
> Can you analyze Gong call 1464927526043145564?

Test 2 - Get rep insights:
> Show me performance insights for sarah.jones@prefect.io over the last quarter

Test 3 - Search calls:
> Find all discovery calls from last month with pricing objections where the rep scored below 70
```

### Performance Characteristics

- **Cold start**: 10-15 seconds (first invocation after idle)
- **Warm start**: <2 seconds (subsequent invocations)
- **Validation time**: 5-8 seconds (database + Gong + Anthropic checks)
- **Concurrent users**: Supports 5-20 simultaneous tool invocations (Neon connection pool)

### Troubleshooting

#### 401 Authentication Errors

**Symptom**: `✗ Gong API authentication failed`

**Solutions**:
1. Verify `GONG_API_KEY` and `GONG_API_SECRET` are correct
2. Confirm `GONG_API_BASE_URL` uses your tenant-specific URL (not generic `api.gong.io`)
3. Test credentials locally: `uv run python tests/test_gong_client_live.py`
4. Regenerate keys at: https://gong.app.gong.io/settings/api/authentication

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

To rotate Gong or Anthropic API keys:

1. Generate new keys:
   - **Gong**: https://gong.app.gong.io/settings/api/authentication
   - **Anthropic**: https://console.anthropic.com/settings/keys

2. Update in Horizon UI:
   - Navigate to server settings
   - Edit environment variables
   - Update `GONG_API_KEY`, `GONG_API_SECRET`, or `ANTHROPIC_API_KEY`
   - Save changes

3. Redeploy server:
   - Click "Redeploy" button
   - Verify new credentials pass validation checks

**Recommended rotation schedule**: Quarterly (every 90 days)

### Monitoring

**Horizon Logs**:
- View real-time logs in Horizon UI
- Look for validation success messages on startup
- Monitor for repeated 401 errors (credential issues)

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

### Weekly Reviews (Automated)

Scheduled every Monday at 6am PT via Prefect Horizon:
- Analyzes all calls from previous week
- Generates rep-specific coaching reports
- Sends team-wide insights to sales leadership

## Development

### Run tests
```bash
pytest tests/
```

### Local development with Docker Compose
```bash
docker-compose up
```

### Check cost metrics
```bash
python -m analysis.metrics
```

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
