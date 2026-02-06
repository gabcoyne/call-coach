# Testing Guide

Comprehensive guide to testing in the Gong Call Coaching application, covering test-driven development (TDD), test types, writing effective tests, and debugging.

## Table of Contents

1. [Test-Driven Development (TDD) Workflow](#test-driven-development-tdd-workflow)
2. [Test Infrastructure](#test-infrastructure)
3. [Test Types](#test-types)
4. [Writing Effective Tests](#writing-effective-tests)
5. [Test Examples](#test-examples)
6. [Running Tests](#running-tests)
7. [Debugging Failing Tests](#debugging-failing-tests)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)

---

## Test-Driven Development (TDD) Workflow

### The Red-Green-Refactor Cycle

Test-driven development follows a three-phase cycle that helps you write clean, working code with confidence:

```
🔴 RED → 🟢 GREEN → 🔵 REFACTOR → 🔴 RED → ...
```

#### Phase 1: Red (Write a Failing Test)

Before writing any implementation code, write a test that defines the desired behavior.

**Steps:**

1. Understand the requirement or feature
2. Write a test that would pass if the feature worked correctly
3. Run the test and watch it fail (this confirms the test is actually testing something)

**Example:**

```python
# tests/analysis/test_cache.py

def test_cache_key_generation_is_deterministic():
    """Cache keys should be consistent for same inputs."""
    # GIVEN the same call ID and dimension
    call_id = "call-123"
    dimension = "discovery"

    # WHEN generating cache keys multiple times
    key1 = generate_cache_key(call_id, dimension)
    key2 = generate_cache_key(call_id, dimension)

    # THEN both keys should be identical
    assert key1 == key2
```

At this point, `generate_cache_key()` doesn't exist yet, so the test will fail with an import error. This is expected!

#### Phase 2: Green (Make the Test Pass)

Write the minimum amount of code necessary to make the test pass. Don't worry about perfection yet.

**Steps:**

1. Implement just enough to satisfy the test
2. Run the test again
3. Verify it passes
4. Resist the urge to add extra features

**Example:**

```python
# analysis/cache.py

import hashlib

def generate_cache_key(call_id: str, dimension: str) -> str:
    """Generate a deterministic cache key."""
    # Simple implementation that satisfies the test
    combined = f"{call_id}:{dimension}"
    return hashlib.sha256(combined.encode()).hexdigest()
```

Run the test: it should now pass!

#### Phase 3: Refactor (Improve the Code)

Now that you have a passing test, you can safely improve the code without breaking functionality.

**Steps:**

1. Look for opportunities to improve code structure
2. Remove duplication
3. Improve names and readability
4. Run tests after each change to ensure nothing broke

**Example:**

```python
# analysis/cache.py

import hashlib
from typing import Protocol

class CacheKeyGenerator(Protocol):
    """Protocol for cache key generation strategies."""
    def generate(self, call_id: str, dimension: str) -> str:
        ...

def generate_cache_key(
    call_id: str,
    dimension: str,
    rubric_version: str = "v1"
) -> str:
    """
    Generate a deterministic cache key including rubric version.

    Cache keys invalidate when rubrics change, ensuring fresh analysis.
    """
    components = [call_id, dimension, rubric_version]
    combined = ":".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()
```

Run the tests again. If they still pass, you've successfully improved the code!

### Why TDD Works

**Forces clear thinking:** You must understand what you're building before you build it.

**Prevents scope creep:** You only write code that makes tests pass.

**Creates living documentation:** Tests show exactly how code should be used.

**Enables fearless refactoring:** Tests catch regressions immediately.

**Catches bugs early:** Finding bugs during development is 10-100x cheaper than in production.

### TDD in Practice

**For new features:**

1. Read the requirement or task description
2. Break it down into small, testable behaviors
3. For each behavior: Red → Green → Refactor
4. Integrate all behaviors
5. Run full test suite

**For bug fixes:**

1. Write a test that reproduces the bug
2. Verify the test fails
3. Fix the bug
4. Verify the test passes
5. Add regression tests for edge cases

**Example workflow (adding cache invalidation):**

```bash
# 1. Create test file
touch tests/analysis/test_cache_invalidation.py

# 2. Write failing test
# (see test examples below)

# 3. Run test - it should fail
pytest tests/analysis/test_cache_invalidation.py -v

# 4. Implement feature
# Edit analysis/cache.py

# 5. Run test again - should pass
pytest tests/analysis/test_cache_invalidation.py -v

# 6. Run full test suite
pytest tests/
```

---

## Test Infrastructure

### Backend (Python)

**Test Framework:** pytest with plugins

- `pytest`: Core testing framework
- `pytest-asyncio`: Async test support
- `pytest-xdist`: Parallel test execution
- `pytest-mock`: Mocking utilities
- `pytest-cov`: Coverage reporting

**Configuration:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v                      # Verbose output
    --strict-markers        # Fail on unknown markers
    --tb=short             # Short traceback format
    --disable-warnings     # Hide deprecation warnings
    -n auto                # Parallel execution
    --cov=analysis         # Coverage for analysis module
    --cov-report=html      # HTML coverage report
    --cov-fail-under=85    # Fail if coverage < 85%
asyncio_mode = auto
markers =
    integration: Integration tests
    slow: Slow tests
    e2e: End-to-end tests
```

**Test Database:**

- Docker Compose provides isolated Postgres instances
- Each test session gets a fresh database
- Fixtures handle setup and teardown

### Frontend (TypeScript/React)

**Test Framework:** Jest with React Testing Library

- `jest`: Test runner and assertion library
- `@testing-library/react`: Component testing utilities
- `@testing-library/user-event`: User interaction simulation
- `jest-dom`: Custom DOM matchers
- `jest-axe`: Accessibility testing

**Configuration:** `frontend/jest.config.js`

```javascript
{
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'lib/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    'app/**/*.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      statements: 75,
      branches: 75,
      functions: 75,
      lines: 75,
    },
  },
}
```

### Test Data

**Fixtures:** Reusable test data defined in `tests/conftest.py`

```python
@pytest.fixture
def sample_gong_call():
    """Sample Gong call metadata."""
    return {
        "id": "1234567890",
        "title": "Prefect Discovery Call - Acme Corp",
        "participants": [...]
    }
```

**Factories:** Dynamic test data generation

```python
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

---

## Test Types

### Unit Tests

Test individual functions or methods in isolation.

**Characteristics:**

- Fast (< 100ms per test)
- No external dependencies
- Mock all I/O operations
- Test one thing at a time

**Use for:**

- Pure functions
- Business logic
- Data transformations
- Utility functions

**Example structure:**

```python
# tests/analysis/test_engine.py

class TestClaudeAnalysis:
    """Tests for Claude API analysis."""

    @patch("analysis.engine.anthropic_client")
    def test_run_claude_analysis_discovery(self, mock_anthropic):
        """Test Claude analysis for discovery dimension."""
        # Arrange: Set up test data and mocks
        mock_response = MagicMock()
        mock_response.content[0].text = '{"scores": {"discovery": 85}}'
        mock_anthropic.messages.create.return_value = mock_response

        # Act: Call the function
        result = _run_claude_analysis(
            dimension=CoachingDimension.DISCOVERY,
            transcript="Sample transcript",
            call_metadata={"title": "Test Call"}
        )

        # Assert: Verify behavior
        assert result is not None
        assert "scores" in result
        assert result["scores"]["discovery"] == 85
```

### Integration Tests

Test how multiple components work together.

**Characteristics:**

- Slower (100ms - 2s per test)
- Use real database
- Mock external APIs only
- Test component interactions

**Use for:**

- API endpoints
- Database operations
- Service layer
- Request/response handling

**Example structure:**

```python
# tests/api/test_rest_api_integration.py

@pytest.mark.integration
class TestAnalyzeCallEndpoint:
    """Integration tests for analyze_call endpoint."""

    def test_post_analyze_call_creates_coaching_session(
        self, client, test_db, sample_call
    ):
        """Test that POST /tools/analyze_call creates database record."""
        # Arrange: Insert test call into database
        insert_call(test_db, sample_call)

        # Mock Claude API only
        with patch("api.rest_server.analyze_call_tool") as mock:
            mock.return_value = {"call_id": sample_call["id"]}

            # Act: Make API request
            response = client.post(
                "/tools/analyze_call",
                json={"call_id": sample_call["id"]}
            )

        # Assert: Verify response and database state
        assert response.status_code == 200
        session = get_coaching_session(test_db, sample_call["id"])
        assert session is not None
```

### End-to-End (E2E) Tests

Test complete user workflows from start to finish.

**Characteristics:**

- Slowest (2s - 30s per test)
- Use real database
- Mock only rate-limited external APIs
- Test user-visible behavior

**Use for:**

- Critical user flows
- Multi-step workflows
- Feature acceptance
- Smoke tests

**Example structure:**

```python
# tests/e2e/test_coaching_workflow.py

@pytest.mark.e2e
class TestCoachingAnalysisWorkflow:
    """E2E tests for complete coaching analysis flow."""

    @pytest.mark.asyncio
    async def test_complete_coaching_analysis_flow(
        self, client, test_db, mock_gong_api
    ):
        """
        Test full workflow: Webhook → Analysis → Storage → Retrieval.

        Simulates:
        1. Gong webhook notification
        2. Fetch call data from Gong
        3. Run Claude analysis
        4. Store results in database
        5. Retrieve via API endpoint
        """
        # 1. Simulate Gong webhook
        webhook_payload = {
            "event": "call.completed",
            "call_id": "call-123",
        }
        response = await client.post("/webhooks/gong", json=webhook_payload)
        assert response.status_code == 200

        # 2. Wait for async processing
        await asyncio.sleep(2)

        # 3. Verify coaching session was created
        session = get_coaching_session(test_db, "call-123")
        assert session is not None
        assert session["scores"]["overall"] > 0

        # 4. Verify retrievable via API
        response = await client.get(f"/api/coaching/sessions/{session['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["call_id"] == "call-123"
```

### Performance Tests

Test system behavior under load.

**Characteristics:**

- Very slow (30s - 5min per test)
- Test at scale
- Measure response times
- Identify bottlenecks

**Use for:**

- API response times
- Database query performance
- Concurrent request handling
- Cache effectiveness

**Example structure:**

```python
# tests/performance/test_api_load.py

@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API endpoints."""

    def test_analyze_call_response_time_under_load(self, client):
        """Test API response time with concurrent requests."""
        import time
        import concurrent.futures

        def make_request():
            start = time.time()
            response = client.post(
                "/tools/analyze_call",
                json={"call_id": "call-123"}
            )
            duration = time.time() - start
            return duration, response.status_code

        # Make 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: make_request(), range(50)))

        durations = [r[0] for r in results]
        status_codes = [r[1] for r in results]

        # Assert performance requirements
        assert all(code == 200 for code in status_codes)
        assert sum(durations) / len(durations) < 2.0  # avg < 2s
        assert max(durations) < 5.0  # p99 < 5s
```

---

## Writing Effective Tests

### Test Structure: Arrange-Act-Assert (AAA)

Every test should follow this clear structure:

```python
def test_cache_hit_prevents_api_call():
    # ARRANGE: Set up test data and preconditions
    call_id = "call-123"
    cached_result = {"scores": {"discovery": 85}}
    mock_cache.set(generate_cache_key(call_id, "discovery"), cached_result)

    # ACT: Perform the action being tested
    result = get_or_create_coaching_session(
        call_id=call_id,
        dimension=CoachingDimension.DISCOVERY,
        transcript="Sample transcript"
    )

    # ASSERT: Verify the expected outcome
    assert result == cached_result
    assert not mock_anthropic.messages.create.called  # API not called
```

### Test Naming Conventions

Use descriptive names that explain what's being tested and the expected behavior.

**Format:** `test_<action>_<condition>_<expected_result>`

**Good examples:**

```python
test_generate_cache_key_same_inputs_returns_same_key()
test_analyze_call_missing_transcript_raises_error()
test_get_rep_insights_no_data_returns_empty_list()
test_rate_limit_exceeded_returns_429_status()
```

**Bad examples:**

```python
test_cache()  # Too vague
test_1()  # Meaningless
test_it_works()  # Doesn't explain what "it" is
```

### Mocking External Dependencies

Mock external services to make tests fast, reliable, and deterministic.

**What to mock:**

- HTTP requests (Claude API, Gong API, Clerk)
- File I/O
- Environment variables
- Current time/dates
- Random number generation

**What NOT to mock:**

- Your own code (defeats the purpose)
- Database (use real DB for integration tests)
- Simple data structures

**Example: Mocking Claude API**

```python
@patch("analysis.engine.anthropic_client")
def test_claude_api_call_with_caching(mock_anthropic):
    """Test that Claude API responses are cached."""
    # Arrange: Set up mock response
    mock_response = MagicMock()
    mock_response.content[0].text = json.dumps({
        "scores": {"discovery": 85},
        "strengths": ["Good questions"]
    })
    mock_anthropic.messages.create.return_value = mock_response

    # Act: Call twice with same inputs
    result1 = run_analysis(call_id="call-123", dimension="discovery")
    result2 = run_analysis(call_id="call-123", dimension="discovery")

    # Assert: API called only once due to caching
    assert mock_anthropic.messages.create.call_count == 1
    assert result1 == result2
```

**Example: Mocking Gong API**

```python
@patch("gong.client.requests.get")
def test_fetch_call_metadata_success(mock_get):
    """Test successful call metadata retrieval."""
    # Arrange: Mock successful API response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "id": "call-123",
            "title": "Discovery Call",
            "duration": 3600
        }
    )

    # Act
    result = fetch_call_metadata("call-123")

    # Assert
    assert result["id"] == "call-123"
    assert result["duration"] == 3600
```

### Testing Async Code

Use `pytest-asyncio` for testing async functions.

```python
@pytest.mark.asyncio
async def test_async_analysis_processing():
    """Test async analysis processing."""
    # Arrange
    call_id = "call-123"

    # Act
    result = await process_call_async(call_id)

    # Assert
    assert result["status"] == "completed"
```

### Testing Error Conditions

Test both happy paths and error scenarios.

```python
def test_analyze_call_missing_call_id_raises_error():
    """Test that missing call ID raises ValueError."""
    with pytest.raises(ValueError, match="call_id is required"):
        analyze_call_tool(call_id=None)

def test_api_call_handles_network_error():
    """Test graceful handling of network errors."""
    with patch("requests.get", side_effect=requests.RequestException):
        result = fetch_call_metadata("call-123")
        assert result is None  # or appropriate error handling
```

### Frontend Component Testing

Use React Testing Library for component tests.

```typescript
// components/ui/__tests__/ScoreBadge.test.tsx

import { render, screen } from '@testing-library/react'
import { ScoreBadge } from '../score-badge'

describe('ScoreBadge', () => {
  it('renders score value correctly', () => {
    render(<ScoreBadge score={85} />)
    expect(screen.getByText('85')).toBeInTheDocument()
  })

  it('applies correct color for high scores', () => {
    const { container } = render(<ScoreBadge score={90} />)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-green-500')
  })

  it('applies correct color for low scores', () => {
    const { container } = render(<ScoreBadge score={40} />)
    const badge = container.firstChild
    expect(badge).toHaveClass('bg-red-500')
  })
})
```

### Testing React Hooks

Use `renderHook` from React Testing Library.

```typescript
// lib/hooks/__tests__/useRepInsights.test.tsx

import { renderHook, waitFor } from "@testing-library/react";
import { useRepInsights } from "../useRepInsights";

describe("useRepInsights", () => {
  it("starts in loading state", () => {
    const { result } = renderHook(() => useRepInsights("rep@example.com"));

    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();
  });

  it("fetches and returns insights", async () => {
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ score: 85 }),
    });

    const { result } = renderHook(() => useRepInsights("rep@example.com"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data?.score).toBe(85);
  });
});
```

---

## Running Tests

### Backend Tests

**Run all tests:**

```bash
pytest tests/
```

**Run specific test file:**

```bash
pytest tests/analysis/test_engine.py
```

**Run specific test function:**

```bash
pytest tests/analysis/test_engine.py::test_cache_hit_prevents_api_call
```

**Run tests matching pattern:**

```bash
pytest tests/ -k "cache"  # Runs all tests with "cache" in name
```

**Run with coverage:**

```bash
pytest tests/ --cov=analysis --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Run in parallel:**

```bash
pytest tests/ -n auto  # Uses all CPU cores
```

**Run only unit tests:**

```bash
pytest tests/ -m "not integration and not e2e"
```

**Run only integration tests:**

```bash
pytest tests/ -m integration
```

**Verbose output:**

```bash
pytest tests/ -v  # Shows test names
pytest tests/ -vv  # Shows test names + more details
```

**Stop on first failure:**

```bash
pytest tests/ -x
```

**Show print statements:**

```bash
pytest tests/ -s
```

### Frontend Tests

**Run all tests:**

```bash
cd frontend
npm test
```

**Run in watch mode (re-runs on file changes):**

```bash
npm run test:watch
```

**Run with coverage:**

```bash
npm run test:coverage
open coverage/lcov-report/index.html  # View coverage report
```

**Run specific test file:**

```bash
npm test -- components/ui/score-badge.test.tsx
```

**Run tests matching pattern:**

```bash
npm test -- --testNamePattern="renders correctly"
```

**Update snapshots:**

```bash
npm test -- -u
```

**Run in CI mode:**

```bash
npm run test:ci
```

### Pre-commit Hooks

Tests run automatically before commits to catch issues early.

**Manual pre-commit run:**

```bash
pre-commit run --all-files
```

**Skip pre-commit (use sparingly):**

```bash
git commit --no-verify -m "message"
```

---

## Debugging Failing Tests

### Common Failure Patterns

#### 1. Import Errors

**Symptom:**

```
ModuleNotFoundError: No module named 'analysis'
```

**Causes:**

- Missing `__init__.py` files
- Incorrect sys.path configuration
- Virtual environment not activated

**Solutions:**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or: uv sync

# Verify PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:/path/to/call-coach"

# Check for __init__.py files
find . -name "__init__.py"
```

#### 2. Fixture Errors

**Symptom:**

```
fixture 'test_db' not found
```

**Causes:**

- Fixture not defined in conftest.py
- Scope mismatch
- Circular dependencies

**Solutions:**

```python
# Check fixture is defined
@pytest.fixture
def test_db():
    # ...

# Verify fixture scope
@pytest.fixture(scope="function")  # or "session", "module"
def test_db():
    # ...

# Check conftest.py is in correct location
tests/
  conftest.py  # Root fixtures
  unit/
    conftest.py  # Unit test fixtures
```

#### 3. Async Test Failures

**Symptom:**

```
RuntimeError: Event loop is closed
```

**Causes:**

- Missing `@pytest.mark.asyncio` decorator
- Incorrect asyncio mode in pytest.ini
- Mixing sync and async code

**Solutions:**

```python
# Add decorator
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result

# Configure pytest.ini
[pytest]
asyncio_mode = auto
```

#### 4. Mock Not Working

**Symptom:**

```
AssertionError: Real API was called instead of mock
```

**Causes:**

- Wrong import path in patch
- Mock applied after import
- Scope issues

**Solutions:**

```python
# Patch where used, not where defined
# ❌ Wrong
@patch("anthropic.Anthropic")
def test_analysis(mock):
    # ...

# ✅ Correct
@patch("analysis.engine.anthropic_client")
def test_analysis(mock):
    # ...

# Verify patch is active
@patch("analysis.engine.anthropic_client")
def test_analysis(mock):
    assert mock.called  # Verify mock is being used
```

#### 5. Flaky Tests (Pass/Fail Randomly)

**Symptoms:**

- Test passes locally but fails in CI
- Test fails intermittently

**Causes:**

- Race conditions in async code
- Timing dependencies
- Shared state between tests
- Order-dependent tests

**Solutions:**

```python
# Use proper async waits instead of sleep
# ❌ Bad: Timing dependent
import time
time.sleep(2)
assert something_happened

# ✅ Good: Event-driven wait
import asyncio
await asyncio.wait_for(wait_for_condition(), timeout=5)

# Ensure test isolation
@pytest.fixture(autouse=True)
def reset_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()

# Make tests order-independent
# Each test should set up its own data
```

#### 6. Database State Issues

**Symptom:**

```
IntegrityError: duplicate key value violates unique constraint
```

**Causes:**

- Tests sharing database state
- Missing transaction rollback
- Fixtures not cleaning up

**Solutions:**

```python
# Use function-scoped database fixture
@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test."""
    db = create_test_database()
    yield db
    db.drop_all()
    db.close()

# Use transactions that auto-rollback
@pytest.fixture
def db_transaction():
    connection = db.engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()
```

### Debugging Techniques

#### 1. Print Debugging (Quick and Dirty)

```python
def test_something():
    result = function_under_test()
    print(f"DEBUG: result = {result}")  # Add print statement
    assert result == expected

# Run with -s flag to see prints
# pytest tests/test_file.py -s
```

#### 2. PDB Debugger (Interactive)

```python
def test_something():
    result = function_under_test()
    import pdb; pdb.set_trace()  # Execution pauses here
    assert result == expected

# Commands in PDB:
# n - next line
# s - step into function
# c - continue execution
# p variable - print variable
# l - show code context
# q - quit debugger
```

#### 3. Pytest Verbose Output

```bash
# Show detailed failure information
pytest tests/test_file.py -vv

# Show local variables on failure
pytest tests/test_file.py -l

# Show full diff on assertion failures
pytest tests/test_file.py --tb=long
```

#### 4. Isolate the Failure

```bash
# Run only the failing test
pytest tests/test_file.py::test_specific_function

# Disable parallel execution
pytest tests/test_file.py -n 0

# Run without coverage (faster)
pytest tests/test_file.py --no-cov
```

#### 5. Check Test Output

```python
# Capture and inspect output
def test_something(capsys):
    function_that_prints()
    captured = capsys.readouterr()
    print(f"STDOUT: {captured.out}")
    print(f"STDERR: {captured.err}")
```

#### 6. Verify Mock Calls

```python
@patch("module.function")
def test_something(mock_func):
    # ... test code ...

    # Debug: Print all calls to mock
    print(f"Called {mock_func.call_count} times")
    print(f"Calls: {mock_func.call_args_list}")

    # Verify specific call
    mock_func.assert_called_once_with(expected_arg)
```

### Debugging Frontend Tests

#### 1. Debug in Jest

```typescript
// Add debugger statement
test("something", () => {
  debugger; // Execution pauses here if running with --inspect
  expect(true).toBe(true);
});

// Run with Node inspector
// node --inspect-brk node_modules/.bin/jest --runInBand
```

#### 2. Print Component State

```typescript
import { render, screen, debug } from '@testing-library/react'

test('renders component', () => {
  const { container } = render(<MyComponent />)

  // Print DOM tree
  debug()

  // Print specific element
  debug(screen.getByRole('button'))
})
```

#### 3. Query Debugging

```typescript
// If element not found
screen.getByRole("button"); // Throws error

// Use getAllBy to see all matches
screen.getAllByRole("button"); // Returns array

// Use screen.logTestingPlaygroundURL()
screen.logTestingPlaygroundURL(); // Opens interactive query builder
```

### Getting Help

1. **Read the error message carefully** - It usually tells you exactly what's wrong
2. **Check the test file** - Look for typos, wrong imports, missing fixtures
3. **Run a single test** - Isolate the problem
4. **Check Git history** - What changed since tests last passed?
5. **Ask for help** - Share the full error message and test code

---

## Best Practices

### DO

✅ Write tests before implementation (TDD)
✅ Test one thing per test function
✅ Use descriptive test names
✅ Follow Arrange-Act-Assert structure
✅ Mock external dependencies
✅ Test both success and error cases
✅ Keep tests fast (< 100ms for unit tests)
✅ Run tests before committing
✅ Aim for 80%+ code coverage
✅ Use fixtures for test data
✅ Clean up resources in teardown

### DON'T

❌ Skip writing tests ("I'll add them later")
❌ Test implementation details
❌ Write tests that depend on test order
❌ Use real external APIs in tests
❌ Hard-code test data inline
❌ Test third-party library code
❌ Write slow unit tests
❌ Share state between tests
❌ Ignore failing tests
❌ Aim for 100% coverage (diminishing returns)

### Test Quality Checklist

Before marking a test complete:

- [ ] Test name clearly describes what's being tested
- [ ] Test follows Arrange-Act-Assert structure
- [ ] Test is fast (< 100ms for unit tests)
- [ ] Test is isolated (doesn't depend on other tests)
- [ ] External dependencies are mocked
- [ ] Test verifies behavior, not implementation
- [ ] Both success and error cases are covered
- [ ] Test is deterministic (no random failures)
- [ ] Test cleans up resources properly
- [ ] Test would fail if the code was broken

---

## Common Pitfalls

### 1. Testing Implementation Instead of Behavior

**❌ Bad:**

```python
def test_cache_uses_redis():
    """Don't test HOW it works."""
    cache = Cache()
    assert cache._redis_client is not None  # Implementation detail
```

**✅ Good:**

```python
def test_cache_stores_and_retrieves_values():
    """Test WHAT it does."""
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"
```

### 2. Tests That Are Too Broad

**❌ Bad:**

```python
def test_entire_analysis_pipeline():
    """Tests too many things at once."""
    result = run_full_pipeline()
    assert result.call_fetched
    assert result.analysis_complete
    assert result.cached
    assert result.stored_in_db
    # Which part failed if this test fails?
```

**✅ Good:**

```python
def test_fetch_call_from_gong():
    """Test one thing."""
    result = fetch_call("call-123")
    assert result.id == "call-123"

def test_run_claude_analysis():
    """Test another thing."""
    result = analyze_transcript("transcript")
    assert "scores" in result
```

### 3. Fragile Tests That Break Often

**❌ Bad:**

```python
def test_analysis_output():
    """Too specific - breaks with minor changes."""
    result = analyze_call("call-123")
    assert result == {
        "scores": {"discovery": 85, "engagement": 90},
        "analyzed_at": "2024-01-15T10:30:00Z",  # Fails if timestamp changes
        "strengths": ["Good opening", "Strong rapport"]  # Order matters
    }
```

**✅ Good:**

```python
def test_analysis_output():
    """Test essential properties only."""
    result = analyze_call("call-123")
    assert "scores" in result
    assert result["scores"]["discovery"] > 0
    assert len(result["strengths"]) > 0
```

### 4. Slow Tests

**❌ Bad:**

```python
def test_analysis():
    """Hits real Claude API - slow and expensive."""
    result = analyze_call("call-123", use_real_api=True)
    time.sleep(5)  # Wait for processing
    assert result
```

**✅ Good:**

```python
@patch("analysis.engine.anthropic_client")
def test_analysis(mock_client):
    """Mocked - fast and free."""
    mock_client.messages.create.return_value = mock_response
    result = analyze_call("call-123")
    assert result
```

### 5. Shared State Between Tests

**❌ Bad:**

```python
# Module-level variable - shared between tests!
_call_cache = {}

def test_first():
    _call_cache["call-123"] = {"score": 85}
    assert True

def test_second():
    # Assumes test_first ran first and set cache
    assert _call_cache["call-123"]["score"] == 85  # Brittle!
```

**✅ Good:**

```python
@pytest.fixture
def call_cache():
    """Fresh cache for each test."""
    cache = {}
    yield cache
    cache.clear()

def test_first(call_cache):
    call_cache["call-123"] = {"score": 85}
    assert True

def test_second(call_cache):
    # Starts with empty cache - isolated
    assert len(call_cache) == 0
```

### 6. Ignoring Test Coverage Gaps

Coverage reports show what's NOT tested. Use them to find gaps.

```bash
# Generate coverage report
pytest tests/ --cov=analysis --cov-report=html
open htmlcov/index.html

# Look for:
# - Red lines (not executed by any test)
# - Yellow lines (partially covered - some branches not tested)
# - Low percentage modules
```

Focus on:

- Critical business logic
- Complex conditional logic
- Error handling paths
- Edge cases

Don't stress about:

- Simple getters/setters
- Trivial utility functions
- Third-party library code
- Auto-generated code

---

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Jest documentation](https://jestjs.io/)
- [Test-Driven Development by Example](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530) (Kent Beck)
- [Growing Object-Oriented Software, Guided by Tests](https://www.amazon.com/Growing-Object-Oriented-Software-Guided-Tests/dp/0321503627)

---

## Getting Help

If you're stuck:

1. Read the error message carefully
2. Check this guide for debugging tips
3. Search existing tests for similar examples
4. Ask in #engineering Slack channel
5. Pair with another developer

Remember: Writing tests is a skill that improves with practice. Start simple, and gradually tackle more complex scenarios.
