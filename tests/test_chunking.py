"""Tests for transcript chunking functionality."""

import pytest

from analysis.chunking import (
    chunk_transcript,
    count_tokens,
    get_chunk_context,
    reconstruct_full_transcript,
)


def test_count_tokens():
    """Test token counting."""
    text = "This is a test sentence."
    token_count = count_tokens(text)
    assert token_count > 0
    assert isinstance(token_count, int)


def test_chunk_small_transcript():
    """Test that small transcripts don't get chunked."""
    text = "This is a short transcript that doesn't need chunking."
    chunks = chunk_transcript(text, max_chunk_size=1000)

    assert len(chunks) == 1
    chunk_text, metadata = chunks[0]
    assert chunk_text == text
    assert metadata.chunk_id == 0
    assert metadata.overlap_tokens == 0


def test_chunk_large_transcript():
    """Test chunking of large transcripts."""
    # Create a large text that will exceed max_chunk_size
    text = "This is a test sentence. " * 10000  # ~30K tokens

    chunks = chunk_transcript(text, max_chunk_size=5000, overlap_percentage=20)

    # Should create multiple chunks
    assert len(chunks) > 1

    # Check chunk metadata
    for idx, (chunk_text, metadata) in enumerate(chunks):
        assert metadata.chunk_id == idx
        assert len(chunk_text) > 0

        # All chunks except first should have overlap
        if idx > 0:
            assert metadata.overlap_tokens > 0


def test_chunk_overlap():
    """Test that chunks have proper overlap."""
    text = "Word " * 20000  # Create large text

    chunks = chunk_transcript(text, max_chunk_size=5000, overlap_percentage=20)

    if len(chunks) > 1:
        # Check overlap exists between consecutive chunks
        for i in range(len(chunks) - 1):
            _, metadata = chunks[i + 1]
            assert metadata.overlap_tokens > 0
            assert metadata.overlap_tokens == int(5000 * 0.2)


def test_reconstruct_transcript():
    """Test reconstruction of chunked transcript."""
    original_text = "This is a test sentence. " * 1000

    # Chunk and reconstruct
    chunks = chunk_transcript(original_text, max_chunk_size=500, overlap_percentage=20)
    reconstructed = reconstruct_full_transcript(chunks)

    # Should be very similar (might have minor token encoding differences)
    # Check length is close
    assert abs(len(reconstructed) - len(original_text)) / len(original_text) < 0.05


def test_get_chunk_context():
    """Test getting chunk context information."""
    text = "Word " * 10000
    chunks = chunk_transcript(text, max_chunk_size=2000)

    if len(chunks) > 1:
        # Test first chunk context
        context = get_chunk_context(chunks, 0)
        assert context["chunk_id"] == 0
        assert context["is_first_chunk"] is True
        assert context["is_last_chunk"] is False

        # Test last chunk context
        last_idx = len(chunks) - 1
        context = get_chunk_context(chunks, last_idx)
        assert context["chunk_id"] == last_idx
        assert context["is_first_chunk"] is False
        assert context["is_last_chunk"] is True


def test_chunk_context_invalid_id():
    """Test that invalid chunk ID raises error."""
    text = "Short text"
    chunks = chunk_transcript(text, max_chunk_size=1000)

    with pytest.raises(ValueError):
        get_chunk_context(chunks, 999)
