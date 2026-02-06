## ADDED Requirements

### Requirement: Analysis engine detects speaker role automatically

The system SHALL identify the Prefect speaker's role on each call and apply the appropriate coaching rubric.

#### Scenario: System identifies Prefect speaker by email domain

- **WHEN** analyzing a call
- **THEN** system queries speakers table for speakers with company_side=true and email ending in '@prefect.io'
- **THEN** if multiple Prefect speakers, system selects primary speaker (highest talk_time_percentage)
- **THEN** system uses selected speaker's email to lookup role

#### Scenario: System looks up speaker role from staff_roles table

- **WHEN** Prefect speaker is identified
- **THEN** system queries staff_roles table for speaker's email
- **THEN** if role found, system uses assigned role (ae, se, csm)
- **THEN** if role not found, system defaults to 'ae' as most common role

#### Scenario: External calls default to AE rubric

- **WHEN** analyzing call with no Prefect speakers (external recording or customer-only call)
- **THEN** system defaults to using AE rubric
- **THEN** coaching analysis proceeds with standard evaluation

### Requirement: Analysis loads role-specific rubric before coaching evaluation

The system SHALL load the appropriate rubric based on detected role before running Claude API analysis.

#### Scenario: AE speaker gets AE rubric

- **WHEN** analyzing call where primary speaker has role='ae'
- **THEN** system loads ae_rubric.json from cache
- **THEN** system passes AE rubric dimensions and criteria to Claude API
- **THEN** coaching results reflect AE-appropriate evaluation

#### Scenario: SE speaker gets SE rubric

- **WHEN** analyzing call where primary speaker has role='se'
- **THEN** system loads se_rubric.json from cache
- **THEN** system passes SE rubric dimensions and criteria to Claude API
- **THEN** coaching results reflect SE-appropriate evaluation (technical focus)

#### Scenario: CSM speaker gets CSM rubric

- **WHEN** analyzing call where primary speaker has role='csm'
- **THEN** system loads csm_rubric.json from cache
- **THEN** system passes CSM rubric dimensions and criteria to Claude API
- **THEN** coaching results reflect CSM-appropriate evaluation (value/retention focus)

### Requirement: Coaching sessions store which role rubric was applied

The system SHALL record in coaching_sessions table which role rubric was used for each analysis.

#### Scenario: Coaching session metadata includes applied role

- **WHEN** storing coaching session in database
- **THEN** system adds "rubric_role" field to metadata JSON
- **THEN** field value is the role used (ae, se, csm)
- **THEN** field enables querying which rubric version was used

#### Scenario: Historical sessions preserve original rubric

- **WHEN** retrieving coaching session from database
- **THEN** system reads rubric_role from metadata
- **THEN** if speaker's current role differs, system still shows original rubric used
- **THEN** historical analyses are not retroactively regraded

### Requirement: Call detail page displays which rubric was applied

The system SHALL show users which role rubric was used to evaluate the call.

#### Scenario: Call page shows rubric badge

- **WHEN** viewing call detail page with coaching insights
- **THEN** page displays badge "Evaluated as: Sales Engineer" (or AE/CSM)
- **THEN** badge appears prominently near coaching scores
- **THEN** badge provides context for evaluation criteria used

#### Scenario: Badge tooltips explain role-specific evaluation

- **WHEN** hovering over rubric badge
- **THEN** tooltip explains "This call was evaluated using SE-specific criteria focusing on technical accuracy and architecture fit"
- **THEN** tooltip helps users understand why certain dimensions are emphasized

### Requirement: Learning insights filter comparisons to same role

The system SHALL only compare rep performance to top performers within the same role when generating learning insights.

#### Scenario: AE learning insights compare to top AEs only

- **WHEN** generating learning insights for rep with role='ae'
- **THEN** system queries closed-won opportunities where owner role='ae'
- **THEN** system excludes SE and CSM calls from comparison set
- **THEN** insights show what top-performing AEs do differently

#### Scenario: SE learning insights compare to top SEs only

- **WHEN** generating learning insights for rep with role='se'
- **THEN** system queries calls where primary speaker role='se'
- **THEN** system filters to SE calls with high technical accuracy scores
- **THEN** insights show SE-specific best practices (not AE techniques)

