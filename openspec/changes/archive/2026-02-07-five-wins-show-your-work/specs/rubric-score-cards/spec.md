## ADDED Requirements

### Requirement: Expandable Score Card UI

The system SHALL provide expandable score cards that allow users to click any score and see detailed Five Wins breakdown with rubric criteria and evidence.

#### Scenario: Collapsed score card

- **WHEN** a user views the call analysis page
- **THEN** the score card SHALL show the overall score (0-100) and performance label
- **AND** SHALL display a "Show How This Score Was Calculated" button

#### Scenario: Expanded score card

- **WHEN** a user clicks "Show How This Score Was Calculated"
- **THEN** the score card SHALL expand to show the Five Wins breakdown
- **AND** SHALL display "Hide Breakdown" button
- **AND** SHALL show "X of 5 Wins Secured" summary

#### Scenario: Smooth expand/collapse animation

- **WHEN** a user toggles the score card
- **THEN** the expansion/collapse SHALL animate smoothly without jank

### Requirement: Five Wins Summary Display

The expanded score card SHALL prominently display a summary of wins secured and at-risk wins for quick assessment.

#### Scenario: Wins secured badge

- **WHEN** the score card is expanded
- **THEN** the system SHALL display "🎯 Wins Secured: X of 5" at the top
- **AND** SHALL list which specific wins are secured (status "met")

#### Scenario: At-risk wins alert

- **WHEN** any wins have status "partial" or "missed"
- **THEN** the system SHALL display "🚨 At Risk:" followed by win names
- **AND** SHALL prioritize by point value (highest first)

### Requirement: Individual Win Display

Each of the five wins SHALL be displayed with clear visual indicators of status, score, and details.

#### Scenario: Win status indicator

- **WHEN** displaying a win
- **THEN** the system SHALL show a visual indicator: ✅ for "met", ⚠️ for "partial", ❌ for "missed"

#### Scenario: Win score display

- **WHEN** displaying a win
- **THEN** the system SHALL show "score/max_score pts" (e.g., "28/35 pts")
- **AND** SHALL show the status label (Met, Partial, Missed)

#### Scenario: Win color coding

- **WHEN** displaying a win
- **THEN** "met" wins SHALL use green styling
- **AND** "partial" wins SHALL use amber/yellow styling
- **AND** "missed" wins SHALL use red styling

### Requirement: Win Breakdown Expansion

Users SHALL be able to expand each individual win to see detailed evidence and explanations.

#### Scenario: Expand single win

- **WHEN** a user clicks on a win
- **THEN** the win SHALL expand to show its evidence items
- **AND** SHALL show the "missed" explanation if status is "partial" or "missed"

#### Scenario: Multiple wins expanded simultaneously

- **WHEN** a user expands multiple wins
- **THEN** all expanded wins SHALL remain open
- **AND** user SHALL be able to collapse them independently

### Requirement: Exchange Evidence Presentation

Each evidence item SHALL be displayed with clear timestamp, summary, and impact information.

#### Scenario: Evidence card layout

- **WHEN** displaying an exchange evidence item
- **THEN** the system SHALL show timestamp range (e.g., "5:20 - 10:15")
- **AND** SHALL show exchange_summary text
- **AND** SHALL show impact statement (visually distinguished from summary)

#### Scenario: Timestamp formatting

- **WHEN** displaying timestamps
- **THEN** the system SHALL format as MM:SS (e.g., "5:20" for 320 seconds)

#### Scenario: Long summary handling

- **WHEN** an exchange_summary exceeds 200 characters
- **THEN** the system MAY truncate with ellipsis and "show more" link
- **OR** MAY wrap text naturally without truncation

### Requirement: Empty Evidence Handling

The UI SHALL handle cases where no evidence exists gracefully.

#### Scenario: No evidence for missed win

- **WHEN** a win has empty evidence array
- **THEN** the system SHALL display the "missed" explanation
- **AND** SHALL show "No evidence found" or similar empty state

### Requirement: Supplementary Frameworks Section

The score card SHALL include a collapsible section for supplementary frameworks (SPICED/Challenger/Sandler) below the Five Wins.

#### Scenario: Supplementary frameworks collapsed by default

- **WHEN** the score card expands
- **THEN** the supplementary frameworks section SHALL be collapsed
- **AND** SHALL show "Show Coaching Frameworks (SPICED/Challenger/Sandler)" button

#### Scenario: Supplementary frameworks expansion

- **WHEN** a user clicks "Show Coaching Frameworks"
- **THEN** the system SHALL expand to show discovery_rubric, engagement_rubric, etc.
- **AND** SHALL use the same criterion breakdown pattern as Five Wins
- **AND** SHALL visually distinguish as secondary/supplementary (different styling)

### Requirement: Mobile Responsive Layout

Score cards SHALL be usable on mobile devices with appropriate responsive layout.

#### Scenario: Mobile vertical stacking

- **WHEN** viewed on mobile viewport (width < 768px)
- **THEN** wins SHALL stack vertically
- **AND** evidence cards SHALL stack vertically
- **AND** all interactive elements SHALL be touch-friendly (min 44px tap target)

### Requirement: Accessibility Standards

Score cards SHALL meet WCAG 2.1 AA accessibility standards.

#### Scenario: Keyboard navigation

- **WHEN** a user navigates with keyboard only
- **THEN** all interactive elements (expand/collapse buttons, wins) SHALL be keyboard accessible
- **AND** focus indicators SHALL be visible

#### Scenario: Screen reader support

- **WHEN** using a screen reader
- **THEN** win status SHALL be announced (e.g., "Business Win, 28 out of 35 points, Partial")
- **AND** expand/collapse state SHALL be announced

#### Scenario: Color contrast

- **WHEN** displaying status colors
- **THEN** text-to-background contrast SHALL meet WCAG AA standards (4.5:1 minimum)

### Requirement: Performance

Score card rendering SHALL be performant without jank or delays.

#### Scenario: Initial render time

- **WHEN** the call analysis page loads
- **THEN** score cards SHALL render within 500ms
- **AND** SHALL NOT block main thread rendering

#### Scenario: Expand/collapse performance

- **WHEN** a user expands or collapses a score card or win
- **THEN** animation SHALL maintain 60fps
- **AND** SHALL complete within 300ms

### Requirement: Error Handling

The UI SHALL handle malformed or missing data gracefully without crashing.

#### Scenario: Missing five_wins_evaluation

- **WHEN** API response lacks five_wins_evaluation field
- **THEN** the system SHALL fall back to displaying the old format (simple score display)
- **AND** SHALL NOT crash or show "[object Object]" errors

#### Scenario: Invalid win status

- **WHEN** a win has an invalid status value (not "met", "partial", or "missed")
- **THEN** the system SHALL default to "missed" status
- **AND** SHALL log a warning to console

#### Scenario: Scores don't sum to total

- **WHEN** sum of win scores doesn't equal overall score
- **THEN** the system SHALL display both values
- **AND** SHALL show a warning indicator
- **AND** SHALL log validation error to console
