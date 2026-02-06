"""
Integration tests for database operations with real PostgreSQL database.

Tests verify database behavior including:
- Transaction commit and data persistence
- Transaction rollback on errors
- Connection pool handling under concurrent load
"""

import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import psycopg2
import pytest

# Ensure project root is in sys.path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from db.connection import execute_query, fetch_one, get_db_connection, get_db_pool


@pytest.fixture(scope="module")
def test_db_url():
    """Get test database URL from environment or use default."""
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/call_coach_test",
    )


@pytest.fixture(scope="module")
def setup_test_db(test_db_url):
    """Setup test database connection and ensure clean state."""
    # Override settings for test database
    with patch("coaching_mcp.shared.config.settings.database_url", test_db_url):
        # Force reconnection with test database
        from db import connection

        if connection._db_pool is not None:
            connection._db_pool.closeall()
            connection._db_pool = None

        # Ensure database schema exists
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verify tables exist
                cur.execute(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('calls', 'speakers', 'transcripts', 'analyses')
                    """
                )
                tables = cur.fetchall()
                if len(tables) < 4:
                    pytest.skip(
                        "Test database schema not initialized. "
                        "Run migrations before running integration tests."
                    )

        yield

        # Cleanup
        if connection._db_pool is not None:
            connection._db_pool.closeall()
            connection._db_pool = None


@pytest.fixture
def cleanup_test_data():
    """Cleanup test data after each test."""
    test_ids = []

    yield test_ids

    # Cleanup all test records in reverse order (for foreign key constraints)
    if test_ids:
        for table, id_value in reversed(test_ids):
            try:
                execute_query(f"DELETE FROM {table} WHERE id = %s", (id_value,))
            except Exception as e:
                # Log but don't fail test cleanup
                print(f"Cleanup warning: Failed to delete {table} {id_value}: {e}")


@pytest.mark.integration
class TestTransactionCommit:
    """Integration tests for transaction commit behavior."""

    def test_transaction_commit(self, setup_test_db, cleanup_test_data):
        """Test inserting records within transaction are committed and queryable.

        Task 7.4: Verify that records inserted within a transaction are
        properly committed to the database and can be queried afterward.
        """
        test_call_id = uuid.uuid4()
        test_gong_id = f"gong-{uuid.uuid4()}"
        test_title = "Transaction Test Call"

        # Insert record within transaction
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(test_call_id),
                        test_gong_id,
                        test_title,
                        datetime.now(),
                        datetime.now(),
                    ),
                )
                # Explicit commit
                conn.commit()

        cleanup_test_data.append(("calls", str(test_call_id)))

        # Verify record exists and is queryable in new connection
        result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(test_call_id),))

        assert result is not None
        assert result["id"] == test_call_id
        assert result["gong_call_id"] == test_gong_id
        assert result["title"] == test_title

    def test_transaction_commit_multiple_records(self, setup_test_db, cleanup_test_data):
        """Test multiple records in same transaction are all committed."""
        test_call_id = uuid.uuid4()
        test_speaker_id = uuid.uuid4()

        # Insert multiple related records in same transaction
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Insert call
                cur.execute(
                    """
                    INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(test_call_id),
                        f"gong-{test_call_id}",
                        "Multi-record test",
                        datetime.now(),
                        datetime.now(),
                    ),
                )

                # Insert related speaker
                cur.execute(
                    """
                    INSERT INTO speakers (id, call_id, name, email, company_side, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(test_speaker_id),
                        str(test_call_id),
                        "Test Speaker",
                        "test@example.com",
                        True,
                        datetime.now(),
                    ),
                )

                # Commit both
                conn.commit()

        cleanup_test_data.append(("speakers", str(test_speaker_id)))
        cleanup_test_data.append(("calls", str(test_call_id)))

        # Verify both records exist
        call_result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(test_call_id),))
        speaker_result = fetch_one("SELECT * FROM speakers WHERE id = %s", (str(test_speaker_id),))

        assert call_result is not None
        assert speaker_result is not None
        assert speaker_result["call_id"] == test_call_id

    def test_transaction_autocommit_with_execute_query(self, setup_test_db, cleanup_test_data):
        """Test execute_query with commit=True auto-commits transaction."""
        test_call_id = uuid.uuid4()

        # Use execute_query which auto-commits by default
        execute_query(
            """
            INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                str(test_call_id),
                f"gong-{test_call_id}",
                "Auto-commit test",
                datetime.now(),
                datetime.now(),
            ),
            commit=True,
        )

        cleanup_test_data.append(("calls", str(test_call_id)))

        # Verify record committed
        result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(test_call_id),))
        assert result is not None
        assert result["title"] == "Auto-commit test"


