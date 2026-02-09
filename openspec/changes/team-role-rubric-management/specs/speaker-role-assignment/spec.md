## ADDED Requirements

### Requirement: Speaker Role Field
The system SHALL store a business role for each speaker from Gong calls to enable role-appropriate coaching analysis.

#### Scenario: Role field exists
- **WHEN** a speaker record is created or retrieved
- **THEN** the speaker SHALL have a `role` field with values: "ae", "se", "csm", "support", or NULL

#### Scenario: Default role handling
- **WHEN** a speaker has no assigned role (NULL)
- **THEN** the system SHALL treat them as "ae" for analysis purposes
- **AND** SHALL display a "Role Not Assigned" warning in the UI

### Requirement: Role Assignment API
The system SHALL provide API endpoints for managers to assign and update speaker roles.

#### Scenario: Get speaker role
- **WHEN** GET /api/v1/speakers/{speaker_id}/role is called
- **THEN** the system SHALL return the speaker's current role and assignment metadata

#### Scenario: Update speaker role
- **WHEN** PUT /api/v1/speakers/{speaker_id}/role with role="csm" is called by a manager
- **THEN** the system SHALL update the speaker's role to "csm"
- **AND** SHALL record who made the change and when

#### Scenario: Invalid role rejected
- **WHEN** PUT /api/v1/speakers/{speaker_id}/role with role="invalid" is called
- **THEN** the system SHALL return 400 error with valid role options

#### Scenario: Non-manager access denied
- **WHEN** a non-manager user calls PUT /api/v1/speakers/{speaker_id}/role
- **THEN** the system SHALL return 403 Forbidden

### Requirement: Bulk Role Assignment
The system SHALL support assigning roles to multiple speakers at once for operational efficiency.

#### Scenario: Bulk role update
- **WHEN** PUT /api/v1/speakers/bulk-roles with array of {speaker_id, role} is called
- **THEN** the system SHALL update all specified speakers' roles
- **AND** SHALL return count of successful and failed updates

#### Scenario: Partial bulk success
- **WHEN** bulk role update includes some invalid speaker IDs
- **THEN** the system SHALL update valid speakers
- **AND** SHALL return list of failed speaker IDs with reasons

### Requirement: Speaker Role UI
The system SHALL provide a UI for managers to view and edit speaker roles in the team management interface.

#### Scenario: Speaker list shows roles
- **WHEN** a manager views /team/dashboard
- **THEN** each speaker SHALL display their current role as a badge
- **AND** unassigned speakers SHALL show "Role Not Assigned" warning

#### Scenario: Inline role editing
- **WHEN** a manager clicks "Edit Role" on a speaker
- **THEN** the system SHALL show a dropdown with role options (AE, SE, CSM, Support)
- **AND** SHALL save the role on selection

#### Scenario: Role filter
- **WHEN** a manager applies role filter on speaker list
- **THEN** the system SHALL show only speakers with selected role(s)

### Requirement: Role-Based Analysis Selection
The system SHALL use the speaker's role to determine which rubric criteria apply during coaching analysis.

#### Scenario: AE analysis uses AE rubric
- **WHEN** analyzing a call where the Prefect speaker has role="ae"
- **THEN** the system SHALL load rubric criteria WHERE role="ae"
- **AND** SHALL evaluate the speaker against AE-specific criteria

#### Scenario: CSM analysis uses CSM rubric
- **WHEN** analyzing a call where the Prefect speaker has role="csm"
- **THEN** the system SHALL load rubric criteria WHERE role="csm"
- **AND** SHALL evaluate against CSM-specific criteria (relationship building, retention focus)

#### Scenario: Unassigned role fallback
- **WHEN** analyzing a call where the speaker has role=NULL
- **THEN** the system SHALL use role="ae" as default
- **AND** SHALL log a warning that role was unassigned

### Requirement: Role Change Audit
The system SHALL track all speaker role changes for accountability and troubleshooting.

#### Scenario: Audit log entry
- **WHEN** a speaker's role is changed
- **THEN** the system SHALL create an audit log entry with: speaker_id, old_role, new_role, changed_by, changed_at

#### Scenario: Audit log retrieval
- **WHEN** GET /api/v1/speakers/{speaker_id}/role-history is called
- **THEN** the system SHALL return all role changes for that speaker ordered by date descending
