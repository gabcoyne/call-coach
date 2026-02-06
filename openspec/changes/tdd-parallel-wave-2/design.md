## Context

The call coaching application currently lacks systematic test coverage across both backend (Python FastAPI/FastMCP) and frontend (Next.js/React). Recent parallel agent work delivered 17 major features, but without accompanying tests. Critical production issues exist:

1. **Broken Middleware**: Rate limiting and compression middleware disabled due to FastAPI/Starlette initialization errors
2. **Zero Backend Coverage**: No pytest tests for analysis engine, caching, database operations, or MCP tools
3. **Minimal Frontend Coverage**: Only 9 test files exist; most components, hooks, and API routes untested
4. **No E2E Testing**: Integration flows between frontend→API→database→Claude API untested
5. **No CI Enforcement**: Pre-commit hooks exist but don't enforce test execution

**Current State**:

- Backend: `pytest.ini` exists, no test files in critical modules
- Frontend: `jest.config.js` configured with 70% coverage targets, largely unmet
- Test utilities: Some test files exist (`test_analysis.py`, `test_role_aware_tools.py`) but incomplete

**Constraints**:

- Must maintain backward compatibility with existing code
- Cannot block current development velocity
- Tests must run fast (<2 min for full suite)
- Parallel agent execution requires isolated test environments

## Goals / Non-Goals

**Goals:**

1. Achieve 80%+ code coverage across backend and frontend within one sprint
2. Fix and thoroughly test broken middleware (rate limiting, compression, auth)
3. Establish TDD workflow where tests are written before implementation
4. Create comprehensive test infrastructure (fixtures, factories, mocks)
5. Integrate testing into CI/CD pipeline with coverage enforcement
6. Enable parallel agent development with isolated test databases
7. Document testing patterns and best practices for future work

**Non-Goals:**

- 100% coverage (diminishing returns; 80% is sufficient)
- Testing third-party libraries (Claude API, Clerk, Gong)
- Performance optimization beyond test execution speed
- Refactoring existing code unless required for testability
- Testing visual/UI aspects (focus on logic and behavior)

## Decisions

### Decision 1: Parallel Agent Test Execution with Isolated Databases

**Choice**: Each agent gets isolated test database using pytest-xdist + database fixtures

**Rationale**:

- Parallel agents cannot share database state
- Faster test execution (8 agents = 8x speed)
- Prevents test pollution and race conditions

**Implementation**:

- pytest-xdist for parallel test execution
- Database fixtures create/teardown per test session
- Use `@pytest.fixture(scope="function")` for isolation
- Docker Compose provides ephemeral Postgres instances

**Alternatives Considered**:

