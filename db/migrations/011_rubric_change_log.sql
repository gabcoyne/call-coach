-- Migration: 011_rubric_change_log.sql
-- Purpose: Create audit trail table for tracking rubric criteria changes
-- Date: 2026-02-07

-- Create change type enum
DO $$ BEGIN
    CREATE TYPE rubric_change_type AS ENUM ('created', 'updated', 'deleted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create rubric_change_log table
CREATE TABLE IF NOT EXISTS rubric_change_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    criterion_id UUID REFERENCES rubric_criteria(id) ON DELETE SET NULL,
    change_type rubric_change_type NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP DEFAULT NOW(),

    -- Store snapshot of full criterion at time of change
    criterion_snapshot JSONB
);

-- Add comments
COMMENT ON TABLE rubric_change_log IS 'Audit trail for all rubric criteria changes';
COMMENT ON COLUMN rubric_change_log.criterion_id IS 'Reference to rubric criterion (nullable if deleted)';
COMMENT ON COLUMN rubric_change_log.change_type IS 'Type of change: created, updated, deleted';
COMMENT ON COLUMN rubric_change_log.field_name IS 'Specific field changed (for updates): description, weight, max_score, etc.';
COMMENT ON COLUMN rubric_change_log.old_value IS 'Previous value before change (for updates and deletes)';
COMMENT ON COLUMN rubric_change_log.new_value IS 'New value after change (for creates and updates)';
COMMENT ON COLUMN rubric_change_log.changed_by IS 'Email of user who made the change';
COMMENT ON COLUMN rubric_change_log.criterion_snapshot IS 'Full JSONB snapshot of criterion for rollback capability';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rubric_change_log_criterion ON rubric_change_log(criterion_id);
CREATE INDEX IF NOT EXISTS idx_rubric_change_log_changed_at ON rubric_change_log(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_rubric_change_log_changed_by ON rubric_change_log(changed_by);
CREATE INDEX IF NOT EXISTS idx_rubric_change_log_type ON rubric_change_log(change_type);

-- Create function to automatically log rubric changes
CREATE OR REPLACE FUNCTION log_rubric_criterion_change()
RETURNS TRIGGER AS $$
DECLARE
    change_type rubric_change_type;
    field_name VARCHAR(50);
    old_val TEXT;
    new_val TEXT;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        change_type := 'created';
        INSERT INTO rubric_change_log (
            criterion_id, change_type, new_value, changed_by, criterion_snapshot
        ) VALUES (
            NEW.id,
            change_type,
            'Created criterion: ' || NEW.criterion_name,
            COALESCE(current_setting('app.current_user', true), 'system'),
            row_to_json(NEW)::jsonb
        );
        RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN
        -- Log each field that changed
        IF (OLD.description != NEW.description) THEN
            INSERT INTO rubric_change_log (
                criterion_id, change_type, field_name, old_value, new_value, changed_by, criterion_snapshot
            ) VALUES (
                NEW.id, 'updated', 'description', OLD.description, NEW.description,
                COALESCE(current_setting('app.current_user', true), 'system'),
                row_to_json(NEW)::jsonb
            );
        END IF;

        IF (OLD.weight != NEW.weight) THEN
            INSERT INTO rubric_change_log (
                criterion_id, change_type, field_name, old_value, new_value, changed_by, criterion_snapshot
            ) VALUES (
                NEW.id, 'updated', 'weight', OLD.weight::TEXT, NEW.weight::TEXT,
                COALESCE(current_setting('app.current_user', true), 'system'),
                row_to_json(NEW)::jsonb
            );
        END IF;

        IF (OLD.max_score != NEW.max_score) THEN
            INSERT INTO rubric_change_log (
                criterion_id, change_type, field_name, old_value, new_value, changed_by, criterion_snapshot
            ) VALUES (
                NEW.id, 'updated', 'max_score', OLD.max_score::TEXT, NEW.max_score::TEXT,
                COALESCE(current_setting('app.current_user', true), 'system'),
                row_to_json(NEW)::jsonb
            );
        END IF;

        IF (OLD.display_order != NEW.display_order) THEN
            INSERT INTO rubric_change_log (
                criterion_id, change_type, field_name, old_value, new_value, changed_by, criterion_snapshot
            ) VALUES (
                NEW.id, 'updated', 'display_order', OLD.display_order::TEXT, NEW.display_order::TEXT,
                COALESCE(current_setting('app.current_user', true), 'system'),
                row_to_json(NEW)::jsonb
            );
        END IF;

        RETURN NEW;

    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO rubric_change_log (
            criterion_id, change_type, old_value, changed_by, criterion_snapshot
        ) VALUES (
            OLD.id,
            'deleted',
            'Deleted criterion: ' || OLD.criterion_name,
            COALESCE(current_setting('app.current_user', true), 'system'),
            row_to_json(OLD)::jsonb
        );
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on rubric_criteria table
DO $$ BEGIN
    CREATE TRIGGER trigger_log_rubric_changes
        AFTER INSERT OR UPDATE OR DELETE ON rubric_criteria
        FOR EACH ROW
        EXECUTE FUNCTION log_rubric_criterion_change();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON FUNCTION log_rubric_criterion_change IS 'Automatically logs all changes to rubric_criteria table for audit trail';

-- Show summary
DO $$
BEGIN
    RAISE NOTICE '=== Rubric Change Log Table Created ===';
    RAISE NOTICE 'Table: rubric_change_log';
    RAISE NOTICE 'Indexes: criterion_id, changed_at, changed_by, change_type';
    RAISE NOTICE 'Trigger: Automatic logging of all rubric_criteria changes';
    RAISE NOTICE 'Features: Field-level tracking, JSONB snapshots for rollback';
    RAISE NOTICE 'Usage: Set app.current_user to track who made changes';
END $$;
