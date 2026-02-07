# discovery-analysis Specification

## Purpose

TBD - created by archiving change five-wins-show-your-work. Update Purpose after archive.

## Requirements

### Requirement: Discovery Analysis Returns Five Wins Evaluation

The system SHALL analyze discovery calls and return five_wins_evaluation as the primary output structure.

#### Scenario: Five Wins primary output

- **WHEN** a discovery call is analyzed
- **THEN** the response SHALL include a `five_wins_evaluation` object with all five wins (business, technical, security, commercial, legal)
- **AND** each win SHALL have score, max_score, status, evidence, and optional missed fields

#### Scenario: Overall score from Five Wins

- **WHEN** discovery analysis completes
- **THEN** the overall score (0-100) SHALL equal the sum of all five_wins_evaluation win scores

### Requirement: Discovery Supplementary Frameworks

The system SHALL provide SPICED-based discovery rubric insights in supplementary_frameworks for coaching depth.

#### Scenario: Discovery rubric supplementary

- **WHEN** a discovery call is analyzed
- **THEN** the response SHALL include `supplementary_frameworks.discovery_rubric` with SPICED criteria
- **AND** discovery_rubric SHALL NOT affect the overall score

#### Scenario: SPICED criteria evaluation

- **WHEN** supplementary_frameworks.discovery_rubric is generated
- **THEN** it SHALL evaluate 8 criteria based on SPICED framework: opening_questions, situation_exploration, pain_identification, impact_quantification, critical_event, decision_process, budget_exploration, success_criteria

### Requirement: Exchange-Based Evidence in Discovery

All evidence in discovery analysis SHALL use exchange summary format instead of isolated quotes.

#### Scenario: Evidence format

- **WHEN** generating evidence for Five Wins or discovery rubric
- **THEN** evidence SHALL use exchange_summary (multi-turn dialogue) with timestamp_start, timestamp_end, and impact
- **AND** SHALL NOT use isolated quote strings

### Requirement: Backward Compatibility

Discovery analysis SHALL maintain backward compatibility with existing response fields.

#### Scenario: Legacy fields preserved

- **WHEN** discovery analysis is returned
- **THEN** the response SHALL still include strengths, areas_for_improvement, specific_examples, and action_items fields
- **AND** these fields SHALL remain populated for clients not yet updated to use five_wins_evaluation

#### Scenario: Graceful handling of old clients

- **WHEN** a client expects old response format
- **THEN** the system SHALL NOT break if five_wins_evaluation is ignored
- **AND** overall score and legacy fields SHALL still be valid

### Requirement: Discovery Analysis Prompt Cache Efficiency

The system SHALL maintain prompt caching efficiency (>80% cache hit rate) when generating five_wins_evaluation.

#### Scenario: Rubric definitions cached

- **WHEN** analyzing discovery calls
- **THEN** rubric definitions (Five Wins and SPICED criteria) SHALL be in the cached system prompt
- **AND** only OUTPUT_REQUIREMENTS section SHALL be uncached

#### Scenario: Cache hit rate maintained

- **WHEN** monitoring discovery analysis over time
- **THEN** prompt cache hit rate SHALL remain above 80%
- **AND** token cost increase SHALL be less than 20% compared to baseline