- SQLite in-memory (rejected: doesn't match Postgres semantics)
- Single shared database with transactions (rejected: rollback issues with async code)

### Decision 2: Test-First Development (TDD) Workflow

**Choice**: Write tests before implementation for all new code

**Process**:

1. Agent receives task from beads
2. Agent writes failing test first
3. Agent implements minimum code to pass test
4. Agent refactors if needed
5. Agent runs full test suite before marking task complete

**Rationale**:

- Forces clear requirements thinking
- Prevents scope creep
- Creates living documentation
- Catches regressions immediately

**Enforcement**:

- Pre-commit hooks run tests
- CI blocks merges if tests fail or coverage drops
- Code review checklist includes "tests written first"

### Decision 3: Mock External Services (Claude API, Gong, Clerk)

**Choice**: Mock all external API calls using `pytest-mock` (backend) and `msw` (frontend)

**Rationale**:

- Tests must be fast and deterministic
- External APIs have rate limits and costs
- Network failures shouldn't break tests
- Easier to test error conditions

**Mock Strategy**:

- Claude API: Return pre-recorded responses from fixtures
- Gong API: Mock HTTP responses with realistic call data
- Clerk Auth: Mock session/user objects
- Database: Use real Postgres (not mocked) for integration tests

**Alternatives Considered**:

- VCR/cassettes (rejected: too brittle with dynamic responses)
- Integration tests only (rejected: too slow)

### Decision 4: Middleware Fix Strategy

**Choice**: Refactor middleware to use FastAPI dependency injection instead of `add_middleware()`

**Problem**: `add_middleware()` with keyword arguments fails in current Starlette version

**Solution**:

```python
# Before (broken):
app.add_middleware(RateLimitMiddleware, default_rate_limit=100)

# After (fixed):
from fastapi import Depends

@app.get("/endpoint")
async def endpoint(rate_limit: RateLimitInfo = Depends(check_rate_limit)):
    ...
```

**Rationale**:

- FastAPI dependencies work consistently
- Better testability (can inject mocks)
- Type-safe and documented in OpenAPI schema

**Testing Approach**:

- Unit tests for rate limit logic (token bucket algorithm)
- Integration tests for dependency injection
- E2E tests for actual rate limiting behavior

### Decision 5: Coverage Targets and Enforcement

**Choice**: 80% coverage minimum, enforced in CI

**Breakdown**:

- Backend: 85% (more critical, less UI complexity)
- Frontend components: 75% (UI has more edge cases)
- Frontend hooks: 90% (business logic, highly testable)
- API routes: 95% (critical path, easy to test)

**Enforcement**:

- `pytest-cov` with `--cov-fail-under=80`
- Jest with `coverageThreshold` in config
- CI job fails if coverage drops below target
- Coverage badge in README

### Decision 6: Test Organization Structure

**Backend**:

```
tests/
  unit/
    analysis/
      test_engine.py
      test_cache.py
    api/
      test_rest_server.py
    middleware/
      test_rate_limit.py
  integration/
    test_api_endpoints.py
    test_database.py
  e2e/
    test_coaching_workflow.py
  fixtures/
    conftest.py
    factories.py
```

**Frontend**:

```
__tests__/
  unit/
    components/
      charts/
        ScoreTrendChart.test.tsx
    lib/
      utils.test.ts
  integration/
    api/
      analyze-call.test.ts
  e2e/
    user-workflows.test.tsx
```

**Rationale**: Clear separation of test types, easy to run subsets

### Decision 7: Fixture and Factory Pattern

**Choice**: Use factories (Faker + factory pattern) for test data generation

**Implementation**:

```python
# factories.py
class CallFactory:
    @staticmethod
    def create(**overrides):
        return {
            "id": str(uuid.uuid4()),
            "title": fake.sentence(),
            "scheduled_at": fake.date_time(),
            **overrides
        }
```

**Rationale**:

- Reduces test boilerplate
- Consistent test data
- Easy to create variations
- Self-documenting

## Risks / Trade-offs

### [Risk] Test suite execution time exceeds 2 minutes

**Mitigation**:

- Use pytest-xdist for parallel execution
- Mark slow tests with `@pytest.mark.slow` for optional runs
- Mock expensive operations (Claude API, Gong calls)
- Database fixtures use connection pooling

### [Risk] Flaky tests due to timing/async issues

**Mitigation**:

- Use `pytest-asyncio` with proper async fixtures
- Avoid sleep() - use event-driven waits
- Deterministic test data (no random UUIDs in assertions)
- Retry logic for external service mocks

### [Risk] Tests break during agent parallel execution

**Mitigation**:

- Isolated test databases per agent session
- No shared state between tests
- Fixture cleanup in teardown phase
- Database transactions rolled back after tests

### [Risk] Coverage targets slow development velocity

**Mitigation**:

- 80% is pragmatic (not 100%)
- Allow CI overrides for prototypes
- Coverage measured on incremental changes (not absolute)
- Documentation on what NOT to test (getters, simple properties)

### [Risk] Middleware refactor introduces breaking changes

**Mitigation**:

- Feature flag new middleware implementation
- A/B test in staging before production rollout
- Rollback plan: revert to no middleware (current state)
- Performance monitoring before/after

### [Trade-off] Mocking external APIs means real integration bugs could slip through

**Acceptance**:

- Separate smoke tests hit real APIs (run nightly, not in CI)
- Monitor production errors carefully
- Staging environment uses real integrations

### [Trade-off] Writing tests first slows initial development

**Acceptance**:

- Long-term velocity gain outweighs short-term slowdown
- Tests prevent regressions (faster debugging)
- Upfront thinking reduces refactoring later

## Migration Plan

### Phase 1: Test Infrastructure Setup (Agents 1-2)

1. Install test dependencies (`pytest-asyncio`, `pytest-xdist`, `@testing-library/react`)
2. Configure pytest with parallel execution
3. Create test database fixtures and factories
4. Set up MSW mocking for frontend

**Validation**: Run `pytest --collect-only` and `npm test -- --listTests`

### Phase 2: Critical Path Testing (Agents 3-8)

1. Backend unit tests (analysis engine, cache, database)
2. Middleware fixes and tests (rate limit, compression, auth)
3. Frontend component tests (charts, forms, viewers)
4. API route tests (coaching, opportunities, admin)

**Validation**: Coverage reports show 60%+ in all modules

### Phase 3: Integration & E2E Testing (Agents 9-12)

1. Backend integration tests (API → DB → Claude)
2. Frontend integration tests (API route workflows)
3. E2E tests (user journeys)
4. Performance tests (load testing critical endpoints)

**Validation**: Full test suite passes, 80%+ coverage

### Phase 4: CI/CD Integration & Documentation (Agent 13-14)

1. Update GitHub Actions workflows with test jobs
2. Add coverage reporting and badges
3. Update pre-commit hooks to run tests
4. Write testing guide documentation

**Validation**: CI green, coverage enforced

### Rollback Strategy

If tests block development:

1. Disable coverage enforcement in CI temporarily
2. Mark failing tests with `@pytest.mark.skip("WIP")`
3. Create beads issues for each skipped test
4. Fix tests incrementally without blocking features

If middleware fix breaks production:

1. Feature flag rollback to no middleware
2. Deploy hotfix within 15 minutes
3. Debug in staging with logs
4. Re-deploy fixed version

## Open Questions

1. **Test database strategy for Neon?** Neon doesn't support CREATE DATABASE. Options:

   - Use separate schemas per agent session
   - Use Supabase's test mode
   - Local Postgres in Docker for tests only
   - **Decision needed**: Likely Docker Compose for dev, Neon for staging tests

2. **Claude API mocking complexity?** Responses are large and context-dependent. How detailed should mocks be?

   - **Proposal**: Record 10 representative responses, use them as fixtures
   - **Alternative**: Generate synthetic responses with templates

3. **Frontend E2E testing tool?** Jest doesn't handle full browser testing well.

   - Playwright vs. Cypress vs. skip E2E?
   - **Recommendation**: Start with Playwright (faster, more reliable than Cypress)

4. **Test data versioning?** Fixtures may become stale as schemas evolve.

   - **Proposal**: Factories generate data dynamically
   - **Alternative**: Version fixtures in migrations

5. **Who reviews test quality?** Agents write tests, but who ensures tests are good?
   - **Proposal**: Code review checklist includes test quality criteria
   - **Alternative**: Senior agent does test-only reviews
