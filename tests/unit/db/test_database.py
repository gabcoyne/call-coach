"""
Unit tests for database connection module.

Tests cover:
- Connection pool initialization
- Parameterized query execution
- Transaction rollback on error
- Connection timeout and retry handling
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from psycopg2 import DatabaseError, InterfaceError, OperationalError

from db.connection import (
    close_db_pool,
    execute_many,
    execute_query,
    fetch_all,
    fetch_one,
    get_db_connection,
    get_db_pool,
)


@pytest.fixture(autouse=True)
def reset_db_pool():
    """Reset the global database pool before each test."""
    import db.connection as db_conn

    db_conn._db_pool = None
    yield
    db_conn._db_pool = None


class TestConnectionPoolInit:
    """Test 4.1: Connection pool initialization."""

    @patch("db.connection.settings")
    @patch("db.connection.pool.ThreadedConnectionPool")
    def test_connection_pool_init_success(self, mock_pool_class, mock_settings):
        """Test successful connection pool initialization with correct parameters."""
        # Arrange
        mock_settings.database_url = "postgresql://user:pass@localhost:5432/testdb"
        mock_settings.database_pool_min_size = 5
        mock_settings.database_pool_max_size = 20
        mock_pool_instance = MagicMock()
        mock_pool_class.return_value = mock_pool_instance

        # Act
        result = get_db_pool()

        # Assert
        assert result is mock_pool_instance
        mock_pool_class.assert_called_once_with(
            minconn=5,
            maxconn=20,
            dsn="postgresql://user:pass@localhost:5432/testdb",
        )

    @patch("db.connection.settings")
    @patch("db.connection.pool.ThreadedConnectionPool")
    def test_connection_pool_singleton_pattern(self, mock_pool_class, mock_settings):
        """Test that connection pool uses singleton pattern."""
        # Arrange
        mock_settings.database_url = "postgresql://user:pass@localhost:5432/testdb"
        mock_settings.database_pool_min_size = 5
        mock_settings.database_pool_max_size = 20
        mock_pool_instance = MagicMock()
        mock_pool_class.return_value = mock_pool_instance

        # Act
        pool1 = get_db_pool()
        pool2 = get_db_pool()

        # Assert
        assert pool1 is pool2
        mock_pool_class.assert_called_once()  # Only called once

    @patch("db.connection.settings")
    @patch("db.connection.pool.ThreadedConnectionPool")
    @patch("db.connection.logger")
    def test_connection_pool_init_failure_sanitizes_password(
        self, mock_logger, mock_pool_class, mock_settings
    ):
        """Test that password is sanitized in error messages."""
        # Arrange
        mock_settings.database_url = (
            "postgresql://user:secret123@localhost:5432/testdb?password=secret456"
        )
        mock_settings.database_pool_min_size = 5
        mock_settings.database_pool_max_size = 20
        mock_pool_class.side_effect = OperationalError(
            "connection failed: password=secret456 invalid"
        )

        # Act & Assert
        with pytest.raises(OperationalError):
            get_db_pool()

        # Verify password was sanitized in log message
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "secret123" not in error_message
        assert "secret456" not in error_message
        assert "***" in error_message

    @patch("db.connection.settings")
    @patch("db.connection.pool.ThreadedConnectionPool")
    def test_connection_pool_logs_initialization(self, mock_pool_class, mock_settings):
        """Test that pool initialization is logged."""
        # Arrange
        mock_settings.database_url = "postgresql://user:pass@localhost:5432/testdb"
        mock_settings.database_pool_min_size = 5
        mock_settings.database_pool_max_size = 20
        mock_pool_instance = MagicMock()
        mock_pool_class.return_value = mock_pool_instance

        # Act
        with patch("db.connection.logger") as mock_logger:
            get_db_pool()

        # Assert
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call("Initializing database connection pool")
        mock_logger.info.assert_any_call("Database pool initialized: 5-20 connections")


class TestQueryExecutionWithParams:
    """Test 4.2: Parameterized query execution."""

    @patch("db.connection.get_db_pool")
    def test_fetch_one_with_tuple_params(self, mock_get_pool):
        """Test fetch_one with tuple-style parameters."""
        # Arrange
        mock_conn = MagicMock()

        # Mock cursor for statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor for actual query
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = {"id": 1, "name": "Test"}

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_one("SELECT * FROM users WHERE id = %s", params=(1,))

        # Assert
        assert result == {"id": 1, "name": "Test"}
        # Should be called once (after the timeout cursor)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))

    @patch("db.connection.get_db_pool")
    def test_fetch_one_with_dict_params(self, mock_get_pool):
        """Test fetch_one with dict-style parameters."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = {"id": 1, "email": "test@example.com"}

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_one(
            "SELECT * FROM users WHERE email = %(email)s",
            params={"email": "test@example.com"},
        )

        # Assert
        assert result == {"id": 1, "email": "test@example.com"}
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == {"email": "test@example.com"}

    @patch("db.connection.get_db_pool")
    def test_fetch_all_with_params(self, mock_get_pool):
        """Test fetch_all returns list of results with parameters."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchall.return_value = [
            {"id": 1, "score": 85},
            {"id": 2, "score": 90},
        ]

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_all("SELECT * FROM calls WHERE score >= %s", params=(80,))

        # Assert
        assert len(result) == 2
        assert result[0] == {"id": 1, "score": 85}
        assert result[1] == {"id": 2, "score": 90}

    @patch("db.connection.get_db_pool")
    def test_execute_query_with_params(self, mock_get_pool):
        """Test execute_query with parameterized INSERT."""
        # Arrange
        mock_conn = MagicMock()

        # Mock cursor for statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor for actual query
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.rowcount = 1

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        execute_query(
            "INSERT INTO calls (id, title) VALUES (%s, %s)",
            params=("call-123", "Test Call"),
        )

        # Assert
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO calls (id, title) VALUES (%s, %s)",
            ("call-123", "Test Call"),
        )
        mock_conn.commit.assert_called_once()

    @patch("db.connection.get_db_pool")
    def test_execute_many_batch_insert(self, mock_get_pool):
        """Test execute_many with batch insert."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.rowcount = 3

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        params_list = [
            ("call-1", "Call 1"),
            ("call-2", "Call 2"),
            ("call-3", "Call 3"),
        ]
        execute_many("INSERT INTO calls (id, title) VALUES (%s, %s)", params_list)

        # Assert
        mock_cursor.executemany.assert_called_once_with(
            "INSERT INTO calls (id, title) VALUES (%s, %s)", params_list
        )
        mock_conn.commit.assert_called_once()

    @patch("db.connection.get_db_pool")
    def test_fetch_one_returns_none_when_no_results(self, mock_get_pool):
        """Test fetch_one returns None when query has no results."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = None

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_one("SELECT * FROM users WHERE id = %s", params=(999,))

        # Assert
        assert result is None


class TestTransactionRollback:
    """Test 4.3: Transaction rollback on error."""

    @patch("db.connection.get_db_pool")
    @patch("db.connection.logger")
    def test_execute_query_rolls_back_on_error(self, mock_logger, mock_get_pool):
        """Test that execute_query rolls back transaction on database error."""
        # Arrange
        mock_conn = MagicMock()

        # Mock cursor for statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor for actual query that will fail
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.execute.side_effect = DatabaseError("constraint violation")

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with pytest.raises(DatabaseError):
            execute_query("INSERT INTO calls (id) VALUES (%s)", params=("duplicate",))

        # Assert rollback was called
        mock_conn.rollback.assert_called_once()
        # Assert commit was NOT called
        mock_conn.commit.assert_not_called()

    @patch("db.connection.get_db_pool")
    def test_execute_many_rolls_back_on_error(self, mock_get_pool):
        """Test that execute_many rolls back on batch insert failure."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.executemany.side_effect = DatabaseError("batch insert failed")

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with pytest.raises(DatabaseError):
            execute_many(
                "INSERT INTO calls (id) VALUES (%s)",
                [("call-1",), ("call-2",)],
            )

        # Assert
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    @patch("db.connection.get_db_pool")
    @patch("db.connection.logger")
    def test_execute_query_logs_error_without_sensitive_data(self, mock_logger, mock_get_pool):
        """Test that error logging sanitizes sensitive parameters."""
        # Arrange
        mock_conn = MagicMock()

        # Mock cursor for statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor for actual query that will fail
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.execute.side_effect = DatabaseError("query failed")

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with patch("db.connection.settings") as mock_settings:
            mock_settings.database_url = "postgresql://user:secret@localhost/db?password=secret123"

            with pytest.raises(DatabaseError):
                execute_query(
                    "INSERT INTO users (email, password) VALUES (%s, %s)",
                    params=("test@example.com", "secret123"),
                )

        # Assert logger was called
        mock_logger.error.assert_called_once()

    @patch("db.connection.get_db_pool")
    def test_execute_query_no_commit_when_commit_false(self, mock_get_pool):
        """Test that execute_query doesn't commit when commit=False."""
        # Arrange
        mock_conn = MagicMock()

        # Mock cursor for statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor for actual query
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.rowcount = 1

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        execute_query(
            "INSERT INTO calls (id) VALUES (%s)",
            params=("call-123",),
            commit=False,
        )

        # Assert
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO calls (id) VALUES (%s)", ("call-123",)
        )
        mock_conn.commit.assert_not_called()


