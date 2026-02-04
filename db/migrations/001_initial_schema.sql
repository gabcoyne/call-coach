-- Gong Call Coaching Agent - Initial Schema
-- PostgreSQL 15+ required for partitioning and JSONB optimizations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- ============================================================================
-- WEBHOOK EVENT TRACKING (Idempotency & Audit Trail)
-- ============================================================================

CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_webhook_id VARCHAR UNIQUE NOT NULL, -- Idempotency key from Gong
    event_type VARCHAR NOT NULL,
    payload JSONB NOT NULL,
    signature_valid BOOLEAN NOT NULL,
    status VARCHAR NOT NULL CHECK (status IN ('received', 'processing', 'completed', 'failed')),
    error_message TEXT,
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

CREATE INDEX idx_webhook_events_status ON webhook_events(status, received_at DESC);
CREATE INDEX idx_webhook_events_gong_id ON webhook_events(gong_webhook_id);

-- ============================================================================
-- CALLS & TRANSCRIPTS
-- ============================================================================

CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_call_id VARCHAR UNIQUE NOT NULL,
    title VARCHAR,
    scheduled_at TIMESTAMP,
    duration_seconds INT,
    call_type VARCHAR, -- discovery, demo, negotiation, technical_deep_dive
    product VARCHAR, -- prefect, horizon, both
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    metadata JSONB -- Store raw Gong metadata
);

CREATE INDEX idx_calls_gong_id ON calls(gong_call_id);
CREATE INDEX idx_calls_date_product ON calls(scheduled_at DESC, product);
CREATE INDEX idx_calls_processed ON calls(processed_at DESC) WHERE processed_at IS NOT NULL;

-- ============================================================================
-- CALL PARTICIPANTS
-- ============================================================================

CREATE TABLE speakers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    email VARCHAR,
    role VARCHAR, -- ae, se, csm, prospect, customer
    company_side BOOLEAN NOT NULL DEFAULT false, -- true = Prefect employee
    talk_time_seconds INT,
    talk_time_percentage DECIMAL(5,2)
);

CREATE INDEX idx_speakers_call ON speakers(call_id);
CREATE INDEX idx_speakers_email ON speakers(email) WHERE email IS NOT NULL;
CREATE INDEX idx_speakers_company_side ON speakers(company_side, email);

-- ============================================================================
-- TRANSCRIPTS (with chunking support)
-- ============================================================================

CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    speaker_id UUID REFERENCES speakers(id) ON DELETE SET NULL,
    sequence_number INT NOT NULL,
    timestamp_seconds INT,
    text TEXT NOT NULL,
    sentiment VARCHAR, -- positive, neutral, negative
    topics VARCHAR[], -- Extracted topics/themes
    chunk_metadata JSONB, -- {chunk_id, start_token, end_token, overlap_tokens}
    full_text_search TSVECTOR -- For full-text search
);

CREATE INDEX idx_transcripts_call ON transcripts(call_id, sequence_number);
CREATE INDEX idx_transcripts_search ON transcripts USING GIN(full_text_search);
CREATE INDEX idx_transcripts_speaker ON transcripts(speaker_id) WHERE speaker_id IS NOT NULL;

