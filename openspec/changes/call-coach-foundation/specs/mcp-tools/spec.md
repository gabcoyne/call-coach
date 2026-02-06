## ADDED Requirements

### Requirement: analyze_call tool

The system SHALL provide analyze_call MCP tool for on-demand call analysis.

#### Scenario: Call analysis request

- **WHEN** user invokes analyze_call(call_id="abc-123")
- **THEN** system returns analysis with scores, strengths, areas_for_improvement, and examples
- **AND** response time is <10s for cached analyses

#### Scenario: Dimension filtering

- **WHEN** user specifies dimensions=["product_knowledge", "discovery"]
- **THEN** system analyzes only requested dimensions

#### Scenario: Force reanalysis

- **WHEN** user sets force_reanalysis=true
- **THEN** system bypasses cache and regenerates analysis

### Requirement: get_rep_insights tool

The system SHALL provide get_rep_insights for performance trends and coaching history.

#### Scenario: Rep performance query

- **WHEN** user invokes get_rep_insights(rep_email="<sarah@prefect.io>", time_period="last_30_days")
- **THEN** system returns score_trends, skill_gaps, improvement_areas, and coaching_plan

#### Scenario: Time period filtering

- **WHEN** user specifies time_period="last_quarter"
- **THEN** system analyzes coaching sessions from last 90 days

### Requirement: search_calls tool

The system SHALL provide search_calls for finding calls by criteria.

#### Scenario: Search by rep

- **WHEN** user searches with filters={rep_email="<alex@prefect.io>", min_score=80}
- **THEN** system returns calls matching all criteria

#### Scenario: Date range search

- **WHEN** user specifies date_range={start="2025-01-01", end="2025-01-31"}
- **THEN** system returns calls within date range

### Requirement: compare_calls tool

The system SHALL provide compare_calls for side-by-side call comparison.

#### Scenario: Call comparison

- **WHEN** user invokes compare_calls(call_ids=["call-1", "call-2"], dimensions=["discovery"])
- **THEN** system returns side-by-side comparison showing scores, strengths, and differences

### Requirement: analyze_product_knowledge tool

The system SHALL verify technical accuracy against product knowledge base.

#### Scenario: Accuracy check

- **WHEN** user invokes analyze_product_knowledge(call_id="abc-123", product="horizon")
- **THEN** system returns correct_statements, inaccurate_statements, and missed_opportunities
- **AND** each includes validation against knowledge base

### Requirement: get_coaching_plan tool

The system SHALL generate personalized coaching plans for reps.

#### Scenario: Coaching plan generation

- **WHEN** user invokes get_coaching_plan(rep_email="<john@prefect.io>")
- **THEN** system returns priority_areas, recommended_actions, practice_scenarios
- **AND** recommendations are based on skill_gaps from recent analyses

### Requirement: Response format

All MCP tools SHALL return structured JSON responses with consistent error handling.

#### Scenario: Successful response

- **WHEN** tool executes successfully
- **THEN** response includes data payload and success status

#### Scenario: Error response

- **WHEN** tool encounters error (e.g., call_id not found)
- **THEN** response includes error message, error_code, and HTTP-style status code
