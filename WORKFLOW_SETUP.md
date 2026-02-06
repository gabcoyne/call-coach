# Protectly Development Workflow - Setup Complete ✅

**Date:** 2026-02-04
**Status:** OpenSpec + Beads fully configured

---

## What Was Set Up

### ✅ OpenSpec (Planning Artifacts)

Created structured planning artifacts for the entire project using the `spec-driven` workflow:

**Change:** `call-coach-foundation`

**Artifacts (4/4 complete):**

1. ✅ **proposal.md** - Why, what, capabilities, impact
2. ✅ **design.md** - 7 critical architectural decisions
3. ✅ **specs/** - 4 capability specifications with requirements
4. ✅ **tasks.md** - 90+ trackable tasks across 7 phases

### ✅ Beads (Task Tracking)

Created hierarchical issue tracking with dependencies:

**Epic:** `bd-31h` - Gong Call Coaching Agent - Complete Implementation

**Phases:**

- ✅ `bd-31h.1` - Phase 1: Foundation (CLOSED)
- ⏳ `bd-31h.2` - Phase 2: Knowledge Base (READY)
- 🔒 `bd-31h.3` - Phase 3: Analysis Engine (blocked by Phase 2)
- 🔒 `bd-31h.4` - Phase 4: FastMCP Server (blocked by Phase 3)
- 🔒 `bd-31h.5` - Phase 5: Weekly Reviews (blocked by Phase 4)
- 🔒 `bd-31h.6` - Phase 6: Production Hardening (blocked by Phase 5)
- 🔒 `bd-31h.7` - Phase 7: Deployment & Rollout (blocked by Phase 6)

**Dependencies:** Sequential (each phase blocks the next)

---

## OpenSpec Artifacts

### Proposal (Why & What)

**Why:** Automate AI-powered coaching for sales calls, reducing manual review time by 80%.

**New Capabilities (9):**

1. webhook-ingestion
2. call-processing
3. transcript-chunking
4. intelligent-caching (60-80% cost reduction)
5. coaching-analysis
6. knowledge-base
7. mcp-tools
8. weekly-reviews
9. cost-monitoring

**Impact:** $336/month total cost (vs $1,787 baseline)

### Design (How - 7 Critical Decisions)

1. **D1: Intelligent Caching** - SHA256 hashing + rubric versioning → 82% cost reduction
2. **D2: Async Webhook Handler** - <500ms response, async Prefect flow
3. **D3: Transcript Chunking** - Sliding window with 20% overlap for 60+ min calls
4. **D4: Parallel Dimension Analysis** - 4x faster via Prefect `.map()`
5. **D5: Database Schema** - Quarterly partitioning, cache-optimized indexes
6. **D6: Prompt Caching** - 50% input token reduction
7. **D7: MCP vs Web UI** - Faster time to value (4-5 days vs 3-4 weeks)

### Specs (What Requirements)

#### webhook-ingestion (5 requirements)

- Signature verification (HMAC-SHA256)
- Idempotency (via webhook ID)
- Response time (<500ms)
- Event storage
- Status tracking

#### intelligent-caching (8 requirements)

- Transcript hashing
- Cache key composition
- Cache lookup with TTL
- Rubric versioning
- Force reanalysis
- Cache statistics

#### coaching-analysis (8 requirements)

- Multi-dimensional analysis (4 dimensions)
- Scoring (0-100 with justification)
- Specific examples (quotes + timestamps)
- Action items
- Rubric adherence
- Parallel execution
- Token usage tracking
- Error handling

#### mcp-tools (7 requirements)

- analyze_call
- get_rep_insights
- search_calls
- compare_calls
- analyze_product_knowledge
- get_coaching_plan
- Structured response format

### Tasks (Implementation Checklist)

**Phase 1 (16/16 complete):** ✅

- Database schema, indexes, models
- Gong API client
- Webhook endpoint with security
- Prefect flows
- Chunking & caching
- Docker Compose
- Tests & docs

**Phase 2 (0/13):** Load coaching rubrics and product docs
**Phase 3 (0/14):** Claude API integration with prompts
**Phase 4 (0/15):** FastMCP server with 9 tools
**Phase 5 (0/13):** Weekly reviews and reporting
**Phase 6 (0/18):** Production hardening
**Phase 7 (0/13):** Deployment and rollout

**Total: 16/102 tasks complete (15.7%)**

---

## Beads Status

```
📊 Issue Database Status

Total Issues:     8
Open:             7
Closed:           1
Ready to Work:    2 (Epic + Phase 2)
Blocked:          5 (Phases 3-7)
```

**Ready Work:**

1. `bd-31h` (Epic) - Overall project tracking
2. `bd-31h.2` (Phase 2) - Knowledge Base - Ready to start!

**Next Steps:**

```bash
bd update bd-31h.2 --status in_progress
# ... work on Phase 2 ...
bd close bd-31h.2 --reason "Phase 2 complete"
```

---

## Workflow Commands

### OpenSpec

```bash
# View change status
openspec status --change "call-coach-foundation"

# Get artifact instructions
openspec instructions <artifact> --change "call-coach-foundation"

# Verify implementation (Phase 5)
openspec verify --change "call-coach-foundation"

# Archive to source of truth (when done)
openspec archive --change "call-coach-foundation"
```

### Beads

```bash
# See ready work
bd ready

# Show all issues
bd list

# Update status
bd update <id> --status in_progress

# Close issue
bd close <id> --reason "Completed <work>"

# Sync with git
bd sync --flush-only
```

---

## File Structure

```
call-coach/
├── openspec/
│   └── changes/
│       └── call-coach-foundation/
│           ├── .openspec.yaml
│           ├── proposal.md
│           ├── design.md
│           ├── specs/
│           │   ├── webhook-ingestion/spec.md
│           │   ├── intelligent-caching/spec.md
│           │   ├── coaching-analysis/spec.md
│           │   └── mcp-tools/spec.md
│           └── tasks.md
├── .beads/
│   ├── issues.jsonl (8 issues)
│   ├── config.yaml
│   └── metadata.json
├── .claude/
│   ├── skills/ (10 OpenSpec skills)
│   └── commands/ (10 OpenSpec commands)
└── [existing implementation files]
```

---

## What Changed from Original Approach

**Before:**

- Jumped straight to implementation
- Manual git commits
- No structured planning artifacts
- No task tracking between sessions

**Now:**

- ✅ OpenSpec planning artifacts (proposal, design, specs, tasks)
- ✅ Beads for persistent task tracking
- ✅ Sequential dependencies preventing premature work
- ✅ Proper workflow for multi-session projects
- ✅ Resumable across context compaction

---

## Benefits

1. **Resumability:** Beads persists via git, survives context compaction
2. **Traceability:** OpenSpec artifacts link requirements → tasks → commits
3. **Collaboration:** Other agents/humans can pick up work
4. **Quality:** Planning before coding prevents rework
5. **Documentation:** Artifacts serve as technical documentation

---

## Next Session

When you resume work:

```bash
# 1. Check ready work
bd ready

# 2. Pick up Phase 2
bd update bd-31h.2 --status in_progress

# 3. Work through Phase 2 tasks (knowledge base loading)
# 4. Close when done
bd close bd-31h.2 --reason "Rubrics and docs loaded"

# 5. Sync
bd sync --flush-only
```

Phase 2 automatically unblocks Phase 3, maintaining workflow progression.

---

**Workflow Status:** ✅ Fully Operational
**Next Phase:** Phase 2 (Knowledge Base) - Ready!
