# Specification

## ADDED Requirements

### Requirement: Rate Limiting Middleware Fixed and Tested

The system SHALL provide functional rate limiting middleware using FastAPI dependency injection with comprehensive tests.

#### Scenario: Rate limit enforced on high-traffic endpoint

- **WHEN** client makes 101 requests in 60 seconds to rate-limited endpoint
- **THEN** request 101 returns 429 Too Many Requests with Retry-After header

#### Scenario: Rate limit headers included in response

- **WHEN** client makes request to rate-limited endpoint
- **THEN** response includes X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers

#### Scenario: Different limits for different endpoints

- **WHEN** expensive endpoint has 10 req/min limit and cheap has 100 req/min
- **THEN** each endpoint enforces its own limit independently

#### Scenario: Per-user rate limiting

- **WHEN** two users hit same endpoint simultaneously
- **THEN** each user's requests counted separately

#### Scenario: Rate limit reset after window expires

- **WHEN** user exhausts rate limit and waits for window expiration
- **THEN** user can make new requests after reset time

### Requirement: Compression Middleware Fixed and Tested

The system SHALL provide response compression middleware that compresses responses above configured threshold.

#### Scenario: Large response compressed with gzip

- **WHEN** API returns response larger than 500 bytes
- **THEN** response is compressed and Content-Encoding: gzip header is set

#### Scenario: Small response not compressed

- **WHEN** API returns response smaller than 500 bytes
- **THEN** response is not compressed to save CPU

#### Scenario: Client without gzip support

- **WHEN** client sends request without Accept-Encoding: gzip
- **THEN** response is not compressed

#### Scenario: Compression level configurable

- **WHEN** middleware configured with compression_level=6
- **THEN** responses use gzip level 6 compression

### Requirement: Auth Middleware Tested

The system SHALL provide authentication middleware tests covering session validation, role checking, and access control.

#### Scenario: Valid Clerk session allows access

- **WHEN** request includes valid Clerk session token
- **THEN** request proceeds to endpoint handler with user context

#### Scenario: Missing session returns 401

- **WHEN** request has no Clerk session token
- **THEN** middleware returns 401 Unauthorized before reaching handler

#### Scenario: Role-based access control

- **WHEN** manager-only endpoint receives request from rep user
- **THEN** middleware returns 403 Forbidden

#### Scenario: Rep can only access own data

- **WHEN** rep requests another rep's data
- **THEN** middleware returns 403 Forbidden

#### Scenario: Manager can access all rep data

- **WHEN** manager requests any rep's data
- **THEN** request proceeds with manager context

### Requirement: Middleware Integration Tests

The system SHALL provide integration tests for middleware working together in FastAPI request pipeline.

#### Scenario: Auth then rate limit then compression

- **WHEN** authenticated request triggers rate limit on compressible response
- **THEN** all middleware execute in correct order

#### Scenario: Middleware error handling

- **WHEN** middleware raises exception during processing
- **THEN** FastAPI error handler catches and returns appropriate status code

#### Scenario: Middleware performance overhead

- **WHEN** request flows through all middleware
- **THEN** total overhead is less than 50ms for non-compressed response

### Requirement: Middleware Dependency Injection Pattern

The system SHALL refactor middleware to use FastAPI dependencies instead of `add_middleware()` for better testability.

#### Scenario: Rate limit dependency injected

- **WHEN** endpoint decorated with `Depends(check_rate_limit)`
- **THEN** rate limit check executes before endpoint logic

#### Scenario: Mock dependency in tests

- **WHEN** test overrides rate limit dependency with mock
- **THEN** endpoint receives mocked rate limit info

#### Scenario: Dependency composition

- **WHEN** endpoint uses multiple dependencies (auth + rate limit)
- **THEN** all dependencies execute in declaration order

### Requirement: Middleware Configuration

The system SHALL allow middleware configuration via environment variables and runtime settings.

#### Scenario: Rate limit config from environment

- **WHEN** RATE_LIMIT_DEFAULT=50 environment variable set
- **THEN** default rate limit is 50 requests per minute

#### Scenario: Dynamic rate limit updates

- **WHEN** rate limit config updated at runtime
- **THEN** new requests use updated limits without restart

#### Scenario: Per-route rate limit overrides

- **WHEN** endpoint specifies custom rate limit in decorator
- **THEN** custom limit overrides default configuration
