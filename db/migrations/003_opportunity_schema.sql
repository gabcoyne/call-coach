-- Migration: Add opportunities, emails, and call-opportunity mappings
-- Date: 2026-02-05
-- Related: openspec/changes/opportunity-coaching-view
--
-- Changes:
-- 1. Add opportunities table for storing Gong opportunity data
-- 2. Add emails table for email touchpoints
-- 3. Add call_opportunities junction table for M:N relationship
-- 4. Add sync_status table to track last sync timestamps
-- 5. Add indexes for efficient queries

-- ============================================================================
-- OPPORTUNITIES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_opportunity_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    account_name VARCHAR,
    owner_email VARCHAR,
    stage VARCHAR,
    close_date DATE,
    amount DECIMAL(15, 2),
    health_score DECIMAL(5, 2), -- Gong's native health score
    metadata JSONB, -- Full Gong response for fields we don't model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE opportunities IS
    'Opportunities synced from Gong API for opportunity-level coaching analysis';

COMMENT ON COLUMN opportunities.gong_opportunity_id IS
    'Unique identifier from Gong API';

COMMENT ON COLUMN opportunities.health_score IS
    'Gong native health score (0-100 scale)';

COMMENT ON COLUMN opportunities.metadata IS
    'Full Gong API response stored as JSONB for fields we do not explicitly model';

-- ============================================================================
-- EMAILS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gong_email_id VARCHAR UNIQUE NOT NULL,
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    subject VARCHAR,
    sender_email VARCHAR,
    recipients VARCHAR[],
    sent_at TIMESTAMP WITH TIME ZONE,
    body_snippet TEXT, -- First 500 chars for timeline preview
    metadata JSONB, -- Full email metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE emails IS
    'Email touchpoints associated with opportunities from Gong API';

COMMENT ON COLUMN emails.body_snippet IS
    'First 500 characters of email body for timeline preview';

COMMENT ON COLUMN emails.metadata IS
    'Full email metadata from Gong API stored as JSONB';

-- ============================================================================
-- CALL_OPPORTUNITIES JUNCTION TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS call_opportunities (
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (call_id, opportunity_id)
);

COMMENT ON TABLE call_opportunities IS
    'Many-to-many junction table linking calls to opportunities';

-- ============================================================================
-- SYNC_STATUS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_status (
    entity_type VARCHAR PRIMARY KEY, -- 'opportunities', 'calls', 'emails'
    last_sync_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    last_sync_status VARCHAR, -- 'success', 'partial', 'failed'
    items_synced INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_details JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sync_status IS
    'Tracks last sync timestamps and status per entity type for incremental sync';

COMMENT ON COLUMN sync_status.entity_type IS
    'Type of entity being synced: opportunities, calls, emails';

COMMENT ON COLUMN sync_status.last_sync_timestamp IS
    'Timestamp of last successful sync, used for modifiedAfter parameter in next sync';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Opportunity indexes for efficient filtering and sorting
CREATE INDEX IF NOT EXISTS idx_opportunities_owner
    ON opportunities(owner_email, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_opportunities_stage
    ON opportunities(stage, close_date);

CREATE INDEX IF NOT EXISTS idx_opportunities_updated
    ON opportunities(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_opportunities_health
    ON opportunities(health_score)
    WHERE health_score IS NOT NULL;

-- Email indexes for timeline queries
CREATE INDEX IF NOT EXISTS idx_emails_opportunity
    ON emails(opportunity_id, sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_emails_sent_at
    ON emails(sent_at DESC);

-- Call_opportunities indexes for junction queries
CREATE INDEX IF NOT EXISTS idx_call_opportunities_opp
    ON call_opportunities(opportunity_id);

CREATE INDEX IF NOT EXISTS idx_call_opportunities_call
    ON call_opportunities(call_id);

-- ============================================================================
-- INITIAL SYNC STATUS RECORDS
-- ============================================================================

INSERT INTO sync_status (entity_type, last_sync_timestamp, last_sync_status)
VALUES
    ('opportunities', '2020-01-01 00:00:00+00', 'never'),
    ('emails', '2020-01-01 00:00:00+00', 'never')
ON CONFLICT (entity_type) DO NOTHING;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Schema migration 003 completed successfully';
    RAISE NOTICE 'Added tables: opportunities, emails, call_opportunities, sync_status';
    RAISE NOTICE 'Added indexes for efficient opportunity queries';
END $$;

-- Verify tables exist
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE c.table_name = columns.table_name) as column_count
FROM information_schema.tables c
WHERE table_name IN ('opportunities', 'emails', 'call_opportunities', 'sync_status')
ORDER BY table_name;
