## ADDED Requirements

### Requirement: Supplementary Frameworks Structure

The system SHALL provide SPICED, Challenger, and Sandler framework insights as supplementary coaching information, subordinate to the primary Five Wins evaluation.

#### Scenario: Supplementary frameworks location

- **WHEN** analysis is returned
- **THEN** SPICED/Challenger/Sandler insights SHALL be in `supplementary_frameworks` object
- **AND** SHALL NOT be part of the primary score calculation

#### Scenario: Frameworks as coaching depth

- **WHEN** displaying supplementary frameworks
- **THEN** they SHALL be positioned below Five Wins
- **AND** SHALL be collapsed by default
- **AND** SHALL be visually styled as secondary/supplementary

### Requirement: Discovery Rubric Supplementary Framework

The system SHALL provide discovery_rubric insights based on SPICED framework with 8 criteria totaling 100 points for coaching depth.

#### Scenario: Discovery rubric structure

- **WHEN** supplementary_frameworks.discovery_rubric is present
- **THEN** it SHALL include 8 criteria: opening_questions (10pts), situation_exploration (15pts), pain_identification (15pts), impact_quantification (15pts), critical_event (10pts), decision_process (15pts), budget_exploration (10pts), success_criteria (10pts)

#### Scenario: Discovery rubric uses exchange evidence

- **WHEN** discovery_rubric criteria include evidence
- **THEN** evidence SHALL use the same exchange summary format as Five Wins (timestamp_start, timestamp_end, exchange_summary, impact)

### Requirement: Engagement Rubric Supplementary Framework

The system SHALL provide engagement_rubric insights with 7 criteria totaling 100 points for rapport and engagement coaching.

#### Scenario: Engagement rubric structure

- **WHEN** supplementary_frameworks.engagement_rubric is present
- **THEN** it SHALL include 7 criteria: talk_listen_ratio (20pts), active_listening (20pts), rapport_building (15pts), energy_enthusiasm (15pts), empathy_validation (15pts), customer_centricity (10pts), engagement_checks (5pts)

### Requirement: Product Knowledge Rubric Supplementary Framework

The system SHALL provide product_knowledge_rubric insights for product mastery coaching when applicable.

#### Scenario: Product knowledge rubric applicability

- **WHEN** a call involves product demonstrations or technical discussions
- **THEN** supplementary_frameworks MAY include product_knowledge_rubric

### Requirement: Objection Handling Rubric Supplementary Framework

The system SHALL provide objection_handling_rubric insights for objection management coaching when applicable.

#### Scenario: Objection handling rubric applicability

- **WHEN** a call includes customer objections or concerns
- **THEN** supplementary_frameworks MAY include objection_handling_rubric

### Requirement: Supplementary Criterion Evaluation Structure

Each criterion in supplementary frameworks SHALL use the same evaluation structure as Five Wins for consistency.

#### Scenario: Criterion structure consistency

- **WHEN** a supplementary criterion is evaluated
- **THEN** it SHALL include score, max_score, status ("met" | "partial" | "missed"), evidence array, and optional missed explanation

#### Scenario: Status threshold consistency

- **WHEN** calculating criterion status
- **THEN** the system SHALL use the same thresholds as Five Wins: "met" (80%+), "partial" (30-79%), "missed" (<30%)

### Requirement: Supplementary Frameworks Independence

Supplementary framework scores SHALL NOT affect the overall call score or Five Wins scores.

#### Scenario: Supplementary scores don't affect overall

- **WHEN** calculating overall call score
- **THEN** the system SHALL only sum five_wins_evaluation scores
- **AND** SHALL NOT include supplementary_frameworks scores in the total

#### Scenario: Supplementary can be omitted

- **WHEN** generating analysis
- **THEN** supplementary_frameworks field MAY be omitted entirely
- **AND** the overall score SHALL still be valid (derived from Five Wins only)

### Requirement: Supplementary Frameworks Optional Display

The UI SHALL make supplementary frameworks optional to view, reinforcing their secondary nature.

#### Scenario: Collapsed by default

- **WHEN** displaying analysis results
- **THEN** supplementary frameworks section SHALL be collapsed
- **AND** SHALL require user action to expand

#### Scenario: Optional lazy loading

- **WHEN** a user expands supplementary frameworks
- **THEN** the system MAY lazy-load the data if not already present
- **AND** SHALL show loading indicator during fetch

### Requirement: Cross-Framework Insights

The system SHALL support providing insights that connect Five Wins to specific supplementary framework criteria.

#### Scenario: Framework correlation

- **WHEN** a Five Win is partial or missed
- **THEN** the missed explanation MAY reference specific supplementary criteria (e.g., "Business Win weak because impact_quantification (SPICED) was missed")

#### Scenario: Coaching recommendations

- **WHEN** displaying supplementary frameworks
- **THEN** the system MAY highlight which criteria would improve specific Five Wins if strengthened
