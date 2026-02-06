## ADDED Requirements

### Requirement: System defines distinct coaching rubrics for AE, SE, and CSM roles

The system SHALL maintain three separate coaching rubrics with role-appropriate evaluation dimensions, criteria, and scoring guidance.

#### Scenario: AE rubric focuses on discovery and objection handling

- **WHEN** loading AE coaching rubric
- **THEN** rubric includes "Discovery & Qualification" dimension with 30% weight
- **THEN** rubric includes "Objection Handling" dimension with 25% weight
- **THEN** rubric includes "Product Positioning", "Relationship Building", "Call Control & Next Steps" dimensions
- **THEN** total dimension weights sum to 100%

#### Scenario: SE rubric focuses on technical accuracy and architecture

- **WHEN** loading SE coaching rubric
- **THEN** rubric includes "Technical Accuracy" dimension with 35% weight
- **THEN** rubric includes "Architecture Fit & Design" dimension with 30% weight
- **THEN** rubric includes "Problem-Solution Mapping", "Technical Objection Resolution", "Collaboration with AE" dimensions
- **THEN** total dimension weights sum to 100%

#### Scenario: CSM rubric focuses on value realization and risk management

- **WHEN** loading CSM coaching rubric
- **THEN** rubric includes "Value Realization Tracking" dimension with 30% weight
- **THEN** rubric includes "Risk Identification" dimension with 25% weight
- **THEN** rubric includes "Relationship Depth", "Expansion Opportunity Spotting", "Product Adoption Coaching" dimensions
- **THEN** total dimension weights sum to 100%

### Requirement: Rubrics are stored as JSON files with standard structure

The system SHALL store each rubric as a JSON file following a consistent schema with dimensions, criteria, and scoring guidance.

#### Scenario: Rubric JSON contains required fields

- **WHEN** loading rubric JSON file
- **THEN** file includes "role" field (ae, se, csm)
- **THEN** file includes "dimensions" array with at least 3 dimensions
- **THEN** each dimension includes "id", "name", "weight", "criteria", "scoring" fields

#### Scenario: Rubric dimensions have weighted scoring

- **WHEN** parsing dimension from rubric JSON
- **THEN** dimension includes "weight" field as decimal (e.g., 0.30 for 30%)
- **THEN** all dimension weights in rubric sum to 1.0
- **THEN** weight is used to calculate overall coaching score

#### Scenario: Rubric criteria are specific and actionable

- **WHEN** reading dimension criteria from rubric
- **THEN** criteria array includes 3-5 specific observable behaviors
- **THEN** each criterion describes what good performance looks like
- **THEN** criteria guide AI coaching analysis

### Requirement: Rubric scoring bands provide clear performance levels

The system SHALL define four scoring bands (0-49, 50-69, 70-89, 90-100) with descriptive labels for each dimension.

#### Scenario: Scoring bands have descriptive labels

- **WHEN** reading scoring guidance from dimension
- **THEN** scoring object includes "90-100" band labeled "Excellent" with description
- **THEN** scoring object includes "70-89" band labeled "Good" with description
- **THEN** scoring object includes "50-69" band labeled "Needs Improvement" with description
- **THEN** scoring object includes "0-49" band labeled "Poor" with description

#### Scenario: Band descriptions are role-specific

- **WHEN** comparing scoring bands across AE and SE rubrics for similar dimension
- **THEN** band descriptions reflect role-appropriate expectations
- **THEN** AE "discovery" excellence focuses on qualification questions
- **THEN** SE "problem-solving" excellence focuses on technical depth

### Requirement: System validates rubric structure on load

The system SHALL validate rubric JSON structure and content to prevent malformed configuration.

#### Scenario: System checks required rubric fields

- **WHEN** loading rubric JSON file
- **THEN** system validates presence of "role" and "dimensions" fields
- **THEN** if missing required fields, system raises validation error
- **THEN** error message specifies which fields are missing

#### Scenario: System validates dimension weights sum to 1.0

