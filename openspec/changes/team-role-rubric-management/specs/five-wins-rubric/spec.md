## ADDED Requirements

### Requirement: Role-Aware Five Wins Evaluation
The Five Wins framework SHALL adapt win criteria based on speaker role while maintaining core win structure.

#### Scenario: AE Five Wins criteria
- **WHEN** evaluating Five Wins for a speaker with role="ae"
- **THEN** Business Win SHALL emphasize: value proposition, ROI quantification, business case building
- **AND** Commercial Win SHALL emphasize: pricing discussion, budget fit, procurement process
- **AND** Other wins SHALL use standard AE criteria

#### Scenario: CSM Five Wins criteria
- **WHEN** evaluating Five Wins for a speaker with role="csm"
- **THEN** Business Win SHALL emphasize: adoption metrics, value realization, expansion opportunities
- **AND** Commercial Win SHALL emphasize: renewal positioning, upsell opportunities, contract health
- **AND** Other wins SHALL adapt to post-sales context

#### Scenario: SE Five Wins criteria
- **WHEN** evaluating Five Wins for a speaker with role="se"
- **THEN** Technical Win SHALL be primary focus with higher weight
- **AND** Business Win SHALL emphasize: technical value, architecture benefits
- **AND** Security Win SHALL have detailed technical criteria

#### Scenario: Support Five Wins applicability
- **WHEN** evaluating Five Wins for a speaker with role="support"
- **THEN** the system SHALL apply simplified win criteria focused on: issue resolution, customer satisfaction, technical accuracy
- **AND** MAY omit Commercial Win evaluation as not applicable to support context
