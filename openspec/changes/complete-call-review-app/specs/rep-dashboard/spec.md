## ADDED Requirements

### Requirement: Display rep performance overview

The system SHALL display a performance summary including average scores, total calls, and trend direction.

#### Scenario: Rep views own dashboard

- **WHEN** a rep user navigates to their dashboard
- **THEN** the system displays their personal performance metrics

#### Scenario: Manager views rep dashboard

- **WHEN** a manager navigates to /dashboard/[repEmail]
- **THEN** the system displays that rep's performance metrics

#### Scenario: Rep attempts to view another rep's dashboard

- **WHEN** a rep user navigates to another rep's dashboard URL
- **THEN** the system returns 403 Forbidden error

### Requirement: Display performance trends

The system SHALL display trend charts showing performance over time for each coaching dimension.

#### Scenario: Trend chart with sufficient data

- **WHEN** a rep has at least 5 analyzed calls
- **THEN** the system displays a line chart showing score trends over time for each dimension

#### Scenario: Insufficient data for trends

- **WHEN** a rep has fewer than 3 analyzed calls
- **THEN** the system displays "Not enough data" message instead of trend chart

### Requirement: Display recent calls list

The system SHALL display the 10 most recent calls with key metadata and scores.

#### Scenario: Recent calls loaded

- **WHEN** a rep has analyzed calls
- **THEN** the system displays up to 10 recent calls with date, type, overall score, and link to full analysis

#### Scenario: No calls available

- **WHEN** a rep has no analyzed calls
- **THEN** the system displays "No calls analyzed yet" message

### Requirement: Display aggregated metrics

The system SHALL display aggregated metrics including average dimension scores and call type distribution.

#### Scenario: Metrics calculated

- **WHEN** a rep has analyzed calls
- **THEN** the system displays average scores for each dimension (discovery, objection-handling, product-demo, closing)

#### Scenario: Call type breakdown

- **WHEN** a rep has multiple call types
- **THEN** the system displays percentage breakdown of discovery, demo, and follow-up calls

### Requirement: Manager view all reps

The system SHALL display a list of all reps with summary performance data for manager users.

#### Scenario: Manager views main dashboard

- **WHEN** a manager user navigates to /dashboard
- **THEN** the system displays a table of all reps with average scores and recent activity

#### Scenario: Manager clicks on rep

- **WHEN** a manager clicks on a rep in the dashboard
- **THEN** the system navigates to that rep's detailed dashboard at /dashboard/[repEmail]

### Requirement: Time range filtering

The system SHALL allow users to filter dashboard data by time range (last 7 days, 30 days, 90 days, all time).

#### Scenario: User selects time range

- **WHEN** a user selects a different time range filter
- **THEN** the system reloads all metrics and charts for the selected period

### Requirement: Loading states

The system SHALL display loading indicators while fetching dashboard data.

#### Scenario: Dashboard loading

- **WHEN** dashboard data is being fetched
- **THEN** the system displays skeleton loaders for metrics and charts

### Requirement: Error handling

The system SHALL display user-friendly error messages when dashboard data cannot be loaded.

#### Scenario: API error

- **WHEN** the backend API returns an error
- **THEN** the system displays error message and retry button

#### Scenario: Rep not found

- **WHEN** a manager navigates to a non-existent rep email
- **THEN** the system displays "Rep not found" error