class TestConnectionTimeoutRetry:
    """Test 4.4: Connection timeout handling with retry."""

    @patch("db.connection.get_db_pool")
    def test_connection_timeout_returns_to_pool(self, mock_get_pool):
        """Test that connection is returned to pool even on timeout."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)

        # Simulate timeout on first cursor execution
        mock_cursor.execute.side_effect = OperationalError("timeout")

        # First cursor for SET statement_timeout
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        # Mock cursor() to return different cursors
        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with pytest.raises(OperationalError):
            fetch_one("SELECT * FROM users WHERE id = %s", params=(1,))

        # Assert connection was returned to pool
        mock_pool.putconn.assert_called_once_with(mock_conn)

    @patch("db.connection.get_db_pool")
    def test_statement_timeout_set_per_connection(self, mock_get_pool):
        """Test that statement_timeout is set for each connection."""
        # Arrange
        mock_conn = MagicMock()
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        mock_query_cursor = MagicMock()
        mock_query_cursor.__enter__ = Mock(return_value=mock_query_cursor)
        mock_query_cursor.__exit__ = Mock(return_value=False)
        mock_query_cursor.fetchone.return_value = {"id": 1}

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_query_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_one("SELECT * FROM users WHERE id = %s", params=(1,))

        # Assert
        # First cursor call should set statement_timeout
        assert mock_conn.cursor.call_count == 2
        mock_timeout_cursor.execute.assert_called_once_with("SET statement_timeout = '30s'")
        # Second cursor call should execute the actual query
        mock_query_cursor.execute.assert_called_once()
        assert result == {"id": 1}

    @patch("db.connection.get_db_pool")
    def test_connection_interface_error_returns_to_pool(self, mock_get_pool):
        """Test that connection is returned to pool on interface error."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.execute.side_effect = InterfaceError("connection closed")

        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with pytest.raises(InterfaceError):
            fetch_one("SELECT * FROM users WHERE id = %s", params=(1,))

        # Assert connection was returned to pool
        mock_pool.putconn.assert_called_once_with(mock_conn)

    @patch("db.connection.get_db_pool")
    def test_connection_context_manager_always_returns_connection(self, mock_get_pool):
        """Test that context manager returns connection even on exception."""
        # Arrange
        mock_conn = MagicMock()
        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)
        mock_timeout_cursor.execute.side_effect = Exception("unexpected error")

        mock_conn.cursor.return_value = mock_timeout_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act & Assert
        with pytest.raises(Exception):
            with get_db_connection() as conn:
                # This will raise during statement_timeout setting
                pass

        # Assert connection was returned to pool
        mock_pool.putconn.assert_called_once_with(mock_conn)


