## Why

Sales teams need AI-powered coaching insights from Gong calls to improve performance across product knowledge, discovery skills, objection handling, and engagement. Currently, manual call reviews are time-consuming and inconsistent. This system automates analysis using Claude AI, provides on-demand coaching via MCP tools, and generates weekly performance reports - reducing coaching time by 80% while providing consistent, data-driven insights.

## What Changes

- **NEW**: End-to-end pipeline from Gong webhooks → Claude analysis → coaching insights stored in Postgres
- **NEW**: Intelligent caching system reducing Claude API costs by 60-80% ($1,787/month → $317/month)
- **NEW**: Transcript chunking to handle 60+ minute calls (>80K tokens)
- **NEW**: FastMCP server with 9 tools for on-demand coaching via Claude Desktop
- **NEW**: Automated weekly coaching reviews with team analytics and trend analysis
- **NEW**: Knowledge base with coaching rubrics and product documentation
- **NEW**: Complete observability for webhook processing, flow execution, and API costs

## Capabilities

### New Capabilities

- `webhook-ingestion`: Receive and validate Gong webhooks with HMAC-SHA256 verification, idempotency handling, and <500ms response time
- `call-processing`: Async Prefect flow to fetch calls, transcripts, and participants from Gong API and store in Postgres
- `transcript-chunking`: Sliding window chunking with 20% overlap for calls exceeding 80K tokens
- `intelligent-caching`: SHA256-based transcript hashing with rubric versioning to cache analyses and reduce API costs by 60-80%
- `coaching-analysis`: Claude-powered analysis across 4 dimensions (product knowledge, discovery, objections, engagement) with structured scoring and examples
- `knowledge-base`: Coaching rubrics and product documentation stored in Postgres with versioning
- `mcp-tools`: 9 FastMCP tools for on-demand coaching (analyze_call, get_rep_insights, search_calls, compare_calls, etc.)
- `weekly-reviews`: Scheduled Prefect flow for batch analysis, trend computation, and automated report generation
- `cost-monitoring`: Token usage tracking and cache hit rate monitoring with dashboards

### Modified Capabilities

<!-- No existing capabilities being modified - this is a greenfield project -->

## Impact

**New Infrastructure:**
- Neon Postgres database with 14 tables, quarterly partitioning, and optimized indexes
- FastAPI webhook server (always-on, <500ms response)
- Prefect flows on Horizon (process_new_call, weekly_coaching_review)
- FastMCP server for Claude Desktop integration

**External Dependencies:**
- Gong API (calls, transcripts, webhooks)
- Claude API (Sonnet 4.5 for analysis)
- Neon Postgres (production database)
- Prefect Cloud (flow orchestration)

**Data Storage:**
- ~100 calls/week × 30K tokens avg = 3M tokens/week stored as transcripts
- Coaching sessions partitioned quarterly (5-year retention = 20 partitions)
- Full-text search indexes on transcripts
- Knowledge base with product docs and rubrics

**Cost Impact:**
- Without optimization: $1,787/month (100 calls/week)
- With caching: $317/month (82% reduction)
- Database: $19/month (Neon Starter)
- **Total**: ~$336/month

**Team Impact:**
- SEs, AEs, CSMs: Access to on-demand coaching insights via Claude Desktop
- Sales Managers: Weekly team performance reports and trend analysis
- Sales Leadership: Aggregate metrics and skill gap identification
