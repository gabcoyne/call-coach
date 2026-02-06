## ADDED Requirements

### Requirement: Search by date range

The system SHALL allow users to filter calls by date range using start and end date pickers.

#### Scenario: User filters by date range

- **WHEN** a user selects a start date of 2026-01-01 and end date of 2026-01-31
- **THEN** the system displays only calls that occurred within that range

#### Scenario: Invalid date range

- **WHEN** a user selects an end date before the start date
- **THEN** the system displays "Invalid date range" validation error

### Requirement: Filter by rep

The system SHALL allow managers to filter calls by rep email address.

#### Scenario: Manager filters by rep

- **WHEN** a manager user selects a rep from the filter dropdown
- **THEN** the system displays only calls for that rep

#### Scenario: Rep user cannot filter by rep

- **WHEN** a rep user views the search page
- **THEN** the rep filter is not displayed and results show only their own calls

### Requirement: Filter by call type

The system SHALL allow users to filter calls by type (discovery, demo, follow-up).

#### Scenario: User filters by call type

- **WHEN** a user selects "demo" from the call type filter
- **THEN** the system displays only demo calls

#### Scenario: Multiple call types selected

- **WHEN** a user selects both "discovery" and "demo" call types
- **THEN** the system displays calls matching either type

### Requirement: Filter by performance score

The system SHALL allow users to filter calls by minimum score threshold.

#### Scenario: User sets minimum score

- **WHEN** a user sets minimum score filter to 80
- **THEN** the system displays only calls with overall score of 80 or higher

#### Scenario: Score filter with no results

- **WHEN** a user sets a score filter that matches no calls
- **THEN** the system displays "No calls match your filters" message

### Requirement: Keyword search

The system SHALL allow users to search calls by keyword in transcript or coaching insights.

#### Scenario: User searches by keyword

- **WHEN** a user enters "pricing" in the search box
- **THEN** the system displays calls where "pricing" appears in transcript or insights

#### Scenario: Empty search

- **WHEN** a user submits an empty search query
- **THEN** the system displays all calls without keyword filtering

### Requirement: Combined filters

The system SHALL apply all active filters simultaneously using AND logic.

#### Scenario: Multiple filters applied

- **WHEN** a user filters by date range "last 30 days", call type "demo", and minimum score 70
- **THEN** the system displays only demo calls from the last 30 days with score >= 70

### Requirement: Display search results

The system SHALL display search results in a list with key metadata and scores.

#### Scenario: Search results displayed

- **WHEN** search returns results
- **THEN** the system displays each call with date, rep, type, overall score, and link to full analysis

#### Scenario: Pagination

- **WHEN** search returns more than 20 results
- **THEN** the system displays pagination controls to navigate results

### Requirement: Clear filters

The system SHALL allow users to clear all filters and reset to default view.

#### Scenario: User clears filters

- **WHEN** a user clicks "Clear filters" button
- **THEN** the system removes all active filters and displays all accessible calls

### Requirement: Loading states

The system SHALL display loading indicators while fetching search results.

#### Scenario: Search loading

- **WHEN** search query is executing
- **THEN** the system displays loading spinner

### Requirement: Error handling

The system SHALL display user-friendly error messages when search fails.

#### Scenario: Search API error

- **WHEN** the backend search API returns an error
- **THEN** the system displays error message and retry button
