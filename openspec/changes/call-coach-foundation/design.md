## Context

Sales teams conduct 100+ calls/week via Gong. Manual call reviews are time-consuming and inconsistent. We need automated AI-powered coaching that:
- Analyzes calls across 4 dimensions (product knowledge, discovery, objections, engagement)
- Provides on-demand insights via Claude Desktop (MCP tools)
- Generates weekly performance reports
- Stays within budget (~$300/month for 100 calls/week)

**Current State:** No automated coaching system exists. Manual reviews happen sporadically.

**Constraints:**
- Budget: <$500/month for Claude API costs
- Latency: Webhook responses must be <500ms (Gong timeout)
- Scale: Support 60+ minute calls (>100K tokens)
- Integration: Must work with existing Gong, Prefect Cloud infrastructure

**Stakeholders:** Sales leadership, SEs, AEs, CSMs, RevOps

## Goals / Non-Goals

**Goals:**
- Automate call analysis with 80%+ accuracy compared to manual coaching
- Reduce per-call cost from $17.87 (baseline) to <$5 via intelligent caching
- Support 60+ minute calls without context limit errors
- Provide <10s response time for cached on-demand queries
- Enable weekly batch processing of 100+ calls
- Track all costs and cache hit rates for optimization

**Non-Goals:**
- Real-time in-call coaching (v2 feature)
- Video/audio analysis beyond transcripts
- CRM integration (Salesforce, HubSpot)
- Custom web UI (use Claude Desktop + MCP for v1)
- Automated role-play generation (v3 feature)

## Decisions

### D1: Intelligent Caching System

**Decision:** Implement three-tier caching with SHA256 transcript hashing, rubric versioning, and prompt caching.

**Rationale:**
- **Problem:** Re-analyzing same transcript for different dimensions costs 120K tokens/call ($0.36/call × 4 dimensions)
- **Solution:** Cache by `dimension + transcript_hash + rubric_version`
- **Impact:** 60-80% cache hit rate → 82% cost reduction ($1,787/month → $317/month)

**Alternatives Considered:**
- Simple call_id caching: Fails when rubrics update, no cross-call deduplication
- No caching: 5× higher costs, unsustainable at scale
- Redis cache: Added complexity, same data already in Postgres

**Implementation:**
```python
cache_key = sha256(f"{dimension}:{transcript_hash}:{rubric_version}")
cached = db.query("SELECT * FROM coaching_sessions WHERE cache_key = %s")
if cached and not force_reanalysis:
    return cached  # Cache hit
# Cache miss - call Claude API
```

### D2: Async Webhook Handler

**Decision:** Lightweight FastAPI endpoint returns 200 OK in <500ms, triggers async Prefect flow for heavy processing.

**Rationale:**
- **Problem:** Gong expects webhook response in <3 seconds. Full transcript analysis takes 30-60 seconds.
- **Solution:** Split into fast path (webhook validation/storage) and slow path (Prefect flow)
- **Impact:** Never timeout, reliable ingestion, retryable processing

**Implementation:**
1. FastAPI validates HMAC-SHA256 signature
2. Store payload in `webhook_events` table (idempotent via `gong_webhook_id`)
3. Return 200 OK immediately
4. Trigger Prefect flow asynchronously (no wait)

**Alternatives Considered:**
- Synchronous processing: Would timeout on long calls
- Queue-based (Celery, RQ): Extra infrastructure, Prefect already handles this
- Lambda/serverless: Cold starts, complexity

### D3: Transcript Chunking

**Decision:** Sliding window chunking with 20% overlap, max 80K tokens/chunk.

