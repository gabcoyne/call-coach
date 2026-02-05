# Database Schema Changes Required for Gong API v2

**Date**: 2026-02-04
**Related**: GONG_CLIENT_AUDIT.md, bd-26r

## Overview

The official Gong API v2 uses a different transcript structure than initially designed. The transcript data model has changed from flat segments to a hierarchical Monologue→Sentence structure.

## Required Changes to `transcripts` Table

### Current Schema (Assumed)

```sql
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(id),
    speaker_id UUID REFERENCES speakers(id),
    sequence_number INT,
    timestamp_seconds INT,  -- Actually stores milliseconds now
    text TEXT,
    sentiment VARCHAR,      -- Not provided by Gong API
    topics VARCHAR[],       -- NEW: Topic classification from Gong
    chunk_metadata JSONB    -- Stores start_ms, end_ms, duration_ms
);
```

### Issues with Current Schema

1. **`timestamp_seconds` misleading**: Field name says "seconds" but Gong provides milliseconds
2. **`sentiment` not provided**: Gong API doesn't return sentiment data (was in original design but not in API)
3. **Missing `end_time`**: Only have start time, duration is computed
4. **Missing `topic` field**: Gong groups sentences by topic (e.g., "Objections", "Introduction")

### Recommended Schema Updates

```sql
-- Option A: Minimal changes (keep existing schema, clarify usage)
ALTER TABLE transcripts
    RENAME COLUMN timestamp_seconds TO start_time_ms;

ALTER TABLE transcripts
    ALTER COLUMN sentiment DROP NOT NULL;  -- Make optional

COMMENT ON COLUMN transcripts.start_time_ms IS
    'Start time in milliseconds from call start (Gong API format)';

COMMENT ON COLUMN transcripts.chunk_metadata IS
    'JSONB containing: start_ms, end_ms, duration_ms, and optional topic';

-- Update existing code to store topic in chunk_metadata.topic
```

```sql
-- Option B: Full restructure (better alignment with Gong API)
CREATE TABLE transcript_sentences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(id) NOT NULL,
    speaker_id UUID REFERENCES speakers(id),
    sequence_number INT NOT NULL,

    -- Times in milliseconds from call start (Gong API format)
    start_time_ms BIGINT NOT NULL,
    end_time_ms BIGINT NOT NULL,
    duration_ms INT GENERATED ALWAYS AS (end_time_ms - start_time_ms) STORED,

    -- Content
    text TEXT NOT NULL,
    topic VARCHAR,  -- e.g., "Objections", "Introduction", "Product Demo"

    -- Metadata
    chunk_metadata JSONB,  -- For chunking large transcripts

    -- Indexes
    CONSTRAINT valid_times CHECK (end_time_ms > start_time_ms),
    INDEX idx_transcript_call_seq ON transcript_sentences(call_id, sequence_number),
    INDEX idx_transcript_speaker ON transcript_sentences(speaker_id),
    INDEX idx_transcript_topic ON transcript_sentences(topic) WHERE topic IS NOT NULL
);

-- Full-text search
CREATE INDEX idx_transcript_search ON transcript_sentences USING GIN(to_tsvector('english', text));
```

## Code Changes Already Made

### Updated Types (`gong/types.py`)

```python
class GongSentence(BaseModel):
    """Single sentence in a transcript monologue."""
    start: int  # milliseconds from call start
    end: int    # milliseconds from call start
    text: str

class GongMonologue(BaseModel):
    """Monologue (continuous speech by one speaker on a topic)."""
    speaker_id: str
    topic: str | None = None
    sentences: list[GongSentence]

class GongTranscript(BaseModel):
    """Full call transcript from Gong."""
    call_id: str
    monologues: list[GongMonologue]

    def get_flat_segments(self) -> list[dict]:
        """Convert to flat segments for backward compatibility."""
        ...
```

### Updated Client (`gong/client.py`)

- ✅ `get_transcript()` now uses `POST /v2/calls/transcript`
- ✅ Parses `Monologue → Sentence` structure
- ✅ Accepts `call_metadata` for optimized date range queries
- ✅ Returns `GongTranscript` with new monologue structure

### Updated Flow (`flows/process_new_call.py`)

- ✅ `store_transcript()` flattens monologues to sentences
- ✅ Stores topic in `topics` array field
- ✅ Stores timing metadata (start_ms, end_ms, duration_ms) in `chunk_metadata` JSONB
- ✅ Passes call metadata to `get_transcript()` for efficiency

## Migration Path

### Phase 1: Update Existing Schema (Quick Fix)

```sql
-- Rename misleading column
ALTER TABLE transcripts RENAME COLUMN timestamp_seconds TO start_time_ms;

-- Make sentiment optional (not provided by Gong)
ALTER TABLE transcripts ALTER COLUMN sentiment DROP NOT NULL;

-- Add column comments
COMMENT ON COLUMN transcripts.start_time_ms IS 'Start time in milliseconds from call start';
COMMENT ON COLUMN transcripts.chunk_metadata IS 'JSONB: {start_ms, end_ms, duration_ms, topic}';

-- Ensure topics and chunk_metadata columns exist
-- (These should be in initial schema creation, but if not:)
ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS topics VARCHAR[];
ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS chunk_metadata JSONB;
```

### Phase 2: Full Migration (Future Enhancement)

1. Create new `transcript_sentences` table with proper schema
2. Migrate existing data:
   ```sql
   INSERT INTO transcript_sentences (
       call_id, speaker_id, sequence_number,
       start_time_ms, end_time_ms, text, topic, chunk_metadata
   )
   SELECT
       call_id, speaker_id, sequence_number,
       start_time_ms,
       (chunk_metadata->>'end_ms')::BIGINT,
       text,
       chunk_metadata->>'topic',
       chunk_metadata - 'topic'  -- Remove topic from metadata
   FROM transcripts;
   ```
3. Update all queries to use new table
4. Drop old `transcripts` table

## Testing Checklist

Before deploying to production, verify:

- [ ] `process_new_call` flow works end-to-end with real Gong webhook
- [ ] Transcript sentences stored with correct timing (milliseconds, not seconds)
- [ ] Topics properly extracted and stored
- [ ] `chunk_metadata` JSONB contains start_ms, end_ms, duration_ms
- [ ] Full-text search works on transcript text
- [ ] Analysis engine can reconstruct full transcript from stored sentences
- [ ] Token counting works correctly for chunking decisions

## Related Files

- `gong/types.py` - Updated data models
- `gong/client.py` - Updated API client
- `flows/process_new_call.py` - Updated storage logic
- `.openspec/GONG_CLIENT_AUDIT.md` - Full API audit
- `db/schema.sql` - Schema definitions (needs updates)
- `db/migrations/` - Migration scripts (future)

## Next Steps

1. **Immediate**: Run Phase 1 migration on dev database
2. **Before Phase 4**: Test with real Gong webhooks
3. **Future**: Implement Phase 2 full restructure if needed
