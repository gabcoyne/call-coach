# Testing Suite Documentation

Comprehensive testing suite for the Call Coaching application covering unit tests, integration tests, API tests, and end-to-end tests.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared pytest fixtures
├── mcp/                  # MCP tool unit tests
│   ├── test_analyze_call.py
│   ├── test_search_calls.py
│   └── test_get_rep_insights.py
├── analysis/             # Analysis module tests
│   ├── test_chunking.py
│   ├── test_cache.py
│   └── test_engine.py
├── api/                  # REST API tests
│   └── test_rest_api.py
└── README.md             # This file

e2e/
├── __init__.py
├── conftest.py           # E2E test fixtures
├── test_authentication.py # Auth flow tests
├── test_call_viewer.py   # Call detail page tests
└── test_coaching.py      # Dashboard & coaching tests

scripts/
└── load_test.py          # Load testing with Locust
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -e ".[dev]"
playwright install  # For E2E tests
```

### Unit and Integration Tests

Run all unit tests:

```bash
pytest tests/ -v
```

Run specific test module:

```bash
pytest tests/mcp/test_analyze_call.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Analysis Tests

```bash
pytest tests/analysis/ -v
```

Test chunking:

```bash
pytest tests/analysis/test_chunking.py -v
```

Test caching:

```bash
pytest tests/analysis/test_cache.py -v
```

Test engine:

```bash
pytest tests/analysis/test_engine.py -v
```

### MCP Tool Tests

```bash
pytest tests/mcp/ -v
```

Test analyze_call tool:

```bash
pytest tests/mcp/test_analyze_call.py -v
```

Test search_calls tool:

```bash
pytest tests/mcp/test_search_calls.py -v
```

Test rep insights tool:

```bash
pytest tests/mcp/test_get_rep_insights.py -v
```

### API Tests

```bash
pytest tests/api/ -v
```

Test with FastAPI test client:

```bash
pytest tests/api/test_rest_api.py::TestAnalyzeCallEndpoint -v
```

### End-to-End Tests

E2E tests require a running instance of the application.

Run all E2E tests:

```bash
pytest e2e/ -v -m e2e --base-url http://localhost:3000
```

Run specific E2E test file:

```bash
pytest e2e/test_call_viewer.py -v -m e2e
```

Set test user credentials:

```bash
export TEST_USER_EMAIL="user@example.com"
export TEST_USER_PASSWORD="password"
export TEST_CALL_ID="1234567890"
export TEST_REP_EMAIL="rep@example.com"
pytest e2e/ -v -m e2e
```

### Load Testing

Start the API server first:

```bash
# In one terminal
uvicorn api.rest_server:app --reload
```

Run load test in another terminal:

```bash
cd scripts
python load_test.py
```

Or with locust CLI:

```bash
locust -f scripts/load_test.py --host http://localhost:8000 --users 10 --spawn-rate 2
```

Open web UI at <http://localhost:8089>

Configure load test with environment variables:

```bash
export LOAD_TEST_HOST="http://localhost:8000"
export LOAD_TEST_USERS="50"
export LOAD_TEST_SPAWN_RATE="5"
export LOAD_TEST_DURATION="5m"
python scripts/load_test.py
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation.

- **MCP Tools** (`tests/mcp/`): Tests for analyze_call, search_calls, get_rep_insights
- **Analysis Modules** (`tests/analysis/`): Tests for chunking, caching, engine
- **API Endpoints** (`tests/api/`): Tests for FastAPI REST endpoints

Run unit tests only:

```bash
pytest tests/ -v -m "not integration and not slow"
```

### Integration Tests

Test interactions between components.

Run integration tests:

```bash
pytest tests/ -v -m integration
```

### Slow Tests

Tests that take longer to run (e.g., with external API calls).

Run slow tests:

```bash
pytest tests/ -v -m slow
```

Skip slow tests:

```bash
pytest tests/ -v -m "not slow"
```

### End-to-End Tests

Test complete user flows through the application UI.

Requires:

- Running Next.js frontend at <http://localhost:3000>
- Running FastAPI backend
- Valid test user credentials

Run E2E tests:

```bash
pytest e2e/ -v -m e2e
```

## Fixtures

### Shared Fixtures (conftest.py)

**sample_gong_call**: Sample call metadata

```python
{
    "id": "1234567890",
    "title": "Prefect Discovery Call - Acme Corp",
    "scheduled": "2025-01-15T10:00:00Z",
    "duration": 3600,
    ...
}
```

**sample_transcript**: Sample transcript content

**sample_webhook_payload**: Sample Gong webhook event

### E2E Fixtures (e2e/conftest.py)

**browser**: Playwright browser instance

**context**: Browser context for test isolation

**page**: Browser page instance

**base_url**: Application URL (default: <http://localhost:3000>)

**test_user**: Test user credentials

**sample_call_id**: Call ID for testing

**sample_rep_email**: Rep email for testing

## Mock Objects

The test suite uses `unittest.mock` for mocking dependencies:

```python
from unittest.mock import patch, MagicMock

