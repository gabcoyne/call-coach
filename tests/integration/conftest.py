"""
Shared fixtures for integration tests.

Provides database connection management, test data factories,
and cleanup utilities for integration testing.
"""

import os
from unittest.mock import patch

import pytest

from db.connection import get_db_connection


@pytest.fixture(scope="session")
def test_database_url():
    """
    Get test database URL from environment.

    Uses TEST_DATABASE_URL environment variable if set,
    otherwise falls back to local test database.

    To use a separate test database:
        export TEST_DATABASE_URL="postgresql://user:pass@host:port/test_db"
    """
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/call_coach_test",
    )


@pytest.fixture(scope="session")
def test_database_available(test_database_url):
    """
    Check if test database is available and skip tests if not.

    This prevents integration tests from failing when database
    is not configured (e.g., in CI without Docker).
    """
    try:
        with patch("coaching_mcp.shared.config.settings.database_url", test_database_url):
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    assert result[0] == 1
        return True
    except Exception as e:
        pytest.skip(f"Test database not available: {e}")


@pytest.fixture(scope="session", autouse=True)
def verify_test_database_schema(test_database_available, test_database_url):
    """
    Verify test database has required schema before running tests.

    Checks that all required tables exist. If not, provides helpful
    error message about running migrations.
    """
    required_tables = ["calls", "speakers", "transcripts", "analyses"]

    with patch("coaching_mcp.shared.config.settings.database_url", test_database_url):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = ANY(%s)
                    """,
                    (required_tables,),
                )
                existing_tables = {row[0] for row in cur.fetchall()}

    missing_tables = set(required_tables) - existing_tables
    if missing_tables:
        pytest.skip(
            f"Test database missing required tables: {missing_tables}. "
            f"Run database migrations before integration tests."
        )


@pytest.fixture(scope="function")
def isolated_database_session(test_database_url):
    """
    Provide isolated database session that rolls back after test.

    Uses savepoint/rollback to ensure test isolation without
    affecting other tests. Useful for tests that modify data.

    Note: Not used by default to allow tests to verify actual
    commit/rollback behavior. Use explicitly when needed.
    """
    with patch("coaching_mcp.shared.config.settings.database_url", test_database_url):
        with get_db_connection() as conn:
            # Start savepoint
            with conn.cursor() as cur:
                cur.execute("SAVEPOINT test_isolation")

            yield conn

            # Rollback to savepoint
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT test_isolation")
