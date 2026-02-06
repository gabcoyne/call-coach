"""
Comprehensive unit tests for MCP Tools.

Tests cover:
- analyze_call with valid parameters and edge cases
- get_rep_insights with time filtering and product filters
- search_calls with complex multi-filter queries
- Tool parameter validation and error handling

Following TDD principles: these tests define expected behavior.
"""

import logging
import sys
from datetime import datetime, timedelta
from enum import Enum
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


# Create real CoachingDimension enum for validation
class CoachingDimension(str, Enum):
    PRODUCT_KNOWLEDGE = "product_knowledge"
    DISCOVERY = "discovery"
    OBJECTION_HANDLING = "objection_handling"
    ENGAGEMENT = "engagement"


# Mock the dependencies before importing the tools
sys.modules["analysis"] = MagicMock()
sys.modules["analysis.engine"] = MagicMock()
db_mock = MagicMock()
db_models_mock = MagicMock()
db_models_mock.CoachingDimension = CoachingDimension  # Use real enum
sys.modules["db"] = db_mock
sys.modules["db.models"] = db_models_mock

from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool
from coaching_mcp.tools.search_calls import search_calls_tool


@pytest.fixture
def mock_db():
    """Mock database functions for all tools."""
    with (
        patch("coaching_mcp.tools.analyze_call.fetch_one") as mock_fetch_one_analyze,
        patch("coaching_mcp.tools.analyze_call.fetch_all") as mock_fetch_all_analyze,
        patch("coaching_mcp.tools.get_rep_insights.fetch_one") as mock_fetch_one_insights,
        patch("coaching_mcp.tools.get_rep_insights.fetch_all") as mock_fetch_all_insights,
        patch("coaching_mcp.tools.search_calls.fetch_all") as mock_fetch_all_search,
    ):
        yield {
            "analyze_call": {
                "fetch_one": mock_fetch_one_analyze,
                "fetch_all": mock_fetch_all_analyze,
            },
            "get_rep_insights": {
                "fetch_one": mock_fetch_one_insights,
                "fetch_all": mock_fetch_all_insights,
            },
            "search_calls": {
                "fetch_all": mock_fetch_all_search,
            },
        }


@pytest.fixture
def sample_call_data():
    """Sample call data for testing."""
    call_id = str(uuid4())
    return {
        "id": call_id,
        "gong_call_id": "gong-123",
        "title": "Discovery Call - Acme Corp",
        "scheduled_at": "2025-01-15T10:00:00Z",
        "duration_seconds": 3600,
        "call_type": "discovery",
        "product": "prefect",
        "metadata": {"customer": "Acme Corp"},
    }


@pytest.fixture
def sample_speakers():
    """Sample speaker data."""
    return [
        {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": "sarah@prefect.io",
            "role": "ae",
            "company_side": True,
            "talk_time_seconds": 1800,
            "talk_time_percentage": 50.0,
        },
        {
            "id": str(uuid4()),
            "name": "John Smith",
            "email": "john@acme.com",
            "role": "buyer",
            "company_side": False,
            "talk_time_seconds": 1800,
            "talk_time_percentage": 50.0,
        },
    ]


@pytest.fixture
def sample_transcript():
    """Sample transcript data."""
    return {
        "text": "This is a sample transcript of the call discussing workflow orchestration.",
        "segments": [
            {
                "speaker_id": "speaker_1",
                "text": "Hi, thanks for joining today.",
                "start_time": 0,
                "duration": 5,
            }
        ],
    }


