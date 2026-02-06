## Context

**Current State:**

- App only analyzes individual calls in isolation
- No opportunity-level data model or caching
- Every analysis requires fresh Gong API calls (expensive, slow)
- No visibility into deal progression patterns across multiple touchpoints
- Coaching focuses on fixing problems, not learning from successful patterns

**Problem:**

- Sales coaching needs context of full customer journey (10-15 calls + 50+ emails per opp)
- Gong API rate limits and latency make real-time fetching impractical
- No way to identify what top performers do differently across opportunities
- Can't surface "good call" patterns for other reps to learn from

**Constraints:**

- Gong API rate limits: 1000 calls/day (daily polling is safe)
- Vercel free tier cron: daily execution minimum
- Neon free tier: 0.5GB storage (need efficient schema)
- Local development first, Vercel deployment later
- Webhook ingestion post-deployment only

## Goals / Non-Goals

**Goals:**

- Enable opportunity-level coaching across all calls and emails for a deal
- Cache Gong data aggressively in Neon to reduce API dependency
- Identify patterns in successful deals for peer learning
- Support daily sync workflow (local Prefect → Vercel cron migration path)
- Build foundation for webhook-based real-time sync later

**Non-Goals:**

- Real-time webhook ingestion (post-deployment feature)
- Bi-directional sync (Gong is source of truth, we're read-only cache)
- Custom opportunity scoring (use Gong's native health scores initially)
- Email content search (just cache, don't index body text yet)
- Historical data backfill (start from today forward)

## Decisions

### Decision 1: Daily Polling with Incremental Sync

**Choice:** Poll Gong API once daily, fetch only changed/new data since last sync.

**Alternatives Considered:**

1. **Webhook-only from day 1** - Can't test locally, requires Vercel deployment first
2. **On-demand fetch per page load** - Slow UX, hits rate limits quickly
3. **Hourly polling** - Wastes API quota, daily cadence sufficient for coaching use case

**Rationale:**

- Gong API supports `modifiedAfter` parameter for incremental queries
- Daily cadence matches manager workflow (review yesterday's calls each morning)
- Rate limit safe: ~100 opps × 10 calls = 1000 API calls, well under limit
- Easy migration path: same code runs as Prefect flow locally or Vercel cron

**Implementation:**

```python
# flows/daily_gong_sync.py
@task
def sync_opportunities(since: datetime):
    """Fetch opportunities modified since last sync."""
    last_sync = db.get_last_sync_timestamp("opportunities")
    opps = gong_client.list_opportunities(modified_after=last_sync)
    for opp in opps:
        db.upsert_opportunity(opp)
        sync_opportunity_calls(opp.id, since)
        sync_opportunity_emails(opp.id, since)
    db.update_sync_timestamp("opportunities", datetime.utcnow())
```

### Decision 2: Normalized Relational Schema (Not Denormalized JSONB)

**Choice:** Create proper tables (opportunities, emails, call_opportunities) with foreign keys.

**Alternatives Considered:**

1. **Store Gong API responses as JSONB blobs** - Simple but hard to query
2. **Single opportunities table with JSONB array of calls/emails** - Violates normal forms, slow filters

**Rationale:**

- Need to query across opportunities (find all calls by rep, filter by stage, etc.)
- JSONB makes it hard to enforce data integrity and join with existing calls table
- Normalized schema enables efficient filtering for opportunity search page
- Storage overhead minimal (5000 opps × 1KB = 5MB well under limits)

**Schema:**

```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_opportunity_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    account_name VARCHAR,
    owner_email VARCHAR,
    stage VARCHAR,
    close_date DATE,
    amount DECIMAL,
    health_score DECIMAL, -- Gong's native health score
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- Full Gong response for fields we don't model
);

CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_email_id VARCHAR UNIQUE NOT NULL,
    opportunity_id UUID REFERENCES opportunities(id),
    subject VARCHAR,
    sender_email VARCHAR,
    recipients VARCHAR[],
    sent_at TIMESTAMP,
    body_snippet TEXT, -- First 500 chars for timeline preview
    metadata JSONB, -- Full email metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE call_opportunities (
    call_id UUID REFERENCES calls(id),
    opportunity_id UUID REFERENCES opportunities(id),
    PRIMARY KEY (call_id, opportunity_id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_opportunities_owner ON opportunities(owner_email, updated_at DESC);
CREATE INDEX idx_opportunities_stage ON opportunities(stage, close_date);
CREATE INDEX idx_emails_opportunity ON emails(opportunity_id, sent_at DESC);
CREATE INDEX idx_call_opportunities_opp ON call_opportunities(opportunity_id);
```

### Decision 3: Learning from "Good Calls" via Comparative Analysis

**Choice:** Add comparative coaching analysis that shows what top performers do differently on successful deals.

**Alternatives Considered:**

1. **Manual tagging of exemplar calls** - Requires manager curation, doesn't scale
2. **Simple "best practices" library** - Static, doesn't adapt to team/product changes
3. **Win/loss analysis only** - Doesn't help during in-flight deals

**Rationale:**

- Coaching is most effective when reps see concrete examples from peers
- Closed-won opps provide ground truth for "what works"
- AI can identify patterns humans miss (e.g., discovery questions that correlate with wins)
- Builds on existing coaching_sessions data (reuse dimension scores)

**Implementation:**

```python
# New MCP tool: get_learning_insights
def get_learning_insights(
    rep_email: str,
    focus_area: str  # "discovery", "objections", "product_knowledge"
) -> dict:
    """
    Compare rep's patterns vs. top performers on won deals.
    Returns: what they do well + what top performers do differently.
    """
    # Find rep's recent opportunities
    rep_opps = db.get_opportunities(owner=rep_email, limit=20)

    # Find similar won opportunities by top performers
    won_opps = db.get_opportunities(
        stage="Closed Won",
        product=rep_opps[0].product,  # Same product line
        limit=50
    )

    # Aggregate coaching scores by focus area
    rep_scores = aggregate_coaching_scores(rep_opps, focus_area)
    winner_scores = aggregate_coaching_scores(won_opps, focus_area)

    # Use Claude to identify behavioral differences
    prompt = f"""
    Compare discovery patterns:

    Rep {rep_email} (mixed results):
    {format_coaching_examples(rep_scores)}

    Top performers (closed-won deals):
    {format_coaching_examples(winner_scores)}

    What do top performers do differently? Give 3 concrete examples.
    """

    return claude_analyze(prompt)
```

**UI Integration:**

- Add "Learn from Winners" section on rep dashboard
- Show side-by-side comparison of rep's calls vs. exemplar calls
- Link to specific call timestamps for concrete examples

### Decision 4: Opportunity Timeline with Expandable Transcripts

**Choice:** Single-page timeline with lazy-loaded transcript details (not separate pages per call).

**Alternatives Considered:**

1. **List of call cards linking to existing call detail pages** - Lots of navigation, loses context
2. **All transcripts expanded by default** - Page too long, slow initial load
3. **Tabbed interface (Calls tab, Emails tab)** - Breaks chronological flow

**Rationale:**

- Coaching needs temporal context (what happened before/after each call?)
- Manager workflow: scan timeline → expand interesting moments → coach
- Lazy loading keeps initial load fast while allowing deep dives

**Component Structure:**

```tsx
// app/opportunities/[id]/page.tsx
export default function OpportunityPage({ params }: { params: { id: string } }) {
  const { data: opp } = useSWR(`/api/opportunities/${params.id}`);
  const { data: timeline } = useSWR(`/api/opportunities/${params.id}/timeline`);

  return (
    <div className="opportunity-detail">
      <OpportunityHeader opp={opp} />
      <OpportunityInsights oppId={params.id} /> {/* Holistic coaching */}
      <Timeline items={timeline} /> {/* Calls + emails chronological */}
    </div>
  );
}

// components/Timeline.tsx
function Timeline({ items }: { items: TimelineItem[] }) {
  return items.map((item) => {
    if (item.type === "call") {
      return <CallTimelineCard call={item} expandable />;
    } else {
      return <EmailTimelineCard email={item} expandable />;
    }
  });
}
```

### Decision 5: Migration Path from Local Prefect to Vercel Cron

**Choice:** Write sync flow as standalone Python module that works in both environments.

**Alternatives Considered:**

1. **Two separate implementations** - Duplicate code, drift risk
2. **Serverless-first** - Can't test locally, requires Vercel from day 1
3. **Docker container** - Overkill for simple daily job

**Rationale:**

- Same code should run via `uv run` locally and as Vercel cron serverless function
- Environment variables handle differences (local .env vs. Vercel env vars)
- Gradual migration: test locally → deploy to Vercel → switch to webhooks

**Implementation:**

```python
# flows/daily_gong_sync.py (works in both environments)
from coaching_mcp.shared import settings

def main():
    """Entry point for both local and serverless execution."""
    sync_opportunities()
    sync_calls()
    sync_emails()

if __name__ == "__main__":
    # Local execution: uv run python -m flows.daily_gong_sync
    main()

# api/cron/daily-sync.py (Vercel serverless function)
from flows.daily_gong_sync import main

def handler(request):
    """Vercel cron handler."""
    main()
    return {"status": "ok"}
```

**Vercel cron config:**

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-sync",
      "schedule": "0 6 * * *" // 6am daily
    }
  ]
}
```

## Risks / Trade-offs

**Risk:** Stale data between syncs (up to 24 hours old)

- **Mitigation:** Daily sync runs at 6am, managers review previous day's calls (acceptable latency)
- **Future:** Add webhook ingestion for real-time updates post-deployment

**Risk:** Gong API schema changes break sync

- **Mitigation:** Store full API responses in `metadata` JSONB, only parse fields we need, add schema validation
- **Monitoring:** Log sync failures, alert on consecutive failures

**Risk:** Storage growth (5000 opps × 50 emails × 500 chars = 125MB)

- **Mitigation:** Neon free tier is 512MB, monitor usage, add retention policy (90 days) if needed
- **Future:** Compress old email bodies, keep only metadata

**Risk:** Rate limit exceeded if many users trigger manual refresh

- **Mitigation:** No manual refresh button in V1, only automated daily sync, add rate limiting if needed later

**Trade-off:** Normalized schema vs. JSONB flexibility

- **Pro:** Easy to query and filter, joins work naturally
- **Con:** Schema migrations needed if Gong adds fields we care about
- **Decision:** Accept migration cost for query performance

**Trade-off:** Daily polling vs. webhooks

- **Pro:** Works locally, no public endpoint required, easy to test
- **Con:** 24-hour latency
- **Decision:** Daily is good enough for coaching use case, webhooks come later

## Migration Plan

**Phase 1: Local Development (This Change)**

1. Add database schema for opportunities/emails
2. Build daily sync Prefect flow
3. Create opportunity detail page UI
4. Add holistic coaching analysis MCP tools
5. Test end-to-end locally

**Phase 2: Vercel Deployment**

1. Deploy Next.js frontend to Vercel
2. Deploy FastMCP server to Vercel serverless functions
3. Configure Vercel cron for daily sync
4. Migrate DATABASE_URL to Vercel environment variables
5. Test in production

**Phase 3: Webhook Ingestion (Future)**

1. Add webhook endpoint to FastMCP server
2. Register webhook with Gong
3. Process webhook events in real-time
4. Keep daily sync as backup (in case webhooks fail)

**Rollback:**

- Phase 1: Just delete new database tables, no breaking changes
- Phase 2: Disable Vercel cron, fall back to local sync
- Phase 3: Unregister webhook, keep daily sync only

## Open Questions

**Q1:** Should we cache Gong call recordings (audio/video URLs)?

- **Answer:** No, just store Gong URLs and fetch on-demand. Storage too expensive.

**Q2:** How to handle opportunities with 100+ calls (large enterprise deals)?

- **Answer:** Timeline pagination - load first 20 items, "Load More" for older items.

**Q3:** Should sync be opportunity-centric or call-centric?

- **Answer:** Opportunity-centric. Fetch opportunities → enrich with calls/emails. Matches manager workflow.

**Q4:** What if a call belongs to multiple opportunities?

- **Answer:** Junction table `call_opportunities` supports M:N. Coaching analysis aggregates across all linked opps.

**Q5:** How to identify "good calls" for learning?

- **Answer:** Use coaching dimension scores + opportunity outcome (Closed Won). Filter to calls with >80 product knowledge score on won deals.
