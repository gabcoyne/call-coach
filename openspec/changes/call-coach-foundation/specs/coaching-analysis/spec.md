## ADDED Requirements

### Requirement: Multi-dimensional analysis

The system SHALL analyze calls across 4 coaching dimensions: product_knowledge, discovery, objection_handling, engagement.

#### Scenario: Full analysis

- **WHEN** call is analyzed without dimension filter
- **THEN** system analyzes all 4 dimensions and returns complete results

#### Scenario: Selective analysis

- **WHEN** user requests specific dimensions [product_knowledge, discovery]
- **THEN** system analyzes only requested dimensions

### Requirement: Scoring

The system SHALL assign scores 0-100 for each dimension with justification.

#### Scenario: Score generation

- **WHEN** dimension is analyzed
- **THEN** system returns score between 0-100
- **AND** provides strengths list and areas_for_improvement list

#### Scenario: Score validation

- **WHEN** analysis completes
- **THEN** score is integer between 0-100 (inclusive)

### Requirement: Specific examples

The system SHALL extract specific transcript quotes with timestamps for good and needs-work examples.

#### Scenario: Example extraction

- **WHEN** analysis identifies strength or improvement area
- **THEN** system provides specific_examples with quote, timestamp, and analysis

#### Scenario: Example format

- **WHEN** example is generated
- **THEN** includes: {quote: string, timestamp: integer, analysis: string}

### Requirement: Action items

The system SHALL generate concrete action items for improvement.

#### Scenario: Action item generation

- **WHEN** areas_for_improvement are identified
- **THEN** system provides 2-5 specific, actionable recommendations

#### Scenario: Action item quality

- **WHEN** action item is generated
- **THEN** it is specific (not generic), tied to transcript evidence, and implementable

### Requirement: Rubric adherence

The system SHALL use active coaching rubric version for analysis.

#### Scenario: Rubric selection

- **WHEN** analysis is requested for dimension
- **THEN** system uses rubric with active=true and latest version for that dimension

#### Scenario: Missing rubric

- **WHEN** no active rubric exists for dimension
- **THEN** system raises ValueError with clear message

### Requirement: Parallel execution

The system SHALL analyze multiple dimensions concurrently to reduce wall-clock time.

#### Scenario: Concurrent analysis

- **WHEN** analyzing 4 dimensions for one call
- **THEN** analyses execute in parallel (not sequential)
- **AND** total time ≈ max(dimension_times), not sum(dimension_times)

### Requirement: Token usage tracking

The system SHALL record token usage for cost monitoring.

#### Scenario: Token tracking

- **WHEN** Claude API call completes
- **THEN** system stores total_tokens_used in analysis_runs table
- **AND** tracks input_tokens and output_tokens separately

### Requirement: Error handling

The system SHALL gracefully handle Claude API failures with retries.

#### Scenario: Transient failure

- **WHEN** Claude API returns 500 error
- **THEN** system retries up to 3 times with exponential backoff

#### Scenario: Permanent failure

- **WHEN** all retries fail
- **THEN** system stores error in analysis_runs.error_message
- **AND** sets status=failed
