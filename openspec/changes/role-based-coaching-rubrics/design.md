## Context

**Current State:**
- Single coaching rubric applied to all Prefect staff regardless of role
- Coaching dimensions (discovery, objections, product knowledge, engagement) weighted equally
- No way to distinguish AE vs SE vs CSM in analysis
- Speakers table has email field but no role information
- Learning insights compare reps across different roles (apples to oranges)

**Problem:**
- SEs evaluated on discovery skills they don't use (they support AEs, not lead discovery)
- CSMs get penalized for not handling objections (they focus on retention, not new sales)
- AEs compared to SEs in technical depth (different expertise expectations)
- Managers manually filter irrelevant coaching feedback

**Constraints:**
- Must work with existing speakers table (email field)
- @prefect.io domain identifies Prefect staff
- Role assignment is manager-only (RBAC via Clerk)
- Must support role changes over time (promotions, transfers)

## Goals / Non-Goals

**Goals:**
- Enable role-specific coaching evaluation for AE, SE, CSM
- Store role assignments persistently in database
- Automatically apply appropriate rubric based on speaker role
- Provide UI for managers to assign/update roles
- Compare performance within role (SE vs top SEs, not vs AEs)

**Non-Goals:**
- Role-based access control for viewing coaching (separate feature)
- Automated role detection from call content (explicit assignment only)
- Historical role tracking / audit trail (just current role)
- Support for non-Prefect staff roles (customers, prospects)
- Custom rubric creation by managers (predefined AE/SE/CSM only)

## Decisions

### Decision 1: Simple staff_roles Table with Email as Primary Key

**Choice:** Create lightweight table with (email, role, assigned_by, assigned_at).

**Alternatives Considered:**
1. **Add role column to speakers table** - Speakers table is per-call, role is per-person (data duplication)
2. **Use Clerk metadata for roles** - Coaching roles != auth roles, need separate persistence
3. **Complex role history table** - Over-engineering, just need current role

**Rationale:**
- Email is unique identifier for Prefect staff
- Role changes are rare (quarterly at most)
- Simple JOIN: `speakers.email → staff_roles.email → get role`
- If role not found, default to AE (most common)

**Schema:**
```sql
CREATE TABLE staff_roles (
    email VARCHAR PRIMARY KEY,  -- e.g., sarah.chen@prefect.io
    role VARCHAR NOT NULL CHECK (role IN ('ae', 'se', 'csm')),
    assigned_by VARCHAR NOT NULL,  -- Manager email who made assignment
    assigned_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_staff_roles_role ON staff_roles(role);
```

### Decision 2: Role-Specific Rubrics as JSON Files

**Choice:** Store three rubric definitions as JSON files, loaded at analysis time.

**Alternatives Considered:**
1. **Hard-code rubrics in Python** - Hard to maintain, requires code deploy to change
2. **Store rubrics in database** - Overkill for ~3 static configs
3. **Single rubric with role-based weighting** - Less flexible, harder to customize per role

**Rationale:**
- JSON is easy to read/edit without code changes
- Each role has fundamentally different dimensions, not just different weights
- Can version control rubric changes
- Loading from disk is fast enough (cached in memory)

**Rubric Structure:**
```json
{
  "role": "ae",
  "dimensions": [
    {
      "id": "discovery",
      "name": "Discovery & Qualification",
      "weight": 0.30,
      "criteria": [
        "Asks open-ended questions about pain points",
        "Identifies budget and timeline (BANT)",
        "Uncovers decision-making process"
      ],
      "scoring": {
        "90-100": "Excellent: Comprehensive discovery with all BANT covered",
        "70-89": "Good: Most key areas explored, minor gaps",
        "50-69": "Needs Improvement: Surface-level questions, missed critical info",
        "0-49": "Poor: Didn't qualify properly or ask discovery questions"
      }
    },
    {
      "id": "objection_handling",
      "name": "Objection Handling",
      "weight": 0.25,
      "criteria": ["..."]
    }
  ]
}
```

**AE Rubric Dimensions (weights):**
- Discovery & Qualification (30%)
- Objection Handling (25%)
- Product Positioning (20%)
- Relationship Building (15%)
- Call Control & Next Steps (10%)

**SE Rubric Dimensions (weights):**
- Technical Accuracy (35%)
- Architecture Fit & Design (30%)
- Problem-Solution Mapping (20%)
- Objection Resolution (Technical) (10%)
- Collaboration with AE (5%)

**CSM Rubric Dimensions (weights):**
- Value Realization Tracking (30%)
- Risk Identification (25%)
- Relationship Depth (20%)
- Expansion Opportunity Spotting (15%)
- Product Adoption Coaching (10%)

### Decision 3: Automatic Role Detection During Analysis

**Choice:** When analyzing a call, lookup speaker role and load appropriate rubric automatically.

**Alternatives Considered:**
1. **Manual rubric selection by manager** - Too slow, error-prone
2. **Analyze with all rubrics, show relevant one** - Wastes Claude API tokens
3. **Role from Clerk user metadata** - Coaching staff != app users (speakers might not have accounts)

**Rationale:**
- Speaker email in transcripts → lookup role → load rubric → analyze
- Falls back to AE rubric if role not assigned (most common case)
- Efficient: only one Claude API call per dimension

**Implementation:**
```python
def analyze_call_with_role_awareness(call_id: str, dimension: str) -> dict:
    # Get Prefect speakers from call
    speakers = db.get_speakers(call_id, company_side=True)
    prefect_speaker = next((s for s in speakers if s.email.endswith('@prefect.io')), None)

    if not prefect_speaker:
        # External call (customer-only), use default rubric
        rubric = load_rubric('ae')
    else:
        # Lookup role
        role = db.get_staff_role(prefect_speaker.email) or 'ae'
        rubric = load_rubric(role)

    # Analyze with role-specific rubric
    return run_claude_analysis(call_id, dimension, rubric)
```

