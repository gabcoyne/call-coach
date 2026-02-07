# five-wins-rubric Specification

## Purpose

TBD - created by archiving change five-wins-show-your-work. Update Purpose after archive.

## Requirements

### Requirement: Five Wins Primary Scoring Framework

The system SHALL evaluate all discovery calls using the Five Wins framework as the primary scoring mechanism, with a total of 100 points distributed across five wins based on their relative importance to deal success.

#### Scenario: Five Wins score distribution

- **WHEN** a call is analyzed
- **THEN** the system SHALL allocate exactly 100 points across: Business Win (35 points), Technical Win (25 points), Security Win (15 points), Commercial Win (15 points), Legal Win (10 points)

#### Scenario: Five Wins replaces SPICED as primary

- **WHEN** analysis results are returned
- **THEN** the `five_wins_evaluation` field SHALL be the primary scoring object
- **AND** SPICED/Challenger/Sandler SHALL be in `supplementary_frameworks` for coaching depth

### Requirement: Business Win Evaluation

The system SHALL evaluate the Business Win (maximum 35 points) based on discovery quality for economic buyer engagement, business value articulation, and ROI demonstration.

#### Scenario: Full Business Win achieved

- **WHEN** the rep identifies current state problems, articulates future state outcomes, defines success metrics, aligns to executive priorities, understands evaluation criteria, and builds a strong quantified business case
- **THEN** the system SHALL award 28-35 points (80-100% of maximum)
- **AND** status SHALL be "met"

#### Scenario: Partial Business Win

- **WHEN** some business discovery elements are present but critical gaps exist (e.g., no critical event identified, no competitive evaluation criteria)
- **THEN** the system SHALL award 10-27 points (30-79% of maximum)
- **AND** status SHALL be "partial"
- **AND** `missed` field SHALL explain specific business discovery gaps

#### Scenario: Business Win at risk

- **WHEN** minimal or no business discovery occurred
- **THEN** the system SHALL award 0-10 points (<30% of maximum)
- **AND** status SHALL be "missed"

### Requirement: Technical Win Evaluation

The system SHALL evaluate the Technical Win (maximum 25 points) based on technical champion validation, use case alignment, and solution fit demonstration.

#### Scenario: Technical requirements validated

- **WHEN** the rep identifies technical requirements, validates use case alignment, understands infrastructure needs, discusses CI/CD integration, and plans demo or POC
- **THEN** the system SHALL award 20-25 points
- **AND** status SHALL be "met"

### Requirement: Security Win Evaluation

The system SHALL evaluate the Security Win (maximum 15 points) based on InfoSec requirements identification and approval process understanding.

#### Scenario: Security process mapped

- **WHEN** the rep identifies InfoSec requirements, understands security review process and timeline, and discusses questionnaire
- **THEN** the system SHALL award 12-15 points
- **AND** status SHALL be "met"

### Requirement: Commercial Win Evaluation

The system SHALL evaluate the Commercial Win (maximum 15 points) based on pricing, packaging, and commercial terms alignment.

#### Scenario: Commercial terms explored

- **WHEN** the rep discusses deployment scope, explores budget range and flexibility, and understands commercial terms
- **THEN** the system SHALL award 12-15 points
- **AND** status SHALL be "met"

### Requirement: Legal Win Evaluation

The system SHALL evaluate the Legal Win (maximum 10 points) based on legal and procurement process understanding.

#### Scenario: Legal process mapped

- **WHEN** the rep identifies legal review process, timeline, contract requirements, and procurement stakeholders
- **THEN** the system SHALL award 8-10 points
- **AND** status SHALL be "met"

### Requirement: Win Status Thresholds

The system SHALL classify each win's status using consistent thresholds across all five wins.

#### Scenario: Win status calculation

- **WHEN** a win's score is 80% or more of its maximum points
- **THEN** status SHALL be "met"

#### Scenario: Partial win status

- **WHEN** a win's score is between 30% and 79% of its maximum points
- **THEN** status SHALL be "partial"

#### Scenario: Missed win status

- **WHEN** a win's score is less than 30% of its maximum points
- **THEN** status SHALL be "missed"

### Requirement: Five Wins Summary Metrics

The system SHALL provide summary metrics showing wins secured and at-risk wins for quick deal health assessment.

#### Scenario: Wins secured count

- **WHEN** analysis is complete
- **THEN** the system SHALL count wins with status "met" as "secured"
- **AND** display "X of 5 Wins Secured" prominently

#### Scenario: At-risk wins identification

- **WHEN** any wins have status "partial" or "missed"
- **THEN** the system SHALL list these as "at-risk wins"
- **AND** prioritize them by point value (highest first)

### Requirement: Overall Score Derivation

The system SHALL derive the overall call score (0-100) from the sum of all Five Wins scores.

#### Scenario: Overall score calculation

- **WHEN** five_wins_evaluation is complete
- **THEN** overall score SHALL equal sum(business_win.score + technical_win.score + security_win.score + commercial_win.score + legal_win.score)

#### Scenario: Score validation

- **WHEN** five_wins_evaluation is returned
- **THEN** the sum of all win scores MUST equal the overall score field
- **AND** any mismatch SHALL be logged as an error
