# Frontend Integration Tests

This directory contains integration tests for the Call Coach frontend application, covering API routes and user workflows.

## Test Coverage

### API Routes Tests (`api-routes.test.ts`)

Tests for API endpoint integration covering:

- **test_route_handler_success (11.1)**: Verifies route handlers return successful responses with valid data

  - Opportunities endpoint with pagination
  - Health check endpoint with service status
  - Coaching sessions list endpoint

- **test_route_validation_error (11.2)**: Verifies routes return validation errors for invalid input

  - Invalid pagination parameters (page=0, limit>200)
  - Negative page numbers
  - Missing required fields for POST requests

- **test_route_database_query (11.3)**: Verifies route interaction with database
  - Parameterized queries with filters
  - Database connection error handling
  - Empty result sets
  - Transaction consistency
  - SQL injection protection
  - Concurrent request handling

### User Workflows Tests (`user-workflows.test.tsx`)

Tests for complete user interaction workflows:

- **test_login_dashboard (11.4)**: Verifies login and dashboard navigation workflow

  - Manager authentication and dashboard rendering
  - Rep authentication and redirect to personal dashboard
  - Loading states during authentication
  - Error handling for failed data fetching
  - Complete login-to-dashboard flow
  - Empty state handling

- **test_create_session (11.5)**: Verifies coaching session creation workflow
  - Fetching existing coaching sessions
  - Creating new coaching sessions via POST
  - Validation error handling
  - Complete end-to-end workflow: analyze call → create session → fetch sessions
  - Error recovery for failed requests

## Test Statistics

- **Total Tests**: 33
- **API Routes Tests**: 19
- **User Workflows Tests**: 14
- **All Passing**: ✅

## Running the Tests

```bash
# Run all integration tests
npm test -- __tests__/integration/

# Run specific test file
npm test -- __tests__/integration/api-routes.test.ts
npm test -- __tests__/integration/user-workflows.test.tsx

# Run with coverage
npm test -- __tests__/integration/ --coverage

# Watch mode for development
npm test -- __tests__/integration/ --watch
```

## Test Approach

These integration tests use mocked fetch calls and component rendering to test the integration between different parts of the application without requiring the full Next.js runtime. This approach:

- **Faster execution**: Tests run in milliseconds
- **Better isolation**: Each test is independent
- **Easier debugging**: Clear failure messages
- **No external dependencies**: Tests work offline

For full end-to-end testing with the Next.js runtime, browser automation, and real API calls, see the E2E test suite.

## Dependencies

- **@testing-library/react**: Component rendering and queries
- **@testing-library/user-event**: User interaction simulation
- **jest**: Test runner and assertions
- **jest-dom**: Additional DOM matchers

## Mock Setup

Global mocks are configured in `/jest.setup.js`:

- Next.js router (`useRouter`, `usePathname`, etc.)
- Clerk authentication (`useUser`, `useAuth`)
- Web APIs (Request, Response, Headers)
- Browser APIs (matchMedia, IntersectionObserver)

## Notes

- MSW (Mock Service Worker) is optional and not yet installed
- Tests use manual mocks via `jest.fn()` for API endpoints
- Component-specific hooks are mocked in each test file as needed

## Tasks Completed

- ✅ 11.1 - Write integration test for API route handler success
- ✅ 11.2 - Write integration test for API route validation error
- ✅ 11.3 - Write integration test for API route DB interaction
- ✅ 11.4 - Write integration test for login to dashboard workflow
- ✅ 11.5 - Write integration test for create coaching session workflow