### Decision 4: Role Assignment UI in Settings (Manager-Only)

**Choice:** Create `/settings/roles` page accessible only to managers.

**Alternatives Considered:**
1. **Edit role inline in coaching view** - Clutters UI, too easy to change accidentally
2. **Backend-only role assignment via SQL** - Not user-friendly for managers
3. **Bulk CSV upload** - Over-engineered for ~20-30 staff

**Rationale:**
- Centralized settings page keeps UI clean
- Managers rarely change roles (quarterly at most)
- Easy to audit who has what role
- RBAC via Clerk: check `user.publicMetadata.role === 'manager'`

**UI Flow:**
1. Manager goes to `/settings/roles`
2. See table of all Prefect staff (from speakers table where email LIKE '%@prefect.io')
3. Each row: Name, Email, Current Role (dropdown: AE/SE/CSM), Last Updated
4. Manager changes dropdown → auto-saves via API
5. Toast notification: "Role updated for sarah.chen@prefect.io"

### Decision 5: Filter Learning Insights by Role

**Choice:** When comparing rep to top performers, only compare within same role.

**Alternatives Considered:**
1. **Cross-role comparisons** - Misleading (SE to AE comparison is apples to oranges)
2. **No filtering** - Current broken behavior
3. **Optional filter toggle** - Adds complexity, unclear value

**Rationale:**
- Top-performing SEs use different techniques than top AEs
- Learning insights should show "what good looks like for YOUR role"
- SE learning from another SE is actionable
- SE learning from an AE is confusing (different job functions)

**Implementation:**
```python
def get_learning_insights(rep_email: str, focus_area: str) -> dict:
    rep_role = db.get_staff_role(rep_email) or 'ae'

    # Only compare to same role
    top_performers = db.get_top_performers(
        role=rep_role,
        focus_area=focus_area,
        min_score=85,
        limit=10
    )

    # Generate comparison with role-appropriate examples
    return compare_with_role_context(rep_email, top_performers, rep_role)
```

## Risks / Trade-offs

**Risk:** Role assignments get out of sync if staff changes roles and manager forgets to update
- **Mitigation:** Add "Last Updated" column in UI to highlight stale assignments
- **Future:** Sync with HR system (Workday) if available

**Risk:** New Prefect staff appear in calls before role assigned
- **Mitigation:** Default to AE rubric (most common role)
- **Future:** Auto-detect likely role from email (if contains "se" or "csm") as suggestion

**Risk:** Speakers with typos in email domain (prefect.com vs prefect.io)
- **Mitigation:** Email validation in speakers table, data cleanup script
- **Monitor:** Alert if unknown @prefect.* domain appears

**Risk:** Role-specific rubrics diverge in quality (e.g., SE rubric less detailed than AE)
- **Mitigation:** Review all rubrics together, ensure consistent quality
- **Ownership:** Sales leadership approves rubric definitions

**Trade-off:** Hard-coded 3 roles (AE/SE/CSM) vs. flexible role system
- **Decision:** Start with 3, add more only if genuinely needed
- **Why:** Covers 95% of Prefect sales org, simpler to maintain

**Trade-off:** Role in separate table vs. speakers table
- **Decision:** Separate table (staff_roles) even though it requires JOIN
- **Why:** Speakers table is per-call, role is per-person (avoid duplication)

## Migration Plan

**Phase 1: Schema & Rubrics (No Breaking Changes)**
1. Create staff_roles table
2. Create analysis/rubrics/ directory with ae_rubric.json, se_rubric.json, csm_rubric.json
3. Update analysis modules to load rubrics dynamically
4. No change to existing behavior (all default to AE rubric)

**Phase 2: Role Assignment UI**
1. Create `/settings/roles` page (manager-only)
2. Build API routes for role CRUD
3. Populate initial roles (manual assignment by manager)

**Phase 3: Activate Role-Aware Analysis**
1. Update analyze_call to detect speaker role
2. Update learning_insights to filter by role
3. Test with mixed-role calls (AE + SE on same call)
4. Verify coaching feedback is role-appropriate

**Phase 4: Backfill Historical Data (Optional)**
1. Analyze which speakers are AE/SE/CSM based on call patterns
2. Generate suggested role assignments
3. Manager reviews and approves

**Rollback:**
- Phase 1-2: Just drop staff_roles table, remove settings page
- Phase 3: Set `ENABLE_ROLE_AWARE_COACHING=false` env var to disable
- No data loss: existing coaching sessions unchanged

## Open Questions

**Q1:** What if a call has multiple Prefect speakers (AE + SE)?
- **Answer:** Use primary speaker (most talk time). SE-led calls use SE rubric, AE-led use AE rubric.

**Q2:** Should we show role-specific insights on the call detail page?
- **Answer:** Yes. Add badge showing which rubric was used: "Evaluated as: Sales Engineer"

**Q3:** Can a person have multiple roles (e.g., SE who sometimes does CSM work)?
- **Answer:** No. One primary role per person. If they wear multiple hats, assign most frequent role.

**Q4:** Should rubrics be editable by managers?
- **Answer:** No, not in V1. Rubrics are set by sales leadership. Editing adds complexity (versioning, validation).

**Q5:** How to handle promotions (AE → CSM)?
- **Answer:** Manager updates role in settings UI. Historical coaching sessions keep original rubric (don't retroactively regrade).
