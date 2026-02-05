# Setup Guide - Gong Call Coaching Agent

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Neon Postgres account)
- Gong API credentials
- Anthropic API key
- Prefect Cloud account (for Horizon deployment)

## Local Development Setup

### 1. Clone and Install

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# For development with testing/linting tools
uv sync --all-extras
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - GONG_API_KEY: From Gong Settings > API
# - GONG_WEBHOOK_SECRET: From Gong Settings > Webhooks
# - ANTHROPIC_API_KEY: From Anthropic Console
# - DATABASE_URL: Your Neon or local PostgreSQL connection string
# - PREFECT_API_KEY: From Prefect Cloud
```

### 3. Database Setup

**Option A: Local PostgreSQL (for development)**

```bash
# Start PostgreSQL with Docker Compose
make docker-up

# Run migrations
make db-migrate
```

**Option B: Neon Postgres (for production-like)**

```bash
# Get your Neon connection string from https://console.neon.tech
# Update DATABASE_URL in .env

# Run migrations
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
```

### 4. Verify Setup

```bash
# Run tests
make test

# Start webhook server
make webhook-server

# In another terminal, check health
curl http://localhost:8000/webhooks/health
```

## Production Deployment

### 1. Neon Database Setup

```bash
# Create Neon project at https://console.neon.tech
# Get connection string and update DATABASE_URL

# Run migrations
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql

# Verify schema
psql $DATABASE_URL -c "\dt"
```

### 2. Deploy Webhook Server to Horizon

```bash
# Build and push Docker image
docker build -f Dockerfile.webhook -t call-coach-webhook:latest .
docker tag call-coach-webhook:latest <your-registry>/call-coach-webhook:latest
docker push <your-registry>/call-coach-webhook:latest

# Deploy to your hosting platform (e.g., Cloud Run, ECS, etc.)
```

### 3. Configure Gong Webhook

1. Go to Gong Settings > API > Webhooks
2. Create new webhook:
   - URL: `https://your-domain.com/webhooks/gong`
   - Events: Select "Call Completed"
   - Secret: Generate and save to `GONG_WEBHOOK_SECRET`
3. Test webhook delivery

### 4. Deploy Prefect Flows to Horizon

```bash
# Authenticate with Prefect Cloud
prefect cloud login

# Deploy flows
prefect deploy flows/process_new_call.py
prefect deploy flows/weekly_review.py

# Verify deployments
prefect deployment ls
```

### 5. Load Knowledge Base

```bash
# Load coaching rubrics
python -m knowledge.loader --type rubrics

# Load product documentation
python -m knowledge.loader --type products
```

## Phase Implementation Status

### ✅ Phase 1: Foundation (COMPLETE)

- [x] Database schema with partitioning and indexes
- [x] Gong API client with error handling
- [x] Webhook endpoint with signature verification
- [x] `process_new_call` Prefect flow
- [x] Transcript chunking with overlap
- [x] Idempotency handling

**Verification:**
```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/webhooks/gong \
  -H "Content-Type: application/json" \
  -H "X-Gong-Webhook-Id: test-123" \
  -H "X-Gong-Signature: test-signature" \
  -d '{"event": "call.completed", "call_id": "test"}'

# Check database
psql $DATABASE_URL -c "SELECT * FROM webhook_events LIMIT 5;"
```

### 🔄 Phase 2: Knowledge Base (IN PROGRESS)

- [ ] Convert coaching rubrics to structured format
- [ ] Load rubrics into database
- [ ] Collect and structure product docs
- [ ] Load knowledge base
- [ ] Query utilities

**Next Steps:**
1. Create `knowledge/rubrics/discovery_rubric_v1.json`
2. Create `knowledge/products/prefect_features.md`
3. Implement `knowledge/loader.py`

### ⏳ Phase 3: Analysis Engine (PENDING)

- [x] Caching logic implementation
- [x] Cache key generation
- [ ] Claude API integration with prompt caching
- [ ] Prompt templates for each dimension
- [ ] Parallel dimension analysis
- [ ] Token usage tracking

**Next Steps:**
1. Implement actual Claude API calls in `analysis/engine.py`
2. Create prompt templates in `analysis/prompts/`
3. Add parallel execution with Prefect `.map()`

### ⏳ Phase 4: FastMCP Server (PENDING)

- [ ] Initialize FastMCP project
- [ ] Implement 9 MCP tools
- [ ] Authentication/authorization
- [ ] Test in Claude Desktop
- [ ] Documentation

### ⏳ Phase 5: Weekly Reviews (PENDING)

- [ ] `weekly_coaching_review` flow
- [ ] Report generation
- [ ] Team analytics
- [ ] Notification system

### ⏳ Phase 6: Production Hardening (PENDING)

- [ ] Error handling and retries
- [ ] Monitoring dashboards
- [ ] Load testing
- [ ] Documentation
- [ ] Security audit

## Common Tasks

### View Recent Calls

```bash
psql $DATABASE_URL -c "
SELECT id, title, scheduled_at, duration_seconds
FROM calls
ORDER BY scheduled_at DESC
LIMIT 10;
"
```

### Check Cache Hit Rate

```bash
psql $DATABASE_URL -c "SELECT * FROM get_cache_hit_rate();"
```

### View Rep Performance

```bash
psql $DATABASE_URL -c "
SELECT * FROM rep_performance_summary
WHERE rep_email = 'sarah@prefect.io';
"
```

### Manually Process a Call

```python
from flows.process_new_call import process_new_call_flow

result = process_new_call_flow(gong_call_id="your-call-id")
print(result)
```

### Analyze a Call

```python
from uuid import UUID
from analysis.engine import analyze_call
from db.models import CoachingDimension

result = analyze_call(
    call_id=UUID("your-call-uuid"),
    dimensions=[CoachingDimension.PRODUCT_KNOWLEDGE, CoachingDimension.DISCOVERY],
)
print(result)
```

## Troubleshooting

### Webhook Not Receiving Events

1. Check webhook server logs: `docker-compose logs webhook-server`
2. Verify Gong webhook configuration
3. Test signature verification with sample payload
4. Check firewall/network settings

### Database Connection Issues

1. Verify DATABASE_URL is correct
2. Check Neon database status
3. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
4. Review connection pool settings

### Analysis Failures

1. Check Claude API key is valid
2. Review token usage and rate limits
3. Check rubric versions exist
4. Verify transcript is not empty

## Monitoring

### Key Metrics to Track

- Webhook processing time (<500ms target)
- Cache hit rate (60-80% target)
- Token usage per call (~30K tokens)
- Analysis completion time (<60s per call)
- Error rate (<1% target)

### Log Locations

- Webhook server: Docker logs or application logs
- Prefect flows: Prefect Cloud UI
- Database queries: PostgreSQL logs

## Support

For issues or questions:
1. Check logs in respective services
2. Review error messages in database (`webhook_events.error_message`, `analysis_runs.error_message`)
3. Consult implementation plan for architecture details
