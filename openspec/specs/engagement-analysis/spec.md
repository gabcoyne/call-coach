# engagement-analysis Specification

## Purpose

TBD - created by archiving change five-wins-show-your-work. Update Purpose after archive.

## Requirements

### Requirement: Engagement Analysis Uses Exchange Evidence

The system SHALL update engagement analysis to use exchange-based evidence format instead of quote-based evidence.

#### Scenario: Exchange evidence in engagement

- **WHEN** engagement analysis is performed
- **THEN** all evidence SHALL use exchange_summary format with timestamp_start, timestamp_end, exchange_summary, and impact
- **AND** SHALL NOT use isolated quote strings

#### Scenario: Multi-turn pattern capture

- **WHEN** generating engagement evidence
- **THEN** exchange_summary SHALL capture dialogue patterns (e.g., "Customer shared frustration, rep paraphrased back, customer expanded")
- **AND** SHALL show listening, rapport, and empathy patterns across turns

### Requirement: Engagement Rubric Evidence Quality

Exchange summaries in engagement analysis SHALL demonstrate engagement behaviors and patterns, not isolated moments.

#### Scenario: Rapport building evidence

- **WHEN** evaluating rapport_building criterion
- **THEN** exchange_summary SHALL show how rapport was or wasn't built over time (e.g., "Rep used customer name, found common ground, customer opened up")

#### Scenario: Active listening evidence

- **WHEN** evaluating active_listening criterion
- **THEN** exchange_summary SHALL show listening behaviors (e.g., "Customer mentioned manual workflows, rep paraphrased, customer confirmed and elaborated")

#### Scenario: Talk-listen ratio evidence

- **WHEN** evaluating talk_listen_ratio criterion
- **THEN** exchange_summary SHALL note conversation balance (e.g., "Rep monologued for 3 minutes without letting customer respond")

### Requirement: Engagement Analysis Backward Compatibility

Engagement analysis SHALL maintain backward compatibility with existing response structure.

#### Scenario: Legacy fields preserved

- **WHEN** engagement analysis is returned
- **THEN** the response SHALL still include strengths, areas_for_improvement, and action_items
- **AND** engagement_metrics (rapport_score, talk_listen_ratio) SHALL still be populated

### Requirement: Engagement Evidence Timestamp Accuracy

Timestamps in engagement evidence SHALL accurately reflect when engagement behaviors occurred in the call.

#### Scenario: Accurate time ranges

- **WHEN** an exchange spans 3:20 to 3:45
- **THEN** timestamp_start SHALL be 200 seconds and timestamp_end SHALL be 225 seconds

#### Scenario: Chronological ordering

- **WHEN** multiple evidence items exist
- **THEN** they SHALL be ordered chronologically by timestamp_start
