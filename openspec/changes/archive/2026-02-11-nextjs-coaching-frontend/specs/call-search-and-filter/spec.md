# Specification

## ADDED Requirements

### Requirement: Multi-Criteria Search Interface

The search interface SHALL provide filters for rep, date range, product, call type, score thresholds, objection types, and topics.

#### Scenario: Filter by rep email

- **WHEN** user enters rep email in search filter
- **THEN** system shows only calls where that rep participated

#### Scenario: Filter by date range

- **WHEN** user selects start and end dates
- **THEN** system shows only calls scheduled within that date range

#### Scenario: Filter by product

- **WHEN** user selects product filter (Prefect, Horizon, Both)
- **THEN** system shows only calls discussing selected product(s)

#### Scenario: Filter by call type

- **WHEN** user selects call type (discovery, demo, technical deep dive, negotiation)
- **THEN** system shows only calls of that type

### Requirement: Score-Based Filtering

The search interface SHALL allow filtering calls by overall score or specific dimension score ranges.

#### Scenario: Filter by minimum overall score

- **WHEN** user sets minimum overall score to 70
- **THEN** system shows only calls with overall score >= 70

#### Scenario: Filter by maximum overall score

- **WHEN** user sets maximum overall score to 80
- **THEN** system shows only calls with overall score <= 80

#### Scenario: Filter by dimension score

- **WHEN** user sets minimum "discovery" score to 75
- **THEN** system shows only calls with discovery dimension score >= 75

### Requirement: Objection Type Filtering

The search interface SHALL allow filtering calls by specific objection types discussed.

#### Scenario: Filter by pricing objections

- **WHEN** user selects "pricing" objection type
- **THEN** system shows only calls where pricing objections were identified

#### Scenario: Filter by multiple objection types

- **WHEN** user selects multiple objection types (pricing, timing, technical, competitor)
- **THEN** system shows calls containing any of the selected objection types

### Requirement: Topic-Based Filtering

The search interface SHALL allow filtering calls by topics discussed during the call.

#### Scenario: Filter by topic keyword

- **WHEN** user enters topic keyword (e.g., "Objections", "Product Demo", "Use Case")
- **THEN** system shows calls where that topic was discussed

#### Scenario: Filter by multiple topics

- **WHEN** user selects multiple topics
- **THEN** system shows calls matching all selected topics (AND logic)

### Requirement: Search Results Display

The search interface SHALL display search results as sortable cards or table with key metrics.

#### Scenario: Results as cards

- **WHEN** user views search results in card view
- **THEN** system displays each call as card with title, date, rep name, overall score, and primary dimension focus

#### Scenario: Results as table

- **WHEN** user switches to table view
- **THEN** system displays results as table with columns: Title, Date, Rep, Score, Call Type, Duration

#### Scenario: Sort results

- **WHEN** user clicks sort dropdown
- **THEN** system offers options: Date (newest/oldest), Score (highest/lowest), Duration (longest/shortest)

### Requirement: Result Count and Pagination

The search interface SHALL display total result count and paginate results for performance.

#### Scenario: Display result count

- **WHEN** user performs search
- **THEN** system shows total number of matching calls (e.g., "42 calls found")

#### Scenario: Paginate results

- **WHEN** search returns more than 20 results
- **THEN** system displays first 20 calls with pagination controls to load more

#### Scenario: Change page size

- **WHEN** user selects page size dropdown
- **THEN** system offers options: 10, 20, 50, 100 results per page

### Requirement: Save and Load Searches

The search interface SHALL allow users to save frequently used search criteria and load them later.

#### Scenario: Save current search

- **WHEN** user clicks "Save Search" after applying filters
- **THEN** system prompts for search name and saves filter configuration

#### Scenario: Load saved search

- **WHEN** user selects saved search from dropdown
- **THEN** system applies all saved filters and displays results

#### Scenario: Delete saved search

- **WHEN** user clicks delete on saved search
- **THEN** system removes saved search from user's list

### Requirement: Export Search Results

The search interface SHALL allow users to export filtered search results for offline analysis.

#### Scenario: Export as CSV

- **WHEN** user clicks "Export CSV"
- **THEN** system downloads CSV file with all matching calls and key metrics

#### Scenario: Export as Excel

- **WHEN** user clicks "Export Excel"
- **THEN** system downloads Excel file with formatted data and summary statistics

### Requirement: Quick Filter Presets

The search interface SHALL provide common filter presets for fast access to frequent searches.

#### Scenario: "My Calls This Week" preset

- **WHEN** rep user clicks "My Calls This Week" preset
- **THEN** system filters to current user's calls from last 7 days

#### Scenario: "Low Performers" preset (manager only)

- **WHEN** manager clicks "Low Performers" preset
- **THEN** system filters to calls with overall score <60 from last 30 days

#### Scenario: "Discovery Calls Needing Review" preset

- **WHEN** manager clicks preset
- **THEN** system filters to discovery calls with discovery dimension score <70 from last 14 days
