# Opportunity Coaching View - Setup Guide

Complete instructions for local development and Vercel deployment of the Opportunity Coaching feature.

## Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) Python package manager
- Access to Neon PostgreSQL database
- Gong API credentials
- Anthropic API key

## Local Development Setup

### 1. Environment Configuration

Create `.env` file in project root (`/Users/gcoyne/src/prefect/call-coach/.env`):

```bash
# Gong API (required for sync)
GONG_API_KEY=<your_gong_access_key>
GONG_API_SECRET=<your_gong_secret_jwt>
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2

# Anthropic API (required for AI insights)
ANTHROPIC_API_KEY=sk-ant-api03-<your_key>

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require

# Optional
LOG_LEVEL=INFO
ENABLE_CACHING=true
```

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000

# Database connection (Next.js server components)
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require

# Clerk Authentication (if enabled)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# Cron job protection
CRON_SECRET=your-random-secret-string
```

### 2. Database Setup

The opportunity tables were created via migration. Verify they exist:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('opportunities', 'emails', 'call_opportunities', 'sync_status');

-- Check indexes
SELECT indexname FROM pg_indexes
WHERE tablename IN ('opportunities', 'emails', 'call_opportunities');
```

Expected tables:

- `opportunities` - Opportunity metadata from Gong
- `emails` - Email records linked to opportunities
- `call_opportunities` - Junction table linking calls to opportunities
- `sync_status` - Tracks last sync timestamp per entity type
- `opportunity_analysis_cache` - Caches AI analysis results

### 3. Start Backend Services

**Terminal 1: REST API Server** (required for frontend)

```bash
cd /Users/gcoyne/src/prefect/call-coach
uv run python api/rest_server.py

# Expected output:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2: Frontend Application**

```bash
cd /Users/gcoyne/src/prefect/call-coach/frontend
npm install  # First time only
npm run dev

# Expected output:
# Ready in 1.5s
# Local: http://localhost:3000
```

### 4. Initial Data Sync

Run the daily sync manually to populate opportunity data:

```bash
cd /Users/gcoyne/src/prefect/call-coach
uv run python -m flows.daily_gong_sync
```

This will:

1. Fetch opportunities from Gong API (modified since last sync)
2. Link existing calls to opportunities via `call_opportunities` junction
3. Fetch and store emails for each opportunity
4. Update `sync_status` table with timestamps

### 5. Verify Setup

1. **Check API health:**

   ```bash
   curl http://localhost:8000/health
   # {"status":"ok","service":"call-coaching-api","tools":5}
   ```

2. **Check opportunities API:**

   ```bash
   curl http://localhost:3000/api/opportunities
   # {"opportunities":[...],"pagination":{...}}
   ```

3. **Open UI:**
   - Navigate to <http://localhost:3000/opportunities>
   - Verify opportunity list displays
   - Click an opportunity to view details

## Feature Components

### Frontend Routes

| Route                 | Component           | Description                             |
| --------------------- | ------------------- | --------------------------------------- |
| `/opportunities`      | `OpportunitiesList` | Searchable, filterable opportunity list |
| `/opportunities/[id]` | `OpportunityDetail` | Detail page with timeline and insights  |

### API Endpoints

| Endpoint                           | Method | Description                     |
| ---------------------------------- | ------ | ------------------------------- |
| `/api/opportunities`               | GET    | List opportunities with filters |
| `/api/opportunities/[id]`          | GET    | Get opportunity detail          |
| `/api/opportunities/[id]/timeline` | GET    | Get paginated timeline          |
| `/api/opportunities/[id]/insights` | GET    | Get AI coaching insights        |
| `/api/cron/daily-sync`             | POST   | Trigger manual sync             |

### MCP Tools

| Tool                    | Description                                |
| ----------------------- | ------------------------------------------ |
| `analyze_opportunity`   | Holistic coaching analysis for opportunity |
| `get_learning_insights` | Compare rep to top performers              |

## Vercel Deployment

### 1. Environment Variables

Configure in Vercel Dashboard > Project Settings > Environment Variables:

```
# Production environment
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
GONG_API_KEY=...
GONG_API_SECRET=...
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
CRON_SECRET=<generate-secure-random-string>
NEXT_PUBLIC_MCP_BACKEND_URL=https://mcp.prefect.io
```

### 2. Cron Configuration

The daily sync is configured in `frontend/vercel.json`:

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

This runs daily at 6:00 AM UTC.

### 3. Deploy

```bash
cd frontend
vercel --prod
```

Or connect GitHub repo for automatic deployments on push.

### 4. Verify Deployment

1. **Check cron configuration:**

   ```bash
   curl https://your-domain.vercel.app/api/cron/daily-sync
   # Returns job config
   ```

2. **Monitor cron logs:**

   - Vercel Dashboard > Project > Functions > Logs
   - Filter by `/api/cron/daily-sync`

3. **Manual trigger (for testing):**

   ```bash
   curl -X POST https://your-domain.vercel.app/api/cron/daily-sync \
     -H "Authorization: Bearer $CRON_SECRET"
   ```

## Troubleshooting

### No Opportunities Showing

1. **Check sync ran:**

   ```sql
   SELECT * FROM sync_status WHERE entity_type = 'opportunities';
   ```

2. **Check for data:**

   ```sql
   SELECT COUNT(*) FROM opportunities;
   ```

3. **Re-run sync:**

   ```bash
   uv run python -m flows.daily_gong_sync
   ```

### Timeline Empty

1. **Check call linkages:**

   ```sql
   SELECT COUNT(*) FROM call_opportunities WHERE opportunity_id = '<opp-uuid>';
   ```

2. **Check emails:**

   ```sql
   SELECT COUNT(*) FROM emails WHERE opportunity_id = '<opp-uuid>';
   ```

3. **Verify calls exist in database:**
   - Calls must be imported via `import_calls.py` before linking

### Insights Not Loading

1. **Check Anthropic API key:**

   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   ```

