## ADDED Requirements

### Requirement: ScoreCard component

The system SHALL provide a reusable ScoreCard component that displays dimension scores with color indicators.

#### Scenario: High score card

- **WHEN** ScoreCard is rendered with score >= 80
- **THEN** the component displays score with green background and "Excellent" label

#### Scenario: Medium score card

- **WHEN** ScoreCard is rendered with score 60-79
- **THEN** the component displays score with yellow background and "Good" label

#### Scenario: Low score card

- **WHEN** ScoreCard is rendered with score < 60
- **THEN** the component displays score with red background and "Needs Improvement" label

#### Scenario: Score card with title

- **WHEN** ScoreCard is rendered with title prop
- **THEN** the component displays the title above the score

### Requirement: TrendChart component

The system SHALL provide a reusable TrendChart component that displays performance trends over time.

#### Scenario: Trend chart with data

- **WHEN** TrendChart is rendered with time series data
- **THEN** the component displays a line chart with date on x-axis and score on y-axis

#### Scenario: Multiple dimensions

- **WHEN** TrendChart is rendered with multiple dimension data
- **THEN** the component displays multiple colored lines, one per dimension, with legend

#### Scenario: Responsive sizing

- **WHEN** TrendChart is rendered on mobile device
- **THEN** the component adjusts chart dimensions to fit screen width

### Requirement: InsightCard component

The system SHALL provide a reusable InsightCard component that displays coaching insights.

#### Scenario: Insight with strengths

- **WHEN** InsightCard is rendered with strengths array
- **THEN** the component displays strengths list with checkmark icons

#### Scenario: Insight with improvement areas

- **WHEN** InsightCard is rendered with improvement areas array
- **THEN** the component displays improvement list with alert icons

#### Scenario: Collapsible insights

- **WHEN** user clicks on InsightCard header
- **THEN** the component expands or collapses the detail content

### Requirement: ActionItem component

The system SHALL provide a reusable ActionItem component that displays actionable recommendations.

#### Scenario: High priority action

- **WHEN** ActionItem is rendered with priority "high"
- **THEN** the component displays with red priority badge

#### Scenario: Medium priority action

- **WHEN** ActionItem is rendered with priority "medium"
- **THEN** the component displays with yellow priority badge

#### Scenario: Low priority action

- **WHEN** ActionItem is rendered with priority "low"
- **THEN** the component displays with blue priority badge

#### Scenario: Checkbox for completion

- **WHEN** ActionItem includes onComplete callback
- **THEN** the component displays checkbox to mark action as complete

### Requirement: Color palette consistency

The system SHALL use consistent color palette across all coaching components.

#### Scenario: Score colors

- **WHEN** any component displays scores
- **THEN** the component uses green (#10b981) for high, yellow (#f59e0b) for medium, red (#ef4444) for low

#### Scenario: Brand colors

- **WHEN** any component needs brand colors
- **THEN** the component uses Prefect blue (#2D5FE3) for primary and gray (#6B7280) for secondary

### Requirement: Responsive design

The system SHALL ensure all coaching components are responsive and mobile-friendly.

#### Scenario: Mobile layout

- **WHEN** coaching components are rendered on mobile (<768px width)
- **THEN** the components stack vertically and adjust font sizes

#### Scenario: Tablet layout

- **WHEN** coaching components are rendered on tablet (768-1024px width)
- **THEN** the components display in 2-column grid where appropriate

#### Scenario: Desktop layout

- **WHEN** coaching components are rendered on desktop (>1024px width)
- **THEN** the components display in 3-column grid where appropriate

### Requirement: Loading states

The system SHALL provide loading variants for all coaching components.

#### Scenario: Component loading

- **WHEN** a coaching component is in loading state
- **THEN** the component displays skeleton loader with similar dimensions

### Requirement: Accessibility

The system SHALL ensure all coaching components meet WCAG 2.1 AA accessibility standards.

#### Scenario: Keyboard navigation

- **WHEN** user navigates with keyboard
- **THEN** all interactive elements are reachable with Tab key and have visible focus indicators

#### Scenario: Screen reader support

- **WHEN** screen reader reads coaching components
- **THEN** all content has appropriate ARIA labels and semantic HTML

#### Scenario: Color contrast

- **WHEN** coaching components display text
- **THEN** text has at least 4.5:1 contrast ratio with background
