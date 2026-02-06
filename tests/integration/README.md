# Backend Integration Tests

Integration tests for the Call Coach backend API and database. These tests verify end-to-end behavior with a real PostgreSQL database.

## What These Tests Cover

### API Integration Tests (`test_api_integration.py`)

Tests REST API endpoints with real database connections:

- **Task 7.1**: `test_post_creates_record` - Verifies POST requests create database records with correct values
- **Task 7.2**: `test_get_retrieves_record` - Verifies GET requests retrieve complete record data from database
- **Task 7.3**: `test_auth_required` - Verifies authentication enforcement on protected endpoints

### Database Integration Tests (`test_database_integration.py`)

Tests database operations and connection pool behavior:

- **Task 7.4**: `test_transaction_commit` - Verifies records inserted in transactions are committed and queryable
- **Task 7.5**: `test_transaction_rollback` - Verifies exceptions during transactions trigger rollback
- **Task 7.6**: `test_connection_pool_load` - Verifies connection pool handles 50 concurrent queries without errors

## Prerequisites

### 1. Test Database Setup

Integration tests require a separate PostgreSQL database for testing. You have two options:

#### Option A: Local PostgreSQL

Install and configure a local PostgreSQL instance:

```bash
# Create test database
createdb call_coach_test

# Run migrations
psql call_coach_test < db/migrations/001_initial_schema.sql
psql call_coach_test < db/migrations/002_gong_api_v2_updates.sql
```

#### Option B: Docker Compose (Recommended)

Use Docker Compose to run a test database:

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run migrations
docker-compose -f docker-compose.test.yml exec postgres psql -U postgres -d call_coach_test -f /migrations/001_initial_schema.sql
```

### 2. Environment Configuration

Set the test database URL:

```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/call_coach_test"
```

Or add to `.env.test`:

```
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/call_coach_test
```

## Running the Tests

### Run All Integration Tests

```bash
pytest tests/integration/ -v
```

### Run API Integration Tests Only

```bash
pytest tests/integration/test_api_integration.py -v
```

### Run Database Integration Tests Only

```bash
pytest tests/integration/test_database_integration.py -v
```

### Run Specific Test

```bash
pytest tests/integration/test_database_integration.py::TestConnectionPoolLoad::test_connection_pool_load -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=db --cov=api --cov-report=html
```

### Skip Integration Tests

Integration tests are marked with `@pytest.mark.integration`. To skip them:

```bash
pytest -m "not integration"
```

## Test Markers

- `@pytest.mark.integration` - Integration tests requiring database
- `@pytest.mark.slow` - Slow-running tests (e.g., connection pool load tests)

Run only fast integration tests:

```bash
pytest tests/integration/ -m "integration and not slow"
```

## Test Isolation

Each test uses the `cleanup_test_data` fixture to track and clean up any data it creates. This ensures:

- Tests don't interfere with each other
- Test database stays clean
- Tests can run in any order

## Continuous Integration

Integration tests run in CI when:

- Pull requests are opened
- Commits are pushed to main/develop branches
- Manual workflow dispatch

CI uses a PostgreSQL service container with the test database pre-configured.

## Troubleshooting

### Tests Skip with "Test database not available"

The test database is not accessible. Check:

1. PostgreSQL is running: `pg_isready`
2. Database exists: `psql -l | grep call_coach_test`
3. Connection string is correct: `echo $TEST_DATABASE_URL`

### Tests Skip with "Test database schema not initialized"

Database exists but schema is missing. Run migrations:

```bash
psql $TEST_DATABASE_URL < db/migrations/001_initial_schema.sql
psql $TEST_DATABASE_URL < db/migrations/002_gong_api_v2_updates.sql
```

### Connection Pool Errors

If you see connection pool errors:

1. Check max connections: `psql -c "SHOW max_connections;"`
2. Reduce concurrent test workers: `pytest -n 2` instead of `-n auto`
3. Increase database max_connections in postgresql.conf

### Cleanup Failures

If cleanup fails (e.g., foreign key violations), check:

1. Test is adding records to `cleanup_test_data` in correct order
2. Foreign key constraints are defined correctly
3. Manual cleanup: `TRUNCATE calls, speakers, transcripts, analyses CASCADE;`

## Best Practices

### Writing New Integration Tests

1. **Use cleanup_test_data fixture**: Always track created records for cleanup
2. **Test real behavior**: Don't mock database calls in integration tests
3. **Verify database state**: Check records exist/don't exist in database
4. **Use unique test data**: Generate UUIDs to avoid conflicts
5. **Handle cleanup failures gracefully**: Log warnings, don't fail tests

### Example Test Pattern

```python
@pytest.mark.integration
def test_my_feature(setup_test_db, cleanup_test_data):
    """Test description."""
    # Create test data
    test_id = uuid.uuid4()
    execute_query("INSERT INTO table...", (test_id,))
    cleanup_test_data.append(("table", str(test_id)))

    # Test behavior
    result = my_function(test_id)

    # Verify results
    assert result is not None

    # Verify database state
    db_record = fetch_one("SELECT * FROM table WHERE id = %s", (test_id,))
    assert db_record["field"] == "expected_value"
```

## Related Documentation

- [Backend Unit Tests](../README.md#backend-unit-tests)
- [Database Schema](../../db/README.md)
- [API Documentation](../../api/README.md)
- [Testing Guide](../../docs/testing-guide.md)
