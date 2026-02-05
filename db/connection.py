"""
Database connection management with connection pooling.
Uses psycopg2 for synchronous operations (Prefect flows, MCP tools).
"""
import logging
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from shared import settings

logger = logging.getLogger(__name__)

# Global connection pool
_db_pool: pool.ThreadedConnectionPool | None = None


def get_db_pool() -> pool.ThreadedConnectionPool:
    """
    Get or create database connection pool.
    Thread-safe singleton pattern.
    """
    global _db_pool

    if _db_pool is None:
        logger.info("Initializing database connection pool")
        try:
            _db_pool = pool.ThreadedConnectionPool(
                minconn=settings.database_pool_min_size,
                maxconn=settings.database_pool_max_size,
                dsn=settings.database_url,
            )
            logger.info(
                f"Database pool initialized: "
                f"{settings.database_pool_min_size}-{settings.database_pool_max_size} connections"
            )
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    return _db_pool


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager for getting a database connection from the pool.
    Automatically returns connection to pool when done.

    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM calls")
                results = cur.fetchall()
    """
    db_pool = get_db_pool()
    conn = db_pool.getconn()

    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def execute_query(
    query: str,
    params: tuple | dict | None = None,
    commit: bool = True,
) -> None:
    """
    Execute a query that doesn't return results (INSERT, UPDATE, DELETE).

    Args:
        query: SQL query string
        params: Query parameters (tuple for %s placeholders, dict for %(name)s)
        commit: Whether to commit the transaction (default: True)
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, params)
                if commit:
                    conn.commit()
                logger.debug(f"Query executed: {cur.rowcount} rows affected")
            except Exception as e:
                conn.rollback()
                logger.error(f"Query failed: {e}\nQuery: {query}\nParams: {params}")
                raise


def execute_many(
    query: str,
    params_list: list[tuple] | list[dict],
    commit: bool = True,
) -> None:
    """
    Execute a query multiple times with different parameters (batch insert).

    Args:
        query: SQL query string
        params_list: List of parameter tuples/dicts
        commit: Whether to commit the transaction (default: True)
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.executemany(query, params_list)
                if commit:
                    conn.commit()
                logger.debug(f"Batch query executed: {cur.rowcount} rows affected")
            except Exception as e:
                conn.rollback()
                logger.error(f"Batch query failed: {e}\nQuery: {query}")
                raise


def fetch_one(
    query: str,
    params: tuple | dict | None = None,
    as_dict: bool = True,
) -> dict[str, Any] | tuple | None:
    """
    Fetch a single row from the database.

    Args:
        query: SQL query string
        params: Query parameters
        as_dict: Return result as dict (default: True)

    Returns:
        Single row as dict or tuple, or None if no results
    """
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if as_dict else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return dict(result) if result and as_dict else result


def fetch_all(
    query: str,
    params: tuple | dict | None = None,
    as_dict: bool = True,
) -> list[dict[str, Any]] | list[tuple]:
    """
    Fetch all rows from the database.

    Args:
        query: SQL query string
        params: Query parameters
        as_dict: Return results as list of dicts (default: True)

    Returns:
        List of rows as dicts or tuples
    """
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if as_dict else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results] if as_dict else results


def close_db_pool() -> None:
    """Close all connections in the pool. Call on application shutdown."""
    global _db_pool

    if _db_pool is not None:
        _db_pool.closeall()
        _db_pool = None
        logger.info("Database connection pool closed")
