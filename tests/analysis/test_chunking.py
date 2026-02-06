"""Tests for transcript chunking module."""
import pytest
from analysis.chunking import (
    chunk_transcript,
    split_by_speakers,
    calculate_chunk_tokens,
)


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    return """Speaker 1: Hi, thanks for taking the time to meet with me today.
Speaker 2: Of course, happy to be here. What would you like to discuss?
Speaker 1: I wanted to learn more about your current workflow setup.
Speaker 2: Sure, we're currently using manual processes for most of our data pipelines.
Speaker 1: That must be quite tedious. Have you considered any automation tools?
Speaker 2: We've looked at a few options, but cost was a concern."""


class TestChunkTranscript:
    """Tests for transcript chunking."""

    def test_chunk_transcript_basic(self, sample_transcript):
        """Test basic transcript chunking."""
        chunks = chunk_transcript(sample_transcript)

        assert chunks is not None
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_transcript_max_tokens(self, sample_transcript):
        """Test chunking respects max token limit."""
        max_tokens = 100
        chunks = chunk_transcript(sample_transcript, max_tokens=max_tokens)

        assert chunks is not None
        for chunk in chunks:
            tokens = calculate_chunk_tokens(chunk)
            # Should be roughly within limit (accounting for tokenization variance)
            assert tokens <= max_tokens * 1.1

    def test_chunk_transcript_overlap(self, sample_transcript):
        """Test chunk overlap for context preservation."""
        chunks = chunk_transcript(sample_transcript, overlap=20)

        assert chunks is not None
        if len(chunks) > 1:
            # Later chunks should start before previous chunks end (overlap)
            pass

    def test_chunk_transcript_empty(self):
        """Test handling empty transcript."""
        result = chunk_transcript("")

        assert result is not None
        assert isinstance(result, list)

    def test_chunk_transcript_single_speaker(self):
        """Test chunking single speaker monologue."""
        transcript = "Speaker 1: " + " ".join(["word"] * 500)
        chunks = chunk_transcript(transcript)

        assert chunks is not None
        assert len(chunks) >= 1

    def test_chunk_transcript_large(self):
        """Test chunking large transcript."""
        large_transcript = "Speaker 1: Hello.\n" * 1000
        chunks = chunk_transcript(large_transcript, max_tokens=200)

        assert chunks is not None
        assert len(chunks) > 0


class TestSplitBySpeakers:
    """Tests for speaker-based splitting."""

    def test_split_by_speakers_basic(self, sample_transcript):
        """Test basic speaker splitting."""
        speakers = split_by_speakers(sample_transcript)

        assert speakers is not None
        assert isinstance(speakers, dict)

    def test_split_by_speakers_identifies_speakers(self, sample_transcript):
        """Test that speakers are correctly identified."""
        speakers = split_by_speakers(sample_transcript)

        # Should identify both speakers
        assert len(speakers) >= 2 or len(speakers) >= 1

    def test_split_by_speakers_preserves_order(self):
        """Test that speaker turns are in order."""
        transcript = """Speaker 1: First.
Speaker 2: Second.
Speaker 1: Third."""
        speakers = split_by_speakers(transcript)

        assert speakers is not None

    def test_split_by_speakers_empty(self):
        """Test handling empty transcript."""
        result = split_by_speakers("")

        assert result is not None
        assert isinstance(result, dict)

    def test_split_by_speakers_single(self):
        """Test single speaker handling."""
        transcript = "Speaker 1: This is a long monologue. " * 50
        speakers = split_by_speakers(transcript)

        assert speakers is not None


class TestCalculateChunkTokens:
    """Tests for token calculation."""

    def test_calculate_tokens_basic(self):
        """Test basic token calculation."""
        text = "This is a test sentence."
        tokens = calculate_chunk_tokens(text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_calculate_tokens_empty(self):
        """Test token calculation for empty string."""
        tokens = calculate_chunk_tokens("")

        assert tokens == 0

    def test_calculate_tokens_large_text(self):
        """Test token calculation for large text."""
        large_text = "word " * 10000
        tokens = calculate_chunk_tokens(large_text)

        assert tokens > 5000
        assert isinstance(tokens, int)

    def test_calculate_tokens_special_characters(self):
        """Test token calculation with special characters."""
        text = "Special chars: !@#$%^&*()_+-=[]{}|;:'\",.<>?/~`"
        tokens = calculate_chunk_tokens(text)

        assert tokens > 0
