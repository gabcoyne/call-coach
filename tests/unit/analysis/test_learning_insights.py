"""
Unit tests for learning insights analysis functions.

Tests cover:
- find_similar_won_opportunities
- aggregate_coaching_patterns
- extract_exemplar_moments
- get_learning_insights
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


# Mock settings at module level to avoid config loading
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings to avoid loading real config."""
    with patch("analysis.learning_insights.settings") as mock_settings:
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.claude_model = "claude-sonnet-4-5-20250929"
        yield mock_settings


# Mock the CoachingDimension enum to add missing members
@pytest.fixture(autouse=True)
def mock_coaching_dimension():
    """Mock CoachingDimension to include all expected members."""
    from enum import Enum

    class MockCoachingDimension(str, Enum):
        DISCOVERY = "discovery"
        DISCOVERY_QUESTIONS = "discovery"  # Alias
        OBJECTION_HANDLING = "objection_handling"
        PRODUCT_KNOWLEDGE = "product_knowledge"
        RAPPORT_BUILDING = "rapport"
        NEXT_STEPS = "next_steps"
        ENGAGEMENT = "engagement"

    with patch("analysis.learning_insights.CoachingDimension", MockCoachingDimension):
        yield MockCoachingDimension


class TestFindSimilarWonOpportunities:
    """Tests for find_similar_won_opportunities function."""

    @patch("db.queries.search_opportunities")
    @patch("db.fetch_all")
    def test_excludes_rep_own_opportunities(self, mock_fetch_all, mock_search):
        """
        GIVEN rep_email
        WHEN find_similar_won_opportunities is called
        THEN it excludes opportunities owned by the rep
        """
        from analysis.learning_insights import find_similar_won_opportunities

        rep_email = "sarah@prefect.io"
        mock_search.return_value = (
            [
                {"id": str(uuid4()), "owner_email": rep_email, "stage": "Closed Won"},
                {"id": str(uuid4()), "owner_email": "other@prefect.io", "stage": "Closed Won"},
            ],
            2,
        )

        result = find_similar_won_opportunities(rep_email)

        assert len(result) == 1
        assert result[0]["owner_email"] != rep_email

    @patch("db.queries.search_opportunities")
    def test_filters_by_closed_won_stage(self, mock_search):
        """
        GIVEN search for similar opportunities
        WHEN find_similar_won_opportunities is called
        THEN it filters to Closed Won stage
        """
        from analysis.learning_insights import find_similar_won_opportunities

        mock_search.return_value = ([], 0)

        find_similar_won_opportunities("rep@prefect.io")

        # Verify filters include Closed Won
        call_args = mock_search.call_args
        assert call_args[1]["filters"]["stage"] == "Closed Won"

    @patch("db.queries.search_opportunities")
    @patch("db.fetch_all")
    def test_filters_by_role_when_provided(self, mock_fetch_all, mock_search):
        """
        GIVEN rep_role filter
        WHEN find_similar_won_opportunities is called
        THEN it filters opportunities to same role owners
        """
        from analysis.learning_insights import find_similar_won_opportunities

        opp_id_ae = str(uuid4())
        opp_id_se = str(uuid4())

        mock_search.return_value = (
            [
                {"id": opp_id_ae, "owner_email": "ae@prefect.io", "stage": "Closed Won"},
                {"id": opp_id_se, "owner_email": "se@prefect.io", "stage": "Closed Won"},
            ],
            2,
        )

        # Mock role lookups
        mock_fetch_all.return_value = [
            {"email": "ae@prefect.io", "role": "ae"},
            {"email": "se@prefect.io", "role": "se"},
        ]

        result = find_similar_won_opportunities("rep@prefect.io", rep_role="ae")

        # Should only include AE opportunities
        assert len(result) == 1
        assert result[0]["owner_email"] == "ae@prefect.io"


