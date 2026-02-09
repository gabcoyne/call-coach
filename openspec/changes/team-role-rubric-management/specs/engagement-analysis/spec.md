## ADDED Requirements

### Requirement: Role-Based Engagement Criteria
The engagement analysis SHALL apply role-appropriate evaluation criteria based on the speaker's assigned role.

#### Scenario: AE engagement criteria
- **WHEN** analyzing engagement for a speaker with role="ae"
- **THEN** the system SHALL evaluate: talk-listen ratio (target 30:70), active listening, rapport building, energy level, objection handling
- **AND** SHALL weight criteria according to AE rubric

#### Scenario: CSM engagement criteria
- **WHEN** analyzing engagement for a speaker with role="csm"
- **THEN** the system SHALL evaluate: empathy, relationship depth, customer advocacy, proactive communication, trust building
- **AND** SHALL weight criteria according to CSM rubric

#### Scenario: SE engagement criteria
- **WHEN** analyzing engagement for a speaker with role="se"
- **THEN** the system SHALL evaluate: technical clarity, stakeholder engagement, patience during technical questions, credibility building
- **AND** SHALL weight criteria according to SE rubric

#### Scenario: Support engagement criteria
- **WHEN** analyzing engagement for a speaker with role="support"
- **THEN** the system SHALL evaluate: responsiveness, empathy during issues, troubleshooting patience, technical communication clarity
- **AND** SHALL weight criteria according to Support rubric
