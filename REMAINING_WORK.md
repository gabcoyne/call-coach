# Remaining Work - Call Coach Project

**Last Updated:** 2026-02-11
**Status:** Post-cleanup, accurate and prioritized

This document provides an authoritative view of genuinely incomplete work after the 2026-02-11 organizational cleanup that archived 3 completed OpenSpec changes and closed 8 completed beads issues.

---

## Summary

**Project Completion:** ~75-80% complete
**Core Features:** Fully functional (backend + frontend)
**Remaining Work:** Production readiness, deployment, polish

---

## Critical Path to Production (P0-P1)

### 1. Database Migration (P0)

**Beads:** `bd-2lm`
**Effort:** 30 minutes
**Status:** Not started

Apply `002_gong_api_v2_updates.sql` migration to update transcripts table for new Gong API structure.

### 2. Coaching Feed Backend (P2, but blocks frontend feature)

**Beads:** `bd-xxk`
**Effort:** 1-2 hours
**Status:** Not started

Frontend feed page exists but returns 404. Need to implement:

- MCP tool `get_coaching_feed` in `coaching_mcp/tools/`
- REST endpoint `POST /coaching/feed` in `api/rest_server.py`
- Feed generation logic (last 7 days analysis, team insights)

### 3. Production Hardening (P1)

**Beads:** `bd-31h.6`
**OpenSpec:** N/A (beads-only task)
**Effort:** 4-8 hours
**Status:** Not started

**Requirements:**

- Monitoring & observability (logs, metrics, traces)
- Rate limiting (already partially implemented, needs tuning)
- Security hardening (review auth, RBAC, secrets management)
- Error handling & recovery
- Performance optimization

### 4. Vercel Deployment (P1)

**Beads:** `bd-2bi`
**OpenSpec:** Multiple changes have deployment specs
**Effort:** 4-6 hours
**Status:** Not started

**Requirements:**

- Vercel project configuration
- Environment variables setup
- Preview deployments for PRs
- Production deployment
- CI/CD integration

**Related OpenSpec:** `complete-call-review-app/specs/vercel-deployment/`

### 5. Deployment & Rollout (P1)

**Beads:** `bd-31h.7`
**Effort:** Variable (depends on rollout strategy)
**Status:** Not started

Final deployment phase for production rollout.

---

## OpenSpec Changes In Progress

### High Value (70%+ complete)

1. **opportunity-coaching-view** (99/124 tasks - 80%)
   - Opportunity analysis and timeline features implemented
   - 25 tasks remaining (likely polish and edge cases)

### Medium Value (40-70% complete)

1. **complete-call-review-app** (77/123 tasks - 63%)

   - Major call analysis features done
   - 46 tasks remaining

2. **fastmcp-cloud-deployment** (21/38 tasks - 55%)

   - Basic deployment infrastructure done
   - 17 tasks remaining

3. **fix-call-detail-page-loading** (28/59 tasks - 47%)

   - Core data loading fixed
   - Error states and polish remaining
   - 31 tasks remaining

4. **role-based-coaching-rubrics** (47/115 tasks - 41%)
   - Backend schema and APIs complete
   - Frontend UI in progress
   - 68 tasks remaining

### Early Stage (under 20%)

1. **call-coach-foundation** (16/102 tasks - 16%)

   - Planning stage for advanced features
   - 86 tasks remaining

2. **team-role-rubric-management** (0/71 tasks - 0%)
   - NOT STARTED - purely planning documents
   - 71 tasks remaining

---

## Optional/Polish Work (P2)

### Vision & Strategy

**Beads:** `bd-ih6` - Remove Gong-duplicate features
**Effort:** Discussion + implementation (4-8 hours)
**Status:** Strategic decision needed

Question: Should Call Coach duplicate Gong features (players, transcripts) or focus purely on manager-driven coaching feedback?

**Components to potentially remove:**

- CallRecordingPlayer.tsx
- EnhancedCallPlayer.tsx
- TranscriptSearch.tsx
- ClipGenerator.tsx

**What stays:**

- Core coaching tools (analyze_call, get_rep_insights)
- Manager reviews and feedback
- Role management
- RBAC enforcement

### Testing & Quality

1. **Unit tests for coaching components** (`bd-9yn`) - 2-4 hours
2. **Accessibility audit with axe-core** (`bd-uee`) - 2-3 hours

---

## What's Already Complete (Don't Redo)

### Backend (100%)

- ✅ FastMCP server with 5 tools
- ✅ REST API bridge (api/rest_server.py)
- ✅ Database schema (34 tables)
- ✅ Gong API integration
- ✅ Claude API integration for analysis
- ✅ Role-based analysis (AE/SE/CSM/Support)
- ✅ Rubric management system
- ✅ Five Wins evaluation framework
- ✅ Intelligent caching

### Frontend (95%)

- ✅ Next.js 15.1.6 with App Router
- ✅ Clerk authentication
- ✅ Design system (24+ UI components)
- ✅ MCP backend integration
- ✅ All major pages:
  - Calls list with search/filters
  - Call detail with analysis
  - Rep performance dashboard
  - Team dashboard
  - Admin controls
  - Settings & role management
  - Feed page (UI only, backend missing)
  - Opportunities analysis
- ✅ SWR data fetching with 6+ hooks
- ✅ Error boundaries and loading states
- ✅ RBAC enforcement

### Infrastructure (80%)

- ✅ Test infrastructure (pytest, Jest)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Pre-commit hooks
- ✅ Rate limiting middleware
- ✅ Neon PostgreSQL database
- ⏳ Deployment configuration (not done)
- ⏳ Production monitoring (not done)

---

## Recommended Next Steps

### Sprint 1: Quick Wins (1 day)

1. Apply database migration (`bd-2lm`) - 30 min
2. Implement coaching feed backend (`bd-xxk`) - 2 hours
3. Test end-to-end that all pages work - 2 hours

### Sprint 2: Production Ready (3-5 days)

1. Production hardening (`bd-31h.6`) - 1-2 days
2. Vercel deployment setup (`bd-2bi`) - 1 day
3. Testing & fixes - 1-2 days

### Sprint 3: Polish (optional, 1-2 weeks)

1. Resolve vision alignment (`bd-ih6`)
2. Complete remaining OpenSpec changes
3. Accessibility audit
4. Unit test coverage

---

## How to Use This Document

**For Planning:**

- Use beads issues for tactical day-to-day work
- Use OpenSpec changes for feature-level planning
- This document is the strategic overview

**For Prioritization:**

- P0 issues block basic functionality
- P1 issues block production deployment
- P2 issues are polish and optional features

**Maintenance:**

- Update this document when major milestones complete
- Run `bd ready` to see current actionable work
- Run `openspec list` to see change progress

---

## Historical Context

**Before 2026-02-11 Cleanup:**

- 10 OpenSpec changes (3 complete but not archived)
- 17 open beads issues (8 actually complete)
- 104 markdown files with unclear status

**After Cleanup:**

- 7 OpenSpec changes (all in active development)
- 9 beads issues (all represent real work)
- 83 markdown files (stale docs removed)
- Clear view of what's done vs. what remains

This document represents the accurate state after validation against the actual codebase implementation.
