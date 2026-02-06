"""
Database query pagination utilities.

Provides cursor-based and offset-based pagination for efficient
query result handling.
"""
import logging
from typing import Any, TypeVar, Generic

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET from page number."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get SQL LIMIT."""
        return self.page_size


class PaginatedResult(BaseModel, Generic[T]):
    """Generic paginated result container."""
    items: list[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Has previous page")
    has_next: bool = Field(..., description="Has next page")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        params: PaginationParams,
    ) -> "PaginatedResult[T]":
        """
        Create paginated result from query results.

        Args:
            items: Query result items for current page
            total: Total count of all items
            params: Pagination parameters

        Returns:
            PaginatedResult with pagination metadata
        """
        total_pages = (total + params.page_size - 1) // params.page_size

        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_previous=params.page > 1,
            has_next=params.page < total_pages,
        )


class CursorPaginationParams(BaseModel):
    """Parameters for cursor-based pagination."""
    cursor: str | None = Field(
        default=None,
        description="Cursor for next page (opaque string)"
    )
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class CursorPaginatedResult(BaseModel, Generic[T]):
    """Cursor-based paginated result."""
    items: list[T]
    next_cursor: str | None = Field(
        None,
        description="Cursor for next page (null if no more pages)"
    )
    has_next: bool = Field(..., description="Has next page")

    @classmethod
    def create(
        cls,
        items: list[T],
        cursor_field: str,
        limit: int,
    ) -> "CursorPaginatedResult[T]":
        """
        Create cursor-based paginated result.

        Args:
            items: Query result items (should fetch limit + 1)
            cursor_field: Field name to use for cursor
            limit: Requested limit

        Returns:
            CursorPaginatedResult with next cursor
        """
        has_next = len(items) > limit
        items_to_return = items[:limit]

        next_cursor = None
        if has_next and items_to_return:
            # Get cursor value from last item
            last_item = items_to_return[-1]
            if isinstance(last_item, dict):
                next_cursor = str(last_item.get(cursor_field))
            else:
                next_cursor = str(getattr(last_item, cursor_field))

        return cls(
            items=items_to_return,
            next_cursor=next_cursor,
            has_next=has_next,
        )


def add_pagination_to_query(
    base_query: str,
    params: PaginationParams,
) -> tuple[str, int, int]:
    """
    Add pagination clauses to SQL query.

    Args:
        base_query: Base SQL query without LIMIT/OFFSET
        params: Pagination parameters

    Returns:
        Tuple of (query with pagination, limit, offset)
    """
    paginated_query = f"{base_query} LIMIT %s OFFSET %s"
    return paginated_query, params.limit, params.offset


def add_cursor_pagination_to_query(
    base_query: str,
    cursor_field: str,
    cursor_value: str | None,
    limit: int,
    order: str = "ASC",
) -> tuple[str, list[Any]]:
    """
    Add cursor-based pagination to SQL query.

    Args:
        base_query: Base SQL query
        cursor_field: Field to use for cursor
        cursor_value: Current cursor value (None for first page)
        limit: Items per page
        order: Sort order (ASC or DESC)

    Returns:
        Tuple of (query with cursor filter, query params)
    """
    params = []

    # Add cursor filter if provided
    if cursor_value:
        operator = ">" if order == "ASC" else "<"
        cursor_filter = f" WHERE {cursor_field} {operator} %s"
        base_query += cursor_filter
        params.append(cursor_value)

    # Add ordering and limit (fetch 1 extra to determine if there's a next page)
    base_query += f" ORDER BY {cursor_field} {order} LIMIT %s"
    params.append(limit + 1)

    return base_query, params


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_paginated_query(params: PaginationParams) -> PaginatedResult[dict]:
    """
    Example of paginated query implementation.

    Args:
        params: Pagination parameters

    Returns:
        Paginated result
    """
    from db.connection import fetch_all, fetch_one

    # Get total count
    count_result = fetch_one("SELECT COUNT(*) as total FROM calls")
    total = count_result["total"] if count_result else 0

    # Get paginated results
    query = "SELECT * FROM calls ORDER BY scheduled_at DESC"
    paginated_query, limit, offset = add_pagination_to_query(query, params)

    items = fetch_all(paginated_query, (limit, offset))

    return PaginatedResult.create(
        items=items,
        total=total,
        params=params,
    )


def example_cursor_paginated_query(
    cursor: str | None,
    limit: int,
) -> CursorPaginatedResult[dict]:
    """
    Example of cursor-based paginated query.

    Args:
        cursor: Current cursor value
        limit: Items per page

    Returns:
        Cursor-based paginated result
    """
    from db.connection import fetch_all

    base_query = "SELECT * FROM calls"
    query, params = add_cursor_pagination_to_query(
        base_query=base_query,
        cursor_field="scheduled_at",
        cursor_value=cursor,
        limit=limit,
        order="DESC",
    )

    items = fetch_all(query, params)

    return CursorPaginatedResult.create(
        items=items,
        cursor_field="scheduled_at",
        limit=limit,
    )