2. **Check REST API logs:**

   - Look for errors in analyze_opportunity tool

3. **Clear cache:**

   ```sql
   DELETE FROM opportunity_analysis_cache WHERE opportunity_id = '<opp-uuid>';
   ```

### Cron Not Running

1. **Verify CRON_SECRET is set** in Vercel environment variables

2. **Check Vercel function logs** for errors

3. **Test manually:**

   ```bash
   curl -X POST https://your-domain/api/cron/daily-sync \
     -H "Authorization: Bearer YOUR_CRON_SECRET"
   ```

## Performance Optimization

### Database Indexes

The following indexes optimize query performance:

```sql
-- Opportunity queries
CREATE INDEX idx_opportunities_owner ON opportunities(owner_email, updated_at DESC);
CREATE INDEX idx_opportunities_stage ON opportunities(stage, close_date);

-- Timeline queries
CREATE INDEX idx_emails_opportunity ON emails(opportunity_id, sent_at DESC);
CREATE INDEX idx_call_opportunities_opp ON call_opportunities(opportunity_id);
```

### Caching

1. **SWR client-side caching:**

   - Opportunities list: `keepPreviousData` for smooth pagination
   - Insights: `dedupingInterval: 3600000` (1 hour)

2. **Server-side analysis cache:**
   - `opportunity_analysis_cache` table stores AI results
   - Invalidated when new calls added to opportunity

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ OpportunitiesList│  │ OpportunityDetail│  │ Insights    │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
│           │                    │                   │         │
│           ▼                    ▼                   ▼         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Routes (/api/opportunities/*)          │ │
│  └────────────────────────────┬───────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    REST API (FastAPI :8000)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ /opportunities  │  │ /opportunities/ │  │ MCP Tools     │  │
│  │ endpoint        │  │ [id]/insights   │  │ Integration   │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬───────┘  │
└───────────┼────────────────────┼───────────────────┼──────────┘
            │                    │                   │
            ▼                    ▼                   ▼
┌───────────────────────────────────────────────────────────────┐
│                    Database (Neon PostgreSQL)                  │
│  ┌────────────┐ ┌────────┐ ┌─────────────────┐ ┌───────────┐  │
│  │opportunities│ │ emails │ │call_opportunities│ │sync_status│  │
│  └────────────┘ └────────┘ └─────────────────┘ └───────────┘  │
└───────────────────────────────────────────────────────────────┘
            ▲
            │
┌───────────┴───────────────────────────────────────────────────┐
│                    Daily Sync Flow (Cron)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │sync_opportunities│→│sync_opp_calls   │→│sync_opp_emails │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                              │                                 │
│                              ▼                                 │
│                     ┌─────────────────┐                        │
│                     │   Gong API      │                        │
│                     └─────────────────┘                        │
└───────────────────────────────────────────────────────────────┘
```

## Related Documentation

- Main project: `/Users/gcoyne/src/prefect/call-coach/CLAUDE.md`
- Database schema: `/Users/gcoyne/src/prefect/call-coach/db/schema.sql`
- Sync flow: `/Users/gcoyne/src/prefect/call-coach/flows/daily_gong_sync.py`
- Frontend components: `/Users/gcoyne/src/prefect/call-coach/frontend/components/opportunities/`
