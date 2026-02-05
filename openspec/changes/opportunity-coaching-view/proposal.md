## Why

Managers need to coach reps across entire opportunities (multiple calls + emails), not just individual calls. Currently the app only shows single-call analysis. Viewing the full customer journey reveals patterns in discovery, objection handling, and relationship building that single calls miss. This enables more strategic coaching focused on deal progression rather than isolated conversations.

## What Changes

- Add opportunity-level data model and database schema (opportunities, emails, call-opportunity mappings)
- Implement daily polling job to sync opportunities, calls, and emails from Gong API into Neon cache
- Create opportunity detail page showing timeline of all touchpoints (calls + emails) with AI analysis
- Add holistic coaching insights that analyze patterns across multiple interactions
- Build opportunity search/filter UI for managers to find deals needing coaching
- Deploy polling job to Vercel cron (initially daily, webhook ingestion added post-deployment)

## Capabilities

### New Capabilities
- `opportunity-data-sync`: Daily polling job that fetches opportunities, calls, and emails from Gong API and caches in Neon PostgreSQL to avoid repeated API calls
- `opportunity-timeline-view`: UI page showing chronological timeline of all calls and emails for an opportunity with expandable transcripts and email content
- `holistic-opportunity-coaching`: AI analysis across multiple touchpoints identifying deal progression patterns, recurring objections, relationship strength trends
- `opportunity-search`: Search and filter opportunities by stage, rep, date range, health score with coaching priority ranking

### Modified Capabilities
<!-- No existing capabilities being modified at spec level -->

## Impact

**Affected Files:**
- `db/schema.sql` - Add opportunities, emails, call_opportunities junction tables
- New: `flows/daily_gong_sync.py` - Prefect flow for polling Gong API
- New: `app/opportunities/[id]/page.tsx` - Opportunity detail page
- New: `app/opportunities/page.tsx` - Opportunity search page
- `coaching_mcp/tools/` - New tools: get_opportunity_insights, analyze_opportunity_progression

**Affected Systems:**
- Neon PostgreSQL - New schema for opportunities and emails
- Gong API - Daily polling for data sync (rate limit friendly)
- Vercel deployment - Cron job for sync flow
- FastMCP server - New opportunity-focused coaching tools

**Dependencies:**
- Gong API rate limits (safe with daily polling)
- Vercel cron execution limits (free tier: daily is fine)
- Database storage growth (monitor opportunity/email volume)

**Benefits:**
- Reduces Gong API calls by 80%+ via aggressive caching
- Enables strategic opportunity-level coaching vs. tactical call-level
- Provides deal health visibility for coaching prioritization
- Sets foundation for webhook ingestion post-deployment
