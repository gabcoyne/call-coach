-- Performance Optimization: Additional Indexes
-- Adds missing indexes identified through query analysis for call-coach

-- ============================================================================
-- COACHING SESSIONS - Enhanced Indexing
-- ============================================================================

-- Composite index for common query patterns (rep + dimension + date range)
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_rep_dimension_date
ON coaching_sessions(rep_id, coaching_dimension, created_at DESC)
WHERE created_at IS NOT NULL;

-- Index for cache lookups (critical path)
-- Upgraded to UNIQUE to enforce cache key uniqueness
CREATE UNIQUE INDEX IF NOT EXISTS idx_coaching_sessions_cache_lookup
ON coaching_sessions(cache_key, created_at DESC)
WHERE cache_key IS NOT NULL;

-- Index for rubric version queries (invalidation lookups)
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_rubric_version
ON coaching_sessions(rubric_version, coaching_dimension)
WHERE rubric_version IS NOT NULL;

-- Index for transcript hash lookups (duplicate detection)
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_transcript_hash
ON coaching_sessions(transcript_hash, created_at DESC)
WHERE transcript_hash IS NOT NULL;

-- Partial index for recent sessions (hot data)
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_recent
ON coaching_sessions(created_at DESC, coaching_dimension)
WHERE created_at > NOW() - INTERVAL '30 days';

-- ============================================================================
-- CALLS - Enhanced Indexing
-- ============================================================================

-- Composite index for call search (date + product + type)
CREATE INDEX IF NOT EXISTS idx_calls_search
ON calls(scheduled_at DESC, product, call_type)
WHERE scheduled_at IS NOT NULL;

-- Index for unprocessed calls (webhook processing queue)
CREATE INDEX IF NOT EXISTS idx_calls_unprocessed
ON calls(created_at DESC)
WHERE processed_at IS NULL;

-- Index for call metadata JSONB queries
CREATE INDEX IF NOT EXISTS idx_calls_metadata_gin
ON calls USING GIN(metadata jsonb_path_ops);

-- ============================================================================
-- SPEAKERS - Enhanced Indexing
-- ============================================================================

-- Composite index for rep lookup and filtering
CREATE INDEX IF NOT EXISTS idx_speakers_email_company
ON speakers(email, company_side, call_id)
WHERE email IS NOT NULL;

-- Index for talk time analysis
CREATE INDEX IF NOT EXISTS idx_speakers_talk_time
ON speakers(call_id, talk_time_percentage DESC)
WHERE talk_time_percentage IS NOT NULL;

-- ============================================================================
-- TRANSCRIPTS - Enhanced Indexing
-- ============================================================================

-- Composite index for sequential transcript retrieval
CREATE INDEX IF NOT EXISTS idx_transcripts_call_sequence
ON transcripts(call_id, sequence_number ASC)
WHERE sequence_number IS NOT NULL;

-- Index for sentiment analysis queries
CREATE INDEX IF NOT EXISTS idx_transcripts_sentiment
ON transcripts(call_id, sentiment)
WHERE sentiment IS NOT NULL;

-- Index for topic searches
CREATE INDEX IF NOT EXISTS idx_transcripts_topics_gin
ON transcripts USING GIN(topics)
WHERE topics IS NOT NULL AND array_length(topics, 1) > 0;

-- ============================================================================
-- ANALYSIS_RUNS - Enhanced Indexing
-- ============================================================================

-- Index for flow run tracking
CREATE INDEX IF NOT EXISTS idx_analysis_runs_flow_run
ON analysis_runs(flow_run_id, status, started_at DESC)
WHERE flow_run_id IS NOT NULL;

-- Index for cache hit analysis
CREATE INDEX IF NOT EXISTS idx_analysis_runs_cache_analysis
ON analysis_runs(cache_hit, completed_at DESC)
WHERE status = 'completed';

-- Index for error tracking
CREATE INDEX IF NOT EXISTS idx_analysis_runs_errors
ON analysis_runs(status, started_at DESC)
WHERE status = 'failed' AND error_message IS NOT NULL;

-- ============================================================================
-- WEBHOOK_EVENTS - Enhanced Indexing
-- ============================================================================