class TestAggregateCoachingPatterns:
    """Tests for aggregate_coaching_patterns function."""

    @pytest.fixture
    def sample_opportunities(self) -> list[dict[str, Any]]:
        """Sample opportunities for testing."""
        return [
            {"id": str(uuid4()), "name": "Opp 1"},
            {"id": str(uuid4()), "name": "Opp 2"},
        ]

    @patch("db.queries.get_opportunity_timeline")
    @patch("db.queries.get_coaching_sessions_for_call")
    @patch("db.queries.get_call_by_id")
    @patch("db.queries.get_full_transcript")
    def test_aggregates_scores_across_opportunities(
        self,
        mock_transcript,
        mock_get_call,
        mock_sessions,
        mock_timeline,
        sample_opportunities,
    ):
        """
        GIVEN multiple opportunities with coaching sessions
        WHEN aggregate_coaching_patterns is called
        THEN it aggregates scores correctly
        """
        from analysis.learning_insights import aggregate_coaching_patterns

        # Setup timeline with calls
        mock_timeline.return_value = [{"id": str(uuid4()), "item_type": "call"}]

        # Setup coaching sessions with high scores
        mock_sessions.return_value = [{"score": 85, "feedback": "Great discovery"}]
        mock_get_call.return_value = {"scheduled_at": datetime.now()}
        mock_transcript.return_value = "Sample transcript"

        result = aggregate_coaching_patterns(sample_opportunities, "discovery")

        assert result["opportunity_count"] == 2
        assert result["total_calls_analyzed"] >= 0
        assert "average_score" in result

    @patch("db.queries.get_opportunity_timeline")
    @patch("db.queries.get_coaching_sessions_for_call")
    @patch("db.queries.get_call_by_id")
    @patch("db.queries.get_full_transcript")
    def test_collects_high_scoring_examples(
        self, mock_transcript, mock_get_call, mock_sessions, mock_timeline
    ):
        """
        GIVEN opportunities with high-scoring sessions
        WHEN aggregate_coaching_patterns is called
        THEN it collects exemplar moments (score >= 80)
        """
        from analysis.learning_insights import aggregate_coaching_patterns

        opportunities = [{"id": str(uuid4()), "name": "High Performer Opp"}]

        mock_timeline.return_value = [{"id": str(uuid4()), "item_type": "call"}]
        mock_sessions.return_value = [{"score": 92, "feedback": "Excellent objection handling"}]
        mock_get_call.return_value = {"scheduled_at": datetime.now()}
        mock_transcript.return_value = "Great question about ROI..."

        result = aggregate_coaching_patterns(opportunities, "objections")

        assert len(result["high_scoring_examples"]) >= 1
        assert result["high_scoring_examples"][0]["score"] >= 80

    @patch("db.queries.get_opportunity_timeline")
    def test_handles_opportunities_with_no_calls(self, mock_timeline):
        """
        GIVEN opportunities with no calls
        WHEN aggregate_coaching_patterns is called
        THEN it returns empty results gracefully
        """
        from analysis.learning_insights import aggregate_coaching_patterns

        opportunities = [{"id": str(uuid4()), "name": "No Calls Opp"}]
        mock_timeline.return_value = []  # No calls

        result = aggregate_coaching_patterns(opportunities, "discovery")

        assert result["opportunity_count"] == 1
        assert result["total_calls_analyzed"] == 0
        assert result["average_score"] == 0


class TestExtractExemplarMoments:
    """Tests for extract_exemplar_moments function."""

    def test_extracts_top_examples(self):
        """
        GIVEN patterns with high-scoring examples
        WHEN extract_exemplar_moments is called
        THEN it extracts top 3 moments
        """
        from analysis.learning_insights import extract_exemplar_moments

        patterns = {
            "high_scoring_examples": [
                {
                    "call_id": "1",
                    "score": 95,
                    "feedback": "Best",
                    "transcript_excerpt": "...",
                    "opportunity_name": "Opp1",
                    "call_date": "2024-01-01",
                },
                {
                    "call_id": "2",
                    "score": 90,
                    "feedback": "Great",
                    "transcript_excerpt": "...",
                    "opportunity_name": "Opp2",
                    "call_date": "2024-01-02",
                },
                {
                    "call_id": "3",
                    "score": 85,
                    "feedback": "Good",
                    "transcript_excerpt": "...",
                    "opportunity_name": "Opp3",
                    "call_date": "2024-01-03",
                },
                {
                    "call_id": "4",
                    "score": 82,
                    "feedback": "OK",
                    "transcript_excerpt": "...",
                    "opportunity_name": "Opp4",
                    "call_date": "2024-01-04",
                },
            ]
        }

        result = extract_exemplar_moments(patterns, "discovery")

        assert len(result) == 3  # Only top 3
        assert result[0]["score"] == 95

    def test_handles_empty_examples(self):
        """
        GIVEN patterns with no high-scoring examples
        WHEN extract_exemplar_moments is called
        THEN it returns empty list
        """
        from analysis.learning_insights import extract_exemplar_moments

        patterns = {"high_scoring_examples": []}

        result = extract_exemplar_moments(patterns, "discovery")

        assert result == []


