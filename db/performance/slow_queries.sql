-- Slow Query Analysis for Call Coach Database
-- Run these queries to identify performance bottlenecks

-- ==============================================================================
-- 1. IDENTIFY SLOW QUERIES
-- ==============================================================================

-- Enable query statistics tracking (run once per session)
-- SET track_io_timing = ON;

-- Find queries by average execution time
SELECT
    calls,
    mean_exec_time,
    max_exec_time,
    total_exec_time,
    query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 20;

-- ==============================================================================
-- 2. ANALYZE COMMON QUERY PATTERNS
-- ==============================================================================

-- Check for missing indexes on frequently queried columns
EXPLAIN ANALYZE
SELECT * FROM calls WHERE gong_call_id = 'sample-id';

EXPLAIN ANALYZE
SELECT * FROM calls WHERE scheduled_at BETWEEN '2024-01-01' AND '2024-12-31';

EXPLAIN ANALYZE
SELECT * FROM calls WHERE product = 'Prefect Cloud' AND scheduled_at > '2024-01-01';

-- Coaching sessions by rep
EXPLAIN ANALYZE
SELECT cs.*
FROM coaching_sessions cs
JOIN speakers s ON cs.rep_id = s.id
WHERE s.email = 'rep@example.com'
AND cs.created_at >= NOW() - INTERVAL '30 days';

-- Full-text search on transcripts
EXPLAIN ANALYZE
SELECT t.*, c.title
FROM transcripts t
JOIN calls c ON t.call_id = c.id
WHERE t.full_text_search @@ plainto_tsquery('english', 'pricing objection');

-- Opportunity timeline (complex union query)
EXPLAIN ANALYZE
SELECT
    'call' as item_type,
    c.id,
    c.title,
    c.scheduled_at as timestamp
FROM calls c
JOIN call_opportunities co ON c.id = co.call_id
WHERE co.opportunity_id = 'sample-uuid'
UNION ALL
SELECT
    'email' as item_type,
    e.id,
    e.subject as title,
    e.sent_at as timestamp
FROM emails e
WHERE e.opportunity_id = 'sample-uuid'
ORDER BY timestamp DESC;

-- ==============================================================================
-- 3. INDEX RECOMMENDATIONS
-- ==============================================================================

-- Composite index for call filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_calls_product_scheduled
ON calls(product, scheduled_at DESC)
WHERE product IS NOT NULL;

-- Index for coaching session lookups by rep and date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_coaching_rep_created
ON coaching_sessions(rep_id, created_at DESC);

-- Index for coaching session lookups by dimension
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_coaching_dimension_created
ON coaching_sessions(coaching_dimension, created_at DESC);

-- Composite index for opportunity timeline queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_call_opportunities_opp_id
ON call_opportunities(opportunity_id)
INCLUDE (call_id);

-- Index for email opportunity lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_emails_opportunity_sent
ON emails(opportunity_id, sent_at DESC);

-- Index for speaker email lookups (rep queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_speakers_email_company
ON speakers(email, company_side)
WHERE email IS NOT NULL;

-- Index for transcript full-text search performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transcripts_fts
ON transcripts USING GIN (full_text_search);

-- Index for transcript call lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transcripts_call_sequence
ON transcripts(call_id, sequence_number);

-- ==============================================================================
-- 4. TABLE STATISTICS
-- ==============================================================================

-- Check table sizes and row counts
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS rows
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

-- Find unused indexes (idx_scan = 0)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ==============================================================================
-- 5. MAINTENANCE RECOMMENDATIONS
-- ==============================================================================

-- Check for tables needing VACUUM
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Run ANALYZE to update query planner statistics
ANALYZE calls;
ANALYZE coaching_sessions;
ANALYZE transcripts;
ANALYZE opportunities;
ANALYZE speakers;

-- ==============================================================================
-- 6. CONNECTION POOLING STATS
-- ==============================================================================

-- Current connection counts
SELECT
    count(*) as total_connections,
    sum(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active,
    sum(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as idle,
    sum(CASE WHEN state = 'idle in transaction' THEN 1 ELSE 0 END) as idle_in_transaction
FROM pg_stat_activity
WHERE datname = current_database();

-- Long-running queries (> 1 second)
SELECT
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
AND now() - query_start > interval '1 second'
ORDER BY duration DESC;