-- Index for event processing queue
CREATE INDEX IF NOT EXISTS idx_webhook_events_processing
ON webhook_events(status, received_at ASC)
WHERE status IN ('received', 'processing');

-- Index for event type filtering
CREATE INDEX IF NOT EXISTS idx_webhook_events_type
ON webhook_events(event_type, received_at DESC);

-- ============================================================================
-- COACHING_METRICS - Enhanced Indexing
-- ============================================================================

-- Composite index for metric trending
CREATE INDEX IF NOT EXISTS idx_coaching_metrics_trending
ON coaching_metrics(metric_name, created_at DESC);

-- Index for session metric lookups
CREATE INDEX IF NOT EXISTS idx_coaching_metrics_session_name
ON coaching_metrics(coaching_session_id, metric_name);

-- ============================================================================
-- COACHING_RUBRICS - Enhanced Indexing
-- ============================================================================

-- Index for active rubric lookups by category
CREATE INDEX IF NOT EXISTS idx_coaching_rubrics_active_lookup
ON coaching_rubrics(category, active, created_at DESC)
WHERE active = true;

-- ============================================================================
-- OPPORTUNITIES - Enhanced Indexing (if opportunities table exists)
-- ============================================================================

-- Check if opportunities table exists before creating indexes
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'opportunities') THEN
        -- Index for opportunity owner queries
        CREATE INDEX IF NOT EXISTS idx_opportunities_owner
        ON opportunities(owner_email, stage, created_at DESC)
        WHERE owner_email IS NOT NULL;

        -- Index for opportunity stage and health tracking
        CREATE INDEX IF NOT EXISTS idx_opportunities_health
        ON opportunities(stage, health_score DESC, updated_at DESC)
        WHERE health_score IS NOT NULL;

        -- Index for opportunity account lookups
        CREATE INDEX IF NOT EXISTS idx_opportunities_account
        ON opportunities(account_name, created_at DESC)
        WHERE account_name IS NOT NULL;
    END IF;
END $$;

-- ============================================================================
-- COVERING INDEXES (for common queries that can skip table lookups)
-- ============================================================================

-- Covering index for rep performance summary
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_rep_summary
ON coaching_sessions(rep_id, created_at DESC)
INCLUDE (coaching_dimension, score, session_type);

-- Covering index for call analysis status
CREATE INDEX IF NOT EXISTS idx_calls_status_summary
ON calls(id, scheduled_at DESC)
INCLUDE (gong_call_id, title, processed_at);

-- ============================================================================
-- MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to analyze table statistics after index creation
CREATE OR REPLACE FUNCTION analyze_coaching_tables()
RETURNS void AS $$
BEGIN
    ANALYZE calls;
    ANALYZE speakers;
    ANALYZE transcripts;
    ANALYZE coaching_sessions;
    ANALYZE analysis_runs;
    ANALYZE coaching_metrics;
    ANALYZE webhook_events;
    ANALYZE coaching_rubrics;

    RAISE NOTICE 'Table statistics updated for query planner';
END;
$$ LANGUAGE plpgsql;

-- Function to get index usage statistics
CREATE OR REPLACE FUNCTION get_index_usage_stats()
RETURNS TABLE (
    schemaname TEXT,
    tablename TEXT,
    indexname TEXT,
    idx_scan BIGINT,
    idx_tup_read BIGINT,
    idx_tup_fetch BIGINT,
    size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.schemaname::TEXT,
        s.tablename::TEXT,
        s.indexrelname::TEXT,
        s.idx_scan,
        s.idx_tup_read,
        s.idx_tup_fetch,
        ROUND(pg_relation_size(i.indexrelid) / (1024.0 * 1024.0), 2) as size_mb
    FROM pg_stat_user_indexes s
    JOIN pg_index i ON s.indexrelid = i.indexrelid
    WHERE s.schemaname = 'public'
    ORDER BY s.idx_scan ASC, size_mb DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EXECUTE MAINTENANCE
-- ============================================================================

-- Update table statistics
SELECT analyze_coaching_tables();

-- Report on index creation
SELECT 'Performance indexes created successfully!' AS status;
SELECT COUNT(*) AS new_indexes_created
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname LIKE 'idx_%';
