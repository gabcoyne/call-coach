# Testing Guide for Call Coaching Application

Comprehensive guide for running, writing, and maintaining tests for the Call Coaching application.

## Quick Start

### Install Test Dependencies

```bash
# Install all dev dependencies including testing tools
pip install -e ".[dev]"

# For E2E tests, install browser binaries
playwright install

# For load testing
pip install locust
```

### Run Tests

```bash
# Run all unit tests (default)
./scripts/run_tests.sh

# Run specific test suite
./scripts/run_tests.sh mcp          # MCP tools
./scripts/run_tests.sh analysis     # Analysis modules
./scripts/run_tests.sh api          # API endpoints
./scripts/run_tests.sh e2e          # End-to-end tests
./scripts/run_tests.sh load         # Load testing

# With coverage report
./scripts/run_tests.sh unit --coverage

# Verbose output
./scripts/run_tests.sh unit --verbose
```

## Test Organization

### Unit Tests (`tests/`)

Test individual components in isolation using mocks.

**Location**: `tests/mcp/`, `tests/analysis/`, `tests/api/`

**Run**: `pytest tests/ -v`

**Coverage**: >70% target for all modules

**Example**:

```python
def test_analyze_call_basic(mock_settings, mock_db):
    result = analyze_call_tool(call_id='test-123')
    assert result is not None
```

### Integration Tests (`tests/`)

Test interactions between components (marked with `@pytest.mark.integration`)

**Run**: `pytest tests/ -v -m integration`

**Example**:

```python
@pytest.mark.integration
def test_analysis_pipeline():
    # Test full analysis flow
    pass
```

### End-to-End Tests (`e2e/`)

Test complete user workflows through the UI with Playwright.

**Requirements**:

- Running frontend at <http://localhost:3000>
- Running backend API
- Valid test user credentials

**Run**:

```bash
export BASE_URL=http://localhost:3000
export TEST_USER_EMAIL=user@example.com
export TEST_USER_PASSWORD=password
pytest e2e/ -v -m e2e
```

**Example**:

```python
@pytest.mark.asyncio
async def test_login_flow(page: Page, base_url):
    await page.goto(f'{base_url}/sign-in')
    # ... test steps
```

### Load Tests (`scripts/load_test.py`)

Test API performance under load with Locust.

**Requirements**: Running API on <http://localhost:8000>

**Run**:

```bash
python scripts/load_test.py
# Opens http://localhost:8089 for web UI
```

**Configure**:

```bash
export LOAD_TEST_USERS=50
export LOAD_TEST_SPAWN_RATE=5
export LOAD_TEST_DURATION=10m
python scripts/load_test.py
```

## Writing Tests

### Test File Structure

```python
"""Module description."""
import pytest
from unittest.mock import patch
from module_under_test import function

# Fixtures
@pytest.fixture
def sample_data():
    return {"key": "value"}

# Test class
class TestFunctionName:
    """Test suite for function_name."""

    def test_basic_behavior(self, sample_data):
        """Test basic functionality."""
        result = function(sample_data)
        assert result is not None

    @pytest.mark.integration
    def test_with_integration(self):
        """Test with external dependencies."""
        pass
```

### Fixtures

Use fixtures for test data and mocks:

```python
@pytest.fixture
def mock_call_data(mock_call_data):  # From fixtures.py
    """Customize call data."""
    data = mock_call_data.copy()
    data['title'] = 'Custom Title'
    return data

def test_with_fixture(mock_call_data):
    """Test using fixture."""
    assert mock_call_data['title'] == 'Custom Title'
```

### Mocking

Mock external dependencies:

```python
from unittest.mock import patch, MagicMock

@patch('module.external_function')
def test_with_mock(mock_func):
    mock_func.return_value = 'mocked'
    # Test code
    assert mock_func.called
```

### Async Tests

Write async tests with `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Parametrized Tests

Test multiple inputs:

```python
@pytest.mark.parametrize('input,expected', [
    ('a', 1),
    ('b', 2),
])
def test_multiple_inputs(input, expected):
    assert process(input) == expected
```

## Coverage

### Check Coverage

```bash
# Generate HTML report
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals

- **Target**: >70% overall coverage
- **Focus areas**:
  - `analysis/` - Core analysis logic
  - `coaching_mcp/tools/` - MCP tool implementations
  - `api/` - REST API endpoints

### Improve Coverage

1. Identify uncovered lines: `pytest --cov-report=term-missing`
2. Add tests for critical paths
3. Use fixtures to reduce test boilerplate
4. Test error conditions and edge cases

## Debugging

### Run with Debug Output

```bash
# Show print statements
pytest tests/ -s

# Verbose output
pytest tests/ -vv

# Show all logging
pytest tests/ --log-cli-level=DEBUG
```

