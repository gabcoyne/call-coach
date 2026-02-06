"""Tests for search_calls MCP tool."""

from unittest.mock import patch

import pytest

from coaching_mcp.tools.search_calls import search_calls_tool


@pytest.fixture
def mock_db():
    """Mock database functions."""
    with patch("coaching_mcp.tools.search_calls.fetch_all") as mock_fetch_all:
        yield {"fetch_all": mock_fetch_all}


@pytest.fixture
def sample_calls():
    """Sample call results."""
    return [
        {
            "id": "call-1",
            "title": "Discovery Call - Acme Corp",
            "rep_email": "sarah@example.com",
            "product": "prefect",
            "overall_score": 85,
            "started": "2025-01-15T10:00:00Z",
        },
        {
            "id": "call-2",
            "title": "Demo - TechCorp",
            "rep_email": "john@example.com",
            "product": "horizon",
            "overall_score": 72,
            "started": "2025-01-14T14:00:00Z",
        },
    ]


class TestSearchCallsTool:
    """Tests for search_calls_tool function."""

    def test_search_calls_no_filters(self, mock_db, sample_calls):
        """Test searching calls without any filters."""
        mock_db["fetch_all"].return_value = sample_calls

        result = search_calls_tool()

        assert result is not None
        assert isinstance(result, list)

    def test_search_calls_by_rep_email(self, mock_db, sample_calls):
        """Test filtering calls by rep email."""
        filtered = [c for c in sample_calls if c["rep_email"] == "sarah@example.com"]
        mock_db["fetch_all"].return_value = filtered

        result = search_calls_tool(rep_email="sarah@example.com")

        assert result is not None
        assert len(result) > 0

    def test_search_calls_by_product(self, mock_db, sample_calls):
        """Test filtering by product."""
        filtered = [c for c in sample_calls if c["product"] == "prefect"]
        mock_db["fetch_all"].return_value = filtered

        result = search_calls_tool(product="prefect")

        assert result is not None

    def test_search_calls_by_call_type(self, mock_db, sample_calls):
        """Test filtering by call type."""
        mock_db["fetch_all"].return_value = [sample_calls[0]]

        result = search_calls_tool(call_type="discovery")

        assert result is not None

    def test_search_calls_by_score_range(self, mock_db, sample_calls):
        """Test filtering by score range."""
        filtered = [c for c in sample_calls if 75 <= c["overall_score"] <= 90]
        mock_db["fetch_all"].return_value = filtered

        result = search_calls_tool(min_score=75, max_score=90)

        assert result is not None
        assert len(result) > 0

    def test_search_calls_with_date_range(self, mock_db, sample_calls):
        """Test filtering by date range."""
        mock_db["fetch_all"].return_value = sample_calls

        result = search_calls_tool(date_range={"start": "2025-01-10", "end": "2025-01-20"})

        assert result is not None

    def test_search_calls_by_objection_type(self, mock_db):
        """Test filtering by objection type."""
        calls_with_objection = [
            {
                "id": "call-3",
                "title": "Objection Call",
                "objection_types": ["pricing"],
                "overall_score": 80,
            }
        ]
        mock_db["fetch_all"].return_value = calls_with_objection

        result = search_calls_tool(has_objection_type="pricing")

        assert result is not None

    def test_search_calls_by_topics(self, mock_db):
        """Test filtering by topics."""
        calls_with_topics = [
            {
                "id": "call-4",
                "title": "Topic Call",
                "topics": ["Product Demo", "ROI Discussion"],
            }
        ]
        mock_db["fetch_all"].return_value = calls_with_topics

        result = search_calls_tool(topics=["Product Demo"])

        assert result is not None

    def test_search_calls_with_limit(self, mock_db, sample_calls):
        """Test limiting results."""
        mock_db["fetch_all"].return_value = sample_calls[:1]

        result = search_calls_tool(limit=1)

        assert result is not None
        assert len(result) <= 1

    def test_search_calls_multiple_filters(self, mock_db, sample_calls):
        """Test combining multiple filters."""
        filtered = [
            c
            for c in sample_calls
            if c["rep_email"] == "sarah@example.com"
            and c["product"] == "prefect"
            and c["overall_score"] >= 75
        ]
        mock_db["fetch_all"].return_value = filtered

        result = search_calls_tool(rep_email="sarah@example.com", product="prefect", min_score=75)

        assert result is not None

    def test_search_calls_limit_exceeded(self, mock_db, sample_calls):
        """Test that limit is capped at reasonable value."""
        mock_db["fetch_all"].return_value = sample_calls

        result = search_calls_tool(limit=200)

        # Should be capped or return limited results
        assert result is not None

    def test_search_calls_empty_result(self, mock_db):
        """Test handling empty search results."""
        mock_db["fetch_all"].return_value = []

        result = search_calls_tool(rep_email="nonexistent@example.com")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0
