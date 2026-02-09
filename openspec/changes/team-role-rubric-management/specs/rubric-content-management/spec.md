## ADDED Requirements

### Requirement: Rubric Criteria Storage
The system SHALL store rubric evaluation criteria in a structured database table for manager editing and role-based application.

#### Scenario: Rubric criteria table structure
- **WHEN** querying rubric criteria
- **THEN** each criterion SHALL have: id, role, dimension, criterion_name, description, weight, max_score, created_at, updated_at

#### Scenario: Role-dimension criteria retrieval
- **WHEN** GET /api/v1/rubrics?role=ae&dimension=discovery is called
- **THEN** the system SHALL return all criteria for AE role and discovery dimension

#### Scenario: Multiple criteria per dimension
- **WHEN** a dimension has multiple criteria
- **THEN** the system SHALL support 1-15 criteria per role-dimension combination
- **AND** SHALL enforce total weights sum to 100 for each dimension

### Requirement: Rubric Viewing Interface
The system SHALL provide a UI for managers to view current rubric criteria organized by role and dimension.

#### Scenario: Rubric overview page
- **WHEN** a manager visits /rubrics
- **THEN** the system SHALL display tabs for each role (AE, SE, CSM, Support)
- **AND** SHALL show accordion sections for each dimension (Discovery, Engagement, Product Knowledge, Objection Handling)

#### Scenario: Criterion detail view
- **WHEN** a manager expands a dimension
- **THEN** the system SHALL show all criteria with: name, description, weight (%), max score
- **AND** SHALL show total weight sum for the dimension

#### Scenario: Search and filter
- **WHEN** a manager searches for keyword "rapport"
- **THEN** the system SHALL highlight all criteria containing "rapport" across all roles and dimensions

### Requirement: Rubric Editing Capabilities
The system SHALL allow managers to edit rubric criteria content while maintaining data integrity.

#### Scenario: Edit criterion description
- **WHEN** a manager clicks "Edit" on a criterion and changes the description
- **THEN** the system SHALL save the updated description
- **AND** SHALL record the change in audit log with timestamp and user

#### Scenario: Edit criterion weight
- **WHEN** a manager changes a criterion weight from 20% to 25%
- **THEN** the system SHALL validate total dimension weights still sum to 100%
- **AND** SHALL reject if total would exceed 100%

#### Scenario: Add new criterion
- **WHEN** a manager clicks "Add Criterion" for a dimension
- **THEN** the system SHALL show form with fields: name, description, weight, max_score
- **AND** SHALL validate weight doesn't cause dimension total to exceed 100%

#### Scenario: Delete criterion
- **WHEN** a manager deletes a criterion
- **THEN** the system SHALL confirm deletion with warning about impact on future analyses
- **AND** SHALL only delete if confirmed

#### Scenario: Reorder criteria
- **WHEN** a manager drags a criterion to reorder
- **THEN** the system SHALL update the display order
- **AND** SHALL preserve the order in subsequent loads

### Requirement: Rubric Templates and Defaults
The system SHALL provide default rubric templates and allow reset to defaults.

#### Scenario: Default rubrics on first load
- **WHEN** accessing rubrics for the first time
- **THEN** the system SHALL show pre-populated default criteria for each role-dimension
- **AND** default criteria SHALL be clearly marked as "Default Template"

#### Scenario: Reset to default
- **WHEN** a manager clicks "Reset to Default" on a dimension
- **THEN** the system SHALL confirm the reset action
- **AND** SHALL restore default criteria for that dimension
- **AND** SHALL log the reset in audit trail

#### Scenario: Export rubric configuration
- **WHEN** a manager clicks "Export Rubrics"
- **THEN** the system SHALL download a JSON file with all current rubric criteria
- **AND** SHALL include metadata: export_date, exported_by

### Requirement: Rubric Validation
The system SHALL enforce data integrity rules on rubric criteria to prevent invalid configurations.

#### Scenario: Weight sum validation
- **WHEN** saving criterion weights for a dimension
- **THEN** the system SHALL verify total weights sum to exactly 100%
- **AND** SHALL reject save with error if sum is not 100%

#### Scenario: Max score validation
- **WHEN** setting a criterion's max_score
- **THEN** the system SHALL enforce max_score is between 1 and 100
- **AND** SHALL reject invalid values

#### Scenario: Name uniqueness
- **WHEN** adding a new criterion
- **THEN** the system SHALL enforce unique criterion names within a role-dimension
- **AND** SHALL reject duplicates with error message

#### Scenario: Description length
- **WHEN** entering criterion description
- **THEN** the system SHALL enforce 10-500 character limit
- **AND** SHALL show character count during editing

### Requirement: Rubric Change Audit
The system SHALL track all rubric criteria changes for accountability and rollback capability.

#### Scenario: Change log entry
- **WHEN** any rubric criterion is created, updated, or deleted
- **THEN** the system SHALL create audit log entry with: criterion_id, change_type, old_value, new_value, changed_by, changed_at

#### Scenario: Audit log viewing
- **WHEN** GET /api/v1/rubrics/audit-log is called
- **THEN** the system SHALL return all rubric changes ordered by date descending
- **AND** SHALL support filtering by role, dimension, date range

#### Scenario: Rollback support
- **WHEN** a manager views audit log for a criterion
- **THEN** the system SHALL show "Restore This Version" option for previous values
- **AND** SHALL allow one-click restoration of previous criterion state

### Requirement: Role-Specific Rubric Application
The system SHALL apply role-appropriate rubric criteria during call analysis based on speaker role.

#### Scenario: AE analysis criteria
- **WHEN** analyzing a call with speaker role="ae"
- **THEN** the analysis engine SHALL load criteria WHERE role="ae" AND dimension={current_dimension}
- **AND** SHALL evaluate against AE-specific criteria only

#### Scenario: CSM analysis criteria
- **WHEN** analyzing a call with speaker role="csm"
- **THEN** the analysis engine SHALL load criteria WHERE role="csm"
- **AND** SHALL use CSM-focused criteria (relationship building, retention, customer health)

#### Scenario: Mixed role call handling
- **WHEN** analyzing a call with multiple Prefect speakers of different roles
- **THEN** the system SHALL analyze each speaker against their role-specific rubric
- **AND** SHALL generate separate coaching insights per speaker

### Requirement: Rubric Preview Before Analysis
The system SHALL allow managers to preview how rubric changes affect analysis before applying.

#### Scenario: Preview mode
- **WHEN** a manager enables "Preview Mode" on rubric editor
- **THEN** the system SHALL show sample analysis output using current criteria
- **AND** SHALL not affect production analyses

#### Scenario: Before/after comparison
- **WHEN** editing a criterion weight
- **THEN** the system SHALL show before/after score impact on sample call
- **AND** SHALL highlight criteria with changed scores
