## 1. Database Schema for Staff Roles

- [x] 1.1 Create db/migrations/004_staff_roles.sql with staff_roles table (email PK, role CHECK constraint, assigned_by, assigned_at, updated_at)
- [x] 1.2 Add index idx_staff_roles_role on role column for filtering queries
- [x] 1.3 Run migration on Neon database to create staff_roles table
- [x] 1.4 Verify table structure with SELECT query

## 2. Role-Specific Rubric JSON Files

- [x] 2.1 Create analysis/rubrics/ directory
- [x] 2.2 Create analysis/rubrics/ae_rubric.json with 5 dimensions (Discovery 30%, Objection Handling 25%, Product Positioning 20%, Relationship Building 15%, Call Control 10%)
- [x] 2.3 Create analysis/rubrics/se_rubric.json with 5 dimensions (Technical Accuracy 35%, Architecture Fit 30%, Problem-Solution Mapping 20%, Technical Objection Resolution 10%, Collaboration with AE 5%)
- [x] 2.4 Create analysis/rubrics/csm_rubric.json with 5 dimensions (Value Realization 30%, Risk Identification 25%, Relationship Depth 20%, Expansion Opportunity 15%, Product Adoption 10%)
- [x] 2.5 Add detailed criteria arrays (3-5 items) for each dimension in all three rubrics
- [x] 2.6 Add scoring bands (0-49, 50-69, 70-89, 90-100) with role-specific descriptions for each dimension
- [x] 2.7 Verify all rubric dimension weights sum to 1.0 exactly

## 3. Rubric Validation and Loading Module

- [x] 3.1 Create analysis/rubric_loader.py module
- [x] 3.2 Implement validate_rubric(rubric_dict) function checking required fields (role, dimensions)
- [x] 3.3 Implement check that dimension weights sum to 1.0 within 0.01 tolerance
- [x] 3.4 Implement check that each dimension has all four scoring bands (0-49, 50-69, 70-89, 90-100)
- [x] 3.5 Implement load_rubric(role: str) function that reads JSON and validates structure
- [x] 3.6 Add in-memory cache for loaded rubrics (dict keyed by role)
- [x] 3.7 Implement reload_rubrics() function to refresh cache from filesystem
- [x] 3.8 Test rubric loading with all three roles and verify validation catches malformed JSON

## 4. Database Queries for Role Management

- [x] 4.1 Add get_staff_role(email: str) function to db/queries.py returning role or None
- [x] 4.2 Add upsert_staff_role(email, role, assigned_by) function for creating/updating role assignments
- [x] 4.3 Add delete_staff_role(email) function for removing role assignment
- [x] 4.4 Add list_all_staff_roles() function returning all role assignments with metadata
- [x] 4.5 Add get_prefect_staff() function querying speakers table for unique emails ending in '@prefect.io'
- [x] 4.6 Test all queries with sample data

## 5. Role-Aware Coaching Analysis Engine

- [x] 5.1 Update analysis/opportunity_coaching.py to import rubric_loader
- [x] 5.2 Implement detect_speaker_role(call_id: str) function that finds Prefect speaker and looks up role
- [x] 5.3 Add fallback to 'ae' role if speaker not found in staff_roles table
- [x] 5.4 Update analyze_call_dimension() to call detect_speaker_role() and load appropriate rubric
- [x] 5.5 Pass role-specific rubric to Claude API in analysis prompt
- [x] 5.6 Store rubric_role in coaching_sessions.metadata JSON field
- [x] 5.7 Add logging for speaker detection and rubric selection (info level)
- [x] 5.8 Test analysis with calls from speakers with different assigned roles

## 6. Learning Insights Role Filtering

- [ ] 6.1 Update analysis/learning_insights.py to accept rep_role parameter
- [ ] 6.2 Modify find_similar_won_opportunities() to filter by opportunity owner role
- [ ] 6.3 Modify aggregate_coaching_patterns() to only compare within same role
- [ ] 6.4 Update get_learning_insights() to detect rep role and pass to comparison functions
- [ ] 6.5 Add role context to generated insights (e.g., "Comparing to top-performing Sales Engineers")
- [ ] 6.6 Test that SE insights only show examples from other SEs, not AEs

## 7. Backend API for Role Assignment

- [ ] 7.1 Create app/api/settings/roles/route.ts with GET handler listing all staff with roles
- [ ] 7.2 Add middleware checking user is manager (Clerk publicMetadata.role === 'manager')
- [ ] 7.3 Return 403 error if non-manager attempts to access
- [ ] 7.4 Query db.get_prefect_staff() and db.list_all_staff_roles(), merge results
- [ ] 7.5 Create app/api/settings/roles/[email]/route.ts with PUT handler for updating role
- [ ] 7.6 Validate email ends in '@prefect.io' in PUT handler, return 400 if not
- [ ] 7.7 Call db.upsert_staff_role() with role, manager email, current timestamp
- [ ] 7.8 Add DELETE handler to remove role assignment
- [ ] 7.9 Test API endpoints with curl/Postman for CRUD operations

## 8. Frontend Role Assignment UI

- [ ] 8.1 Create app/settings/roles/page.tsx with manager-only guard
- [ ] 8.2 Fetch staff and roles from /api/settings/roles with useSWR
- [ ] 8.3 Create components/RoleAssignmentTable.tsx for displaying staff list
- [ ] 8.4 Add columns: Name, Email, Role (dropdown), Last Updated
- [ ] 8.5 Implement role dropdown with three options (AE, SE, CSM)
- [ ] 8.6 Add onChange handler that calls PUT /api/settings/roles/[email]
- [ ] 8.7 Display success toast on role update
- [ ] 8.8 Add search input to filter staff by name or email
- [ ] 8.9 Add role filter dropdown (Show All / AE only / SE only / CSM only / Unassigned)
- [ ] 8.10 Add "Last updated" column with relative time (e.g., "2 days ago")
- [ ] 8.11 Show assigned_by in tooltip on hover over Last Updated
- [ ] 8.12 Test page loads for manager user, redirects for non-manager

