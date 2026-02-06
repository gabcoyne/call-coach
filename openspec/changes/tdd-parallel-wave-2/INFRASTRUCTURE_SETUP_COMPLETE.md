# Test Infrastructure Setup - Complete

**Date**: 2026-02-05
**Agent**: infrastructure-agent
**Tasks Completed**: 1.1 - 1.8

## Summary

All test infrastructure for TDD Parallel Wave 2 has been successfully set up. Other agents can now proceed with writing tests.

---

## Backend Test Infrastructure

### Dependencies Installed ✓

Added to `pyproject.toml` dev dependencies:

- `pytest-xdist>=3.5.0` - Parallel test execution
- `faker>=22.0.0` - Test data generation

### pytest.ini Configuration ✓

**Location**: `/Users/gcoyne/src/prefect/call-coach/pytest.ini`

**Key settings**:

- `-n auto` - Run tests in parallel using all available CPU cores
- `--dist loadscope` - Distribute tests by scope for better parallelization
- `--cov-fail-under=85` - Enforce 85% minimum coverage threshold
- Coverage modules: `analysis`, `coaching_mcp`, `api`, `db`, `cache`, `middleware`

**Usage**:

```bash
# Run all tests in parallel with coverage
pytest

# Run specific test file
pytest tests/test_analysis_engine.py

# Run tests with specific marker
pytest -m "not integration"

# Run with verbose output
pytest -v
```

### Test Database Setup ✓

**Location**: `/Users/gcoyne/src/prefect/call-coach/docker-compose.test.yml`

**Services**:

- `postgres-test` - PostgreSQL 15 on port 5433

  - DB: `call_coach_test`
  - User: `test_user`
  - Password: `test_password`

- `redis-test` - Redis 7 on port 6380
  - Ephemeral (no persistence)

**Usage**:

```bash
# Start test infrastructure
docker compose -f docker-compose.test.yml up -d

# Stop test infrastructure
docker compose -f docker-compose.test.yml down

# View logs
docker compose -f docker-compose.test.yml logs -f
```

### Test Fixtures ✓

**Location**: `/Users/gcoyne/src/prefect/call-coach/tests/fixtures/conftest.py`

**Available fixtures**:

- `test_db_config` - Database configuration dictionary
- `db_connection_sync` - Synchronous DB connection (session scope)
- `db_connection` - Async DB connection (function scope)
- `db_transaction` - Auto-rollback transaction for test isolation
- `clean_database` - Truncates all tables between tests
- `redis_client` - Redis client with auto-flush

**Usage example**:

```python
async def test_something(db_transaction, redis_client):
    # Your test code here - changes will be rolled back
    await db_transaction.execute("INSERT INTO ...")
    await redis_client.set("key", "value")
```

### Test Data Factories ✓

**Location**: `/Users/gcoyne/src/prefect/call-coach/tests/fixtures/factories.py`

**Available factories**:

- `CallFactory` - Generate call records
- `RepFactory` - Generate sales rep records
- `OpportunityFactory` - Generate opportunity records
- `AnalysisFactory` - Generate analysis records
- `CoachingSessionFactory` - Generate coaching session records
- `InsightFactory` - Generate insight records

**Usage example**:

```python
from tests.fixtures.factories import CallFactory, RepFactory, create_test_scenario

# Create single record
call = CallFactory.create(rep_id="rep-123")

# Create batch of records
calls = CallFactory.create_batch(10, rep_id="rep-123")

# Create complete test scenario with related data
scenario = create_test_scenario(num_reps=2, calls_per_rep=3)
# Returns: {"reps": [...], "calls": [...], "opportunities": [...], "analyses": [...]}
```

---

## Frontend Test Infrastructure

### Dependencies Installed ✓

Added to `frontend/package.json` devDependencies:

- `msw@latest` - Mock Service Worker for API mocking

Note: Testing Library packages were already installed:

- `@testing-library/react@^16.1.0`
- `@testing-library/jest-dom@^6.6.3`
- `@testing-library/user-event@^14.5.2`

### jest.config.js Configuration ✓

**Location**: `/Users/gcoyne/src/prefect/call-coach/frontend/jest.config.js`

**Key changes**:

- Coverage thresholds updated to **75%** for all metrics:
  - statements: 75%
  - branches: 75%
  - functions: 75%
  - lines: 75%

**Usage**:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

### MSW API Mocking Setup ✓

**Handler definitions**: `/Users/gcoyne/src/prefect/call-coach/frontend/__mocks__/handlers.ts`

**Integration**: `/Users/gcoyne/src/prefect/call-coach/frontend/jest.setup.js`

**Available mock endpoints**:

- `GET /api/calls` - List calls
- `GET /api/calls/:id` - Get call by ID
- `POST /api/calls` - Create call
- `GET /api/calls/:callId/analysis` - Get call analyses
- `POST /api/calls/:callId/analysis` - Create analysis
- `GET /api/reps/:repId/insights` - Get rep insights
- `GET /api/reps/:repId/stats` - Get rep statistics
- `GET /api/coaching-sessions` - List coaching sessions
- `GET /api/coaching-sessions/:id` - Get session by ID
- `POST /api/coaching-sessions` - Create session
- `PUT /api/coaching-sessions/:id` - Update session
- `GET /api/opportunities` - List opportunities
- `GET /api/opportunities/:id/insights` - Get opportunity insights
- `GET /api/search` - Search across entities
- `GET /api/error/*` - Error simulation endpoints (500, 404, 401)

