# Specification

## ADDED Requirements

### Requirement: Display Call Metadata

The viewer SHALL display comprehensive call metadata including title, date, duration, participants, and call type.

#### Scenario: Call header information

- **WHEN** user opens call analysis
- **THEN** system displays call title, scheduled date, duration in MM:SS format, and call type (discovery, demo, technical deep dive, negotiation)

#### Scenario: Participant list with roles

- **WHEN** user views call details
- **THEN** system lists all participants with names, roles (SE, AE, CSM, prospect, customer), talk time percentage, and company affiliation

### Requirement: Overall Score Display

The viewer SHALL prominently display the overall call score with visual indicators.

#### Scenario: Score badge with color coding

- **WHEN** user views call analysis
- **THEN** system shows overall score (0-100) in large badge with color: green (>80), yellow (60-80), red (<60)

#### Scenario: Score trend indicator

- **WHEN** rep has previous calls
- **THEN** system shows arrow icon indicating score improvement, decline, or no change compared to previous call

### Requirement: Dimension Scores Breakdown

The viewer SHALL display individual dimension scores (product knowledge, discovery, objection handling, engagement) with detailed breakdowns.

#### Scenario: Dimension score cards

- **WHEN** user views call analysis
- **THEN** system displays 4 cards showing dimension name, score (0-100), and visual progress bar

#### Scenario: Dimension comparison to team average

- **WHEN** manager views call analysis
- **THEN** system shows how dimension score compares to team average with +/- delta

### Requirement: Strengths and Areas for Improvement

The viewer SHALL list specific strengths and areas for improvement identified in the analysis.

#### Scenario: Strengths section

- **WHEN** user expands strengths section
- **THEN** system displays bulleted list of positive behaviors and effective techniques used

#### Scenario: Areas for improvement section

- **WHEN** user expands areas for improvement section
- **THEN** system displays bulleted list of skills to develop with specific recommendations

### Requirement: Transcript Snippets with Highlights

The viewer SHALL display relevant transcript snippets with highlighted examples of good and needs-work moments.

#### Scenario: Good example snippet

- **WHEN** user views specific examples
- **THEN** system shows transcript quote with timestamp, speaker, green highlight, and analysis of why it was effective

#### Scenario: Needs work example snippet

- **WHEN** user views areas needing improvement
- **THEN** system shows transcript quote with timestamp, speaker, yellow highlight, and coaching suggestion

#### Scenario: Jump to timestamp in Gong

- **WHEN** user clicks timestamp on snippet
- **THEN** system opens Gong web player at that exact moment in the call (if Gong integration available)

### Requirement: Action Items for Rep

The viewer SHALL display prioritized action items for the rep to focus on.

#### Scenario: Action items list

- **WHEN** user views action items section
- **THEN** system displays 3-5 prioritized action items with clear, actionable language

#### Scenario: Mark action item complete

- **WHEN** rep clicks checkbox on action item
- **THEN** system marks item as complete and updates completion status

### Requirement: Coaching Notes Section

The viewer SHALL allow managers to add private coaching notes attached to the call analysis.

#### Scenario: Manager adds coaching note

- **WHEN** manager clicks "Add Note" and enters text
- **THEN** system saves note with timestamp and manager name, visible only to managers

#### Scenario: Rep cannot see coaching notes

- **WHEN** rep views their own call analysis
- **THEN** system hides coaching notes section (manager-only feature)

### Requirement: Share Analysis

The viewer SHALL allow users to share call analysis via link or export.

#### Scenario: Generate shareable link

- **WHEN** user clicks "Share" button
- **THEN** system generates public link with call analysis (respects permissions - managers can share any call, reps only own calls)

#### Scenario: Export as PDF

- **WHEN** user clicks "Export PDF"
- **THEN** system generates formatted PDF report with all analysis sections
