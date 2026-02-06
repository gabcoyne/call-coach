## Why

Different sales roles (Account Executives, Sales Engineers, Customer Success Managers) require different coaching evaluation criteria. AEs need discovery and objection handling skills, SEs need deep technical knowledge, CSMs need relationship management and value realization focus. One-size-fits-all coaching misses role-specific gaps and wastes managers' time reviewing irrelevant dimensions. Prefect staff are identifiable by @prefect.io email domain.

## What Changes

- Add role assignment capability for Prefect staff (AE, SE, CSM) based on @prefect.io email domain
- Create role-specific coaching rubrics with different evaluation dimensions and scoring criteria
- Update coaching analysis to apply role-appropriate rubrics automatically
- Add role selection UI for managers to assign/update roles
- Modify coaching insights to show role-specific strengths and gaps
- Store role assignments in database for persistence

## Capabilities

### New Capabilities

- `role-assignment-ui`: UI components for managers to assign and update staff roles (AE/SE/CSM) with @prefect.io domain validation
- `role-specific-rubrics`: Three distinct coaching rubrics tailored to AE, SE, and CSM evaluation criteria with different dimensions and scoring weights
- `role-aware-coaching-analysis`: Coaching analysis engine that automatically applies appropriate rubric based on assigned role and adjusts scoring/recommendations

### Modified Capabilities

<!-- No existing capabilities being modified at spec level - this is additive -->

## Impact

**Affected Files:**

- `db/schema.sql` - Add staff_roles table (email, role, assigned_by, assigned_at)
- `app/settings/roles/page.tsx` - New role assignment UI page
- `analysis/rubrics/` - New role-specific rubric definitions (ae_rubric.json, se_rubric.json, csm_rubric.json)
- `analysis/opportunity_coaching.py` - Update to load role-specific rubrics
- `analysis/learning_insights.py` - Filter comparisons to same role only
- `coaching_mcp/tools/analyze_call.py` - Detect speaker role and apply appropriate rubric
- `lib/db/roles.ts` - New database queries for role CRUD

**Affected Systems:**

- Neon PostgreSQL - New staff_roles table
- Coaching analysis module - Role detection and rubric selection logic
- Frontend UI - New settings page for role management

**Dependencies:**

- Existing speakers table has email field for domain validation
- Clerk authentication for manager-only access to role assignment

**Benefits:**

- More relevant coaching feedback (SE evaluated on technical accuracy, not discovery)
- Faster manager workflow (skip irrelevant dimensions)
- Better peer comparisons (compare SEs to top-performing SEs, not AEs)
- Clearer role expectations and development paths
