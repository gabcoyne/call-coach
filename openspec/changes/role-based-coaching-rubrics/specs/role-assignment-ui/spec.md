## ADDED Requirements

### Requirement: Settings page displays all Prefect staff with role assignments

The system SHALL provide a settings page at `/settings/roles` accessible only to managers that lists all Prefect staff identified by @prefect.io email domain.

#### Scenario: Manager navigates to roles settings page

- **WHEN** user with manager role navigates to `/settings/roles`
- **THEN** page displays list of all speakers with @prefect.io email addresses
- **THEN** each row shows name, email, current role, and last updated timestamp

#### Scenario: Non-manager cannot access roles page

- **WHEN** user without manager role attempts to access `/settings/roles`
- **THEN** system redirects to unauthorized page or shows 403 error
- **THEN** user cannot view or modify role assignments

#### Scenario: Page shows unassigned staff with default role

- **WHEN** viewing staff member who has no role assigned
- **THEN** page displays "AE (default)" as current role
- **THEN** dropdown allows selecting actual role

### Requirement: Manager can assign role to staff member

The system SHALL allow managers to assign one of three roles (AE, SE, CSM) to any Prefect staff member.

#### Scenario: Manager assigns role from dropdown

- **WHEN** manager selects role from dropdown for a staff member
- **THEN** system saves role assignment with manager email and timestamp
- **THEN** system displays success toast notification
- **THEN** role change is immediately reflected in UI

#### Scenario: Role assignment persists across sessions

- **WHEN** manager assigns role and later returns to settings page
- **THEN** assigned role is still displayed for that staff member
- **THEN** last updated timestamp shows when role was assigned

#### Scenario: Only three role options available

- **WHEN** manager opens role dropdown
- **THEN** dropdown shows exactly three options: "Account Executive (AE)", "Sales Engineer (SE)", "Customer Success Manager (CSM)"
- **THEN** no other role options are available

### Requirement: System validates email domain for role assignment

The system SHALL only allow role assignment to email addresses ending in @prefect.io domain.

#### Scenario: Staff list only shows Prefect employees

- **WHEN** loading staff list on roles settings page
- **THEN** system queries speakers table for emails ending in '@prefect.io'
- **THEN** customer and prospect emails are excluded from list

#### Scenario: API rejects role assignment for non-Prefect email

- **WHEN** API receives role assignment request for email not ending in @prefect.io
- **THEN** API returns 400 error with message "Only @prefect.io emails can be assigned roles"
- **THEN** no role assignment is created in database

### Requirement: Role changes are tracked with audit metadata

The system SHALL record who assigned the role and when for audit purposes.

#### Scenario: Role assignment stores manager identity

- **WHEN** manager assigns role to staff member
- **THEN** system stores manager's email in assigned_by field
- **THEN** system stores current timestamp in assigned_at field

#### Scenario: Role update preserves original assignment timestamp

- **WHEN** manager changes existing role assignment
- **THEN** system updates updated_at timestamp to current time
- **THEN** system preserves original assigned_at timestamp
- **THEN** system updates assigned_by to current manager's email

#### Scenario: UI displays last modified information

- **WHEN** viewing staff member with assigned role
- **THEN** UI shows "Last updated: 2 days ago by <manager@prefect.io>"
- **THEN** relative timestamp is human-readable

### Requirement: Role assignment API endpoints support CRUD operations

The system SHALL provide backend API endpoints for creating, reading, updating, and deleting role assignments.

#### Scenario: GET endpoint lists all role assignments

- **WHEN** calling GET /api/settings/roles
- **THEN** API returns array of all staff with role assignments
- **THEN** response includes email, role, assigned_by, assigned_at, updated_at for each staff member

#### Scenario: PUT endpoint updates role assignment

- **WHEN** calling PUT /api/settings/roles/[email] with role payload
- **THEN** API validates manager permission via Clerk
- **THEN** API updates or creates role assignment in database
- **THEN** API returns updated role assignment

#### Scenario: DELETE endpoint removes role assignment

- **WHEN** calling DELETE /api/settings/roles/[email]
- **THEN** API removes role assignment from database
- **THEN** staff member reverts to default AE role
- **THEN** API returns 204 No Content

### Requirement: UI provides search and filter for staff list

The system SHALL allow managers to search and filter the staff list for easier role management.

#### Scenario: Search filters by name or email

- **WHEN** manager types in search box
- **THEN** staff list filters to show only matching names or emails
- **THEN** search is case-insensitive
- **THEN** partial matches are supported

#### Scenario: Filter shows only specific role

- **WHEN** manager selects "Show only SEs" filter
- **THEN** staff list displays only members with SE role assigned
- **THEN** count shows "X SEs" in filter label

#### Scenario: Filter shows unassigned staff

- **WHEN** manager selects "Show unassigned" filter
- **THEN** staff list displays only members without explicit role assignment
- **THEN** these members are using default AE role

### Requirement: System provides bulk role assignment capability

The system SHALL allow managers to assign roles to multiple staff members at once for efficiency.

#### Scenario: Manager selects multiple staff members

- **WHEN** manager checks checkboxes next to multiple staff rows
- **THEN** bulk action bar appears at top of table
- **THEN** bar shows count of selected staff

#### Scenario: Bulk assign role to selected staff

- **WHEN** manager selects role from bulk action dropdown and clicks "Assign"
- **THEN** system assigns selected role to all checked staff members
- **THEN** system displays success toast with count of assignments made
- **THEN** all rows update to show new role

#### Scenario: Bulk actions respect permissions

- **WHEN** manager attempts bulk role assignment
- **THEN** system validates manager role for current user
- **THEN** if not manager, system prevents action and shows error