## 9. Bulk Role Assignment Feature

- [ ] 9.1 Add checkbox column to RoleAssignmentTable for row selection
- [ ] 9.2 Add "Select All" checkbox in table header
- [ ] 9.3 Show bulk action bar when 2+ rows selected with count (e.g., "3 selected")
- [ ] 9.4 Add bulk role dropdown in action bar (AE / SE / CSM)
- [ ] 9.5 Add "Assign Role" button in action bar
- [ ] 9.6 Implement onClick handler that calls PUT for each selected email in parallel
- [ ] 9.7 Show progress indicator while bulk assignment in progress
- [ ] 9.8 Display success toast with count (e.g., "Updated 5 staff members")
- [ ] 9.9 Clear selection after successful bulk assignment
- [ ] 9.10 Test bulk assigning 10 staff members to SE role

## 10. Call Detail Page Rubric Badge

- [ ] 10.1 Update app/calls/[id]/page.tsx to fetch coaching session metadata
- [ ] 10.2 Extract rubric_role from coaching_sessions.metadata JSON
- [ ] 10.3 Create components/RubricBadge.tsx displaying role used for evaluation
- [ ] 10.4 Show badge text: "Evaluated as: Account Executive" (or SE/CSM)
- [ ] 10.5 Style badge with role-specific colors (AE = blue, SE = green, CSM = purple)
- [ ] 10.6 Add tooltip explaining role-specific evaluation criteria
- [ ] 10.7 Position badge prominently near coaching scores section
- [ ] 10.8 Test badge displays correctly for calls with AE, SE, CSM rubrics

## 11. Rep Dashboard Role-Specific Metrics

- [ ] 11.1 Update app/reps/[email]/page.tsx to fetch rep role from staff_roles
- [ ] 11.2 Modify dashboard layout to emphasize role-appropriate dimensions
- [ ] 11.3 For AE role: show Discovery, Objection Handling, Product Positioning prominently
- [ ] 11.4 For SE role: show Technical Accuracy, Architecture Fit, Problem-Solution Mapping prominently
- [ ] 11.5 For CSM role: show Value Realization, Risk Identification, Relationship Depth prominently
- [ ] 11.6 De-emphasize or hide dimensions not relevant to role (e.g., hide discovery for SEs)
- [ ] 11.7 Display dimension weights from rubric next to each score (e.g., "Technical Accuracy: 35%")
- [ ] 11.8 Add section header: "Performance by [Role] Standards"
- [ ] 11.9 Test dashboard shows different metrics for AE vs SE vs CSM

## 12. Opportunity Insights Role-Aware Aggregation

- [ ] 12.1 Update components/OpportunityInsights.tsx to detect roles of all speakers on opportunity calls
- [ ] 12.2 Group calls by speaker role (AE calls, SE calls, CSM calls)
- [ ] 12.3 Display separate coaching summaries per role: "AE Performance" and "SE Performance" sections
- [ ] 12.4 Show role badges next to each call in timeline indicating which rubric was used
- [ ] 12.5 Generate role-specific recommendations (e.g., "AE should improve discovery, SE should add more architecture options")
- [ ] 12.6 Test opportunity with mixed AE+SE calls shows separate evaluations

## 13. MCP Tool Updates for Role-Aware Analysis

- [ ] 13.1 Update coaching_mcp/tools/analyze_call.py to detect speaker role before analysis
- [ ] 13.2 Load role-specific rubric and pass to analysis engine
- [ ] 13.3 Update coaching_mcp/tools/get_learning_insights.py to filter by rep role
- [ ] 13.4 Add role parameter to tool input schema (optional, auto-detected if not provided)
- [ ] 13.5 Update tool descriptions to mention role-aware evaluation
- [ ] 13.6 Test tools via Claude Desktop with calls from different role speakers

## 14. Documentation and Testing

- [ ] 14.1 Update CLAUDE.md with section on role-based coaching
- [ ] 14.2 Document how to assign roles in settings UI
- [ ] 14.3 Document rubric structure and how to add new dimensions
- [ ] 14.4 Create sample data script populating staff_roles for testing (assign roles to known Prefect emails)
- [ ] 14.5 Test end-to-end: assign role → analyze call → verify correct rubric used → see insights
- [ ] 14.6 Test learning insights only compare within role
- [ ] 14.7 Verify role changes are reflected in future analyses (not retroactive)
- [ ] 14.8 Test bulk role assignment with 20 staff members
- [ ] 14.9 Verify non-managers cannot access /settings/roles
- [ ] 14.10 Document in README how role-based coaching improves relevance

## 15. Salesforce Sync Investigation (Parallel Task)

- [ ] 15.1 Check if Gong CRM integration exposes opportunities via API
- [ ] 15.2 Test GET /v2/crm/opportunities endpoint with proper authentication
- [ ] 15.3 If available, update flows/daily_gong_sync.py to use correct endpoint
- [ ] 15.4 Parse Salesforce opportunity data (owner, stage, amount) from Gong response
- [ ] 15.5 Run sync and verify real opportunities populate database
- [ ] 15.6 If CRM endpoint unavailable, document limitation in CLAUDE.md
