## ADDED Requirements

### Requirement: Opportunity detail page displays header with key opportunity info

The system SHALL display a header section showing opportunity name, account, owner, stage, close date, amount, and health score.

#### Scenario: Header shows opportunity metadata

- **WHEN** manager navigates to opportunity detail page
- **THEN** page displays opportunity name as title
- **THEN** page shows account name, owner email, current stage
- **THEN** page shows close date, deal amount, and Gong health score

#### Scenario: Header indicates opportunity health visually

- **WHEN** viewing opportunity with health score
- **THEN** page displays color-coded health indicator (green/yellow/red)
- **THEN** health score is shown numerically
- **THEN** visual cues help manager prioritize coaching needs

### Requirement: Timeline displays chronological view of all calls and emails

The system SHALL render a timeline showing all calls and emails associated with the opportunity in chronological order.

#### Scenario: Timeline shows calls and emails in date order

- **WHEN** viewing opportunity timeline
- **THEN** page displays all calls and emails sorted by date (newest first)
- **THEN** each timeline item shows type icon (phone for calls, envelope for emails)
- **THEN** each item shows timestamp, participants, and brief preview

#### Scenario: Timeline lazy-loads transcript and email content

- **WHEN** viewing timeline initially
- **THEN** page loads summary data for all timeline items quickly
- **THEN** transcript and email body are not loaded until expanded
- **THEN** initial page load completes in under 2 seconds

#### Scenario: Empty timeline shows helpful message

- **WHEN** opportunity has no associated calls or emails yet
- **THEN** page displays "No calls or emails recorded for this opportunity"
- **THEN** message explains data syncs daily from Gong

### Requirement: Call timeline cards are expandable to show full transcript

The system SHALL allow managers to expand call cards to view the full transcript and coaching analysis inline.

#### Scenario: Collapsed call card shows summary

- **WHEN** viewing call in timeline
- **THEN** collapsed card shows call title, date, duration, participants
- **THEN** card shows coaching score badges for key dimensions
- **THEN** card shows "Expand" button or icon

#### Scenario: Expanding call card loads transcript

- **WHEN** manager clicks to expand call card
- **THEN** card expands to show full transcript with speaker attribution
- **THEN** card displays coaching insights and scores
- **THEN** expansion animation is smooth and responsive

#### Scenario: Call card links to full call analysis page

- **WHEN** viewing expanded call card
- **THEN** card includes "View Full Analysis" link
- **THEN** link navigates to existing call detail page
- **THEN** manager can dive deeper if needed

### Requirement: Email timeline cards are expandable to show body snippet

The system SHALL allow managers to expand email cards to view the first 500 characters of email content.

#### Scenario: Collapsed email card shows summary

- **WHEN** viewing email in timeline
- **THEN** collapsed card shows subject line, sender, recipients, timestamp
- **THEN** card shows "Expand" button or icon

#### Scenario: Expanding email card shows body snippet

- **WHEN** manager clicks to expand email card
- **THEN** card expands to show first 500 characters of email body
- **THEN** card indicates if email is truncated ("... See full email in Gong")
- **THEN** card includes link to view full email in Gong

### Requirement: Timeline supports pagination for opportunities with many touchpoints

The system SHALL paginate timeline items to maintain performance for opportunities with 100+ interactions.

#### Scenario: Timeline loads first 20 items by default

- **WHEN** viewing opportunity with 50+ timeline items
- **THEN** page loads first 20 items (most recent)
- **THEN** page shows "Load More" button at bottom
- **THEN** initial load completes quickly

#### Scenario: Loading more items appends to timeline

- **WHEN** manager clicks "Load More" button
- **THEN** page fetches next 20 timeline items
- **THEN** new items are appended to timeline smoothly
- **THEN** scroll position is preserved

### Requirement: Timeline is responsive on mobile and tablet devices

The system SHALL render timeline optimally on different screen sizes.

#### Scenario: Mobile layout stacks timeline items vertically

- **WHEN** viewing timeline on mobile device
- **THEN** timeline items stack vertically with full width
- **THEN** text is readable without horizontal scrolling
- **THEN** expand/collapse controls are touch-friendly

#### Scenario: Desktop layout uses optimal spacing

- **WHEN** viewing timeline on desktop
- **THEN** timeline uses comfortable margins and spacing
- **THEN** cards have appropriate max-width for readability
- **THEN** layout takes advantage of available screen width
