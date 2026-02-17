"""
Unit tests for opportunity coaching analysis functions.

Tests cover:
- analyze_opportunity_patterns
- identify_recurring_themes
- analyze_objection_progression
- assess_relationship_strength
- generate_coaching_recommendations
- detect_speaker_role
- cache key generation
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
    with patch("analysis.opportunity_coaching.settings") as mock_settings:
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.claude_model = "claude-sonnet-4-5-20250929"
        yield mock_settings


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    @patch("db.queries.get_opportunity_timeline")
    def test_cache_key_includes_call_ids(self, mock_timeline):
        """
        GIVEN an opportunity with calls
        WHEN _get_opportunity_cache_key is called
        THEN the cache key includes all call IDs
        """
        from analysis.opportunity_coaching import _get_opportunity_cache_key

        opp_id = str(uuid4())
        call_ids = [str(uuid4()), str(uuid4())]
        mock_timeline.return_value = [
            {"id": call_ids[0], "item_type": "call"},
            {"id": call_ids[1], "item_type": "call"},
            {"id": str(uuid4()), "item_type": "email"},  # Should be excluded
        ]

        key1 = _get_opportunity_cache_key(opp_id, "patterns")

        assert key1 is not None
        assert len(key1) == 64  # SHA256 hex length

        # Verify cache key changes when calls change
        mock_timeline.return_value.append({"id": str(uuid4()), "item_type": "call"})
        key2 = _get_opportunity_cache_key(opp_id, "patterns")

        assert key1 != key2


class TestAnalyzeOpportunityPatterns:
    """Tests for analyze_opportunity_patterns function."""

    @pytest.fixture
    def sample_coaching_session(self) -> dict[str, Any]:
        """Sample coaching session data."""
        return {
            "score": 75,
            "created_at": datetime.now(),
            "feedback": "Good discovery questions",
        }

    @patch("analysis.opportunity_coaching._get_cached_analysis")
    @patch("analysis.opportunity_coaching._set_cached_analysis")
    @patch("db.queries.get_opportunity")
    @patch("db.queries.search_opportunities")
    @patch("db.queries.get_opportunity_timeline")
    @patch("db.queries.get_coaching_sessions_for_call")
    def test_patterns_aggregates_scores_by_dimension(
        self,
        mock_sessions,
        mock_timeline,
        mock_search,
        mock_get_opp,
        mock_set_cache,
        mock_get_cache,
        sample_coaching_session,
    ):
        """
        GIVEN opportunity with multiple calls
        WHEN analyze_opportunity_patterns is called
        THEN it aggregates scores per dimension
        """
        from analysis.opportunity_coaching import analyze_opportunity_patterns

        opp_id = str(uuid4())
        mock_get_cache.return_value = None  # No cache hit
        mock_get_opp.return_value = {"name": "Test Opp", "id": opp_id}
        mock_search.return_value = ([], 0)
        mock_timeline.return_value = [
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "call"},
        ]
        mock_sessions.return_value = [sample_coaching_session]

        result = analyze_opportunity_patterns(opp_id, use_cache=True)

        assert result["call_count"] == 2
        assert "average_scores" in result

    @patch("analysis.opportunity_coaching._get_cached_analysis")
    @patch("db.queries.get_opportunity")
    @patch("db.queries.search_opportunities")
    @patch("db.queries.get_opportunity_timeline")
    def test_patterns_returns_message_when_no_calls(
        self, mock_timeline, mock_search, mock_get_opp, mock_get_cache
    ):
        """
        GIVEN opportunity with no calls
        WHEN analyze_opportunity_patterns is called
        THEN it returns message about no calls
        """
        from analysis.opportunity_coaching import analyze_opportunity_patterns

        opp_id = str(uuid4())
        mock_get_cache.return_value = None
        mock_get_opp.return_value = {"name": "Test Opp", "id": opp_id}
        mock_search.return_value = ([], 0)
        mock_timeline.return_value = []  # No calls

        result = analyze_opportunity_patterns(opp_id, use_cache=False)

        assert result["call_count"] == 0
        assert "message" in result
        assert "No calls" in result["message"]

    @patch("analysis.opportunity_coaching.queries.get_opportunity")
    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_patterns_raises_for_missing_opportunity(
        self, mock_get_cache, mock_timeline, mock_get_opp
    ):
        """
        GIVEN nonexistent opportunity ID
        WHEN analyze_opportunity_patterns is called
        THEN it raises ValueError
        """
        from analysis.opportunity_coaching import analyze_opportunity_patterns

        mock_get_cache.return_value = None
        mock_timeline.return_value = []  # For cache key generation
        mock_get_opp.return_value = None

        with pytest.raises(ValueError) as exc:
            analyze_opportunity_patterns("nonexistent-id")

        assert "not found" in str(exc.value)

    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_patterns_uses_cache_when_available(self, mock_get_cache, mock_timeline):
        """
        GIVEN cached analysis
        WHEN analyze_opportunity_patterns is called with use_cache=True
        THEN it returns cached result
        """
        from analysis.opportunity_coaching import analyze_opportunity_patterns

        cached_result = {"call_count": 5, "average_scores": {"discovery": 80}}
        mock_get_cache.return_value = cached_result
        mock_timeline.return_value = []  # Won't be called due to cache hit

        result = analyze_opportunity_patterns("any-id", use_cache=True)

        assert result == cached_result


class TestIdentifyRecurringThemes:
    """Tests for identify_recurring_themes function."""

    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_themes_returns_empty_when_no_calls(self, mock_get_cache, mock_timeline):
        """
        GIVEN opportunity with no calls
        WHEN identify_recurring_themes is called
        THEN it returns empty themes
        """
        from analysis.opportunity_coaching import identify_recurring_themes

        mock_get_cache.return_value = None
        mock_timeline.return_value = []

        result = identify_recurring_themes(str(uuid4()), use_cache=False)

        assert result["themes"] == []
        assert "message" in result

    @patch("analysis.opportunity_coaching.anthropic.Anthropic")
    @patch("analysis.opportunity_coaching.queries.get_call_by_id")
    @patch("analysis.opportunity_coaching.queries.get_full_transcript")
    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._set_cached_analysis")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_themes_calls_claude_for_analysis(
        self,
        mock_get_cache,
        mock_set_cache,
        mock_timeline,
        mock_transcript,
        mock_get_call,
        mock_anthropic,
    ):
        """
        GIVEN opportunity with calls
        WHEN identify_recurring_themes is called
        THEN it uses Claude to analyze transcripts
        """
        from analysis.opportunity_coaching import identify_recurring_themes

        opp_id = str(uuid4())
        call_id = str(uuid4())

        mock_get_cache.return_value = None
        mock_timeline.return_value = [{"id": call_id, "item_type": "call"}]
        mock_transcript.return_value = "Sample transcript text..."
        mock_get_call.return_value = {"scheduled_at": datetime.now()}

        # Mock Claude response
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Theme 1: Pricing concerns")]
        mock_client.messages.create.return_value = mock_response

        result = identify_recurring_themes(opp_id, use_cache=False)

        assert "themes" in result
        mock_client.messages.create.assert_called_once()


class TestAnalyzeObjectionProgression:
    """Tests for analyze_objection_progression function."""

    @patch("analysis.opportunity_coaching.anthropic.Anthropic")
    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_objections_returns_empty_when_no_calls(
        self, mock_get_cache, mock_timeline, mock_anthropic
    ):
        """
        GIVEN opportunity with no calls
        WHEN analyze_objection_progression is called
        THEN it handles gracefully
        """
        from analysis.opportunity_coaching import analyze_objection_progression

        mock_get_cache.return_value = None
        mock_timeline.return_value = []

        # Mock Claude for empty case
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="No objection data available")]
        mock_client.messages.create.return_value = mock_response

        result = analyze_objection_progression(str(uuid4()), use_cache=False)

        assert "calls_analyzed" in result or "objection_analysis" in result


class TestAssessRelationshipStrength:
    """Tests for assess_relationship_strength function."""

    @patch("analysis.opportunity_coaching._get_cached_analysis")
    @patch("analysis.opportunity_coaching._set_cached_analysis")
    @patch("db.queries.get_opportunity_timeline")
    @patch("db.queries.get_call_by_id")
    def test_relationship_calculates_metrics(
        self, mock_get_call, mock_timeline, mock_set_cache, mock_get_cache
    ):
        """
        GIVEN opportunity with calls and emails
        WHEN assess_relationship_strength is called
        THEN it calculates engagement metrics
        """
        from analysis.opportunity_coaching import assess_relationship_strength

        opp_id = str(uuid4())

        mock_get_cache.return_value = None
        mock_timeline.return_value = [
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "email"},
            {"id": str(uuid4()), "item_type": "email"},
            {"id": str(uuid4()), "item_type": "email"},
        ]
        mock_get_call.return_value = {
            "scheduled_at": datetime.now(),
            "duration": 1800,
        }

        result = assess_relationship_strength(opp_id, use_cache=False)

        assert result["call_count"] == 2
        assert result["email_count"] == 3
        assert "email_to_call_ratio" in result
        assert result["email_to_call_ratio"] == 1.5  # 3 emails / 2 calls

    @patch("analysis.opportunity_coaching._get_cached_analysis")
    @patch("analysis.opportunity_coaching._set_cached_analysis")
    @patch("db.queries.get_opportunity_timeline")
    @patch("db.queries.get_call_by_id")
    def test_relationship_detects_trend(
        self, mock_get_call, mock_timeline, mock_set_cache, mock_get_cache
    ):
        """
        GIVEN multiple calls with varying duration
        WHEN assess_relationship_strength is called
        THEN it determines duration trend
        """
        from analysis.opportunity_coaching import assess_relationship_strength

        opp_id = str(uuid4())

        mock_get_cache.return_value = None
        mock_timeline.return_value = [
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "call"},
            {"id": str(uuid4()), "item_type": "call"},
        ]

        # Simulate increasing call durations
        durations = [1000, 1200, 2000, 2500]
        call_idx = [0]

        def get_call_side_effect(call_id):
            duration = durations[call_idx[0] % len(durations)]
            call_idx[0] += 1
            return {"scheduled_at": datetime.now(), "duration": duration}

        mock_get_call.side_effect = get_call_side_effect

        result = assess_relationship_strength(opp_id, use_cache=False)

        assert result["call_duration_trend"] in ["strengthening", "weakening", "stable"]


class TestDetectSpeakerRole:
    """Tests for detect_speaker_role function."""

    @patch("db.queries.get_speakers_for_call")
    @patch("db.queries.get_staff_role")
    def test_detects_ae_role(self, mock_staff_role, mock_speakers):
        """
        GIVEN call with AE speaker
        WHEN detect_speaker_role is called
        THEN it returns 'ae'
        """
        from analysis.opportunity_coaching import detect_speaker_role

        call_id = str(uuid4())
        mock_speakers.return_value = [
            {
                "email": "sarah@prefect.io",
                "company_side": True,
                "talk_time_percentage": 60,
            },
        ]
        mock_staff_role.return_value = "ae"

        result = detect_speaker_role(call_id)

        assert result == "ae"

    @patch("db.queries.get_speakers_for_call")
    @patch("db.queries.get_staff_role")
    def test_defaults_to_ae_when_no_role(self, mock_staff_role, mock_speakers):
        """
        GIVEN call with speaker without assigned role
        WHEN detect_speaker_role is called
        THEN it defaults to 'ae'
        """
        from analysis.opportunity_coaching import detect_speaker_role

        mock_speakers.return_value = [
            {
                "email": "new@prefect.io",
                "company_side": True,
                "talk_time_percentage": 60,
            },
        ]
        mock_staff_role.return_value = None

        result = detect_speaker_role(str(uuid4()))

        assert result == "ae"

    @patch("db.queries.get_speakers_for_call")
    def test_defaults_to_ae_when_no_prefect_speakers(self, mock_speakers):
        """
        GIVEN call with no Prefect speakers
        WHEN detect_speaker_role is called
        THEN it defaults to 'ae'
        """
        from analysis.opportunity_coaching import detect_speaker_role

        mock_speakers.return_value = [
            {"email": "customer@acme.com", "company_side": False, "talk_time_percentage": 80},
        ]

        result = detect_speaker_role(str(uuid4()))

        assert result == "ae"


class TestGenerateCoachingRecommendations:
    """Tests for generate_coaching_recommendations function."""

    @patch("analysis.opportunity_coaching.anthropic.Anthropic")
    @patch("analysis.opportunity_coaching.assess_relationship_strength")
    @patch("analysis.opportunity_coaching.analyze_objection_progression")
    @patch("analysis.opportunity_coaching.identify_recurring_themes")
    @patch("analysis.opportunity_coaching.analyze_opportunity_patterns")
    @patch("analysis.opportunity_coaching._set_cached_analysis")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_recommendations_uses_all_analyses(
        self,
        mock_get_cache,
        mock_set_cache,
        mock_patterns,
        mock_themes,
        mock_objections,
        mock_relationship,
        mock_anthropic,
    ):
        """
        GIVEN opportunity with analysis data
        WHEN generate_coaching_recommendations is called
        THEN it synthesizes recommendations from all analyses
        """
        from analysis.opportunity_coaching import generate_coaching_recommendations

        opp_id = str(uuid4())

        mock_get_cache.return_value = None
        mock_patterns.return_value = {"call_count": 5, "average_scores": {}}
        mock_themes.return_value = {"themes": "Pricing concerns"}
        mock_objections.return_value = {"objection_analysis": "Security objections recurring"}
        mock_relationship.return_value = {
            "call_count": 5,
            "email_count": 10,
            "email_to_call_ratio": 2.0,
            "call_duration_trend": "stable",
        }

        # Mock Claude response
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="1. Address pricing early\n2. Prepare security documentation\n3. Follow up more frequently"
            )
        ]
        mock_client.messages.create.return_value = mock_response

        result = generate_coaching_recommendations(opp_id, use_cache=False)

        assert isinstance(result, list)
        assert len(result) >= 1

    @patch("analysis.opportunity_coaching.queries.get_opportunity_timeline")
    @patch("analysis.opportunity_coaching._get_cached_analysis")
    def test_recommendations_returns_cached_list(self, mock_get_cache, mock_timeline):
        """
        GIVEN cached recommendations
        WHEN generate_coaching_recommendations is called
        THEN it returns the cached list
        """
        from analysis.opportunity_coaching import generate_coaching_recommendations

        cached_recs = ["Rec 1", "Rec 2", "Rec 3"]
        mock_get_cache.return_value = cached_recs
        mock_timeline.return_value = []  # Won't be called due to cache hit

        result = generate_coaching_recommendations("any-id", use_cache=True)

        assert result == cached_recs
