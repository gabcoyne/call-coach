-- Migration: 007_add_dashboard_fields.sql
-- Purpose: Add fields needed for dashboard team/rep views
-- Date: 2026-02-06

-- Add columns to calls table for dashboard
ALTER TABLE calls ADD COLUMN IF NOT EXISTS prefect_reps VARCHAR[] DEFAULT '{}';
ALTER TABLE calls ADD COLUMN IF NOT EXISTS overall_score INT;
ALTER TABLE calls ADD COLUMN IF NOT EXISTS date DATE;

-- Add indexes for dashboard queries
CREATE INDEX IF NOT EXISTS idx_calls_prefect_reps ON calls USING GIN(prefect_reps);
CREATE INDEX IF NOT EXISTS idx_calls_date ON calls(date DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_calls_overall_score ON calls(overall_score) WHERE overall_score IS NOT NULL;

-- Add comments
COMMENT ON COLUMN calls.prefect_reps IS 'Array of Prefect employee names who participated in the call';
COMMENT ON COLUMN calls.overall_score IS 'Overall coaching score (0-100) from analysis';
COMMENT ON COLUMN calls.date IS 'Call date (extracted from scheduled_at for easier querying)';

-- Backfill date from scheduled_at for existing calls
UPDATE calls SET date = scheduled_at::date WHERE date IS NULL AND scheduled_at IS NOT NULL;

-- Backfill prefect_reps from speakers table for existing calls
UPDATE calls c
SET prefect_reps = (
    SELECT array_agg(DISTINCT s.name)
    FROM speakers s
    WHERE s.call_id = c.id AND s.company_side = true
)
WHERE prefect_reps = '{}';