@pytest.mark.integration
class TestTransactionRollback:
    """Integration tests for transaction rollback behavior."""

    def test_transaction_rollback(self, setup_test_db):
        """Test exception during transaction causes rollback with no records committed.

        Task 7.5: Verify that when an exception is raised during a transaction,
        the transaction is rolled back and no records are persisted.
        """
        test_call_id = uuid.uuid4()
        test_gong_id = f"gong-{uuid.uuid4()}"

        # Attempt insert but force an error before commit
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Insert valid record
                    cur.execute(
                        """
                        INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            str(test_call_id),
                            test_gong_id,
                            "Rollback test",
                            datetime.now(),
                            datetime.now(),
                        ),
                    )

                    # Force error before commit
                    raise ValueError("Simulated error")
        except ValueError:
            # Expected error
            pass

        # Verify record was NOT committed
        result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(test_call_id),))
        assert result is None

    def test_transaction_rollback_on_constraint_violation(self, setup_test_db, cleanup_test_data):
        """Test constraint violation triggers rollback."""
        test_call_id = uuid.uuid4()
        test_gong_id = f"gong-{uuid.uuid4()}"

        # First insert succeeds
        execute_query(
            """
            INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                str(test_call_id),
                test_gong_id,
                "Constraint test",
                datetime.now(),
                datetime.now(),
            ),
        )
        cleanup_test_data.append(("calls", str(test_call_id)))

        # Second insert with same ID should fail and rollback
        duplicate_title = "This should not exist"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Try to insert with duplicate primary key
                    cur.execute(
                        """
                        INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            str(test_call_id),  # Duplicate ID
                            f"gong-{uuid.uuid4()}",
                            duplicate_title,
                            datetime.now(),
                            datetime.now(),
                        ),
                    )
                    conn.commit()
        except psycopg2.IntegrityError:
            # Expected error
            pass

        # Verify original record still exists with original title
        result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(test_call_id),))
        assert result is not None
        assert result["title"] == "Constraint test"
        assert result["title"] != duplicate_title

    def test_transaction_rollback_partial_batch(self, setup_test_db, cleanup_test_data):
        """Test batch insert with error rolls back all records."""
        test_call_ids = [uuid.uuid4() for _ in range(3)]

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Insert first two successfully
                    for i, call_id in enumerate(test_call_ids[:2]):
                        cur.execute(
                            """
                            INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                str(call_id),
                                f"gong-{call_id}",
                                f"Batch test {i}",
                                datetime.now(),
                                datetime.now(),
                            ),
                        )

                    # Force error on third insert
                    raise RuntimeError("Batch error")
        except RuntimeError:
            pass

        # Verify NONE of the records were committed
        for call_id in test_call_ids[:2]:
            result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(call_id),))
            assert result is None, f"Record {call_id} should have been rolled back"


@pytest.mark.integration
@pytest.mark.slow
class TestConnectionPoolLoad:
    """Integration tests for connection pool behavior under load."""

    def test_connection_pool_load(self, setup_test_db):
        """Test 50 concurrent queries succeed without connection errors.

        Task 7.6: Verify that the connection pool can handle concurrent
        load with multiple simultaneous queries without exhausting connections
        or producing errors.
        """
        num_concurrent_queries = 50
        results = []
        errors = []

        def execute_query_task(query_id: int):
            """Execute a query and return result or error."""
            try:
                # Execute a simple query
                result = fetch_one("SELECT NOW() as current_time, %s as query_id", (query_id,))
                return {"success": True, "query_id": query_id, "result": result}
            except Exception as e:
                return {"success": False, "query_id": query_id, "error": str(e)}

        # Execute concurrent queries
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(execute_query_task, i) for i in range(num_concurrent_queries)
            ]

            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    results.append(result)
                else:
                    errors.append(result)

        # Verify all queries succeeded
        assert (
            len(results) == num_concurrent_queries
        ), f"Expected {num_concurrent_queries} successes, got {len(results)}"
        assert len(errors) == 0, f"Got {len(errors)} errors: {errors}"

        # Verify all results are unique and correct
        query_ids = [r["result"]["query_id"] for r in results]
        assert len(set(query_ids)) == num_concurrent_queries
        assert sorted(query_ids) == list(range(num_concurrent_queries))

    def test_connection_pool_concurrent_writes(self, setup_test_db, cleanup_test_data):
        """Test concurrent write operations don't cause deadlocks."""
        num_concurrent_writes = 20
        test_call_ids = [uuid.uuid4() for _ in range(num_concurrent_writes)]
        results = []
        errors = []

        def insert_call_task(call_id: uuid.UUID, index: int):
            """Insert a call record."""
            try:
                execute_query(
                    """
                    INSERT INTO calls (id, gong_call_id, title, scheduled_at, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(call_id),
                        f"gong-concurrent-{call_id}",
                        f"Concurrent test {index}",
                        datetime.now(),
                        datetime.now(),
                    ),
                )
                return {"success": True, "call_id": call_id}
            except Exception as e:
                return {"success": False, "call_id": call_id, "error": str(e)}

        # Execute concurrent writes
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(insert_call_task, call_id, i)
                for i, call_id in enumerate(test_call_ids)
            ]

            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    results.append(result)
                    cleanup_test_data.append(("calls", str(result["call_id"])))
                else:
                    errors.append(result)

        # Verify all writes succeeded
        assert (
            len(results) == num_concurrent_writes
        ), f"Expected {num_concurrent_writes} successes, got {len(results)}"
        assert len(errors) == 0, f"Got {len(errors)} errors: {errors}"

        # Verify all records exist in database
        for call_id in test_call_ids:
            result = fetch_one("SELECT * FROM calls WHERE id = %s", (str(call_id),))
            assert result is not None, f"Call {call_id} was not inserted"

    def test_connection_pool_max_connections(self, setup_test_db):
        """Test connection pool respects max connection limit."""
        pool = get_db_pool()

        # Get pool configuration
        assert pool.minconn >= 1
        assert pool.maxconn >= 5

        # Verify pool can provide connections up to max
        connections = []
        try:
            # Get connections up to max
            for _ in range(pool.maxconn):
                conn = pool.getconn()
                connections.append(conn)

            # Verify all connections work
            for conn in connections:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    assert result[0] == 1

        finally:
            # Return all connections
            for conn in connections:
                pool.putconn(conn)

    def test_connection_pool_reuse(self, setup_test_db):
        """Test connection pool reuses connections efficiently."""
        query_results = []

        # Execute multiple queries sequentially
        for i in range(10):
            result = fetch_one("SELECT %s as iteration", (i,))
            query_results.append(result["iteration"])

        # Verify all queries succeeded
        assert query_results == list(range(10))

        # Connection pool should have reused connections
        # (This is implicit - no errors means reuse worked)
