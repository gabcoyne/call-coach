## ADDED Requirements

### Requirement: Clerk application configuration

The system SHALL be configured with a valid Clerk application including publishable and secret API keys.

#### Scenario: Valid Clerk keys configured

- **WHEN** the application starts with valid NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY
- **THEN** the application loads without authentication errors

#### Scenario: Invalid Clerk keys

- **WHEN** the application starts with placeholder or invalid Clerk keys
- **THEN** the application displays "Publishable key not valid" error and blocks page load

### Requirement: Email and password authentication

The system SHALL support email and password authentication through Clerk.

#### Scenario: User signs up with email and password

- **WHEN** a new user submits the sign-up form with valid email and password
- **THEN** Clerk creates the user account and redirects to /dashboard

#### Scenario: User signs in with email and password

- **WHEN** an existing user submits the sign-in form with correct credentials
- **THEN** Clerk authenticates the user and redirects to /dashboard

#### Scenario: Invalid login credentials

- **WHEN** a user submits incorrect email or password
- **THEN** Clerk displays an authentication error message

### Requirement: Google OAuth authentication

The system SHALL support Google OAuth as an alternative authentication method.

#### Scenario: User signs in with Google

- **WHEN** a user clicks "Sign in with Google" and completes OAuth flow
- **THEN** Clerk creates or authenticates the user and redirects to /dashboard

### Requirement: Manager and rep roles

The system SHALL support two user roles: manager and rep, stored in Clerk publicMetadata.

#### Scenario: User with manager role

- **WHEN** a user's publicMetadata.role is set to "manager"
- **THEN** the user has access to all reps' data and manager-only features

#### Scenario: User with rep role

- **WHEN** a user's publicMetadata.role is set to "rep" or is unset
- **THEN** the user has access only to their own data

#### Scenario: First user defaults to manager

- **WHEN** the first user is created in the system
- **THEN** their publicMetadata.role MUST be manually set to "manager" in Clerk Dashboard

### Requirement: Protected routes

The system SHALL protect all routes except /sign-in and /sign-up, requiring authentication.

#### Scenario: Unauthenticated user accesses protected route

- **WHEN** an unauthenticated user navigates to /dashboard, /calls, or /search
- **THEN** the system redirects to /sign-in

#### Scenario: Authenticated user accesses protected route

- **WHEN** an authenticated user navigates to /dashboard, /calls, or /search
- **THEN** the system displays the requested page

### Requirement: Sign-out functionality

The system SHALL allow authenticated users to sign out.

#### Scenario: User signs out

- **WHEN** an authenticated user clicks the sign-out button
- **THEN** Clerk clears the session and redirects to /sign-in
