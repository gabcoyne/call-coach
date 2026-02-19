# Testing Guide

How to run tests and write new tests for Call Coach.

## Running Tests

### Python Tests

**Run all tests**:

```bash
pytest tests/ -v
```

**Run specific test file**:

```bash
pytest tests/test_chunking.py -v
```

**Run specific test**:

```bash
pytest tests/test_chunking.py::test_chunk_transcript -v
```

**Run with coverage**:

```bash
pytest tests/ --cov=coaching_mcp --cov-report=html
# Opens htmlcov/index.html in browser
```

**Run excluding slow tests**:

```bash
pytest tests/ -v -m "not slow"
```

### Frontend Tests

**Run all tests**:

```bash
cd frontend
npm run test
```

**Run in watch mode** (re-runs on file change):

```bash
npm run test:watch
```

**Run with coverage**:

```bash
npm run test:coverage
```

**Run specific test file**:

```bash
npm run test -- SearchPage.test.tsx
```

---

## Test Structure

### Python Test Structure

```
tests/
├── conftest.py              # Fixtures and configuration
├── test_chunking.py         # Transcript chunking tests
├── test_analysis.py         # Analysis engine tests
├── test_cache.py            # Caching logic tests
├── test_database.py         # Database operations tests
├── dlt_tests/               # DLT pipeline tests
│   └── test_bigquery_to_postgres.py
└── fixtures/
    └── sample_transcript.json  # Test data
```

### Frontend Test Structure

```
frontend/
├── __tests__/
│   ├── components/          # Component tests
│   ├── pages/              # Page tests
│   └── lib/                # Utility function tests
└── *.test.tsx              # Inline test files
```

---

## Writing Tests

### Python Test Example

**test_chunking.py**:

```python
import pytest
from analysis.chunking import chunk_transcript, count_tokens

class TestChunking:
    """Test transcript chunking functionality"""

    def test_chunk_short_transcript(self):
        """Should not chunk transcripts under 4K tokens"""
        transcript = "This is a short transcript with just a few words."
        chunks = chunk_transcript(transcript)

        assert len(chunks) == 1
        assert chunks[0]["text"] == transcript

    def test_chunk_long_transcript(self):
        """Should chunk long transcripts into overlapping segments"""
        # Create a long transcript (>4000 tokens)
        transcript = " ".join(["word"] * 5000)
        chunks = chunk_transcript(transcript)

        # Should create multiple chunks
        assert len(chunks) > 1

        # Check overlap (20%)
        for i in range(len(chunks) - 1):
            current_end = chunks[i]["end_token"]
            next_start = chunks[i + 1]["start_token"]
            overlap = current_end - next_start
            assert overlap > 0  # Should have overlap

    @pytest.mark.parametrize("transcript_length", [1000, 5000, 10000])
    def test_chunk_various_lengths(self, transcript_length):
        """Should handle transcripts of various lengths"""
        transcript = " ".join(["word"] * transcript_length)
        chunks = chunk_transcript(transcript)

        assert len(chunks) >= 1
        assert all(c["text"] for c in chunks)  # All chunks have text

    def test_token_counting(self):
        """Should accurately count tokens"""
        text = "Hello world, this is a test."
        tokens = count_tokens(text)

        assert tokens > 0
        assert isinstance(tokens, int)
        assert tokens == 7  # Approximate (tiktoken encoding)
```

**Run tests**:

```bash
pytest tests/test_chunking.py -v
```

### Frontend Test Example

**SearchPage.test.tsx**:

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SearchPage from "@/app/search/page";
import { SWRConfig } from "swr";

describe("SearchPage", () => {
  it("renders search input", () => {
    const mockFetcher = jest.fn();
    render(
      <SWRConfig value={{ fetcher: mockFetcher }}>
        <SearchPage />
      </SWRConfig>
    );

    const input = screen.getByPlaceholderText("Search calls...");
    expect(input).toBeInTheDocument();
  });

  it("calls API on search submission", async () => {
    const mockFetcher = jest.fn().mockResolvedValue({
      results: [
        {
          call_id: "123",
          title: "Acme Corp",
          score: 95,
        },
      ],
    });

    render(
      <SWRConfig value={{ fetcher: mockFetcher }}>
        <SearchPage />
      </SWRConfig>
    );

    const input = screen.getByPlaceholderText("Search calls...");
    fireEvent.change(input, { target: { value: "discovery" } });

    const button = screen.getByText("Search");
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockFetcher).toHaveBeenCalledWith(
        expect.stringContaining("discovery")
      );
    });
  });

  it("displays search results", async () => {
    const mockFetcher = jest.fn().mockResolvedValue({
      results: [
        {
          call_id: "123",
          title: "Acme Corp - Discovery",
          score: 95,
        },
      ],
    });

    render(
      <SWRConfig value={{ fetcher: mockFetcher }}>
        <SearchPage />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.getByText("Acme Corp - Discovery")).toBeInTheDocument();
      expect(screen.getByText("95")).toBeInTheDocument();
    });
  });
});
```

**Run tests**:

```bash
npm run test -- SearchPage.test.tsx
```

---

## Test Markers

### Python Test Markers

```python
@pytest.mark.integration  # Integration test (requires external services)
@pytest.mark.slow        # Slow test (takes >5 seconds)
@pytest.mark.asyncio     # Async test
@pytest.mark.e2e         # End-to-end test
```

**Run only unit tests** (no external dependencies):

```bash
pytest tests/ -v -m "not integration and not slow"
```

**Run only integration tests**:

```bash
pytest tests/ -v -m "integration"
```

---

## Mocking & Fixtures

### Python Fixtures

**conftest.py**:

```python
import pytest
from unittest.mock import Mock, patch
from db.models import Call