-- Auto-update full_text_search on insert/update
CREATE OR REPLACE FUNCTION update_transcript_search() RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_search := to_tsvector('english', NEW.text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transcript_search_update
    BEFORE INSERT OR UPDATE OF text ON transcripts
    FOR EACH ROW
    EXECUTE FUNCTION update_transcript_search();

-- ============================================================================
-- ANALYSIS RUN TRACKING (Flow Observability)
-- ============================================================================

CREATE TABLE analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    webhook_event_id UUID REFERENCES webhook_events(id) ON DELETE SET NULL,
    flow_run_id UUID, -- Prefect flow run ID
    status VARCHAR NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    dimensions_analyzed VARCHAR[], -- ['product_knowledge', 'discovery', ...]
    cache_hit BOOLEAN DEFAULT false,
    total_tokens_used INT,
    error_message TEXT,
    metadata JSONB, -- Model version, prompt version, etc.
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_analysis_runs_call ON analysis_runs(call_id, started_at DESC);
CREATE INDEX idx_analysis_runs_status ON analysis_runs(status, started_at DESC);
CREATE INDEX idx_analysis_runs_flow ON analysis_runs(flow_run_id) WHERE flow_run_id IS NOT NULL;

-- ============================================================================
-- COACHING SESSIONS (Partitioned by date for scalability)
-- ============================================================================

CREATE TABLE coaching_sessions (
    id UUID DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    rep_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
    coaching_dimension VARCHAR NOT NULL, -- product_knowledge, discovery, objections, engagement
    session_type VARCHAR NOT NULL, -- real_time, weekly_review, on_demand
    analyst VARCHAR NOT NULL, -- claude-sonnet-4.5, human_coach
    created_at TIMESTAMP DEFAULT NOW(),

    -- Caching support (CRITICAL for cost optimization)
    cache_key VARCHAR,
    transcript_hash VARCHAR, -- SHA256 of transcript content
    rubric_version VARCHAR, -- Version of rubric used

    -- Score for this dimension (0-100)
    score INT CHECK (score >= 0 AND score <= 100),

    -- Detailed analysis
    strengths TEXT[],
    areas_for_improvement TEXT[],
    specific_examples JSONB, -- {good: [...], needs_work: [...]}
    action_items TEXT[],

    -- Full analysis text
    full_analysis TEXT,
    metadata JSONB,

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create quarterly partitions for 2025-2026
CREATE TABLE coaching_sessions_2025_q1 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE coaching_sessions_2025_q2 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE coaching_sessions_2025_q3 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE coaching_sessions_2025_q4 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE coaching_sessions_2026_q1 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE coaching_sessions_2026_q2 PARTITION OF coaching_sessions
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

-- Indexes for performance (CRITICAL - missing indexes = slow queries)
CREATE INDEX idx_coaching_sessions_cache ON coaching_sessions(cache_key, transcript_hash, rubric_version);
CREATE INDEX idx_coaching_sessions_call_rep ON coaching_sessions(call_id, rep_id, created_at DESC);
CREATE INDEX idx_coaching_sessions_dimension ON coaching_sessions(coaching_dimension, created_at DESC);
CREATE INDEX idx_coaching_sessions_rep ON coaching_sessions(rep_id, created_at DESC);

-- ============================================================================
-- GRANULAR METRICS FOR TRENDING
-- ============================================================================

CREATE TABLE coaching_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coaching_session_id UUID NOT NULL, -- References coaching_sessions(id) but no FK due to partitioning
    metric_name VARCHAR NOT NULL, -- talk_ratio, question_count, technical_accuracy, etc.
    metric_value DECIMAL NOT NULL,
    metric_context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coaching_metrics_session ON coaching_metrics(coaching_session_id);
CREATE INDEX idx_coaching_metrics_name ON coaching_metrics(metric_name, created_at DESC);

-- ============================================================================
-- KNOWLEDGE BASE (Product docs, competitive intel)
-- ============================================================================

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product VARCHAR NOT NULL, -- prefect, horizon
    category VARCHAR NOT NULL, -- feature, differentiation, use_case, pricing, competitor
    content TEXT NOT NULL,
    metadata JSONB,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_base_product ON knowledge_base(product, category);

-- ============================================================================
-- COACHING RUBRICS (Versioned for cache invalidation)
-- ============================================================================

CREATE TABLE coaching_rubrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL, -- Semantic version (e.g., "1.0.0")
    category VARCHAR NOT NULL, -- discovery, objection_handling, product_knowledge, engagement
    criteria JSONB NOT NULL, -- Structured evaluation criteria
    scoring_guide JSONB,
    examples JSONB,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    deprecated_at TIMESTAMP,
    UNIQUE(category, version)
);

CREATE INDEX idx_coaching_rubrics_active ON coaching_rubrics(category, active, version DESC);

-- ============================================================================
-- COACHING FEEDBACK (Continuous improvement loop)
-- ============================================================================

CREATE TABLE coaching_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coaching_session_id UUID NOT NULL, -- References coaching_sessions(id) but no FK due to partitioning
    rep_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
    feedback_type VARCHAR NOT NULL CHECK (feedback_type IN ('accurate', 'inaccurate', 'missing_context', 'helpful', 'not_helpful')),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coaching_feedback_session ON coaching_feedback(coaching_session_id);
CREATE INDEX idx_coaching_feedback_rep ON coaching_feedback(rep_id, created_at DESC);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Rep performance summary view
CREATE VIEW rep_performance_summary AS
SELECT
    s.id AS rep_id,
    s.name AS rep_name,
    s.email AS rep_email,
    s.role AS rep_role,
    COUNT(DISTINCT c.id) AS total_calls,
    ROUND(AVG(cs.score), 2) AS avg_score,
    COUNT(DISTINCT cs.id) AS total_coaching_sessions,
    MAX(cs.created_at) AS last_coached
FROM speakers s
JOIN calls c ON s.call_id = c.id
LEFT JOIN coaching_sessions cs ON cs.rep_id = s.id
WHERE s.company_side = true
GROUP BY s.id, s.name, s.email, s.role;

-- Call analysis status view
CREATE VIEW call_analysis_status AS
SELECT
    c.id AS call_id,
    c.gong_call_id,
    c.title,
    c.scheduled_at,
    c.processed_at,
    ar.status AS analysis_status,
    ar.dimensions_analyzed,
    ar.cache_hit,
    ar.completed_at AS analysis_completed_at,
    COUNT(cs.id) AS coaching_sessions_count
FROM calls c
LEFT JOIN analysis_runs ar ON ar.call_id = c.id
LEFT JOIN coaching_sessions cs ON cs.call_id = c.id
GROUP BY c.id, c.gong_call_id, c.title, c.scheduled_at, c.processed_at,
         ar.status, ar.dimensions_analyzed, ar.cache_hit, ar.completed_at;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get cache hit rate for a date range
CREATE OR REPLACE FUNCTION get_cache_hit_rate(
    start_date TIMESTAMP DEFAULT NOW() - INTERVAL '30 days',
    end_date TIMESTAMP DEFAULT NOW()
)
RETURNS TABLE (
    total_analyses INT,
    cache_hits INT,
    cache_hit_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INT AS total_analyses,
        SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END)::INT AS cache_hits,
        ROUND(
            100.0 * SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
            2
        ) AS cache_hit_rate
    FROM analysis_runs
    WHERE started_at BETWEEN start_date AND end_date
    AND status = 'completed';
END;
$$ LANGUAGE plpgsql;

-- Function to find duplicate transcripts (for cache deduplication)
CREATE OR REPLACE FUNCTION find_duplicate_transcripts()
RETURNS TABLE (
    transcript_hash VARCHAR,
    call_count INT,
    call_ids UUID[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cs.transcript_hash,
        COUNT(DISTINCT cs.call_id)::INT AS call_count,
        ARRAY_AGG(DISTINCT cs.call_id) AS call_ids
    FROM coaching_sessions cs
    WHERE cs.transcript_hash IS NOT NULL
    GROUP BY cs.transcript_hash
    HAVING COUNT(DISTINCT cs.call_id) > 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (adjust as needed for your security model)
-- ============================================================================

-- Create application role
-- CREATE ROLE call_coach_app WITH LOGIN PASSWORD 'change_me_in_production';
-- GRANT CONNECT ON DATABASE callcoach TO call_coach_app;
-- GRANT USAGE ON SCHEMA public TO call_coach_app;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO call_coach_app;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO call_coach_app;

-- ============================================================================
-- INITIALIZATION COMPLETE
-- ============================================================================

-- Verify setup
SELECT 'Schema initialized successfully!' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'public';
