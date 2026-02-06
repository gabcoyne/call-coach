-- Query Optimization: Optimized Queries for Common Operations
-- Replaces slow queries with optimized versions using proper indexes

-- ============================================================================
-- OPTIMIZED QUERY: Get Coaching Sessions with Cache Lookup
-- ============================================================================

-- Original: Sequential scan on coaching_sessions
-- Optimized: Uses idx_coaching_sessions_cache_lookup (unique index)
CREATE OR REPLACE FUNCTION get_cached_coaching_session(
    p_cache_key VARCHAR,
    p_transcript_hash VARCHAR,
    p_rubric_version VARCHAR,
    p_dimension VARCHAR,
    p_cache_ttl_days INT DEFAULT 90
)
RETURNS TABLE (
    id UUID,
    call_id UUID,
    rep_id UUID,
    coaching_dimension VARCHAR,
    score INT,
    strengths TEXT[],
    areas_for_improvement TEXT[],
    specific_examples JSONB,
    action_items TEXT[],
    full_analysis TEXT,
    created_at TIMESTAMP,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cs.id,
        cs.call_id,
        cs.rep_id,
        cs.coaching_dimension,
        cs.score,
        cs.strengths,
        cs.areas_for_improvement,
        cs.specific_examples,
        cs.action_items,
        cs.full_analysis,
        cs.created_at,
        cs.metadata
    FROM coaching_sessions cs
    WHERE cs.cache_key = p_cache_key
    AND cs.transcript_hash = p_transcript_hash
    AND cs.rubric_version = p_rubric_version
    AND cs.coaching_dimension = p_dimension
    AND cs.created_at > NOW() - (p_cache_ttl_days || ' days')::INTERVAL
    ORDER BY cs.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- OPTIMIZED QUERY: Get Rep Performance Summary
-- ============================================================================

-- Original: Multiple joins with aggregations
-- Optimized: Uses covering indexes and CTEs
CREATE OR REPLACE FUNCTION get_rep_performance_summary(
    p_rep_email VARCHAR,
    p_days_back INT DEFAULT 30
)
RETURNS TABLE (
    rep_id UUID,
    rep_name VARCHAR,
    rep_email VARCHAR,
    total_calls INT,
    total_sessions INT,
    avg_score NUMERIC,
    avg_product_knowledge NUMERIC,
    avg_discovery NUMERIC,
    avg_objection_handling NUMERIC,
    avg_engagement NUMERIC,
    recent_trend VARCHAR,
    last_coached TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    WITH rep_info AS (
        SELECT DISTINCT ON (s.email)
            s.id,
            s.name,
            s.email
        FROM speakers s
        WHERE s.email = p_rep_email
        AND s.company_side = true
        LIMIT 1
    ),
    recent_sessions AS (
        SELECT
            cs.rep_id,
            cs.coaching_dimension,
            cs.score,
            cs.created_at
        FROM coaching_sessions cs
        WHERE cs.rep_id = (SELECT id FROM rep_info)
        AND cs.created_at > NOW() - (p_days_back || ' days')::INTERVAL
    ),
    dimension_scores AS (
        SELECT
            coaching_dimension,
            ROUND(AVG(score), 2) as avg_score
        FROM recent_sessions
        GROUP BY coaching_dimension
    ),
    trend_calc AS (
        SELECT
            CASE
                WHEN COUNT(*) < 2 THEN 'insufficient_data'
                WHEN AVG(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN score ELSE NULL END) >
                     AVG(CASE WHEN created_at <= NOW() - INTERVAL '7 days' THEN score ELSE NULL END)
                THEN 'improving'
                WHEN AVG(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN score ELSE NULL END) <
                     AVG(CASE WHEN created_at <= NOW() - INTERVAL '7 days' THEN score ELSE NULL END)
                THEN 'declining'
                ELSE 'stable'
            END as trend
        FROM recent_sessions
    )
    SELECT
        ri.id,
        ri.name,
        ri.email,
        COUNT(DISTINCT c.id)::INT as total_calls,
        COUNT(DISTINCT rs.created_at)::INT as total_sessions,
        ROUND(AVG(rs.score), 2) as avg_score,
        (SELECT avg_score FROM dimension_scores WHERE coaching_dimension = 'product_knowledge'),
        (SELECT avg_score FROM dimension_scores WHERE coaching_dimension = 'discovery'),
        (SELECT avg_score FROM dimension_scores WHERE coaching_dimension = 'objection_handling'),
        (SELECT avg_score FROM dimension_scores WHERE coaching_dimension = 'engagement'),
        (SELECT trend FROM trend_calc),
        MAX(rs.created_at) as last_coached
    FROM rep_info ri
    LEFT JOIN speakers s ON s.email = ri.email AND s.company_side = true
    LEFT JOIN calls c ON c.id = s.call_id
    LEFT JOIN recent_sessions rs ON rs.rep_id = ri.id
    GROUP BY ri.id, ri.name, ri.email;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- OPTIMIZED QUERY: Search Calls with Filters
-- ============================================================================

-- Original: Multiple OR conditions causing index issues
-- Optimized: Uses composite indexes and proper WHERE clause ordering
CREATE OR REPLACE FUNCTION search_calls_optimized(
    p_rep_email VARCHAR DEFAULT NULL,
    p_product VARCHAR DEFAULT NULL,
    p_call_type VARCHAR DEFAULT NULL,
    p_start_date TIMESTAMP DEFAULT NULL,
    p_end_date TIMESTAMP DEFAULT NULL,
    p_min_score INT DEFAULT NULL,
    p_max_score INT DEFAULT NULL,
    p_limit INT DEFAULT 20,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    call_id UUID,
    gong_call_id VARCHAR,
    title VARCHAR,
    scheduled_at TIMESTAMP,
    duration_seconds INT,
    call_type VARCHAR,
    product VARCHAR,
    rep_name VARCHAR,
    rep_email VARCHAR,
    avg_score NUMERIC,
    session_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.gong_call_id,
        c.title,
        c.scheduled_at,
        c.duration_seconds,
        c.call_type,
        c.product,
        s.name as rep_name,
        s.email as rep_email,
        ROUND(AVG(cs.score), 2) as avg_score,
        COUNT(DISTINCT cs.id)::INT as session_count
    FROM calls c
    INNER JOIN speakers s ON s.call_id = c.id AND s.company_side = true
    LEFT JOIN coaching_sessions cs ON cs.call_id = c.id
    WHERE
        (p_rep_email IS NULL OR s.email = p_rep_email)
        AND (p_product IS NULL OR c.product = p_product)
        AND (p_call_type IS NULL OR c.call_type = p_call_type)
        AND (p_start_date IS NULL OR c.scheduled_at >= p_start_date)
        AND (p_end_date IS NULL OR c.scheduled_at <= p_end_date)
    GROUP BY c.id, c.gong_call_id, c.title, c.scheduled_at, c.duration_seconds,
             c.call_type, c.product, s.name, s.email
    HAVING
        (p_min_score IS NULL OR AVG(cs.score) >= p_min_score)
        AND (p_max_score IS NULL OR AVG(cs.score) <= p_max_score)
    ORDER BY c.scheduled_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- OPTIMIZED QUERY: Get Call with All Details (for analysis)
-- ============================================================================

-- Original: Multiple separate queries causing N+1 problem
-- Optimized: Single query with JSON aggregation
CREATE OR REPLACE FUNCTION get_call_with_details(p_call_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'call', jsonb_build_object(
            'id', c.id,
            'gong_call_id', c.gong_call_id,
            'title', c.title,
            'scheduled_at', c.scheduled_at,
            'duration_seconds', c.duration_seconds,
            'call_type', c.call_type,
            'product', c.product,
            'metadata', c.metadata
        ),
        'speakers', (
            SELECT jsonb_agg(jsonb_build_object(
                'id', s.id,
                'name', s.name,
                'email', s.email,
                'role', s.role,
                'company_side', s.company_side,
                'talk_time_seconds', s.talk_time_seconds,
                'talk_time_percentage', s.talk_time_percentage
            ) ORDER BY s.talk_time_percentage DESC)
            FROM speakers s
            WHERE s.call_id = c.id
        ),
        'transcript_segments', (
            SELECT jsonb_agg(jsonb_build_object(
                'sequence_number', t.sequence_number,
                'speaker_id', t.speaker_id,
                'timestamp_seconds', t.timestamp_seconds,
                'text', t.text,
                'sentiment', t.sentiment
            ) ORDER BY t.sequence_number)
            FROM transcripts t
            WHERE t.call_id = c.id
        ),
        'coaching_sessions', (
            SELECT jsonb_agg(jsonb_build_object(
                'id', cs.id,
                'dimension', cs.coaching_dimension,
                'score', cs.score,
                'created_at', cs.created_at
            ) ORDER BY cs.created_at DESC)
            FROM coaching_sessions cs
            WHERE cs.call_id = c.id
        )
    ) INTO result
    FROM calls c
    WHERE c.id = p_call_id;

    RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- OPTIMIZED QUERY: Get Transcript (Fast Assembly)
-- ============================================================================

-- Original: Multiple fetches with array building in application
-- Optimized: Single query with STRING_AGG
CREATE OR REPLACE FUNCTION get_call_transcript(p_call_id UUID)
RETURNS TEXT AS $$
DECLARE
    transcript TEXT;
BEGIN
    SELECT STRING_AGG(
        CONCAT(
            '[', t.timestamp_seconds, 's] ',
            COALESCE(s.name, 'Unknown'), ': ',
            t.text
        ),
        E'\n\n'
        ORDER BY t.sequence_number
    ) INTO transcript
    FROM transcripts t
    LEFT JOIN speakers s ON s.id = t.speaker_id
    WHERE t.call_id = p_call_id;

    RETURN transcript;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- OPTIMIZED QUERY: Cache Statistics
-- ============================================================================

-- Optimized cache hit rate calculation with proper indexes
CREATE OR REPLACE FUNCTION get_cache_statistics(
    p_days_back INT DEFAULT 30
)
RETURNS TABLE (
    total_analyses INT,
    unique_transcripts INT,
    estimated_cache_hits INT,
    cache_hit_rate NUMERIC,
    avg_score NUMERIC,
    tokens_analyzed BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INT as total_analyses,
        COUNT(DISTINCT cs.transcript_hash)::INT as unique_transcripts,
        (COUNT(*) - COUNT(DISTINCT cs.transcript_hash))::INT as estimated_cache_hits,
        ROUND(
            100.0 * (COUNT(*) - COUNT(DISTINCT cs.transcript_hash)) / NULLIF(COUNT(*), 0),
            2
        ) as cache_hit_rate,
        ROUND(AVG(cs.score), 2) as avg_score,
        SUM((cs.metadata->>'input_tokens')::BIGINT) as tokens_analyzed
    FROM coaching_sessions cs
    WHERE cs.created_at > NOW() - (p_days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- MATERIALIZED VIEW: Rep Performance Dashboard
-- ============================================================================

-- Create materialized view for fast dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_rep_performance AS
SELECT
    s.id as rep_id,
    s.name as rep_name,
    s.email as rep_email,
    COUNT(DISTINCT c.id) as total_calls,
    COUNT(DISTINCT cs.id) as total_sessions,
    ROUND(AVG(cs.score), 2) as avg_score,
    ROUND(AVG(CASE WHEN cs.coaching_dimension = 'product_knowledge' THEN cs.score END), 2) as avg_product_knowledge,
    ROUND(AVG(CASE WHEN cs.coaching_dimension = 'discovery' THEN cs.score END), 2) as avg_discovery,
    ROUND(AVG(CASE WHEN cs.coaching_dimension = 'objection_handling' THEN cs.score END), 2) as avg_objection_handling,
    ROUND(AVG(CASE WHEN cs.coaching_dimension = 'engagement' THEN cs.score END), 2) as avg_engagement,
    MAX(cs.created_at) as last_coached,
    NOW() as last_refreshed
FROM speakers s
LEFT JOIN calls c ON c.id = s.call_id
LEFT JOIN coaching_sessions cs ON cs.rep_id = s.id
WHERE s.company_side = true
AND s.email IS NOT NULL
GROUP BY s.id, s.name, s.email;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_rep_performance_email
ON mv_rep_performance(rep_email);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_rep_performance_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rep_performance;
    RAISE NOTICE 'Rep performance view refreshed';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- QUERY PLAN ANALYSIS HELPER
-- ============================================================================

-- Function to analyze query performance
CREATE OR REPLACE FUNCTION analyze_query_plan(query_text TEXT)
RETURNS TABLE (
    query_plan TEXT
) AS $$
BEGIN
    RETURN QUERY EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) ' || query_text;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MAINTENANCE HELPERS
-- ============================================================================

-- Function to vacuum and analyze tables
CREATE OR REPLACE FUNCTION maintain_performance_tables()
RETURNS void AS $$
BEGIN
    -- Vacuum analyze critical tables
    VACUUM ANALYZE coaching_sessions;
    VACUUM ANALYZE calls;
    VACUUM ANALYZE speakers;
    VACUUM ANALYZE transcripts;

    -- Refresh materialized view
    PERFORM refresh_rep_performance_view();

    RAISE NOTICE 'Performance maintenance completed';
END;
$$ LANGUAGE plpgsql;

-- Report success
SELECT 'Query optimizations created successfully!' AS status;
