## ADDED Requirements

### Requirement: Exchange Summary Evidence Structure

The system SHALL provide evidence using multi-turn exchange summaries with timestamp ranges instead of isolated quotes, enabling users to understand conversational patterns and missed opportunities.

#### Scenario: Exchange summary format

- **WHEN** evidence is generated for a criterion or win
- **THEN** each evidence item SHALL include timestamp_start (seconds), timestamp_end (seconds), exchange_summary (string), and impact (string)

#### Scenario: Multi-turn dialogue capture

- **WHEN** creating an exchange_summary
- **THEN** the summary SHALL describe what happened across multiple conversation turns (e.g., "Rep asked X, customer responded Y, rep did/didn't Z")
- **AND** SHALL NOT be a single isolated quote

### Requirement: Exchange Summary Content Quality

Exchange summaries SHALL capture conversational patterns, rep behavior, and customer responses to show what was strong or what was missed.

#### Scenario: Pattern-based summary

- **WHEN** generating exchange_summary
- **THEN** the summary SHALL show the dialogue flow and pattern (e.g., "Rep asked about challenges, customer deflected with 'it's fine', rep moved on without digging deeper")
- **AND** SHALL NOT be vague (e.g., "Rep and customer discussed requirements")

#### Scenario: Missed opportunity identification

- **WHEN** a criterion or win is partial or missed
- **THEN** exchange_summary SHALL explain what the rep didn't do (e.g., "customer mentioned pain but rep didn't quantify impact")

#### Scenario: Strong execution demonstration

- **WHEN** a criterion or win is met
- **THEN** exchange_summary SHALL show what the rep did well (e.g., "Rep asked ROI question, customer mentioned faster deployments, rep quantified '$400K/year', customer confirmed priority")

### Requirement: Impact Field Explanation

Each evidence item SHALL include an impact statement explaining why this exchange mattered for the criterion or win being evaluated.

#### Scenario: Impact for partial/missed criteria

- **WHEN** evidence is for a partial or missed criterion
- **THEN** impact SHALL explain what was missed and why it matters (e.g., "Missed opportunity to uncover business impact - customer was signaling hidden pain")

#### Scenario: Impact for met criteria

- **WHEN** evidence is for a met criterion
- **THEN** impact SHALL explain what was strong (e.g., "Strong discovery - rep quantified impact and connected to executive priorities")

### Requirement: Timestamp Range Accuracy

Timestamp ranges SHALL accurately reflect the duration of the multi-turn exchange being summarized.

#### Scenario: Exchange duration

- **WHEN** an exchange spans from 5:20 to 10:15 in the call
- **THEN** timestamp_start SHALL be 320 seconds and timestamp_end SHALL be 615 seconds

#### Scenario: Timestamp ordering

- **WHEN** multiple evidence items exist for a criterion
- **THEN** timestamp_start values SHALL be in chronological order

### Requirement: Evidence Quantity Limits

The system SHALL limit evidence to avoid overwhelming users while providing sufficient examples.

#### Scenario: Evidence per win limit

- **WHEN** generating evidence for a Five Win
- **THEN** the system SHALL provide 1-3 exchange evidence items
- **AND** SHALL NOT exceed 3 evidence items per win

#### Scenario: Evidence per criterion limit

- **WHEN** generating evidence for a supplementary criterion (SPICED/Challenger/Sandler)
- **THEN** the system SHALL provide 1-3 exchange evidence items
- **AND** SHALL NOT exceed 3 evidence items per criterion

### Requirement: Evidence Prioritization

When multiple exchanges could serve as evidence, the system SHALL prioritize the most impactful and representative examples.

#### Scenario: Impactful evidence selection

- **WHEN** multiple exchanges demonstrate a criterion
- **THEN** the system SHALL select exchanges that best illustrate the pattern
- **AND** SHALL prefer exchanges with clear impact (strong or missed)
- **AND** SHALL prefer exchanges distributed across the call (not clustered)

### Requirement: Empty Evidence Handling

The system SHALL handle cases where no evidence exists gracefully.

#### Scenario: No evidence for missed criterion

- **WHEN** a criterion is missed and no relevant exchanges occurred
- **THEN** evidence array SHALL be empty
- **AND** missed field SHALL explain what was absent (e.g., "Rep never asked about budget or discussed commercial terms")

#### Scenario: Evidence required for met criteria

- **WHEN** a criterion status is "met"
- **THEN** evidence array SHALL contain at least 1 evidence item demonstrating the criterion