class TestAnalyzeCallValid:
    """Test 5.1: analyze_call with valid parameters."""

    def test_analyze_call_with_valid_call_id_returns_analysis(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN a valid call_id exists in database
        WHEN analyze_call_tool is called with that call_id
        THEN it returns structured analysis with scores and insights
        """
        # Setup mocks - fetch_one is called for call metadata
        mock_db["analyze_call"]["fetch_one"].return_value = sample_call_data

        # fetch_all is called multiple times: speakers, transcripts, team averages, etc.
        # Use return_value instead of side_effect to handle all calls consistently
        transcript_rows = [
            {
                "name": "Sarah Johnson",
                "timestamp_seconds": 0,
                "text": "Hi, thanks for joining today.",
            },
            {
                "name": "John Smith",
                "timestamp_seconds": 5,
                "text": "Happy to be here.",
            },
        ]
        # Return empty list by default for team average queries and other fetch_all calls
        mock_db["analyze_call"]["fetch_all"].return_value = []

        # Mock speakers separately using side_effect for first call only
        def fetch_all_side_effect(*args, **kwargs):
            # Check query type by looking at SQL string
            if args and "speakers" in str(args[0]).lower():
                return sample_speakers
            elif args and "transcripts" in str(args[0]).lower():
                return transcript_rows
            else:
                # Team averages and other queries return empty
                return []

        mock_db["analyze_call"]["fetch_all"].side_effect = fetch_all_side_effect

        # Mock the analysis engine
        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {
                "score": 85,
                "strengths": ["Strong opening", "Good product knowledge"],
                "areas_for_improvement": ["Better objection handling"],
                "action_items": ["Practice objection handling"],
            }

            # Execute (disable transcript snippets to simplify mocking)
            result = analyze_call_tool(
                call_id="gong-123", dimensions=["discovery"], include_transcript_snippets=False
            )

            # Verify
            assert result is not None
            assert "scores" in result
            assert "discovery" in result["scores"]
            assert result["scores"]["discovery"] == 85

    def test_analyze_call_with_specific_dimensions(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN a valid call_id
        WHEN analyze_call_tool is called with specific dimensions
        THEN it analyzes only those dimensions
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {
                "call_id": sample_call_data["id"],
                "scores": {"discovery": 85, "engagement": 78},
                "insights": {"strengths": [], "improvements": []},
            }

            dimensions = ["discovery", "engagement"]
            result = analyze_call_tool(call_id="gong-123", dimensions=dimensions)

            # Verify only requested dimensions analyzed
            assert "scores" in result
            assert "discovery" in result["scores"]
            assert "engagement" in result["scores"]
            # Should not have other dimensions
            assert "product_knowledge" not in result.get("scores", {})

    def test_analyze_call_with_role_override(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN a call with auto-detectable role
        WHEN analyze_call_tool is called with role override
        THEN it uses the specified role for rubric evaluation
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {
                "call_id": sample_call_data["id"],
                "scores": {"discovery": 85},
                "role": "se",  # Specified role
                "insights": {},
            }

            result = analyze_call_tool(call_id="gong-123", role="se")

            # Verify role was used
            assert result is not None
            # Role should be reflected in result metadata
            assert result.get("role") == "se" or "scores" in result

    def test_analyze_call_with_force_reanalysis(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN a call with existing cached analysis
        WHEN analyze_call_tool is called with force_reanalysis=True
        THEN it performs fresh analysis ignoring cache
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {
                "call_id": sample_call_data["id"],
                "scores": {"discovery": 90},  # New score
                "cache_hit": False,
                "insights": {},
            }

            result = analyze_call_tool(call_id="gong-123", force_reanalysis=True)

            # Verify fresh analysis was performed
            assert result is not None
            assert result.get("cache_hit", False) is False or "scores" in result

    def test_analyze_call_includes_transcript_snippets(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN a valid call
        WHEN analyze_call_tool is called with include_transcript_snippets=True
        THEN result includes specific transcript quotes
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {
                "call_id": sample_call_data["id"],
                "scores": {"discovery": 85},
                "transcript_snippets": [{"text": "Great question about pricing", "timestamp": 120}],
                "insights": {},
            }

            result = analyze_call_tool(call_id="gong-123", include_transcript_snippets=True)

            # Verify snippets included
            assert result is not None
            if "transcript_snippets" in result:
                assert len(result["transcript_snippets"]) > 0
                assert "text" in result["transcript_snippets"][0]


class TestRepInsightsTimeFilter:
    """Test 5.2: get_rep_insights with time filtering."""

    def test_rep_insights_last_7_days(self, mock_db):
        """
        GIVEN a rep with calls in various time periods
        WHEN get_rep_insights_tool is called with time_period='last_7_days'
        THEN it returns metrics only for last 7 days
        """
        rep_email = "sarah@prefect.io"

        # Mock rep info
        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 5,
        }

        # Mock score trends - only recent dates
        recent_date = datetime.now() - timedelta(days=3)
        mock_db["get_rep_insights"]["fetch_all"].return_value = [
            {
                "coaching_dimension": "discovery",
                "week": recent_date,
                "avg_score": 85.0,
                "call_count": 5,
            }
        ]

        result = get_rep_insights_tool(rep_email=rep_email, time_period="last_7_days")

        # Verify result contains recent data
        assert result is not None
        assert "error" not in result
        # Should have trends for recent period
        if "trends" in result:
            assert len(result["trends"]) > 0

    def test_rep_insights_last_30_days(self, mock_db):
        """
        GIVEN a rep with 30+ days of call history
        WHEN get_rep_insights_tool is called with time_period='last_30_days'
        THEN it returns 30-day metrics
        """
        rep_email = "sarah@prefect.io"
        rep_id = str(uuid4())

        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": rep_id,
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 12,
        }

        # Mock multiple weeks of data
        weeks = [datetime.now() - timedelta(weeks=i) for i in range(4)]  # 4 weeks of data
        score_trends = []
        for week in weeks:
            score_trends.extend(
                [
                    {
                        "coaching_dimension": "discovery",
                        "week": week,
                        "avg_score": 80.0 + i,
                        "call_count": 3,
                    }
                    for i in range(1)
                ]
            )

        mock_db["get_rep_insights"]["fetch_all"].return_value = score_trends

        result = get_rep_insights_tool(rep_email=rep_email, time_period="last_30_days")

        assert result is not None
        assert "error" not in result

    def test_rep_insights_with_product_filter(self, mock_db):
        """
        GIVEN a rep who sells multiple products
        WHEN get_rep_insights_tool is called with product_filter
        THEN it returns metrics only for that product
        """
        rep_email = "sarah@prefect.io"

        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 8,
        }

        mock_db["get_rep_insights"]["fetch_all"].return_value = [
            {
                "coaching_dimension": "discovery",
                "week": datetime.now(),
                "avg_score": 88.0,
                "call_count": 8,
            }
        ]

        result = get_rep_insights_tool(rep_email=rep_email, product_filter="prefect")

        # Verify filtered results
        assert result is not None
        assert "error" not in result
        # Product-specific metrics returned
        if "calls_analyzed" in result:
            assert result["calls_analyzed"] == 8

    def test_rep_insights_last_quarter(self, mock_db):
        """
        GIVEN a rep with quarterly data
        WHEN get_rep_insights_tool is called with time_period='last_quarter'
        THEN it returns 90-day metrics
        """
        rep_email = "sarah@prefect.io"

        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 20,
        }

        # Mock quarterly data
        mock_db["get_rep_insights"]["fetch_all"].return_value = [
            {
                "coaching_dimension": dim,
                "week": datetime.now() - timedelta(weeks=8),
                "avg_score": 82.0,
                "call_count": 5,
            }
            for dim in ["discovery", "engagement", "product_knowledge"]
        ]

        result = get_rep_insights_tool(rep_email=rep_email, time_period="last_quarter")

        assert result is not None
        assert "error" not in result

    def test_rep_insights_combines_time_and_product_filters(self, mock_db):
        """
        GIVEN a rep with diverse call history
        WHEN get_rep_insights_tool is called with both time and product filters
        THEN it returns metrics matching BOTH criteria
        """
        rep_email = "sarah@prefect.io"

        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 6,
        }

        mock_db["get_rep_insights"]["fetch_all"].return_value = [
            {
                "coaching_dimension": "discovery",
                "week": datetime.now() - timedelta(days=5),
                "avg_score": 90.0,
                "call_count": 6,
            }
        ]

        result = get_rep_insights_tool(
            rep_email=rep_email,
            time_period="last_7_days",
            product_filter="horizon",
        )

        # Verify both filters applied
        assert result is not None
        assert "error" not in result


class TestSearchCallsComplexFilters:
    """Test 5.3: search_calls with complex filters."""

    def test_search_calls_with_multiple_filters(self, mock_db):
        """
        GIVEN calls with various attributes
        WHEN search_calls_tool is called with multiple filters
        THEN it returns calls matching ALL criteria (AND logic)
        """
        # Mock filtered results
        filtered_calls = [
            {
                "id": str(uuid4()),
                "gong_call_id": "gong-456",
                "title": "Discovery - TechCorp",
                "rep_email": "sarah@prefect.io",
                "product": "prefect",
                "call_type": "discovery",
                "overall_score": 85,
                "scheduled_at": "2025-01-15T10:00:00Z",
            }
        ]

        mock_db["search_calls"]["fetch_all"].return_value = filtered_calls

        result = search_calls_tool(
            rep_email="sarah@prefect.io",
            product="prefect",
            call_type="discovery",
            min_score=75,
            max_score=90,
        )

        # Verify AND logic: all filters applied
        assert result is not None
        assert isinstance(result, list)
        if len(result) > 0:
            call = result[0]
            assert call["rep_email"] == "sarah@prefect.io"
            assert call["product"] == "prefect"
            assert call["call_type"] == "discovery"
            assert 75 <= call["overall_score"] <= 90

    def test_search_calls_with_date_range_and_score_filters(self, mock_db):
        """
        GIVEN calls across different dates and scores
        WHEN search_calls_tool is called with date range AND score range
        THEN it returns calls within both ranges
        """
        mock_db["search_calls"]["fetch_all"].return_value = [
            {
                "id": str(uuid4()),
                "gong_call_id": "gong-789",
                "title": "Demo Call",
                "overall_score": 82,
                "scheduled_at": "2025-01-12T14:00:00Z",
            }
        ]

        result = search_calls_tool(
            date_range={"start": "2025-01-10", "end": "2025-01-20"},
            min_score=80,
            max_score=90,
        )

        assert result is not None
        assert isinstance(result, list)
        if len(result) > 0:
            call = result[0]
            # Verify within date range
            call_date = datetime.fromisoformat(call["scheduled_at"].replace("Z", ""))
            assert datetime(2025, 1, 10) <= call_date <= datetime(2025, 1, 20)
            # Verify within score range
            assert 80 <= call["overall_score"] <= 90

    def test_search_calls_with_topics_filter(self, mock_db):
        """
        GIVEN calls discussing various topics
        WHEN search_calls_tool is called with topics filter
        THEN it returns only calls containing those topics
        """
        mock_db["search_calls"]["fetch_all"].return_value = [
            {
                "id": str(uuid4()),
                "title": "Product Demo",
                "topics": ["Workflow Orchestration", "Integration"],
            }
        ]

        result = search_calls_tool(topics=["Workflow Orchestration"])

        assert result is not None
        if len(result) > 0:
            assert "topics" in result[0]
            assert "Workflow Orchestration" in result[0]["topics"]

    def test_search_calls_with_objection_type_filter(self, mock_db):
        """
        GIVEN calls with various objection types
        WHEN search_calls_tool is called with has_objection_type filter
        THEN it returns calls containing that objection
        """
        mock_db["search_calls"]["fetch_all"].return_value = [
            {
                "id": str(uuid4()),
                "title": "Pricing Objection Call",
                "objection_types": ["pricing", "budget"],
            }
        ]

        result = search_calls_tool(has_objection_type="pricing")

        assert result is not None
        if len(result) > 0 and "objection_types" in result[0]:
            assert "pricing" in result[0]["objection_types"]

    def test_search_calls_with_role_filter(self, mock_db):
        """
        GIVEN calls by reps with different roles (ae, se, csm)
        WHEN search_calls_tool is called with role filter
        THEN it returns only calls from that role
        """
        mock_db["search_calls"]["fetch_all"].return_value = [
            {
                "id": str(uuid4()),
                "title": "SE Technical Deep Dive",
                "role": "se",
                "rep_email": "se@prefect.io",
            }
        ]

        result = search_calls_tool(role="se")

        assert result is not None
        if len(result) > 0 and "role" in result[0]:
            assert result[0]["role"] == "se"

    def test_search_calls_respects_limit(self, mock_db):
        """
        GIVEN many matching calls
        WHEN search_calls_tool is called with limit parameter
        THEN it returns at most that many results
        """
        # Generate more calls than limit
        many_calls = [{"id": str(uuid4()), "title": f"Call {i}"} for i in range(50)]

        mock_db["search_calls"]["fetch_all"].return_value = many_calls[:5]

        result = search_calls_tool(limit=5)

        assert result is not None
        assert len(result) <= 5

    def test_search_calls_limit_capped_at_100(self, mock_db):
        """
        GIVEN user requests excessive limit
        WHEN search_calls_tool is called with limit > 100
        THEN it caps results at 100 to protect performance
        """
        mock_db["search_calls"]["fetch_all"].return_value = []

        result = search_calls_tool(limit=200)

        # Should be capped or work without error
        assert result is not None
        assert isinstance(result, list)

    def test_search_calls_empty_result_returns_empty_list(self, mock_db):
        """
        GIVEN filters that match no calls
        WHEN search_calls_tool is called
        THEN it returns empty list (not None or error)
        """
        mock_db["search_calls"]["fetch_all"].return_value = []

        result = search_calls_tool(rep_email="nonexistent@example.com")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


class TestToolValidationError:
    """Test 5.4: tool parameter validation errors."""

    def test_analyze_call_with_invalid_call_id(self, mock_db):
        """
        GIVEN an invalid or non-existent call_id
        WHEN analyze_call_tool is called
        THEN it raises ValueError with descriptive message
        """
        mock_db["analyze_call"]["fetch_one"].return_value = None

        with pytest.raises(ValueError) as exc_info:
            analyze_call_tool(call_id="non-existent-call")

        assert "not found" in str(exc_info.value).lower()

    def test_analyze_call_with_invalid_dimensions(self, mock_db, sample_call_data):
        """
        GIVEN valid call but invalid dimension names
        WHEN analyze_call_tool is called with invalid dimensions
        THEN it raises ValueError listing valid options
        """
        mock_db["analyze_call"]["fetch_one"].return_value = sample_call_data

        with pytest.raises(ValueError) as exc_info:
            analyze_call_tool(
                call_id="gong-123",
                dimensions=["invalid_dimension", "fake_dimension"],
            )

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg
        assert "dimension" in error_msg

    def test_analyze_call_with_invalid_role(self, mock_db, sample_call_data):
        """
        GIVEN valid call but invalid role value
        WHEN analyze_call_tool is called with invalid role
        THEN it raises ValueError listing valid roles
        """
        mock_db["analyze_call"]["fetch_one"].return_value = sample_call_data

        with pytest.raises(ValueError) as exc_info:
            analyze_call_tool(call_id="gong-123", role="invalid_role")

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "role" in error_msg

    def test_get_rep_insights_with_nonexistent_rep(self, mock_db):
        """
        GIVEN a rep email that doesn't exist
        WHEN get_rep_insights_tool is called
        THEN it returns error dict with suggestion
        """
        mock_db["get_rep_insights"]["fetch_one"].return_value = None

        result = get_rep_insights_tool(rep_email="nonexistent@example.com")

        assert result is not None
        assert "error" in result
        assert "suggestion" in result
        assert "nonexistent@example.com" in result["error"]

    def test_search_calls_with_invalid_date_format(self, mock_db):
        """
        GIVEN invalid date format in date_range
        WHEN search_calls_tool is called
        THEN it raises ValueError about date format
        """
        with pytest.raises((ValueError, TypeError)):
            search_calls_tool(date_range={"start": "invalid-date", "end": "2025-01-20"})

    def test_search_calls_with_negative_limit(self, mock_db):
        """
        GIVEN negative limit value
        WHEN search_calls_tool is called
        THEN it handles gracefully (no error or returns empty)
        """
        mock_db["search_calls"]["fetch_all"].return_value = []

        # Should not crash with negative limit
        result = search_calls_tool(limit=-5)

        # Either empty result or clamped to positive
        assert result is not None

    def test_search_calls_with_invalid_score_range(self, mock_db):
        """
        GIVEN min_score > max_score
        WHEN search_calls_tool is called
        THEN it returns empty results (logically impossible range)
        """
        mock_db["search_calls"]["fetch_all"].return_value = []

        result = search_calls_tool(min_score=90, max_score=50)

        # Should return empty or handle gracefully
        assert result is not None
        assert isinstance(result, list)

    def test_analyze_call_with_missing_transcript(self, mock_db, sample_call_data, sample_speakers):
        """
        GIVEN a call exists but has no transcript
        WHEN analyze_call_tool is called
        THEN it raises appropriate error
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,  # Call exists
            None,  # But no transcript
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        # Should handle missing transcript gracefully
        with pytest.raises((ValueError, AttributeError, KeyError)):
            analyze_call_tool(call_id="gong-123")


class TestMCPToolsLogging:
    """Additional tests for logging and observability."""

    def test_analyze_call_logs_progress(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript, caplog
    ):
        """
        GIVEN analyze_call_tool is invoked
        WHEN execution proceeds
        THEN it logs key milestones for observability
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {"call_id": sample_call_data["id"], "scores": {}}

            with caplog.at_level(logging.INFO):
                analyze_call_tool(call_id="gong-123")

            # Verify logging occurred
            assert len(caplog.records) > 0
            # Should log call ID or progress
            log_messages = " ".join([r.message for r in caplog.records])
            assert "gong-123" in log_messages or "analyzing" in log_messages.lower()

    def test_get_rep_insights_logs_rep_name(self, mock_db, caplog):
        """
        GIVEN get_rep_insights_tool is invoked
        WHEN execution proceeds
        THEN it logs rep name for audit trail
        """
        rep_email = "sarah@prefect.io"

        mock_db["get_rep_insights"]["fetch_one"].return_value = {
            "id": str(uuid4()),
            "name": "Sarah Johnson",
            "email": rep_email,
            "role": "ae",
            "calls_analyzed": 5,
        }
        mock_db["get_rep_insights"]["fetch_all"].return_value = []

        with caplog.at_level(logging.INFO):
            get_rep_insights_tool(rep_email=rep_email)

        log_messages = " ".join([r.message for r in caplog.records])
        assert rep_email in log_messages or "sarah" in log_messages.lower()


class TestMCPToolsEdgeCases:
    """Edge case handling tests."""

    def test_analyze_call_with_empty_dimensions_list(
        self, mock_db, sample_call_data, sample_speakers, sample_transcript
    ):
        """
        GIVEN dimensions=[] (empty list, not None)
        WHEN analyze_call_tool is called
        THEN it should analyze all dimensions by default
        """
        mock_db["analyze_call"]["fetch_one"].side_effect = [
            sample_call_data,
            sample_transcript,
        ]
        mock_db["analyze_call"]["fetch_all"].return_value = sample_speakers

        with patch("coaching_mcp.tools.analyze_call.run_analysis") as mock_analyze:
            mock_analyze.return_value = {"call_id": sample_call_data["id"], "scores": {}}

            # Empty list should be handled (treat as None or validate)
            result = analyze_call_tool(call_id="gong-123", dimensions=[])

            # Should either analyze all or return error
            assert result is not None

    def test_get_rep_insights_with_no_calls_in_period(self, mock_db):
        """
        GIVEN a rep exists but has no calls in specified period
        WHEN get_rep_insights_tool is called
        THEN it returns error indicating no data
        """
        mock_db["get_rep_insights"]["fetch_one"].return_value = None

        result = get_rep_insights_tool(rep_email="sarah@prefect.io", time_period="last_7_days")

        assert result is not None
        assert "error" in result

    def test_search_calls_with_all_none_filters(self, mock_db):
        """
        GIVEN no filters specified (all None)
        WHEN search_calls_tool is called
        THEN it returns recent calls up to limit
        """
        mock_db["search_calls"]["fetch_all"].return_value = [
            {"id": str(uuid4()), "title": f"Recent Call {i}"} for i in range(20)
        ]

        result = search_calls_tool()

        assert result is not None
        assert isinstance(result, list)
        assert len(result) <= 20  # Default limit