**Usage example**:

```typescript
import { render, screen, waitFor } from "@testing-library/react";
import { server } from "../jest.setup";
import { http, HttpResponse } from "msw";

test("component fetches and displays data", async () => {
  render(<MyComponent />);

  await waitFor(() => {
    expect(screen.getByText("Mock Sales Call")).toBeInTheDocument();
  });
});

test("component handles API error", async () => {
  // Override handler for this test
  server.use(
    http.get("/api/calls", () => {
      return HttpResponse.json(
        { error: "Internal Server Error" },
        { status: 500 }
      );
    })
  );

  render(<MyComponent />);

  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});
```

**Mock data creators** (exported from handlers.ts):

- `createMockCall(id, overrides)`
- `createMockAnalysis(id, call_id, overrides)`
- `createMockRepInsight(id, rep_id, overrides)`
- `createMockCoachingSession(id, rep_id, overrides)`

---

## Environment Variables

### Backend Tests

Set these in your environment or `.env.test`:

```bash
TEST_DB_HOST=localhost
TEST_DB_PORT=5433
TEST_DB_USER=test_user
TEST_DB_PASSWORD=test_password
TEST_DB_NAME=call_coach_test

TEST_REDIS_HOST=localhost
TEST_REDIS_PORT=6380
```

### Frontend Tests

MSW uses `NEXT_PUBLIC_API_URL` or defaults to `http://localhost:3000`.

---

## Quick Start for Other Agents

### Backend Agent - Writing Backend Tests

1. Start test infrastructure:

   ```bash
   docker compose -f docker-compose.test.yml up -d
   ```

2. Import fixtures and factories in your test:

   ```python
   from tests.fixtures.factories import CallFactory, RepFactory

   async def test_my_feature(db_transaction):
       # Create test data
       call = CallFactory.create()

       # Your test logic here
       ...
   ```

3. Run your tests:

   ```bash
   pytest tests/your_test_file.py -v
   ```

### Frontend Agent - Writing Frontend Tests

1. Import testing utilities:

   ```typescript
   import { render, screen, waitFor } from "@testing-library/react";
   import userEvent from "@testing-library/user-event";
   ```

2. Write your test (API calls are automatically mocked):

   ```typescript
   test("component behavior", async () => {
     render(<YourComponent />);

     // Interact with component
     const button = screen.getByRole("button");
     await userEvent.click(button);

     // Assert results
     await waitFor(() => {
       expect(screen.getByText("Expected text")).toBeInTheDocument();
     });
   });
   ```

3. Run your tests:

   ```bash
   cd frontend && npm test
   ```

---

## Troubleshooting

### Backend

**Issue**: Tests fail with database connection errors

- **Solution**: Ensure `docker-compose.test.yml` is running
- **Check**: `docker compose -f docker-compose.test.yml ps`

**Issue**: Coverage below 85%

- **Solution**: Add more test cases or adjust threshold temporarily
- **Note**: Threshold can be lowered in `pytest.ini` if needed for initial development

### Frontend

**Issue**: MSW not intercepting requests

- **Solution**: Check that `jest.setup.js` is properly configured
- **Verify**: MSW server is started in `beforeAll` hook

**Issue**: Coverage below 75%

- **Solution**: Add more test cases for uncovered branches
- **Note**: Run `npm run test:coverage` to see detailed coverage report

---

## Files Modified/Created

### Modified

- `/Users/gcoyne/src/prefect/call-coach/pyproject.toml` - Added pytest-xdist and faker
- `/Users/gcoyne/src/prefect/call-coach/pytest.ini` - Added parallel execution and 85% coverage
- `/Users/gcoyne/src/prefect/call-coach/frontend/package.json` - Added msw
- `/Users/gcoyne/src/prefect/call-coach/frontend/jest.config.js` - Updated to 75% coverage
- `/Users/gcoyne/src/prefect/call-coach/frontend/jest.setup.js` - Integrated MSW
- `/Users/gcoyne/src/prefect/call-coach/openspec/changes/tdd-parallel-wave-2/tasks.md` - Marked tasks 1.1-1.8 complete

### Created

- `/Users/gcoyne/src/prefect/call-coach/docker-compose.test.yml` - Test database infrastructure
- `/Users/gcoyne/src/prefect/call-coach/tests/fixtures/conftest.py` - Database fixtures
- `/Users/gcoyne/src/prefect/call-coach/tests/fixtures/factories.py` - Test data factories
- `/Users/gcoyne/src/prefect/call-coach/frontend/__mocks__/handlers.ts` - MSW API handlers

---

## Next Steps

Infrastructure is complete. Other agents can now:

1. **Backend agents** (tasks 2.x - 7.x): Write backend unit and integration tests
2. **Frontend agents** (tasks 8.x - 11.x): Write frontend component, hook, and integration tests
3. **E2E agents** (tasks 12.x): Write end-to-end tests
4. **CI/CD agents** (tasks 13.x): Integrate tests into GitHub Actions
5. **Documentation agents** (tasks 14.x): Write testing guides
6. **Verification agents** (tasks 15.x): Run test suites and verify coverage

**CRITICAL**: All agents should start test infrastructure before writing tests:

```bash
docker compose -f docker-compose.test.yml up -d
```