**Rationale:**
- **Problem:** 60-minute calls exceed 100K tokens (Claude's 200K limit leaves room for prompts)
- **Solution:** Split into chunks with overlap to preserve context
- **Impact:** Support unlimited call length, maintain analysis quality

**Configuration:**
- Max chunk size: 80K tokens (leaves 120K for prompts, knowledge base, response)
- Overlap: 20% (16K tokens) maintains speaker/topic continuity
- Aggregation: Combine chunk-level scores into call-level metrics

**Alternatives Considered:**
- No chunking (fail on long calls): Unacceptable for 60+ min calls
- Fixed-size chunks with no overlap: Loses context at boundaries
- Sentence-based splitting: More complex, marginal quality gain

### D4: Parallel Dimension Analysis

**Decision:** Use Prefect `.map()` to analyze all 4 dimensions concurrently.

**Rationale:**
- **Problem:** Sequential analysis takes 4 × 60s = 4 minutes wall-clock time
- **Solution:** Analyze product_knowledge, discovery, objections, engagement in parallel
- **Impact:** 4× faster (4 minutes → 1 minute), same token cost

**Implementation:**
```python
@flow
def analyze_call(call_id, dimensions):
    results = analyze_dimension.map(
        dimension=dimensions,
        call_id=unmapped(call_id),
        transcript=unmapped(transcript)
    )
    return aggregate_results(results)
```

### D5: Database Schema Design

**Decision:** Partitioned `coaching_sessions` table by created_at (quarterly), separate tables for caching metadata.

**Rationale:**
- **Problem:** Coaching sessions grow unbounded (26K sessions/year at 100 calls/week × 4 dimensions)
- **Solution:** Quarterly partitions for archival, indexes on cache keys
- **Impact:** Fast queries, archivable old data, optimized for cache lookups

**Schema Highlights:**
- `coaching_sessions`: Partitioned by `created_at` (quarterly)
- `cache_key`, `transcript_hash`, `rubric_version` columns for caching
- Indexes on `(cache_key, transcript_hash, rubric_version)` for O(1) cache lookups
- `webhook_events` table for audit trail and idempotency

### D6: Prompt Caching

**Decision:** Use Claude's prompt caching feature for static content (rubrics, knowledge base, system prompts).

**Rationale:**
- **Problem:** Every API call repeats 10-15K tokens of rubrics and knowledge base
- **Solution:** Mark static content as cacheable in prompt structure
- **Impact:** 50% input token reduction on cache hits (cached content costs 90% less)

**Implementation:**
```python
response = anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",
    system=[
        {"type": "text", "text": rubric_content, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": knowledge_base, "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": transcript}]
)
```

### D7: MCP vs Web UI

**Decision:** Use FastMCP server for on-demand queries via Claude Desktop instead of building custom web UI.

**Rationale:**
- **Time to Value:** MCP integration takes 4-5 days vs 3-4 weeks for web UI
- **User Experience:** Sales managers already use Claude Desktop for other tasks
- **Flexibility:** Natural language queries vs rigid UI forms
- **Cost:** No frontend infrastructure needed

**Future:** Web UI can be added in Phase 7 if adoption is high.

## Risks / Trade-offs

### R1: Cache Staleness
**Risk:** Using outdated analysis when rubrics are updated.
**Mitigation:** Rubric versioning invalidates cache. Track `rubric_version` in cache keys. Admins can force reanalysis.

### R2: Long Call Quality
**Risk:** Chunked analysis may miss cross-segment patterns.
**Mitigation:** 20% overlap preserves context. Future: Use Claude's 1M context when available.

### R3: Gong API Rate Limits
**Risk:** Fetching 100 transcripts/day may hit rate limits.
**Mitigation:** Exponential backoff, queue-based processing. Prefect retries handle transient errors.

### R4: Cost Overruns
**Risk:** Cache miss rate exceeds 40%, costs balloon.
**Mitigation:** Monitor cache hit rate daily. Alert if <50%. Implement additional cache warming strategies.

### R5: PII/Data Privacy
**Risk:** Call transcripts contain sensitive customer information.
**Mitigation:** Neon SSL encryption, soft-delete for departed reps, 5-year retention policy. No data leaves Neon/Claude.

### R6: Claude API Availability
**Risk:** Claude API outages block all analysis.
**Mitigation:** Retry logic, exponential backoff. Queue calls for retry during outages. No real-time SLA required.

## Migration Plan

**Phase 1: Foundation (Week 1-2)**
1. Provision Neon database
2. Deploy webhook server to staging
3. Configure Gong webhook (test environment)
4. Validate end-to-end: webhook → database
5. Deploy to production

**Phase 2-3: Analysis Engine (Week 3-5)**
1. Load coaching rubrics (v1.0.0)
2. Load product knowledge base
3. Deploy analysis flows to Horizon
4. Test with 10 sample calls
5. Validate cache hit rate >60%

**Phase 4: MCP Tools (Week 6-7)**
1. Deploy FastMCP server
2. Test with sales leadership (5 users)
3. Gather feedback, iterate
4. Roll out to all sales managers

**Phase 5-6: Weekly Reviews & Hardening (Week 8-10)**
1. Deploy weekly review flow
2. Set up monitoring dashboards
3. Load test with 500 calls/week
4. Production hardening

**Rollback Strategy:**
- Webhook server: Disable Gong webhook, revert deployment
- Database: All migrations are additive, rollback drops new tables
- Flows: Pause/delete Prefect deployments
- MCP: Users remove from Claude Desktop config

**Monitoring:**
- Webhook response time <500ms (P99)
- Cache hit rate >60%
- Token usage <150M/month
- Analysis completion time <60s/call (P95)
- Error rate <1%

## Open Questions

1. **Coaching Rubrics:** Need finalized rubrics from sales leadership. Who owns this?
2. **Product Docs:** Who maintains product knowledge base? Update frequency?
3. **Access Control:** Do reps have access to their own coaching data via MCP tools?
4. **Notification Channels:** Weekly reports via email or Slack? Distribution list?
5. **Retention Policy:** 5-year retention OK, or shorter for compliance?
6. **Gong API Credentials:** Who provisions and rotates API keys?
7. **Cost Approval:** $336/month ongoing cost approved by whom?