### Break on Failure

```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Drop into debugger on error
pytest tests/ --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Run Single Test

```bash
# By test name
pytest tests/mcp/test_analyze_call.py::TestAnalyzeCallTool::test_analyze_call_basic

# By pattern
pytest tests/ -k "analyze_call"

# By marker
pytest tests/ -m integration
```

### Performance Analysis

```bash
# Show slowest tests
pytest tests/ --durations=10

# Profile execution
pytest tests/ --profile
```

## Best Practices

### 1. Keep Tests Focused

```python
# Good: Single assertion
def test_analyze_call_returns_scores():
    result = analyze_call('call-123')
    assert 'scores' in result

# Avoid: Multiple unrelated assertions
def test_analyze_call():
    result = analyze_call('call-123')
    assert 'scores' in result
    assert result['rep'] is not None
    assert 'analysis' in result
```

### 2. Use Descriptive Names

```python
# Good
def test_analyze_call_with_invalid_call_id_returns_error()

# Avoid
def test_analyze_call()
```

### 3. Organize with Test Classes

```python
class TestAnalyzeCall:
    """Group related tests."""

    def test_basic(self): pass
    def test_with_cache(self): pass
    def test_error_handling(self): pass
```

### 4. Test Behavior, Not Implementation

```python
# Good: Test what it does
assert len(chunks) > 0
assert all(len(c) <= max_tokens for c in chunks)

# Avoid: Test how it does it
assert 'split' in function_source_code
```

### 5. Mock External Dependencies

```python
# Good: Mock external API
@patch('module.external_api')
def test_function(mock_api):
    mock_api.return_value = {'data': 'mocked'}

# Avoid: Actually calling external API
def test_function():
    result = external_api.call()  # Real API call!
```

### 6. Use Fixtures for Setup

```python
# Good
@pytest.fixture
def sample_call(mock_call_data):
    return mock_call_data

def test_with_fixture(sample_call):
    assert sample_call is not None

# Avoid
def test_setup_everything():
    call = create_call()
    transcript = create_transcript()
    # ...
```

## Common Issues

### Import Errors

If tests can't import your modules:

```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Async Issues

If you see "RuntimeError: Event loop is closed":

```bash
# Ensure asyncio_mode is set in pytest.ini
# Already configured in this project
pytest tests/
```

### Database Errors

For tests needing database:

```bash
# Use test database
export DATABASE_URL="postgresql://user:pass@localhost/call_coach_test"
pytest tests/
```

### Playwright Issues

If E2E tests fail with browser errors:

```bash
# Reinstall browser binaries
playwright install --with-deps

# Run E2E tests with trace for debugging
pytest e2e/ --trace on
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:

- Push to main/develop
- Pull requests

View results:

1. Go to GitHub repo
2. Click "Actions" tab
3. View workflow runs

### Local CI Simulation

Run the same tests as CI locally:

```bash
# Python tests
pytest tests/ -v --cov

# Frontend tests
cd frontend && npm test

# E2E tests (requires running servers)
pytest e2e/ -v -m e2e
```

## Maintenance

### Update Tests for Code Changes

When you modify code:

1. Run affected tests: `pytest tests/module/ -v`
2. Update test expectations if behavior changed
3. Add new tests for new functionality
4. Check coverage: `pytest --cov`

### Slow Tests

Mark slow tests:

```python
@pytest.mark.slow
def test_slow_analysis():
    # Takes 10+ seconds
    pass

# Skip slow tests in quick runs
pytest tests/ -m "not slow"
```

### Skip Tests Temporarily

```python
@pytest.mark.skip(reason="Not ready yet")
def test_future_feature():
    pass

# Or skip during test run
pytest tests/ -k "not future"
```

## Advanced Testing

### Test Multiple Python Versions

```bash
# Test with multiple Python versions
tox -e py311 -e py312

# Or manually
for version in 3.11 3.12; do
    python$version -m pytest tests/
done
```

### Generate Test Report

```bash
# HTML report with details
pytest tests/ --html=report.html --self-contained-html

# JUnit XML for CI integration
pytest tests/ --junit-xml=results.xml
```

### Benchmark Tests

```python
def test_chunking_performance(benchmark):
    result = benchmark(chunk_transcript, large_transcript)
    assert len(result) > 0
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Playwright Documentation](https://playwright.dev/python/)
- [Locust Documentation](https://docs.locust.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

## Support

For test-related issues:

1. Check this guide and test README
2. Review similar test files for patterns
3. Check existing fixtures in `tests/fixtures.py`
4. Run with `--verbose` and `--log-cli-level=DEBUG`
5. Use debugger with `--pdb`
