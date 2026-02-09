## Why

Prefect staff participating in calls (Support, CSM, Sales Engineers, AEs) are currently treated as generic "reps" without role differentiation, causing rubrics to apply incorrectly to their performance. Additionally, there's no way to view or edit the rubric content and scoring criteria that drive coaching analysis, making it impossible to refine the coaching system based on what actually matters for each role.

## What Changes

- Add speaker-to-role association system that maps speakers from calls to their actual business role (Support, CSM, SE, AE)
- Create role-based rubric application so coaching analysis uses role-appropriate criteria
- Build rubric content viewer/editor for managers to review and refine scoring criteria
- Extend speaker data model to include role assignment
- Add UI for managing speaker roles in team management page
- Add dedicated rubric management page for viewing/editing rubric criteria

## Capabilities

### New Capabilities
- `speaker-role-assignment`: Map speakers from Gong calls to their business role (Support, CSM, Sales Engineer, Account Executive) with UI for role management
- `rubric-content-management`: View and edit rubric scoring criteria, dimensions, and weights for each role type

### Modified Capabilities
- `discovery-analysis`: Rubric criteria application must respect speaker role
- `engagement-analysis`: Rubric criteria application must respect speaker role
- `five-wins-rubric`: Win criteria may vary by speaker role (AE vs SE vs CSM)

## Impact

**Database**:
- `speakers` table: Add `role` column (support, csm, se, ae)
- `coaching_dimensions` table: May need role-specific rubric references

**Backend**:
- `analysis/engine.py`: Apply role-appropriate rubrics during analysis
- `analysis/prompts/*.py`: May need role-specific prompt variations
- `coaching_mcp/tools/analyze_call.py`: Pass speaker role to analysis engine
- `db/queries.py`: Add speaker role queries and rubric CRUD operations

**Frontend**:
- `/team/dashboard`: Add speaker role management interface
- `/rubrics` (new): Rubric content viewer and editor page
- `components/coaching/*`: Display role-aware coaching insights

**API**:
- `api/v1/speakers.py` (new): Speaker role management endpoints
- `api/v1/rubrics.py` (new): Rubric content management endpoints
