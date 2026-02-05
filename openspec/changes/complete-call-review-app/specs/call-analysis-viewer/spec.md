## ADDED Requirements

### Requirement: Display call metadata
The system SHALL display call metadata including title, participants, date, duration, and call type.

#### Scenario: Call metadata loaded
- **WHEN** a user navigates to /calls/[callId]
- **THEN** the system displays call title, participants, date/time, duration, and type (discovery, demo, follow-up)

### Requirement: Display transcript
The system SHALL display the full call transcript with speaker labels and timestamps.

#### Scenario: Transcript rendered
- **WHEN** a call has a transcript available
- **THEN** the system displays each transcript segment with speaker name and timestamp

#### Scenario: No transcript available
- **WHEN** a call does not have a transcript
- **THEN** the system displays "Transcript not available" message

### Requirement: Display coaching insights
The system SHALL display coaching insights organized by dimension (discovery, objection-handling, product-demo, closing).

#### Scenario: Coaching insights loaded
- **WHEN** a call has been analyzed
- **THEN** the system displays insights grouped by dimension with scores, strengths, and improvement areas

#### Scenario: Call not analyzed
- **WHEN** a call has not been analyzed
- **THEN** the system displays "Analyze this call" button to trigger analysis

### Requirement: Display dimension scores
The system SHALL display dimension scores as numeric values (0-100) with visual indicators.

#### Scenario: High score displayed
- **WHEN** a dimension score is 80 or above
- **THEN** the system displays the score with green color indicator

#### Scenario: Medium score displayed
- **WHEN** a dimension score is between 60 and 79
- **THEN** the system displays the score with yellow color indicator

#### Scenario: Low score displayed
- **WHEN** a dimension score is below 60
- **THEN** the system displays the score with red color indicator

### Requirement: Display action items
The system SHALL display actionable recommendations for the rep to improve performance.

#### Scenario: Action items displayed
- **WHEN** coaching analysis includes action items
- **THEN** the system displays each action item with priority level (high, medium, low)

#### Scenario: No action items
- **WHEN** coaching analysis has no action items
- **THEN** the system displays "No action items" message

### Requirement: Loading states
The system SHALL display loading indicators while fetching call data and analysis.

#### Scenario: Loading call data
- **WHEN** call data is being fetched from the backend
- **THEN** the system displays a skeleton loader for call metadata and transcript

#### Scenario: Loading coaching analysis
- **WHEN** coaching analysis is being fetched
- **THEN** the system displays a loading spinner in the insights section

### Requirement: Error handling
The system SHALL display user-friendly error messages when call data cannot be loaded.

#### Scenario: Call not found
- **WHEN** a user navigates to a non-existent callId
- **THEN** the system displays "Call not found" error and returns to call list

#### Scenario: API error
- **WHEN** the backend API returns an error
- **THEN** the system displays the error message and provides a retry button
