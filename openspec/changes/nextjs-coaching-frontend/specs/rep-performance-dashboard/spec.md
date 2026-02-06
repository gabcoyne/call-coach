## ADDED Requirements

### Requirement: Rep Overview Header

The dashboard SHALL display rep identity, role, and high-level performance summary.

#### Scenario: Rep profile information

- **WHEN** user views dashboard
- **THEN** system displays rep name, email, role (SE/AE/CSM), and avatar

#### Scenario: Summary statistics

- **WHEN** user views dashboard header
- **THEN** system shows total calls analyzed, average score, and date range of data

### Requirement: Score Trends Over Time

The dashboard SHALL visualize rep performance trends across all coaching dimensions over selected time period.

#### Scenario: Line chart with dimension trends

- **WHEN** user views performance trends section
- **THEN** system displays line chart with separate lines for product knowledge, discovery, objection handling, and engagement scores over time

#### Scenario: Time period selector

- **WHEN** user clicks time period dropdown
- **THEN** system offers options: Last 7 days, Last 30 days, Last quarter, Last year, All time

#### Scenario: Hover for data point details

- **WHEN** user hovers over point on trend line
- **THEN** system shows tooltip with exact date, score, and call title

### Requirement: Skill Gaps Identification

The dashboard SHALL identify and prioritize skill gaps based on current vs. target scores.

#### Scenario: Skill gap cards

- **WHEN** user views skill gaps section
- **THEN** system displays cards for each gap showing skill name, current score, target score, and priority (high/medium/low)

#### Scenario: Gap priority calculation

- **WHEN** system calculates priorities
- **THEN** system assigns "high" if gap >20 points, "medium" if 10-20 points, "low" if <10 points

#### Scenario: Recommended actions for gap

- **WHEN** user expands skill gap card
- **THEN** system shows specific coaching recommendations and practice scenarios

### Requirement: Improvement Areas and Recent Wins

The dashboard SHALL highlight areas showing improvement and recent coaching successes.

#### Scenario: Improvement areas with trend

- **WHEN** user views improvement section
- **THEN** system shows dimensions with positive trend (improving) with percentage change

#### Scenario: Recent wins list

- **WHEN** user views recent wins section
- **THEN** system displays 3-5 recent calls where rep scored above average with specific strengths highlighted

### Requirement: Dimension Score Distribution

The dashboard SHALL show how rep's scores distribute across all dimensions using radar chart.

#### Scenario: Radar chart visualization

- **WHEN** user views dimension distribution section
- **THEN** system displays radar chart with 4 axes (product knowledge, discovery, objection handling, engagement) and rep's scores plotted

#### Scenario: Comparison to team average

- **WHEN** manager views rep dashboard
- **THEN** system overlays team average scores on radar chart for comparison

### Requirement: Call History Table

The dashboard SHALL display sortable, filterable table of all analyzed calls for the rep.

#### Scenario: Call history with key metrics

- **WHEN** user views call history section
- **THEN** system shows table with columns: Date, Title, Call Type, Overall Score, Duration, Primary Dimension Focus

#### Scenario: Sort by column

- **WHEN** user clicks column header
- **THEN** system sorts table by that column (ascending/descending)

#### Scenario: Filter by call type

- **WHEN** user selects call type filter
- **THEN** system shows only calls matching selected type (discovery, demo, technical deep dive, negotiation)

#### Scenario: Click call to view analysis

- **WHEN** user clicks row in call history table
- **THEN** system navigates to call analysis viewer for that call

### Requirement: Personalized Coaching Plan

The dashboard SHALL generate and display a personalized coaching plan based on rep's performance data.

#### Scenario: Coaching plan with focus areas

- **WHEN** user views coaching plan section
- **THEN** system displays 3-5 priority focus areas with timeline (e.g., "Improve discovery skills - 4 weeks")

#### Scenario: Practice scenarios

- **WHEN** user expands coaching plan focus area
- **THEN** system shows recommended practice scenarios and example calls to study

#### Scenario: Follow-up metrics

- **WHEN** user views coaching plan
- **THEN** system displays metrics to track for measuring improvement (e.g., "Question count per call", "SPICED coverage %")

### Requirement: Rep-Only vs Manager View

The dashboard SHALL adapt content based on user role (rep sees own data only, manager sees all reps).

#### Scenario: Rep viewing own dashboard

- **WHEN** rep user accesses dashboard
- **THEN** system shows only their personal performance data and coaching plan

#### Scenario: Manager viewing rep dashboard

- **WHEN** manager accesses rep dashboard
- **THEN** system shows full data including private coaching notes and team comparison metrics

#### Scenario: Manager dashboard selector

- **WHEN** manager views dashboard
- **THEN** system provides dropdown to switch between different rep dashboards
