-- Migration: Update schema for Gong API v2 compatibility
-- Date: 2026-02-04
-- Related: .openspec/GONG_CLIENT_AUDIT.md, .openspec/SCHEMA_CHANGES_NEEDED.md
--
-- Changes:
-- 1. Rename timestamp_seconds to start_time_ms (more accurate)
-- 2. Make sentiment optional (not provided by Gong API)
-- 3. Add comments clarifying millisecond timestamps
-- 4. Ensure topics and chunk_metadata columns exist

-- ============================================================================
-- TRANSCRIPTS TABLE UPDATES
-- ============================================================================

-- Step 1: Rename misleading column name
-- Note: This is a metadata change only - the column already stores milliseconds
-- but was named "timestamp_seconds" which was confusing
ALTER TABLE transcripts
    RENAME COLUMN timestamp_seconds TO start_time_ms;

-- Step 2: Add column comments for clarity
COMMENT ON COLUMN transcripts.start_time_ms IS
    'Start time in milliseconds from call start (Gong API v2 format)';

COMMENT ON COLUMN transcripts.chunk_metadata IS
    'JSONB containing timing and topic metadata: {start_ms, end_ms, duration_ms, topic}';

COMMENT ON COLUMN transcripts.topics IS
    'Array of topics/themes extracted by Gong (e.g., ["Call Setup", "Objections", "Product Demo"])';

COMMENT ON COLUMN transcripts.sentiment IS
    'Sentiment analysis (NOTE: Not provided by Gong API v2, may be null or populated by future analysis)';

-- Step 3: Ensure sentiment can be null (Gong API doesn't provide it)
-- If the column was created with NOT NULL, this will allow nulls
ALTER TABLE transcripts
    ALTER COLUMN sentiment DROP NOT NULL;

-- Step 4: Create index on topics for faster filtering
CREATE INDEX IF NOT EXISTS idx_transcripts_topics
    ON transcripts USING GIN(topics)
    WHERE topics IS NOT NULL AND array_length(topics, 1) > 0;

-- ============================================================================
-- UPDATE EXISTING DATA (if any)
-- ============================================================================

-- If there's existing data with old structure, we need to migrate it
-- This is a safety check - new deployments won't have data yet

DO $$
DECLARE
    row_count INTEGER;
BEGIN
    -- Check if there are any transcripts
    SELECT COUNT(*) INTO row_count FROM transcripts;

    IF row_count > 0 THEN
        RAISE NOTICE 'Found % existing transcript rows - checking for data migration needs', row_count;

        -- Check if chunk_metadata contains the new structure
        -- If not, log a warning (manual migration may be needed)
        PERFORM 1 FROM transcripts
        WHERE chunk_metadata IS NOT NULL
        AND NOT (chunk_metadata ? 'start_ms' AND chunk_metadata ? 'end_ms')
        LIMIT 1;

        IF FOUND THEN
            RAISE WARNING 'Some transcripts have old chunk_metadata structure - manual migration recommended';
            RAISE NOTICE 'See .openspec/SCHEMA_CHANGES_NEEDED.md for migration guide';
        ELSE
            RAISE NOTICE 'All transcript data appears compatible with new schema';
        END IF;
    ELSE
        RAISE NOTICE 'No existing transcript data found - clean migration';
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify the changes
DO $$
BEGIN
    RAISE NOTICE 'Schema migration 002 completed successfully';
    RAISE NOTICE 'Transcripts table updated for Gong API v2 compatibility';
    RAISE NOTICE '  - timestamp_seconds → start_time_ms (renamed)';
    RAISE NOTICE '  - sentiment column allows NULL';
    RAISE NOTICE '  - Added comments for clarity';
    RAISE NOTICE '  - Added topics GIN index';
END $$;

-- Query to show transcript structure
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'transcripts'
ORDER BY ordinal_position;
