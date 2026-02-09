# Call Detail Debugging Spec

## ADDED Requirements

### Requirement: Systematic authentication flow validation

The system SHALL provide a structured debugging approach to validate authentication flow across SSR/CSR boundaries in Next.js App Router.

#### Scenario: Authentication state verified in browser

- **WHEN** call detail page loads in browser
- **THEN** Clerk authentication cookies SHALL be present and valid
- **THEN** API routes accessed via client-side fetch SHALL include authentication credentials

#### Scenario: Authentication state traced through request lifecycle

- **WHEN** debugging authentication issues
- **THEN** system SHALL log authentication state at SSR, hydration, and client fetch boundaries
- **THEN** logs SHALL identify where authentication context is lost

### Requirement: SWR configuration verification

The system SHALL verify SWR hook configuration matches working patterns for authenticated data fetching.

#### Scenario: SWR hook configuration compared to working examples

- **WHEN** SWR hook fails to trigger fetch
- **THEN** hook configuration SHALL be compared line-by-line with known working hooks (e.g., use-current-user.ts)
- **THEN** differences SHALL be documented with explanation of impact

#### Scenario: SWR fetcher function validated

- **WHEN** SWR hook is configured
- **THEN** fetcher function SHALL be defined inline or via config
- **THEN** fetcher function SHALL include credentials and headers required for authentication

### Requirement: Network request inspection

The system SHALL enable programmatic inspection of network requests using Chrome DevTools MCP.

#### Scenario: Missing network requests detected

- **WHEN** page shows loading state indefinitely
- **THEN** DevTools network tab SHALL be inspected programmatically
- **THEN** absence of expected API request SHALL be documented with component state

#### Scenario: Failed network requests diagnosed

- **WHEN** API request fails
- **THEN** response status, headers, and body SHALL be captured
- **THEN** authentication headers SHALL be verified present and valid

### Requirement: React component lifecycle analysis

The system SHALL enable inspection of React component state and lifecycle during debugging.

#### Scenario: Component state inspected during infinite loading

- **WHEN** call detail page shows skeleton loaders indefinitely
- **THEN** CallAnalysisViewer component state SHALL be inspected
- **THEN** SWR hook state (data, error, isLoading, isValidating) SHALL be logged
- **THEN** props passed from server component SHALL be verified

#### Scenario: Hydration mismatch detected

- **WHEN** SSR/CSR boundary causes issues
- **THEN** React hydration errors SHALL be captured from console
- **THEN** server-rendered HTML SHALL be compared with client-rendered HTML

### Requirement: Error state documentation

The system SHALL document all error states encountered during debugging with reproduction steps.

#### Scenario: Error states captured with full context

- **WHEN** any error occurs during investigation
- **THEN** error message, stack trace, component state, and network state SHALL be captured
- **THEN** minimal reproduction steps SHALL be documented
- **THEN** error SHALL be categorized (authentication, SWR config, network, SSR/CSR boundary)
