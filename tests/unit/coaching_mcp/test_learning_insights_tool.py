"""
Unit tests for get_learning_insights tool.

Tests cover:
- Valid rep email with focus area
- Invalid rep email handling
- Invalid focus area handling
- Empty results handling
- Error handling in underlying analysis
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_insights():
    """Sample learning insights response."""
    return {
        "rep_performance": {
            "opportunities": 5,
            "calls": 12,
            "average_score": 7.2,
        },
        "top_performer_benchmark": {
            "opportunities": 8,
            "calls": 20,
            "average_score": 8.5,
        },
        "behavioral_differences": "Top performers ask 2x more impact quantification questions",
        "exemplar_moments": [
            {
                "opportunity_name": "Acme Corp",
                "score": 9.0,
                "call_date": "2024-01-15",
                "what_they_did": "Asked about business impact of current solution",
                "transcript_excerpt": "Can you quantify the cost of your current process?",
            }
        ],
    }


class TestGetLearningInsightsTool:
    """Test get_learning_insights tool."""

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_valid_rep_with_focus_area_returns_insights(
        self, mock_get_insights, sample_insights
    ):
        """
        GIVEN a valid rep email and focus area
        WHEN get_learning_insights_tool is called
        THEN it returns formatted insights comparing to top performers
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_get_insights.return_value = sample_insights

        # Create mock server
        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        # Register tool
        register_learning_insights_tool(mock_server)

        # Call tool (await since it's async)
        result = await registered_tool({"rep_email": "sarah@prefect.io", "focus_area": "discovery"})

        # Verify
        assert result is not None
        assert len(result) > 0
        text_content = result[0].text
        assert "sarah@prefect.io" in text_content
        assert "discovery" in text_content.lower()
        assert "7.2" in text_content  # Rep score
        assert "8.5" in text_content  # Top performer score
        assert "Acme Corp" in text_content  # Exemplar

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_missing_rep_email_returns_error(self, mock_get_insights):
        """
        GIVEN no rep email provided
        WHEN get_learning_insights_tool is called
        THEN it returns error message
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        register_learning_insights_tool(mock_server)

        # Call without rep_email
        result = await registered_tool({})

        # Verify error
        assert len(result) > 0
        assert "error" in result[0].text.lower()
        assert "rep_email" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_invalid_focus_area_returns_error(self, mock_get_insights):
        """
        GIVEN invalid focus area
        WHEN get_learning_insights_tool is called
        THEN it returns error with valid options
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        register_learning_insights_tool(mock_server)

        # Call with invalid focus area
        result = await registered_tool({"rep_email": "sarah@prefect.io", "focus_area": "invalid"})

        # Verify error
        assert len(result) > 0
        text = result[0].text
        assert "error" in text.lower()
        assert "discovery" in text  # Should list valid options

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_nonexistent_rep_returns_error(self, mock_get_insights):
        """
        GIVEN rep email that doesn't exist
        WHEN get_learning_insights_tool is called
        THEN it returns error message
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_get_insights.return_value = {"error": "Rep not found: nonexistent@example.com"}

        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        register_learning_insights_tool(mock_server)

        result = await registered_tool(
            {"rep_email": "nonexistent@example.com", "focus_area": "discovery"}
        )

        # Verify error
        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_exception_in_analysis_returns_error(self, mock_get_insights):
        """
        GIVEN underlying analysis raises exception
        WHEN get_learning_insights_tool is called
        THEN it returns error message
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_get_insights.side_effect = Exception("Database connection failed")

        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        register_learning_insights_tool(mock_server)

        result = await registered_tool({"rep_email": "sarah@prefect.io", "focus_area": "discovery"})

        # Verify error handling
        assert len(result) > 0
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("coaching_mcp.tools.get_learning_insights.get_learning_insights")
    async def test_default_focus_area_is_discovery(self, mock_get_insights, sample_insights):
        """
        GIVEN no focus area specified
        WHEN get_learning_insights_tool is called
        THEN it defaults to discovery
        """
        from coaching_mcp.tools.get_learning_insights import register_learning_insights_tool

        mock_get_insights.return_value = sample_insights

        mock_server = MagicMock()
        registered_tool = None

        def capture_tool(func):
            nonlocal registered_tool
            registered_tool = func
            return func

        mock_server.call_tool = lambda: capture_tool

        register_learning_insights_tool(mock_server)

        result = await registered_tool({"rep_email": "sarah@prefect.io"})

        # Verify discovery was used
        mock_get_insights.assert_called_once_with("sarah@prefect.io", "discovery")
        assert len(result) > 0