#### Scenario: Learning insights indicate role filter applied

- **WHEN** displaying learning insights
- **THEN** insights header shows "Comparing to top-performing Sales Engineers"
- **THEN** user understands comparison is within role, not cross-role

### Requirement: Rep dashboard shows role-specific performance metrics

The system SHALL display performance metrics filtered and weighted by the rep's role.

#### Scenario: AE dashboard emphasizes discovery and objection handling scores

- **WHEN** viewing dashboard for rep with role='ae'
- **THEN** dashboard prominently displays discovery_score and objection_handling_score
- **THEN** technical_accuracy_score is de-emphasized or hidden
- **THEN** metrics match AE rubric dimension weights

#### Scenario: SE dashboard emphasizes technical and architecture scores

- **WHEN** viewing dashboard for rep with role='se'
- **THEN** dashboard prominently displays technical_accuracy_score and architecture_fit_score
- **THEN** discovery_score is de-emphasized (SE supports AE, doesn't lead discovery)
- **THEN** metrics match SE rubric dimension weights

#### Scenario: Dashboard indicates which dimensions matter for role

- **WHEN** viewing performance metrics
- **THEN** dashboard shows dimension weights from rubric (e.g., "Technical Accuracy: 35% of overall score")
- **THEN** user understands relative importance of each dimension for their role

### Requirement: Mixed-role calls use primary speaker's role

The system SHALL determine rubric to use based on primary speaker when multiple Prefect staff are on call.

#### Scenario: AE-led call with SE support uses AE rubric

- **WHEN** analyzing call with AE (60% talk time) and SE (40% talk time)
- **THEN** system identifies AE as primary speaker by highest talk_time_percentage
- **THEN** system applies AE rubric to analyze entire call
- **THEN** coaching focuses on AE skills (discovery, objection handling)

#### Scenario: SE-led technical deep dive uses SE rubric

- **WHEN** analyzing call with SE (70% talk time) and AE (30% talk time)
- **THEN** system identifies SE as primary speaker
- **THEN** system applies SE rubric to analyze entire call
- **THEN** coaching focuses on SE skills (technical accuracy, architecture)

#### Scenario: Equal talk time defaults to role hierarchy

- **WHEN** analyzing call where AE and SE have equal talk time (both 50%)
- **THEN** system applies role hierarchy: AE > SE > CSM
- **THEN** AE rubric is used by default
- **THEN** hierarchy reflects typical call ownership (AEs own deals)

### Requirement: Opportunity-level coaching aggregates role-aware scores

The system SHALL aggregate coaching scores across all calls in opportunity using role-aware analysis.

#### Scenario: Opportunity with mixed roles shows per-call rubrics

- **WHEN** viewing opportunity timeline with AE discovery call and SE technical call
- **THEN** discovery call shows "Evaluated as: Account Executive"
- **THEN** technical call shows "Evaluated as: Sales Engineer"
- **THEN** each call evaluated with appropriate rubric

#### Scenario: Opportunity insights highlight role-specific gaps

- **WHEN** generating holistic opportunity insights
- **THEN** insights separate AE performance (discovery, objection handling) from SE performance (technical depth)
- **THEN** coaching recommendations are role-specific: "AE should improve BANT coverage, SE should provide more architecture options"
- **THEN** opportunity owner role determines primary coaching focus

### Requirement: System logs rubric selection for debugging

The system SHALL log which rubric was selected and why for each coaching analysis.

#### Scenario: Analysis logs speaker detection and role lookup

- **WHEN** starting coaching analysis
- **THEN** system logs "Detected Prefect speaker: <sarah.chen@prefect.io> (60% talk time)"
- **THEN** system logs "Speaker role: ae (from staff_roles table)"
- **THEN** system logs "Using AE rubric for analysis"

#### Scenario: Logs show default role fallback

- **WHEN** analyzing call where speaker has no assigned role
- **THEN** system logs "No role assigned for speaker, defaulting to 'ae'"
- **THEN** logs enable debugging missing role assignments

#### Scenario: Logs show rubric validation results

- **WHEN** loading rubric file
- **THEN** system logs "Loaded ae_rubric.json: 5 dimensions, weights sum to 1.0, validation passed"
- **THEN** logs confirm rubric structure is valid before use
