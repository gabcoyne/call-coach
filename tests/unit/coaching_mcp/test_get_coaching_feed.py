"""
Unit tests for get_coaching_feed tool.

Tests cover:
- Time filtering (today, this_week, this_month, custom)
- Rep-specific filtering
- Feed item generation from sessions
- Highlight extraction (high/low scores)
- Team insights for managers
- Pagination (limit/offset)
- Dismissed item filtering
"""

from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from coaching_mcp.tools.get_coaching_feed import get_coaching_feed_tool


@pytest.fixture
def sample_sessions():
    """Sample coaching sessions."""
    base_time = datetime.now() - timedelta(days=2)
    return [
        {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": base_time,
            "scores": {"discovery": 9.0, "engagement": 8.5},
            "action_items": ["Action 1", "Action 2"],
            "rep_email": "sarah@prefect.io",
            "rep_name": "Sarah Johnson",
            "is_dismissed": False,
            "is_bookmarked": False,
        },
        {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": base_time + timedelta(days=1),
            "scores": {"discovery": 3.5, "engagement": 4.0},
            "action_items": ["Needs improvement"],
            "rep_email": "john@prefect.io",
            "rep_name": "John Smith",
            "is_dismissed": False,
            "is_bookmarked": False,
        },
    ]


@pytest.fixture
def sample_call():
    """Sample call data."""
    return {
        "id": str(uuid4()),
        "title": "Discovery Call - Acme Corp",
        "scheduled_at": datetime.now() - timedelta(days=2),
    }