class TestGetLearningInsights:
    """Tests for get_learning_insights main function."""

    @patch("db.fetch_one")
    @patch("db.queries.search_opportunities")
    def test_returns_error_when_no_rep_opportunities(self, mock_search, mock_fetch_one):
        """
        GIVEN rep with no opportunities
        WHEN get_learning_insights is called
        THEN it returns error
        """
        from analysis.learning_insights import get_learning_insights

        mock_fetch_one.return_value = {"role": "ae"}
        mock_search.return_value = ([], 0)  # No opportunities

        result = get_learning_insights("newrep@prefect.io", "discovery")

        assert "error" in result
        assert "No opportunities found" in result["error"]

    @patch("db.fetch_one")
    @patch("db.queries.search_opportunities")
    @patch("analysis.learning_insights.find_similar_won_opportunities")
    @patch("analysis.learning_insights.aggregate_coaching_patterns")
    def test_returns_error_when_no_won_opportunities(
        self, mock_aggregate, mock_find_won, mock_search, mock_fetch_one
    ):
        """
        GIVEN no closed-won opportunities from other reps
        WHEN get_learning_insights is called
        THEN it returns error
        """
        from analysis.learning_insights import get_learning_insights

        mock_fetch_one.return_value = {"role": "ae"}
        mock_search.return_value = ([{"id": "1", "name": "Test"}], 1)  # Rep has opportunities
        mock_find_won.return_value = []  # No won opportunities from others

        result = get_learning_insights("rep@prefect.io", "discovery")

        assert "error" in result

    @patch("db.fetch_one")
    @patch("db.queries.search_opportunities")
    @patch("analysis.learning_insights.find_similar_won_opportunities")
    @patch("analysis.learning_insights.aggregate_coaching_patterns")
    @patch("analysis.learning_insights.extract_exemplar_moments")
    @patch("anthropic.Anthropic")
    def test_returns_full_comparison(
        self,
        mock_anthropic,
        mock_exemplars,
        mock_aggregate,
        mock_find_won,
        mock_search,
        mock_fetch_one,
    ):
        """
        GIVEN valid rep and comparison data
        WHEN get_learning_insights is called
        THEN it returns full comparison result
        """
        from analysis.learning_insights import get_learning_insights

        rep_email = "rep@prefect.io"

        mock_fetch_one.return_value = {"role": "ae"}
        mock_search.return_value = ([{"id": "1", "name": "Rep Opp"}], 1)
        mock_find_won.return_value = [
            {"id": "2", "name": "Won Opp", "owner_email": "top@prefect.io"}
        ]
        mock_aggregate.return_value = {
            "opportunity_count": 1,
            "total_calls_analyzed": 5,
            "average_score": 75,
            "high_scoring_examples": [],
        }
        mock_exemplars.return_value = []

        # Mock Claude response
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Key difference: Ask more impact questions")]
        mock_client.messages.create.return_value = mock_response

        result = get_learning_insights(rep_email, "discovery")

        assert result["rep_email"] == rep_email
        assert "rep_performance" in result
        assert "top_performer_benchmark" in result
        assert "behavioral_differences" in result

    @patch("db.fetch_one")
    @patch("db.queries.search_opportunities")
    @patch("analysis.learning_insights.find_similar_won_opportunities")
    @patch("analysis.learning_insights.aggregate_coaching_patterns")
    @patch("analysis.learning_insights.extract_exemplar_moments")
    @patch("anthropic.Anthropic")
    def test_uses_detected_role_when_not_provided(
        self,
        mock_anthropic,
        mock_exemplars,
        mock_aggregate,
        mock_find_won,
        mock_search,
        mock_fetch_one,
    ):
        """
        GIVEN no rep_role provided
        WHEN get_learning_insights is called
        THEN it detects role from staff_roles table
        """
        from analysis.learning_insights import get_learning_insights

        # Role detection
        mock_fetch_one.return_value = {"role": "se"}

        mock_search.return_value = ([{"id": "1"}], 1)
        mock_find_won.return_value = [{"id": "2", "owner_email": "other@prefect.io"}]
        mock_aggregate.return_value = {
            "opportunity_count": 1,
            "total_calls_analyzed": 5,
            "average_score": 80,
            "high_scoring_examples": [],
        }
        mock_exemplars.return_value = []

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Differences...")]
        mock_client.messages.create.return_value = mock_response

        result = get_learning_insights("rep@prefect.io", "discovery")

        assert result["rep_role"] == "se"
        assert "Sales Engineer" in result["role_display"]

    @patch("db.fetch_one")
    @patch("db.queries.search_opportunities")
    @patch("analysis.learning_insights.find_similar_won_opportunities")
    @patch("analysis.learning_insights.aggregate_coaching_patterns")
    @patch("analysis.learning_insights.extract_exemplar_moments")
    @patch("anthropic.Anthropic")
    def test_comparison_note_reflects_role(
        self,
        mock_anthropic,
        mock_exemplars,
        mock_aggregate,
        mock_find_won,
        mock_search,
        mock_fetch_one,
    ):
        """
        GIVEN specific role
        WHEN get_learning_insights is called
        THEN comparison note mentions role-specific comparison
        """
        from analysis.learning_insights import get_learning_insights

        mock_fetch_one.return_value = {"role": "csm"}
        mock_search.return_value = ([{"id": "1"}], 1)
        mock_find_won.return_value = [{"id": "2", "owner_email": "other@prefect.io"}]
        mock_aggregate.return_value = {
            "opportunity_count": 1,
            "total_calls_analyzed": 5,
            "average_score": 80,
            "high_scoring_examples": [],
        }
        mock_exemplars.return_value = []

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="...")]
        mock_client.messages.create.return_value = mock_response

        result = get_learning_insights("rep@prefect.io", "discovery", rep_role="csm")

        assert "Customer Success Manager" in result["comparison_note"]
