-- Migration: 010_rubric_criteria.sql
-- Purpose: Create table for storing role-based rubric evaluation criteria
-- Date: 2026-02-07

-- Create rubric_criteria table
CREATE TABLE IF NOT EXISTS rubric_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role speaker_role NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    criterion_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL CHECK (char_length(description) BETWEEN 10 AND 500),
    weight INTEGER NOT NULL CHECK (weight >= 0 AND weight <= 100),
    max_score INTEGER NOT NULL CHECK (max_score >= 1 AND max_score <= 100),
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique criterion names per role-dimension
    CONSTRAINT unique_criterion_per_role_dimension UNIQUE (role, dimension, criterion_name)
);

-- Add comments
COMMENT ON TABLE rubric_criteria IS 'Stores evaluation criteria for role-based coaching rubrics';
COMMENT ON COLUMN rubric_criteria.role IS 'Business role: ae, se, csm, support';
COMMENT ON COLUMN rubric_criteria.dimension IS 'Coaching dimension: discovery, engagement, product_knowledge, objection_handling, five_wins';
COMMENT ON COLUMN rubric_criteria.criterion_name IS 'Short name for the criterion (e.g., "Opening Questions", "SPICED Framework")';
COMMENT ON COLUMN rubric_criteria.description IS 'Detailed description of what this criterion evaluates';
COMMENT ON COLUMN rubric_criteria.weight IS 'Percentage weight of this criterion within the dimension (must sum to 100 per role-dimension)';
COMMENT ON COLUMN rubric_criteria.max_score IS 'Maximum score for this criterion';
COMMENT ON COLUMN rubric_criteria.display_order IS 'Display order in UI (lower numbers first)';

-- Create indexes (idempotent)
CREATE INDEX IF NOT EXISTS idx_rubric_criteria_role_dimension ON rubric_criteria(role, dimension);
CREATE INDEX IF NOT EXISTS idx_rubric_criteria_dimension ON rubric_criteria(dimension);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_rubric_criteria_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (idempotent)
DO $$ BEGIN
    CREATE TRIGGER trigger_rubric_criteria_updated_at
        BEFORE UPDATE ON rubric_criteria
        FOR EACH ROW
        EXECUTE FUNCTION update_rubric_criteria_updated_at();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Validation function to check dimension weights sum to 100
CREATE OR REPLACE FUNCTION validate_dimension_weights(
    p_role speaker_role,
    p_dimension VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    total_weight INTEGER;
BEGIN
    SELECT COALESCE(SUM(weight), 0)
    INTO total_weight
    FROM rubric_criteria
    WHERE role = p_role AND dimension = p_dimension;

    RETURN total_weight = 100;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_dimension_weights IS 'Validates that all criteria weights for a role-dimension sum to exactly 100%';

-- Show summary
DO $$
BEGIN
    RAISE NOTICE '=== Rubric Criteria Table Created ===';
    RAISE NOTICE 'Table: rubric_criteria';
    RAISE NOTICE 'Indexes: idx_rubric_criteria_role_dimension, idx_rubric_criteria_dimension';
    RAISE NOTICE 'Constraints: unique criterion names per role-dimension';
    RAISE NOTICE 'Validation: weights must sum to 100%% per role-dimension';
    RAISE NOTICE 'Next: Run migration 011 to seed default rubric criteria';
END $$;