class TestConnectionPoolManagement:
    """Additional tests for connection pool lifecycle."""

    @patch("db.connection._db_pool")
    @patch("db.connection.logger")
    def test_close_db_pool_closes_all_connections(self, mock_logger, mock_pool):
        """Test that close_db_pool closes all connections."""
        # Arrange
        mock_pool_instance = MagicMock()

        # Act
        with patch("db.connection._db_pool", mock_pool_instance):
            close_db_pool()

        # Assert
        mock_pool_instance.closeall.assert_called_once()

    @patch("db.connection._db_pool", None)
    @patch("db.connection.logger")
    def test_close_db_pool_when_no_pool_exists(self, mock_logger):
        """Test that close_db_pool handles None pool gracefully."""
        # Act (should not raise)
        close_db_pool()

        # Assert - no errors raised
        assert True

    @patch("db.connection.get_db_pool")
    def test_fetch_one_as_dict_true(self, mock_get_pool):
        """Test fetch_one returns dict when as_dict=True."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchone.return_value = {"id": 1, "name": "Test"}

        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_one("SELECT * FROM users WHERE id = %s", params=(1,), as_dict=True)

        # Assert
        assert result == {"id": 1, "name": "Test"}
        assert isinstance(result, dict)

    @patch("db.connection.get_db_pool")
    def test_fetch_all_as_dict_false(self, mock_get_pool):
        """Test fetch_all returns tuples when as_dict=False."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)
        mock_cursor.fetchall.return_value = [(1, "Test"), (2, "Test2")]

        mock_timeout_cursor = MagicMock()
        mock_timeout_cursor.__enter__ = Mock(return_value=mock_timeout_cursor)
        mock_timeout_cursor.__exit__ = Mock(return_value=False)

        mock_conn.cursor.side_effect = [mock_timeout_cursor, mock_cursor]
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_get_pool.return_value = mock_pool

        # Act
        result = fetch_all("SELECT * FROM users", as_dict=False)

        # Assert
        assert result == [(1, "Test"), (2, "Test2")]
        assert isinstance(result[0], tuple)
