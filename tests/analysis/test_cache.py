"""Tests for analysis caching module."""
import pytest
from unittest.mock import patch, MagicMock
from analysis.cache import (
    generate_transcript_hash,
    get_cached_analysis,
    store_analysis_with_cache,
    get_active_rubric_version,
)


class TestTranscriptHash:
    """Tests for transcript hashing."""

    def test_generate_hash_basic(self):
        """Test basic hash generation."""
        transcript = "This is a sample transcript."
        hash_val = generate_transcript_hash(transcript)

        assert hash_val is not None
        assert isinstance(hash_val, str)

    def test_generate_hash_deterministic(self):
        """Test that same transcript produces same hash."""
        transcript = "Same transcript content"
        hash1 = generate_transcript_hash(transcript)
        hash2 = generate_transcript_hash(transcript)

        assert hash1 == hash2

    def test_generate_hash_different_transcripts(self):
        """Test that different transcripts produce different hashes."""
        hash1 = generate_transcript_hash("Transcript A")
        hash2 = generate_transcript_hash("Transcript B")

        assert hash1 != hash2

    def test_generate_hash_empty(self):
        """Test hashing empty string."""
        hash_val = generate_transcript_hash("")

        assert hash_val is not None


class TestGetCachedAnalysis:
    """Tests for retrieving cached analyses."""

    @patch('analysis.cache.fetch_one')
    def test_get_cached_analysis_found(self, mock_fetch):
        """Test retrieving existing cached analysis."""
        mock_fetch.return_value = {
            'id': 'session-123',
            'analysis': '{"scores": {"discovery": 85}}',
        }

        result = get_cached_analysis(
            call_id='call-123',
            dimension='discovery',
            transcript_hash='hash123',
            rubric_version='v1',
        )

        assert result is not None

    @patch('analysis.cache.fetch_one')
    def test_get_cached_analysis_not_found(self, mock_fetch):
        """Test handling missing cached analysis."""
        mock_fetch.return_value = None

        result = get_cached_analysis(
            call_id='nonexistent',
            dimension='discovery',
            transcript_hash='hash123',
            rubric_version='v1',
        )

        assert result is None

    @patch('analysis.cache.fetch_one')
    def test_get_cached_analysis_expired_rubric(self, mock_fetch):
        """Test handling cache with old rubric version."""
        mock_fetch.return_value = None

        result = get_cached_analysis(
            call_id='call-456',
            dimension='engagement',
            transcript_hash='hash456',
            rubric_version='v2',  # Different version
        )

        assert result is None


class TestStoreAnalysisWithCache:
    """Tests for storing analyses with cache metadata."""

    @patch('analysis.cache.fetch_one')
    @patch('analysis.cache.store_analysis')
    def test_store_analysis_basic(self, mock_store, mock_fetch):
        """Test basic analysis storage."""
        mock_fetch.return_value = {'id': 'session-123'}

        session_id = store_analysis_with_cache(
            call_id='call-123',
            dimension='discovery',
            analysis_data={'scores': {'discovery': 85}},
            transcript_hash='hash123',
            rubric_version='v1',
        )

        assert session_id is not None

    @patch('analysis.cache.fetch_one')
    @patch('analysis.cache.store_analysis')
    def test_store_analysis_with_metadata(self, mock_store, mock_fetch):
        """Test storing analysis with additional metadata."""
        mock_fetch.return_value = {'id': 'session-456'}

        analysis_data = {
            'scores': {'discovery': 75, 'engagement': 80},
            'strengths': ['Good listening'],
            'improvements': ['Better closing'],
        }

        session_id = store_analysis_with_cache(
            call_id='call-456',
            dimension='discovery',
            analysis_data=analysis_data,
            transcript_hash='hash456',
            rubric_version='v1',
        )

        assert session_id is not None


class TestGetActiveRubricVersion:
    """Tests for retrieving active rubric version."""

    @patch('analysis.cache.fetch_one')
    def test_get_rubric_version_discovery(self, mock_fetch):
        """Test getting rubric version for discovery dimension."""
        mock_fetch.return_value = {'version': 'v1', 'active': True}

        version = get_active_rubric_version('discovery')

        assert version is not None

    @patch('analysis.cache.fetch_one')
    def test_get_rubric_version_engagement(self, mock_fetch):
        """Test getting rubric version for engagement dimension."""
        mock_fetch.return_value = {'version': 'v1', 'active': True}

        version = get_active_rubric_version('engagement')

        assert version is not None

    @patch('analysis.cache.fetch_one')
    def test_get_rubric_version_objection_handling(self, mock_fetch):
        """Test getting rubric version for objection handling."""
        mock_fetch.return_value = {'version': 'v1', 'active': True}

        version = get_active_rubric_version('objection_handling')

        assert version is not None

    @patch('analysis.cache.fetch_one')
    def test_get_rubric_version_not_found(self, mock_fetch):
        """Test handling missing rubric version."""
        mock_fetch.return_value = None

        with pytest.raises(ValueError):
            get_active_rubric_version('unknown_dimension')

    @patch('analysis.cache.fetch_one')
    def test_get_rubric_version_inactive(self, mock_fetch):
        """Test handling inactive rubric version."""
        mock_fetch.return_value = {'version': 'v1', 'active': False}

        with pytest.raises(ValueError):
            get_active_rubric_version('discovery')