@patch('coaching_mcp.tools.analyze_call.fetch_one')
def test_analyze_call(mock_fetch):
    mock_fetch.return_value = {'id': 'call-123'}
    # Test code
```

## Coverage Goals

Target >70% coverage across:

- `analysis/` - Core analysis modules
- `coaching_mcp/tools/` - MCP tool implementations
- `api/` - REST API endpoints

Check coverage:

```bash
pytest tests/ --cov --cov-report=term-missing
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:

- Push to main/develop branches
- Pull requests

Run CI tests locally:

```bash
pytest tests/ -v --cov
```

### Coverage Reports

Coverage reports are generated during CI and uploaded to Codecov.

View locally:

```bash
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

## Common Issues

### Async Test Issues

If you see "RuntimeError: Event loop is closed":

```python
# pytest.ini already configured with asyncio_mode = auto
# Ensure pytest-asyncio is installed: pip install pytest-asyncio
```

### Playwright Issues

If Playwright tests fail with "Executable not found":

```bash
playwright install  # Install browser binaries
```

### Import Issues

Tests should auto-discover by having `tests/` directory in project root and `conftest.py` at the right level.

If imports fail:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/ -v
```

### Database Connection

Some tests may need a test database. Configure with:

```bash
export DATABASE_URL="postgresql://user:pass@localhost/call_coach_test"
pytest tests/ -v
```

## Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch
from module_under_test import function_to_test

@pytest.fixture
def sample_data():
    return {"key": "value"}

class TestFunctionToTest:
    def test_basic_behavior(self, sample_data):
        result = function_to_test(sample_data)
        assert result is not None

    @patch('module_under_test.external_dependency')
    def test_with_mocked_dependency(self, mock_dep, sample_data):
        mock_dep.return_value = "mocked"
        result = function_to_test(sample_data)
        assert mock_dep.called
```

### E2E Test Template

```python
import pytest
from playwright.async_api import Page

@pytest.mark.asyncio
class TestFeature:
    async def test_user_flow(self, page: Page, base_url):
        await page.goto(f'{base_url}/path')
        await page.wait_for_selector('text=/expected text/')
        assert '/path' in page.url
```

## Debugging Tests

### Run with verbose output

```bash
pytest tests/ -vv -s  # -s shows print statements
```

### Run with debugger

```bash
pytest tests/ --pdb  # Breaks on failure
```

### Run single test

```bash
pytest tests/mcp/test_analyze_call.py::TestAnalyzeCallTool::test_analyze_call_basic -v
```

### Capture logs

```bash
pytest tests/ --log-cli-level=DEBUG
```

## Performance Testing

### Profile test execution

```bash
pytest tests/ --durations=10  # Show 10 slowest tests
```

### Run subset of tests

```bash
pytest tests/mcp/ -v  # Just MCP tests
```

## Continuous Improvement

Track test improvements:

1. Monitor coverage: `pytest --cov` and review htmlcov/
2. Identify untested code paths
3. Add tests for critical paths
4. Review failing tests in CI
5. Keep tests maintainable and focused
