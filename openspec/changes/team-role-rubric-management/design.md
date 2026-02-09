## Context

Currently, all Prefect staff in calls are treated as generic "reps" in the system, regardless of their actual role (Support, CSM, Sales Engineer, Account Executive). This causes coaching rubrics designed for AEs to incorrectly apply to Support staff or CSMs, leading to irrelevant feedback. Additionally, rubric content (scoring criteria, dimension weights, evaluation prompts) is hardcoded in Python files, making it impossible for managers to review or refine what the system evaluates without code changes.

**Current State**:
- `speakers` table has `company_side` boolean but no role differentiation
- Analysis prompts in `analysis/prompts/*.py` are role-agnostic
- Rubric criteria are Python strings in prompt files
- No UI exists for managing speaker roles or viewing rubric content

**Stakeholders**:
- Sales managers need to assign correct roles to speakers
- Managers need to review/edit rubric criteria for their team's roles
- Analysis engine needs role information to apply appropriate rubrics
- Frontend needs to display role-aware coaching insights

## Goals / Non-Goals

**Goals:**
- Add speaker role field to database and propagate through analysis pipeline
- Apply role-appropriate rubrics during coaching analysis (AE rubrics for AEs, CSM rubrics for CSMs)
- Create UI for managers to assign/edit speaker roles
- Create UI for managers to view and edit rubric content
- Store rubric content in database as structured data (not hardcoded Python strings)
- Maintain backward compatibility (calls with speakers lacking roles use default rubrics)

**Non-Goals:**
- Automatic role detection from call content (manual assignment only)
- Role-based access control beyond existing manager permissions (RBAC stays same)
- Historical re-analysis of old calls with new role assignments (future calls only)
- Multi-tenancy or per-customer rubric customization (single rubric set per role)

## Decisions

### Decision 1: Speaker Role as Database Column vs External Mapping

**Chosen**: Add `role` column directly to `speakers` table

**Rationale**:
- Simpler data model - role is intrinsic speaker attribute
- Efficient query performance (no joins needed)
- Easier to maintain consistency (role always with speaker record)
- **Alternative considered**: Separate `speaker_roles` mapping table → Rejected for unnecessary complexity

**Trade-off**: Denormalization means role updates require updating all speaker records. Acceptable since roles rarely change.

### Decision 2: Rubric Storage - Database vs Python Prompts

**Chosen**: Hybrid approach - store rubric metadata in DB, keep prompts in Python

**Rationale**:
- Rubric **criteria and weights** go in `rubric_criteria` table (editable via UI)
- Rubric **prompts** stay in `analysis/prompts/*.py` (require code review for safety)
- Separates "what to evaluate" (criteria - user editable) from "how to evaluate" (prompts - developer controlled)
- **Alternative considered**: All in database → Rejected due to prompt injection risk
- **Alternative considered**: All in Python → Rejected due to poor user experience for managers

**Trade-off**: Split system increases complexity but balances flexibility with safety.

### Decision 3: Role-Based Prompt Selection

**Chosen**: Single prompt with role parameter, role-specific criteria from DB

**Rationale**:
- Prompt template stays generic: "Evaluate {dimension} for {role} using criteria: {criteria}"
- Role-specific criteria loaded from `rubric_criteria WHERE role = {speaker_role}`
- Avoids prompt proliferation (4 roles × 4 dimensions = 16 prompt files)
- **Alternative considered**: Separate prompt files per role → Rejected due to maintenance burden

### Decision 4: UI Structure - Integrated vs Separate Pages

**Chosen**: Separate pages for speaker roles and rubrics

**Rationale**:
- `/team/dashboard` → Speaker role management (who is what role)
- `/rubrics` → Rubric content management (what criteria apply to each role)
- Clearer mental model (people vs evaluation criteria)
- **Alternative considered**: Combined page → Rejected due to cognitive overload

## Risks / Trade-offs

**Risk**: Rubric edits could degrade coaching quality if managers set poor criteria
→ **Mitigation**: Add "reset to default" option and audit log of rubric changes

**Risk**: Role assignment lag (new speakers won't have roles until manually assigned)
→ **Mitigation**: Default to "ae" role if unassigned, show "role not assigned" warning in UI

**Risk**: Prompt injection via user-edited criteria field
→ **Mitigation**: Strict validation on criteria text (no code, no special chars), max length 500 chars

**Trade-off**: Storing rubric criteria in DB means losing version control for criteria changes
→ **Mitigation**: Add `rubric_change_log` table to track all edits with timestamps and user

**Risk**: Role-based analysis breaks backward compatibility for old calls
→ **Mitigation**: Analysis engine falls back to default rubric if speaker has no role

## Migration Plan

**Phase 1: Database Schema** (non-breaking)
1. Add `role` column to `speakers` table (nullable, default NULL)
2. Create `rubric_criteria` table with columns: id, role, dimension, criterion_name, weight, max_score
3. Create `rubric_change_log` table for audit trail
4. Backfill existing speaker roles based on email domain or manual CSV import

**Phase 2: Backend Changes** (backward compatible)
1. Update `analyze_call_tool` to read speaker role from database
2. Modify `analysis/engine.py` to load role-specific criteria from `rubric_criteria` table
3. Add API endpoints: `GET/PUT /api/v1/speakers/{id}/role`, `GET/PUT /api/v1/rubrics`
4. Analysis gracefully handles NULL role (uses default rubric)

**Phase 3: Frontend Changes**
1. Add role dropdown to `/team/dashboard` speaker list
2. Create `/rubrics` page with table of criteria per role/dimension
3. Add role badge display in coaching analysis views

**Rollback Strategy**:
- Phase 1: Drop new tables and columns (data loss acceptable in dev)
- Phase 2: Feature flag `ENABLE_ROLE_BASED_RUBRICS` to disable new logic
- Phase 3: Frontend changes are additive (old views still work)

## Open Questions

1. **Should CSMs have different rubrics than AEs?** → Need product input on CSM success criteria
2. **Max number of criteria per dimension?** → Propose 5-10 to avoid overwhelming prompts
3. **Who can edit rubrics?** → Managers only, or also admins? → Assume managers + admins
4. **Default role for new speakers?** → "ae" or "unassigned"? → Lean toward "unassigned" with UI warning
