## 1. Database Schema

- [ ] 1.1 Create migration adding `role` column to `speakers` table (nullable, default NULL)
- [ ] 1.2 Create `rubric_criteria` table with columns: id, role, dimension, criterion_name, description, weight, max_score, display_order
- [ ] 1.3 Create `rubric_change_log` table for audit trail
- [ ] 1.4 Create `speaker_role_history` table for role change tracking
- [ ] 1.5 Seed default rubric criteria for all role-dimension combinations (AE, SE, CSM, Support × Discovery, Engagement, Five Wins)
- [ ] 1.6 Add indexes on `rubric_criteria` (role, dimension) and `speakers` (role)
- [ ] 1.7 Backfill existing speaker roles where possible (based on email patterns or manual mapping)

## 2. Backend: Speaker Role Management

- [ ] 2.1 Add `get_speaker_role(speaker_id)` query function
- [ ] 2.2 Add `update_speaker_role(speaker_id, role, changed_by)` query function
- [ ] 2.3 Add `bulk_update_speaker_roles(updates)` query function for batch operations
- [ ] 2.4 Add `get_speaker_role_history(speaker_id)` query function
- [ ] 2.5 Create `api/v1/speakers.py` with GET/PUT endpoints for speaker roles
- [ ] 2.6 Add role validation in speaker API (only allow: ae, se, csm, support)
- [ ] 2.7 Add RBAC check (managers only) for speaker role endpoints

## 3. Backend: Rubric Content Management

- [ ] 3.1 Add `get_rubric_criteria(role, dimension)` query function
- [ ] 3.2 Add `update_rubric_criterion(criterion_id, updates)` query function
- [ ] 3.3 Add `create_rubric_criterion(role, dimension, criterion_data)` query function
- [ ] 3.4 Add `delete_rubric_criterion(criterion_id)` query function
- [ ] 3.5 Add `validate_dimension_weights(role, dimension)` function (sum must equal 100)
- [ ] 3.6 Add `log_rubric_change(criterion_id, change_type, old_value, new_value, changed_by)` function
- [ ] 3.7 Create `api/v1/rubrics.py` with GET/PUT/POST/DELETE endpoints
- [ ] 3.8 Add rubric change audit log endpoint GET /api/v1/rubrics/audit-log

## 4. Backend: Role-Based Analysis Integration

- [ ] 4.1 Update `analyze_call_tool` to fetch speaker role from database
- [ ] 4.2 Modify `analysis/engine.py` to accept speaker role parameter
- [ ] 4.3 Update `analysis/engine.py` to load role-specific rubric criteria from database
- [ ] 4.4 Modify analysis prompt builder to inject role-specific criteria into prompts
- [ ] 4.5 Add fallback logic: if speaker role is NULL, use role="ae" as default
- [ ] 4.6 Update `discovery.py` prompt to use dynamic criteria based on role
- [ ] 4.7 Update `engagement.py` prompt to use dynamic criteria based on role
- [ ] 4.8 Update `five_wins.py` prompt to adapt win criteria based on role
- [ ] 4.9 Add role information to analysis response metadata

## 5. Frontend: Speaker Role Management UI

- [ ] 5.1 Add `role` field display to speaker cards in /team/dashboard
- [ ] 5.2 Add "Role Not Assigned" warning badge for speakers with NULL role
- [ ] 5.3 Create inline role editor dropdown with options (AE, SE, CSM, Support)
- [ ] 5.4 Add bulk role assignment interface (select multiple speakers → assign role)
- [ ] 5.5 Add role filter to speaker list view
- [ ] 5.6 Create speaker role history modal showing past role changes
- [ ] 5.7 Add success/error toasts for role update operations

## 6. Frontend: Rubric Management Page

- [ ] 6.1 Create `/rubrics` route and page component
- [ ] 6.2 Add role tabs (AE, SE, CSM, Support) to rubric page
- [ ] 6.3 Create dimension accordion sections (Discovery, Engagement, Five Wins, etc.)
- [ ] 6.4 Display criterion cards with: name, description, weight, max score
- [ ] 6.5 Add edit mode for criteria: inline editing of description and weight
- [ ] 6.6 Add weight validation: ensure dimension total equals 100%
- [ ] 6.7 Create "Add Criterion" form with validation
- [ ] 6.8 Add delete criterion confirmation dialog
- [ ] 6.9 Add "Reset to Default" button per dimension with confirmation
- [ ] 6.10 Add criterion search/filter across all roles
- [ ] 6.11 Add drag-and-drop reordering for criteria display order

## 7. Frontend: Rubric Audit and History

- [ ] 7.1 Create rubric change history view showing recent edits
- [ ] 7.2 Add "Restore Previous Version" functionality to audit log
- [ ] 7.3 Add filter controls for audit log (date range, role, dimension, user)
- [ ] 7.4 Create export rubric configuration to JSON feature

## 8. Frontend: Role-Aware Coaching Display

- [ ] 8.1 Add role badge to coaching analysis header (show which role rubric was used)
- [ ] 8.2 Update criterion display to show role-specific criteria names
- [ ] 8.3 Add tooltip explaining role-based evaluation on analysis pages
- [ ] 8.4 Update ScoreCard component to show role context

## 9. Testing

- [ ] 9.1 Write unit tests for speaker role query functions
- [ ] 9.2 Write unit tests for rubric CRUD query functions
- [ ] 9.3 Write integration tests for speaker role API endpoints
- [ ] 9.4 Write integration tests for rubric API endpoints
- [ ] 9.5 Write tests for role-based analysis selection logic
- [ ] 9.6 Write tests for weight validation (sum = 100%)
- [ ] 9.7 Write frontend tests for speaker role editor component
- [ ] 9.8 Write frontend tests for rubric management page

## 10. Documentation and Deployment

- [ ] 10.1 Update API documentation with new speaker and rubric endpoints
- [ ] 10.2 Create manager guide for using rubric editor
- [ ] 10.3 Create default rubric criteria documentation (what each criterion means)
- [ ] 10.4 Add feature flag `ENABLE_ROLE_BASED_RUBRICS` for gradual rollout
- [ ] 10.5 Create migration rollback script in case of issues
- [ ] 10.6 Update coaching analysis documentation to explain role-based evaluation
