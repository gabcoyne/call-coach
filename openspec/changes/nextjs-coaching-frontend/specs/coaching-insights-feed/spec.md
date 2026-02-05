## ADDED Requirements

### Requirement: Chronological Activity Feed
The feed SHALL display recent coaching activities in reverse chronological order (newest first).

#### Scenario: Recent analyses feed
- **WHEN** user views coaching insights feed
- **THEN** system displays latest call analyses with date, rep name, overall score, and quick preview

#### Scenario: Feed item click
- **WHEN** user clicks feed item
- **THEN** system navigates to full call analysis viewer for that call

#### Scenario: Infinite scroll pagination
- **WHEN** user scrolls to bottom of feed
- **THEN** system loads next 20 feed items automatically

### Requirement: Team-Wide Insights
The feed SHALL highlight team-wide patterns, trends, and aggregate statistics (manager view only).

#### Scenario: Team performance summary card
- **WHEN** manager views feed
- **THEN** system displays card with team average score, total calls this week, and improvement trend

#### Scenario: Common objection pattern alert
- **WHEN** system detects multiple calls with same objection type
- **THEN** system displays insight card: "Pricing objections increased 40% this week across 12 calls"

#### Scenario: Top performer highlight
- **WHEN** manager views feed
- **THEN** system displays card highlighting rep with highest average score this week

### Requirement: Coaching Highlights
The feed SHALL surface notable coaching moments and exemplary call excerpts.

#### Scenario: Excellent discovery question highlight
- **WHEN** system detects exceptionally good discovery question in analysis
- **THEN** system displays highlight card with transcript snippet, rep name, and "Why This Worked" analysis

#### Scenario: Successful objection handling example
- **WHEN** call has strong objection handling with high score
- **THEN** system displays highlight card with objection type, rep response, and outcome

#### Scenario: Skill improvement milestone
- **WHEN** rep shows significant improvement in dimension score (e.g., +15 points over 4 weeks)
- **THEN** system displays celebration card congratulating rep on improvement

### Requirement: Filter Feed by Type
The feed SHALL allow users to filter by feed item types (analyses, insights, highlights, milestones).

#### Scenario: Show only call analyses
- **WHEN** user selects "Call Analyses" filter
- **THEN** system displays only individual call analysis feed items

#### Scenario: Show only team insights
- **WHEN** manager selects "Team Insights" filter
- **THEN** system displays only aggregate pattern and trend cards

#### Scenario: Show only highlights
- **WHEN** user selects "Coaching Highlights" filter
- **THEN** system displays only exemplary moment cards

### Requirement: Time-Based Feed Filtering
The feed SHALL allow filtering by time period (today, this week, this month, custom range).

#### Scenario: Today's feed
- **WHEN** user selects "Today" filter
- **THEN** system shows only feed items from current day

#### Scenario: This week's feed
- **WHEN** user selects "This Week" filter
- **THEN** system shows feed items from Monday to Sunday of current week

#### Scenario: Custom date range
- **WHEN** user selects custom date range
- **THEN** system shows feed items within specified start and end dates

### Requirement: Rep-Specific vs Team Feed
The feed SHALL show different content based on user role (reps see own activity only, managers see team-wide).

#### Scenario: Rep viewing feed
- **WHEN** rep user views coaching insights feed
- **THEN** system shows only items related to their own calls and improvements

#### Scenario: Manager viewing team feed
- **WHEN** manager views feed
- **THEN** system shows all team members' activities, team insights, and aggregate patterns

### Requirement: Feed Item Actions
The feed SHALL provide quick actions on feed items without navigating away.

#### Scenario: Like/bookmark feed item
- **WHEN** user clicks bookmark icon on feed item
- **THEN** system saves item to user's bookmarked items for later review

#### Scenario: Share feed item
- **WHEN** user clicks share icon on highlight card
- **THEN** system generates shareable link or allows internal sharing with team members

#### Scenario: Dismiss insight
- **WHEN** manager clicks "Dismiss" on team insight card
- **THEN** system removes card from feed and marks as acknowledged

### Requirement: Feed Notifications
The feed SHALL show new item indicators and send optional email digests.

#### Scenario: New items badge
- **WHEN** new feed items are added since user's last visit
- **THEN** system displays badge with count of new items (e.g., "5 new")

#### Scenario: Auto-refresh feed
- **WHEN** user has feed open for >5 minutes and new items arrive
- **THEN** system displays banner: "3 new items available. Click to refresh"

#### Scenario: Weekly digest email
- **WHEN** enabled in user preferences
- **THEN** system sends email every Monday with top highlights and insights from previous week
