## ADDED Requirements

### Requirement: Opportunity insights section analyzes patterns across all touchpoints
The system SHALL provide AI-generated insights that analyze patterns across all calls and emails for the opportunity.

#### Scenario: Insights identify recurring themes
- **WHEN** viewing opportunity with multiple calls
- **THEN** insights section shows recurring discussion topics across calls
- **THEN** insights highlight patterns in customer concerns or questions
- **THEN** insights note evolution of topics over time

#### Scenario: Insights identify objection patterns
- **WHEN** analyzing opportunity with objections raised in multiple calls
- **THEN** insights list all objections encountered across timeline
- **THEN** insights track which objections were resolved vs. recurring
- **THEN** insights suggest strategies for addressing unresolved objections

#### Scenario: Insights assess relationship strength progression
- **WHEN** analyzing opportunity interactions over time
- **THEN** insights evaluate rapport and engagement trends
- **THEN** insights note positive shifts (more questions, deeper discussions)
- **THEN** insights flag negative signals (shorter calls, less engagement)

### Requirement: Opportunity insights highlight deal progression patterns
The system SHALL analyze how the opportunity progresses through sales stages based on interaction quality.

#### Scenario: Insights correlate call quality with stage advancement
- **WHEN** opportunity has advanced through multiple stages
- **THEN** insights show coaching scores at each stage transition
- **THEN** insights identify what improved before stage advancement
- **THEN** insights suggest areas to strengthen for next stage

#### Scenario: Insights identify gaps in discovery or qualification
- **WHEN** analyzing discovery and qualification calls
- **THEN** insights check coverage of BANT/MEDDIC criteria
- **THEN** insights flag missing qualification areas
- **THEN** insights suggest questions to ask in next interaction

#### Scenario: Insights predict deal health based on interaction patterns
- **WHEN** analyzing opportunity engagement trends
- **THEN** insights compare current patterns to historical won/lost deals
- **THEN** insights surface leading indicators of risk (declining engagement, unresolved objections)
- **THEN** insights provide coaching priorities to improve deal health

### Requirement: MCP tool provides holistic opportunity coaching insights
The system SHALL expose a FastMCP tool that analyzes opportunities and returns structured coaching recommendations.

#### Scenario: analyze_opportunity returns comprehensive insights
- **WHEN** calling analyze_opportunity MCP tool with opportunity_id
- **THEN** tool returns deal progression analysis
- **THEN** tool returns recurring themes and objection patterns
- **THEN** tool returns relationship strength assessment
- **THEN** tool returns coaching recommendations for next steps

#### Scenario: Tool aggregates coaching scores across all calls
- **WHEN** tool analyzes opportunity with 10 calls
- **THEN** tool computes average scores per dimension (discovery, objections, product knowledge)
- **THEN** tool identifies trend lines (improving, declining, stable)
- **THEN** tool flags dimensions needing focused coaching

### Requirement: Learning insights compare rep patterns to top performers on won deals
The system SHALL provide comparative analysis showing how rep's patterns differ from top performers on similar closed-won opportunities.

#### Scenario: get_learning_insights MCP tool shows what top performers do differently
- **WHEN** calling get_learning_insights with rep_email and focus_area
- **THEN** tool finds rep's recent opportunities in that focus area
- **THEN** tool finds similar closed-won opportunities by top performers
- **THEN** tool identifies 3 concrete behavioral differences
- **THEN** tool provides specific examples from top performer calls

#### Scenario: Learning insights link to exemplar call moments
- **WHEN** viewing learning insights for discovery skills
- **THEN** insights include timestamps and quotes from top performer calls
- **THEN** insights explain why each example is effective
- **THEN** rep can listen to specific moments for learning

#### Scenario: Learning insights filter by product and opportunity type
- **WHEN** comparing to top performers
- **THEN** system only compares similar deals (same product, similar size)
- **THEN** system ensures examples are relevant to rep's context
- **THEN** coaching recommendations are actionable and realistic

### Requirement: Opportunity coaching insights appear on opportunity detail page
The system SHALL display holistic coaching insights prominently on the opportunity detail page.

#### Scenario: Insights section appears above timeline
- **WHEN** viewing opportunity detail page
- **THEN** page shows "Opportunity Insights" section before timeline
- **THEN** section includes key patterns, objections, and coaching recommendations
- **THEN** section is visually distinct and easy to scan

#### Scenario: Insights can be expanded or collapsed
- **WHEN** viewing opportunity insights
- **THEN** section is expanded by default
- **THEN** manager can collapse section to focus on timeline
- **THEN** collapsed state is remembered in session

#### Scenario: Insights include actionable next steps
- **WHEN** viewing coaching recommendations
- **THEN** insights provide 3-5 specific action items for next interaction
- **THEN** action items reference specific patterns from timeline
- **THEN** recommendations are practical and implementable

### Requirement: Insights loading state provides feedback during AI analysis
The system SHALL show appropriate loading states while AI generates holistic insights.

#### Scenario: Insights show skeleton loader during generation
- **WHEN** opportunity page loads and insights are being generated
- **THEN** page shows skeleton loader in insights section
- **THEN** timeline loads independently without waiting for insights
- **THEN** insights populate when AI analysis completes

#### Scenario: Insights generation completes within 5 seconds
- **WHEN** generating insights for typical opportunity (10-15 calls)
- **THEN** AI analysis completes within 5 seconds
- **THEN** user sees insights without long wait
- **THEN** caching reduces subsequent load times