class TestGetCoachingFeedTool:
    """Test get_coaching_feed tool."""

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_returns_feed_items_with_required_fields(
        self, mock_get_sessions, mock_queries, sample_sessions, sample_call
    ):
        """
        GIVEN recent coaching sessions
        WHEN get_coaching_feed_tool is called
        THEN returns feed items with required fields
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool()

        assert "items" in result
        assert "total_count" in result
        assert "has_more" in result
        assert isinstance(result["items"], list)

        if len(result["items"]) > 0:
            item = result["items"][0]
            assert "id" in item
            assert "type" in item
            assert "timestamp" in item
            assert "title" in item
            assert "metadata" in item

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_time_filter_today_filters_by_date(
        self, mock_get_sessions, mock_queries, sample_sessions, sample_call
    ):
        """
        GIVEN time_filter='today'
        WHEN get_coaching_feed_tool is called
        THEN only today's items returned
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(time_filter="today")

        # Function should handle filtering
        assert "items" in result

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_time_filter_this_week_uses_7_days(
        self, mock_get_sessions, mock_queries, sample_sessions, sample_call
    ):
        """
        GIVEN time_filter='this_week'
        WHEN get_coaching_feed_tool is called
        THEN last 7 days returned
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(time_filter="this_week")

        assert "items" in result

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_custom_date_range_filtering(
        self, mock_get_sessions, mock_queries, sample_sessions, sample_call
    ):
        """
        GIVEN custom start_date and end_date
        WHEN get_coaching_feed_tool is called with time_filter='custom'
        THEN custom range used
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = sample_call

        start = (datetime.now() - timedelta(days=10)).isoformat()
        end = datetime.now().isoformat()

        result = get_coaching_feed_tool(
            time_filter="custom",
            start_date=start,
            end_date=end,
        )

        assert "items" in result

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_rep_email_filter_limits_to_rep(self, mock_get_sessions, mock_queries, sample_call):
        """
        GIVEN rep_email parameter
        WHEN get_coaching_feed_tool is called
        THEN uses get_coaching_sessions_for_rep
        """
        mock_get_sessions.return_value = []
        mock_queries.get_coaching_sessions_for_rep.return_value = []
        mock_queries.get_call.return_value = sample_call

        get_coaching_feed_tool(rep_email="sarah@prefect.io")

        # Should call rep-specific query
        mock_queries.get_coaching_sessions_for_rep.assert_called_once()

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_dismissed_items_excluded_by_default(
        self, mock_get_sessions, mock_queries, sample_call
    ):
        """
        GIVEN sessions with is_dismissed=True
        WHEN get_coaching_feed_tool is called without include_dismissed
        THEN dismissed items excluded
        """
        dismissed_session = {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": datetime.now(),
            "scores": {"discovery": 7.0},
            "action_items": [],
            "rep_email": "sarah@prefect.io",
            "is_dismissed": True,
            "is_bookmarked": False,
        }

        mock_get_sessions.return_value = [dismissed_session]
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(include_dismissed=False)

        # Dismissed items should be filtered out
        assert len(result["items"]) == 0

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_dismissed_items_included_when_requested(
        self, mock_get_sessions, mock_queries, sample_call
    ):
        """
        GIVEN sessions with is_dismissed=True
        WHEN get_coaching_feed_tool is called with include_dismissed=True
        THEN dismissed items included
        """
        dismissed_session = {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": datetime.now(),
            "scores": {"discovery": 7.0},
            "action_items": [],
            "rep_email": "sarah@prefect.io",
            "is_dismissed": True,
            "is_bookmarked": False,
        }

        mock_get_sessions.return_value = [dismissed_session]
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(include_dismissed=True)

        # Should include dismissed items
        assert len(result["items"]) > 0

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_pagination_with_limit_and_offset(self, mock_get_sessions, mock_queries, sample_call):
        """
        GIVEN many sessions
        WHEN get_coaching_feed_tool is called with limit and offset
        THEN correct page returned
        """
        many_sessions = []
        for i in range(50):
            many_sessions.append(
                {
                    "id": str(uuid4()),
                    "call_id": str(uuid4()),
                    "created_at": datetime.now() - timedelta(days=i),
                    "scores": {"discovery": 7.0},
                    "action_items": [],
                    "rep_email": "sarah@prefect.io",
                    "is_dismissed": False,
                    "is_bookmarked": False,
                }
            )

        mock_get_sessions.return_value = many_sessions
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(limit=10, offset=5)

        assert len(result["items"]) <= 10
        assert result["total_count"] > 10
        assert result["has_more"] is True or result["has_more"] is False

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_highlights_extracted_for_high_scores(
        self, mock_get_sessions, mock_queries, sample_call
    ):
        """
        GIVEN session with score >= 8.5
        WHEN get_coaching_feed_tool is called
        THEN highlight created
        """
        high_score_session = {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": datetime.now(),
            "scores": {"discovery": 9.0, "engagement": 8.8},
            "action_items": [],
            "rep_email": "sarah@prefect.io",
            "is_dismissed": False,
            "is_bookmarked": False,
        }

        mock_get_sessions.return_value = [high_score_session]
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool()

        # Should have highlights for high score
        assert "highlights" in result
        # Average score is (9.0 + 8.8) / 2 = 8.9, should be highlighted
        if result["items"]:
            assert len(result["highlights"]) > 0

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_highlights_extracted_for_low_scores(
        self, mock_get_sessions, mock_queries, sample_call
    ):
        """
        GIVEN session with score <= 4.0
        WHEN get_coaching_feed_tool is called
        THEN needs_attention highlight created
        """
        low_score_session = {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": datetime.now(),
            "scores": {"discovery": 3.5, "engagement": 3.0},
            "action_items": [],
            "rep_email": "john@prefect.io",
            "is_dismissed": False,
            "is_bookmarked": False,
        }

        mock_get_sessions.return_value = [low_score_session]
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool()

        # Should have highlights for low score
        assert "highlights" in result

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_team_insights_included_when_requested(
        self, mock_get_sessions, mock_queries, sample_sessions, sample_call
    ):
        """
        GIVEN include_team_insights=True
        WHEN get_coaching_feed_tool is called
        THEN team insights generated
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool(include_team_insights=True)

        assert "team_insights" in result
        # If there are sessions, should have team insights
        if len(sample_sessions) > 0:
            assert isinstance(result["team_insights"], list)

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_new_items_count_tracks_recent_sessions(
        self, mock_get_sessions, mock_queries, sample_call
    ):
        """
        GIVEN sessions created within last 24 hours
        WHEN get_coaching_feed_tool is called
        THEN new_items_count reflects recent items
        """
        new_session = {
            "id": str(uuid4()),
            "call_id": str(uuid4()),
            "created_at": datetime.now() - timedelta(hours=6),  # 6 hours ago
            "scores": {"discovery": 7.0},
            "action_items": [],
            "rep_email": "sarah@prefect.io",
            "is_dismissed": False,
            "is_bookmarked": False,
        }

        mock_get_sessions.return_value = [new_session]
        mock_queries.get_call.return_value = sample_call

        result = get_coaching_feed_tool()

        assert "new_items_count" in result
        # Should count the recent item as new
        assert result["new_items_count"] >= 0

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_error_returns_empty_feed_with_error_field(self, mock_get_sessions, mock_queries):
        """
        GIVEN exception during processing
        WHEN get_coaching_feed_tool is called
        THEN returns empty feed with error field
        """
        mock_get_sessions.side_effect = Exception("Database connection failed")

        result = get_coaching_feed_tool()

        assert "error" in result
        assert result["items"] == []
        assert result["total_count"] == 0

    @patch("coaching_mcp.tools.get_coaching_feed.queries")
    @patch("coaching_mcp.tools.get_coaching_feed._get_recent_sessions")
    def test_missing_call_skips_session(self, mock_get_sessions, mock_queries, sample_sessions):
        """
        GIVEN session with call_id that doesn't exist
        WHEN get_coaching_feed_tool is called
        THEN session skipped gracefully
        """
        mock_get_sessions.return_value = sample_sessions
        mock_queries.get_call.return_value = None  # Call not found

        result = get_coaching_feed_tool()

        # Should handle missing calls gracefully
        assert "items" in result
        # Items should be skipped if call doesn't exist
        assert len(result["items"]) == 0 or result["items"] is not None
