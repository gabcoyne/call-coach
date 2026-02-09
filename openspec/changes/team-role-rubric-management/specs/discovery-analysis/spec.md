## ADDED Requirements

### Requirement: Role-Based Discovery Criteria
The discovery analysis SHALL apply role-appropriate evaluation criteria based on the speaker's assigned role.

#### Scenario: AE discovery criteria
- **WHEN** analyzing discovery for a speaker with role="ae"
- **THEN** the system SHALL evaluate: opening questions, SPICED framework, pain identification, impact quantification, decision process, budget exploration
- **AND** SHALL weight criteria according to AE rubric

#### Scenario: CSM discovery criteria
- **WHEN** analyzing discovery for a speaker with role="csm"
- **THEN** the system SHALL evaluate: relationship exploration, usage patterns, expansion opportunities, health indicators, renewal risk factors
- **AND** SHALL weight criteria according to CSM rubric

#### Scenario: SE discovery criteria
- **WHEN** analyzing discovery for a speaker with role="se"
- **THEN** the system SHALL evaluate: technical requirements, architecture fit, integration complexity, technical stakeholder mapping
- **AND** SHALL weight criteria according to SE rubric

#### Scenario: Support discovery criteria
- **WHEN** analyzing discovery for a speaker with role="support"
- **THEN** the system SHALL evaluate: issue identification, impact assessment, troubleshooting methodology, customer environment understanding
- **AND** SHALL weight criteria according to Support rubric
