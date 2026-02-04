"""
Transcript chunking for handling long calls.
Uses sliding window with overlap to maintain context across chunks.
"""
import logging
from typing import Any

import tiktoken

from config import settings
from db.models import ChunkMetadata

logger = logging.getLogger(__name__)

# Initialize tokenizer (cl100k_base is used by Claude models)
tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens
    """
    return len(tokenizer.encode(text))


def chunk_transcript(
    transcript: str,
    max_chunk_size: int | None = None,
    overlap_percentage: int | None = None,
) -> list[tuple[str, ChunkMetadata]]:
    """
    Chunk a long transcript into smaller segments with overlap.

    Uses sliding window approach:
    - Each chunk has max_chunk_size tokens (default: 80K)
    - Overlap between chunks is overlap_percentage (default: 20%)
    - This ensures context continuity across chunk boundaries

    Args:
        transcript: Full transcript text
        max_chunk_size: Max tokens per chunk (default from settings)
        overlap_percentage: Overlap as percentage (default from settings)

    Returns:
        List of (chunk_text, chunk_metadata) tuples
    """
    max_chunk_size = max_chunk_size or settings.max_chunk_size_tokens
    overlap_percentage = overlap_percentage or settings.chunk_overlap_percentage

    # Tokenize full transcript
    tokens = tokenizer.encode(transcript)
    total_tokens = len(tokens)

    logger.info(
        f"Chunking transcript: {total_tokens:,} tokens "
        f"(max_chunk={max_chunk_size:,}, overlap={overlap_percentage}%)"
    )

    # If transcript fits in one chunk, no need to split
    if total_tokens <= max_chunk_size:
        logger.info("Transcript fits in single chunk, no splitting needed")
        return [
            (
                transcript,
                ChunkMetadata(
                    chunk_id=0,
                    start_token=0,
                    end_token=total_tokens,
                    overlap_tokens=0,
                ),
            )
        ]

    # Calculate overlap size
    overlap_tokens = int(max_chunk_size * (overlap_percentage / 100))
    stride = max_chunk_size - overlap_tokens

    chunks: list[tuple[str, ChunkMetadata]] = []
    chunk_id = 0
    start_idx = 0

    while start_idx < total_tokens:
        # Calculate chunk boundaries
        end_idx = min(start_idx + max_chunk_size, total_tokens)

        # Extract tokens for this chunk
        chunk_tokens = tokens[start_idx:end_idx]

        # Decode back to text
        chunk_text = tokenizer.decode(chunk_tokens)

        # Create metadata
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            start_token=start_idx,
            end_token=end_idx,
            overlap_tokens=overlap_tokens if chunk_id > 0 else 0,
        )

        chunks.append((chunk_text, metadata))

        logger.debug(
            f"Created chunk {chunk_id}: "
            f"tokens {start_idx:,}-{end_idx:,} "
            f"({len(chunk_tokens):,} tokens)"
        )

        # Move to next chunk
        chunk_id += 1
        start_idx += stride

        # If we're at the end, break
        if end_idx >= total_tokens:
            break

    logger.info(f"Split transcript into {len(chunks)} chunks")
    return chunks


def reconstruct_full_transcript(
    chunks: list[tuple[str, ChunkMetadata]]
) -> str:
    """
    Reconstruct full transcript from chunks by removing overlaps.

    Args:
        chunks: List of (chunk_text, chunk_metadata) tuples

    Returns:
        Full reconstructed transcript
    """
    if not chunks:
        return ""

    if len(chunks) == 1:
        return chunks[0][0]

    # Start with first chunk (no overlap to remove)
    full_text = chunks[0][0]

    # For subsequent chunks, skip the overlap portion
    for chunk_text, metadata in chunks[1:]:
        # Tokenize chunk
        chunk_tokens = tokenizer.encode(chunk_text)

        # Skip overlap tokens at the beginning
        non_overlap_tokens = chunk_tokens[metadata.overlap_tokens :]

        # Decode and append
        non_overlap_text = tokenizer.decode(non_overlap_tokens)
        full_text += non_overlap_text

    return full_text


def get_chunk_context(
    chunks: list[tuple[str, ChunkMetadata]],
    chunk_id: int,
) -> dict[str, Any]:
    """
    Get context information for a specific chunk.
    Useful for understanding chunk position in the full transcript.

    Args:
        chunks: All chunks
        chunk_id: ID of chunk to get context for

    Returns:
        Context dict with position info
    """
    if chunk_id >= len(chunks):
        raise ValueError(f"Chunk ID {chunk_id} out of range (total: {len(chunks)})")

    chunk_text, metadata = chunks[chunk_id]
    total_chunks = len(chunks)

    # Calculate progress through transcript
    if total_chunks == 1:
        progress_pct = 100.0
    else:
        progress_pct = (chunk_id / (total_chunks - 1)) * 100

    return {
        "chunk_id": chunk_id,
        "total_chunks": total_chunks,
        "start_token": metadata.start_token,
        "end_token": metadata.end_token,
        "chunk_size": metadata.end_token - metadata.start_token,
        "overlap_tokens": metadata.overlap_tokens,
        "progress_percentage": round(progress_pct, 1),
        "is_first_chunk": chunk_id == 0,
        "is_last_chunk": chunk_id == total_chunks - 1,
    }