@pytest.fixture
def sample_call():
    """Sample call for testing"""
    return Call(
        id="test-call-123",
        gong_call_id="1464927526043145564",
        title="Test Call",
        duration_seconds=1800,
        created_at="2026-02-05T12:00:00Z",
    )

@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    with patch("db.connection.get_db_connection") as mock:
        conn = Mock()
        conn.cursor.return_value.__enter__.return_value = Mock()
        mock.return_value.__enter__.return_value = conn
        yield mock

def test_with_fixtures(sample_call, mock_db_connection):
    """Test using fixtures"""
    assert sample_call.title == "Test Call"
    assert mock_db_connection.called
```

### Frontend Mocks

**test-utils.tsx**:

```typescript
import { render } from "@testing-library/react";
import { SWRConfig } from "swr";

export const renderWithMocks = (component: React.ReactNode) => {
  const mockFetcher = jest.fn();

  return render(
    <SWRConfig value={{ fetcher: mockFetcher }}>
      {component}
    </SWRConfig>
  );
};

// Usage
it("renders dashboard", () => {
  renderWithMocks(<Dashboard />);
  expect(screen.getByText("Performance")).toBeInTheDocument();
});
```

---

## Coverage Goals

### Python

**Target**: 80%+ coverage

**Current**: Check with:

```bash
pytest --cov=coaching_mcp --cov-report=term-missing

# Or HTML report:
pytest --cov=coaching_mcp --cov-report=html
open htmlcov/index.html
```

**Low coverage areas**:

- Error handling
- Edge cases
- Integration with external services

### Frontend

**Target**: 70%+ coverage

**Check coverage**:

```bash
npm run test:coverage

# View report:
cd frontend
open coverage/lcov-report/index.html
```

---

## CI/CD Integration

### GitHub Actions

**.github/workflows/tests.yml**:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"

      - name: Run Python tests
        run: pytest tests/ -v --cov=coaching_mcp

      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 20

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm install

      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

**Push code to enable CI**:

```bash
git push origin feature-branch

# Tests run automatically on GitHub Actions
# Check results in PR
```

---

## Test Data

### Using Test Fixtures

**fixtures/sample_transcript.json**:

```json
{
  "call_id": "1464927526043145564",
  "transcript": [
    {
      "speaker": "Rep",
      "text": "Hi, thanks for taking the time to chat today."
    },
    {
      "speaker": "Customer",
      "text": "Happy to, what can you tell me about your product?"
    }
  ]
}
```

**Load in tests**:

```python
import json

@pytest.fixture
def sample_transcript():
    with open("tests/fixtures/sample_transcript.json") as f:
        return json.load(f)

def test_analysis(sample_transcript):
    # Use sample transcript
    result = analyze(sample_transcript)
    assert result["score"] > 0
```

---

## Performance Testing

### Load Testing

**Install Locust**:

```bash
pip install locust
```

**tests/load_test.py**:

```python
from locust import HttpUser, task, between

class AnalysisUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def analyze_call(self):
        self.client.post(
            "/coaching/analyze-call",
            json={"gong_call_id": "1464927526043145564"}
        )
```

**Run load test**:

```bash
locust -f tests/load_test.py --host http://localhost:8001
# Visit http://localhost:8089 to start test
```

---

## Troubleshooting Tests

### "Database connection failed"

**Cause**: Test database not configured

**Solution**:

```bash
# Create test database
psql $DATABASE_URL -c "CREATE DATABASE callcoach_test"

# Run migrations for test DB
export TEST_DATABASE_URL=postgresql://...?sslmode=require
psql $TEST_DATABASE_URL -f db/migrations/001_initial_schema.sql

# Run tests
pytest tests/
```

### "Test timeout"

**Cause**: Test taking too long

**Solution**:

```bash
# Add timeout to pytest.ini
[pytest]
timeout = 10  # seconds

# Or run without slow tests
pytest tests/ -v -m "not slow"
```

### "Flaky test (sometimes passes, sometimes fails)"

**Cause**: Timing or randomness issue

**Solution**:

```python
# Add explicit waits
import time

def test_async_operation():
    result = start_operation()
    time.sleep(0.5)  # Wait for completion
    assert result.is_complete()

# Or use pytest-asyncio
@pytest.mark.asyncio
async def test_async():
    result = await async_operation()
    assert result
```

---

## Best Practices

1. **Test one thing**: Each test should verify one behavior
2. **Use descriptive names**: `test_analyzes_discovery_correctly`
3. **Arrange-Act-Assert**: Setup, execute, verify
4. **Mock external services**: Don't call real APIs in tests
5. **Keep tests fast**: <1 second per test
6. **Test edge cases**: Empty input, large input, errors
7. **Use fixtures**: Reuse common setup
8. **Document why**: Comments explain intent, not code

---

## Next Steps

1. Run existing tests: `pytest tests/ -v`
2. Write test for new feature
3. Verify coverage: `pytest --cov=coaching_mcp`
4. Check CI passes before merging PR

---

**Questions?** See [Troubleshooting Guide](../troubleshooting/README.md) or check test examples in the codebase.