- **WHEN** validating loaded rubric
- **THEN** system sums all dimension weights
- **THEN** if sum is not 1.0 (within 0.01 tolerance), system raises validation error
- **THEN** error message shows actual sum and expected sum

#### Scenario: System validates scoring band completeness

- **WHEN** validating dimension scoring
- **THEN** system checks for all four scoring bands (0-49, 50-69, 70-89, 90-100)
- **THEN** if any band is missing, system raises validation error
- **THEN** error specifies dimension and missing band

### Requirement: Rubrics are loaded from filesystem and cached in memory

The system SHALL load rubric JSON files from the filesystem at startup and cache them for performance.

#### Scenario: Rubrics loaded at server startup

- **WHEN** analysis module initializes
- **THEN** system loads ae_rubric.json, se_rubric.json, csm_rubric.json from analysis/rubrics/
- **THEN** system validates each rubric structure
- **THEN** system caches rubrics in memory for fast access

#### Scenario: Rubric cache is used for analysis

- **WHEN** coaching analysis requests rubric for role
- **THEN** system returns cached rubric without re-reading file
- **THEN** cache hit provides sub-millisecond rubric access

#### Scenario: Rubric files can be reloaded without restart

- **WHEN** rubric JSON file is updated on filesystem
- **THEN** system provides reload endpoint or signal handler
- **THEN** calling reload re-reads and re-validates rubric files
- **THEN** cached rubrics are updated with new content

### Requirement: AE rubric emphasizes sales process and pipeline management

The AE rubric SHALL evaluate skills critical to moving deals through the sales pipeline.

#### Scenario: AE discovery dimension checks BANT coverage

- **WHEN** analyzing call with AE rubric discovery dimension
- **THEN** criteria include "Identifies budget and timeline (BANT)"
- **THEN** criteria include "Uncovers decision-making process and stakeholders"
- **THEN** scoring excellent requires comprehensive discovery with all BANT covered

#### Scenario: AE objection handling dimension evaluates closing skills

- **WHEN** analyzing call with AE rubric objection handling dimension
- **THEN** criteria include "Addresses pricing concerns with value justification"
- **THEN** criteria include "Turns objections into opportunities"
- **THEN** scoring evaluates ability to advance deal despite pushback

### Requirement: SE rubric emphasizes technical depth and solution design

The SE rubric SHALL evaluate technical skills and ability to architect solutions for customer needs.

#### Scenario: SE technical accuracy dimension checks product knowledge

- **WHEN** analyzing call with SE rubric technical accuracy dimension
- **THEN** criteria include "Accurately explains Prefect/Horizon architecture and features"
- **THEN** criteria include "Provides correct technical details without misinformation"
- **THEN** scoring penalizes any technical inaccuracies heavily

#### Scenario: SE architecture fit dimension evaluates design skills

- **WHEN** analyzing call with SE rubric architecture fit dimension
- **THEN** criteria include "Assesses customer's existing stack and integration points"
- **THEN** criteria include "Proposes architecture aligned with customer constraints"
- **THEN** scoring rewards thoughtful design discussions over generic demos

### Requirement: CSM rubric emphasizes retention and expansion

The CSM rubric SHALL evaluate skills critical to customer success, adoption, and expansion revenue.

#### Scenario: CSM value realization dimension tracks ROI

- **WHEN** analyzing call with CSM rubric value realization dimension
- **THEN** criteria include "Tracks metrics showing customer ROI from Prefect"
- **THEN** criteria include "Identifies blockers to realizing expected value"
- **THEN** scoring rewards proactive value tracking and success planning

#### Scenario: CSM risk identification dimension evaluates churn prevention

- **WHEN** analyzing call with CSM rubric risk identification dimension
- **THEN** criteria include "Spots early warning signs of dissatisfaction or churn risk"
- **THEN** criteria include "Probes on renewal likelihood and budget concerns"
- **THEN** scoring rewards early risk detection and mitigation planning
