"""
Test fixtures for database connections and cleanup.

Provides fixtures for test database setup, cleanup, and transaction management.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import psycopg2
import pytest
import pytest_asyncio
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Test database configuration
TEST_DB_CONFIG = {
    "host": os.getenv("TEST_DB_HOST", "localhost"),
    "port": int(os.getenv("TEST_DB_PORT", "5433")),
    "user": os.getenv("TEST_DB_USER", "test_user"),
    "password": os.getenv("TEST_DB_PASSWORD", "test_password"),
    "database": os.getenv("TEST_DB_NAME", "call_coach_test"),
}


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_config() -> dict:
    """Provide test database configuration."""
    return TEST_DB_CONFIG.copy()


@pytest.fixture(scope="session")
def db_connection_sync(test_db_config: dict) -> Generator:
    """
    Provide a synchronous database connection for session-level operations.

    This fixture creates tables before tests and can be used for cleanup.
    """
    conn = psycopg2.connect(**test_db_config)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Create tables (if schema file exists)
    cursor = conn.cursor()
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "schema.sql"
    )

    if os.path.exists(schema_file):
        with open(schema_file) as f:
            cursor.execute(f.read())

    yield conn

    # Cleanup: drop all tables
    cursor.execute(
        """
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """
    )

    cursor.close()
    conn.close()


@pytest_asyncio.fixture
async def db_connection(test_db_config: dict) -> AsyncGenerator:
    """
    Provide an async database connection for tests.

    Each test gets a fresh connection that is closed after the test completes.
    """
    try:
        import asyncpg

        conn = await asyncpg.connect(
            host=test_db_config["host"],
            port=test_db_config["port"],
            user=test_db_config["user"],
            password=test_db_config["password"],
            database=test_db_config["database"],
        )

        yield conn

    finally:
        await conn.close()


@pytest_asyncio.fixture
async def db_transaction(db_connection) -> AsyncGenerator:
    """
    Provide a database transaction that is rolled back after each test.

    This ensures test isolation - changes made during a test are not persisted.
    """
    transaction = db_connection.transaction()
    await transaction.start()

    try:
        yield db_connection
    finally:
        await transaction.rollback()


@pytest.fixture
def clean_database(db_connection_sync):
    """
    Clean all data from database tables while preserving schema.

    Use this fixture when you need a completely clean database state.
    """
    cursor = db_connection_sync.cursor()

    # Get all table names
    cursor.execute(
        """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """
    )

    tables = [row[0] for row in cursor.fetchall()]

    # Truncate all tables
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} CASCADE")

    cursor.close()

    yield

    # Cleanup after test
    cursor = db_connection_sync.cursor()
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
    cursor.close()


@pytest_asyncio.fixture
async def redis_client():
    """
    Provide a Redis client for cache tests.

    Flushes the test database before and after each test.
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis(
            host=os.getenv("TEST_REDIS_HOST", "localhost"),
            port=int(os.getenv("TEST_REDIS_PORT", "6380")),
            db=0,
            decode_responses=True,
        )

        # Flush before test
        await client.flushdb()

        yield client

        # Flush after test
        await client.flushdb()
        await client.close()

    except ImportError:
        pytest.skip("redis package not installed")
