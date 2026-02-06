## ADDED Requirements

### Requirement: Opportunities page displays searchable list of all opportunities

The system SHALL provide a page that lists all opportunities with search and filter capabilities.

#### Scenario: Default view shows recent opportunities

- **WHEN** manager navigates to opportunities page
- **THEN** page displays most recently updated opportunities
- **THEN** each opportunity shows name, account, owner, stage, close date, health score
- **THEN** list is sorted by updated_at DESC by default

#### Scenario: List view is paginated for performance

- **WHEN** viewing opportunities list with 500+ records
- **THEN** page loads first 50 opportunities
- **THEN** page provides pagination controls to navigate pages
- **THEN** page load completes quickly

#### Scenario: Clicking opportunity navigates to detail page

- **WHEN** manager clicks on opportunity in list
- **THEN** page navigates to opportunity detail page with timeline
- **THEN** navigation preserves filter and pagination state in URL

### Requirement: Search filters opportunities by name or account

The system SHALL allow managers to filter opportunities using text search on name and account fields.

#### Scenario: Search by opportunity name

- **WHEN** manager types "Acme" in search box
- **THEN** list filters to opportunities with "Acme" in name (case-insensitive)
- **THEN** search is debounced to avoid excessive queries
- **THEN** results update within 300ms of typing pause

#### Scenario: Search by account name

- **WHEN** manager searches for account name
- **THEN** list filters to opportunities matching account field
- **THEN** partial matches are supported
- **THEN** search works across both name and account fields

#### Scenario: Clear search resets to all opportunities

- **WHEN** manager clears search box
- **THEN** list shows all opportunities again
- **THEN** previous filters remain applied

### Requirement: Filter opportunities by owner, stage, and health score

The system SHALL provide filter controls for opportunity owner, sales stage, and health score ranges.

#### Scenario: Filter by opportunity owner

- **WHEN** manager selects owner from dropdown
- **THEN** list shows only opportunities owned by selected rep
- **THEN** dropdown is populated from unique owners in database
- **THEN** manager can select multiple owners

#### Scenario: Filter by sales stage

- **WHEN** manager selects stage (Discovery, Demo, Negotiation, Closed Won, Closed Lost)
- **THEN** list shows only opportunities in selected stage(s)
- **THEN** manager can select multiple stages
- **THEN** badge colors match stage semantics

#### Scenario: Filter by health score range

- **WHEN** manager filters by health score
- **THEN** page provides slider or range input
- **THEN** list shows opportunities within selected health score range
- **THEN** low health scores are prioritized for coaching

### Requirement: Sort opportunities by multiple criteria

The system SHALL allow managers to sort opportunity list by different fields.

#### Scenario: Sort by close date

- **WHEN** manager selects "Close Date" sort option
- **THEN** list sorts opportunities by close_date (ascending or descending)
- **THEN** urgent opportunities (closing soon) appear first when ascending

#### Scenario: Sort by health score

- **WHEN** manager selects "Health Score" sort option
- **THEN** list sorts by health_score (low to high or high to low)
- **THEN** at-risk opportunities appear first when low-to-high

#### Scenario: Sort by deal amount

- **WHEN** manager selects "Amount" sort option
- **THEN** list sorts by opportunity amount
- **THEN** largest deals appear first when descending

### Requirement: Opportunities list shows coaching priority indicators

The system SHALL highlight opportunities that need coaching attention based on health score and interaction patterns.

#### Scenario: Low health score opportunities are visually flagged

- **WHEN** viewing opportunities with health_score < 50
- **THEN** row displays red warning indicator
- **THEN** tooltip explains "Low health - needs coaching"

#### Scenario: Stale opportunities without recent activity are flagged

- **WHEN** opportunity has no calls or emails in 14+ days
- **THEN** row displays amber warning indicator
- **THEN** tooltip shows days since last interaction

#### Scenario: Opportunities with unresolved objections are highlighted

- **WHEN** opportunity has recurring objections across multiple calls
- **THEN** row displays coaching priority badge
- **THEN** clicking badge navigates to opportunity insights

### Requirement: Opportunities list is responsive and accessible

The system SHALL ensure opportunity list works well on mobile devices and meets accessibility standards.

#### Scenario: Mobile view uses card layout

- **WHEN** viewing opportunities on mobile device
- **THEN** list switches to stacked card layout
- **THEN** each card shows key info in readable format
- **THEN** filters collapse into drawer or dropdown

#### Scenario: Keyboard navigation works for power users

- **WHEN** using keyboard to navigate list
- **THEN** arrow keys move focus between opportunities
- **THEN** Enter key opens opportunity detail
- **THEN** Tab key navigates through filter controls

#### Scenario: Screen reader support for accessibility

- **WHEN** using screen reader on opportunities page
- **THEN** page announces filter changes
- **THEN** opportunity rows have descriptive labels
- **THEN** health score indicators are announced meaningfully

### Requirement: API endpoint supports efficient opportunity list queries

The system SHALL provide backend API endpoint that returns filtered and sorted opportunity data with pagination.

#### Scenario: API accepts filter and sort parameters

- **WHEN** frontend calls /api/opportunities with query params
- **THEN** API filters by owner_email, stage, health_score_min, health_score_max, search
- **THEN** API sorts by specified field and direction
- **THEN** API returns paginated results with total count

#### Scenario: API query uses database indexes for performance

- **WHEN** executing opportunity list query
- **THEN** query uses indexes on owner_email, stage, updated_at
- **THEN** query completes in under 100ms for 5000 records
- **THEN** pagination limits result set size

#### Scenario: API includes aggregated interaction counts

- **WHEN** returning opportunity list
- **THEN** each opportunity includes call_count and email_count
- **THEN** aggregation uses efficient JOIN with COUNT
- **THEN** manager can see activity level at a glance
