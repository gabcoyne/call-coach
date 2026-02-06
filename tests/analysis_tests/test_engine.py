"""Tests for analysis engine."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from analysis.engine import _run_claude_analysis, get_or_create_coaching_session
from db.models import CoachingDimension


@pytest.fixture
def sample_call_id():
    """Sample call UUID."""
    return uuid4()


@pytest.fixture
def sample_rep_id():
    """Sample rep UUID."""
    return uuid4()


@pytest.fixture
def sample_transcript():
    """Sample call transcript."""
    return """Speaker 1: Hi John, thanks for joining the call.
Speaker 2: Of course, happy to be here.
Speaker 1: Let me ask you about your current data pipeline setup.
Speaker 2: We're currently using batch jobs, but it's getting complex.
Speaker 1: I understand. Have you considered using a workflow orchestration tool?
Speaker 2: We've looked at a few options, but weren't sure about cost.
Speaker 1: Let me walk you through how Prefect could help."""


class TestGetOrCreateCoachingSession:
    """Tests for getting or creating coaching sessions."""

    @patch("analysis.engine.get_cached_analysis")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.generate_transcript_hash")
    def test_get_cached_session(
        self, mock_hash, mock_rubric, mock_cache, sample_call_id, sample_rep_id, sample_transcript
    ):
        """Test retrieving cached coaching session."""
        mock_hash.return_value = "hash123"
        mock_rubric.return_value = "v1"
        mock_cache.return_value = {
            "session_id": "session-123",
            "call_id": str(sample_call_id),
            "scores": {"discovery": 85},
        }

        result = get_or_create_coaching_session(
            call_id=sample_call_id,
            rep_id=sample_rep_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            force_reanalysis=False,
        )

        assert result is not None
        assert "scores" in result

    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine._run_claude_analysis")
    @patch("analysis.engine.store_analysis_with_cache")
    def test_create_new_session(
        self,
        mock_store,
        mock_claude,
        mock_fetch,
        mock_rubric,
        mock_hash,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
    ):
        """Test creating new coaching session (cache miss)."""
        mock_hash.return_value = "hash123"
        mock_rubric.return_value = "v1"
        mock_fetch.return_value = {
            "id": str(sample_call_id),
            "title": "Test Call",
            "rep_email": "test@example.com",
        }
        mock_claude.return_value = {
            "scores": {"discovery": 80},
            "strengths": ["Good listening"],
        }
        mock_store.return_value = "new-session-123"

        with patch("analysis.engine.get_cached_analysis", return_value=None):
            result = get_or_create_coaching_session(
                call_id=sample_call_id,
                rep_id=sample_rep_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                force_reanalysis=False,
            )

            assert result is not None

    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine._run_claude_analysis")
    @patch("analysis.engine.store_analysis_with_cache")
    def test_force_reanalysis(
        self,
        mock_store,
        mock_claude,
        mock_fetch,
        mock_rubric,
        mock_hash,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
    ):
        """Test forcing reanalysis despite cache."""
        mock_hash.return_value = "hash123"
        mock_rubric.return_value = "v1"
        mock_fetch.return_value = {
            "id": str(sample_call_id),
            "title": "Test Call",
            "rep_email": "test@example.com",
        }
        mock_claude.return_value = {
            "scores": {"discovery": 85},
            "fresh": True,
        }
        mock_store.return_value = "forced-session-123"

        result = get_or_create_coaching_session(
            call_id=sample_call_id,
            rep_id=sample_rep_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            force_reanalysis=True,  # Force reanalysis
        )

        assert result is not None
        # Claude analysis should have been called
        assert mock_claude.called

    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.get_active_rubric_version")
    def test_session_type_on_demand(
        self, mock_rubric, mock_hash, sample_call_id, sample_rep_id, sample_transcript
    ):
        """Test session type specification."""
        mock_hash.return_value = "hash123"
        mock_rubric.return_value = "v1"

        with (
            patch("analysis.engine.get_cached_analysis", return_value=None),
            patch("analysis.engine.fetch_one"),
            patch("analysis.engine._run_claude_analysis", return_value={}),
            patch("analysis.engine.store_analysis_with_cache", return_value="session-123"),
        ):

            result = get_or_create_coaching_session(
                call_id=sample_call_id,
                rep_id=sample_rep_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                session_type="on_demand",
            )

            assert result is not None


class TestRunClaudeAnalysis:
    """Tests for Claude API analysis."""

    @patch("analysis.engine.anthropic_client")
    def test_run_claude_analysis_discovery(self, mock_anthropic):
        """Test Claude analysis for discovery dimension."""
        mock_response = MagicMock()
        mock_response.content[0].text = '{"scores": {"discovery": 85}, "strengths": []}'
        mock_anthropic.messages.create.return_value = mock_response

        result = _run_claude_analysis(
            dimension=CoachingDimension.DISCOVERY,
            transcript="Sample transcript",
            call_metadata={"title": "Test Call"},
        )

        assert result is not None

    @patch("analysis.engine.anthropic_client")
    def test_run_claude_analysis_engagement(self, mock_anthropic):
        """Test Claude analysis for engagement dimension."""
        mock_response = MagicMock()
        mock_response.content[0].text = '{"scores": {"engagement": 75}}'
        mock_anthropic.messages.create.return_value = mock_response

        result = _run_claude_analysis(
            dimension=CoachingDimension.ENGAGEMENT,
            transcript="Sample transcript",
            call_metadata={},
        )

        assert result is not None

    @patch("analysis.engine.anthropic_client")
    def test_run_claude_analysis_handles_api_error(self, mock_anthropic):
        """Test handling of Claude API errors."""
        mock_anthropic.messages.create.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            _run_claude_analysis(
                dimension=CoachingDimension.DISCOVERY,
                transcript="Sample transcript",
                call_metadata={},
            )
