-- Migration: 012_speaker_role_history.sql
-- Purpose: Create audit trail table for tracking speaker role changes
-- Date: 2026-02-07

-- Create speaker_role_history table
CREATE TABLE IF NOT EXISTS speaker_role_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
    old_role speaker_role,
    new_role speaker_role,
    changed_by VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP DEFAULT NOW(),
    change_reason TEXT,

    -- Metadata for context
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Add comments
COMMENT ON TABLE speaker_role_history IS 'Audit trail for all speaker role assignments and changes';
COMMENT ON COLUMN speaker_role_history.speaker_id IS 'Reference to speaker whose role changed';
COMMENT ON COLUMN speaker_role_history.old_role IS 'Previous role (NULL if first assignment)';
COMMENT ON COLUMN speaker_role_history.new_role IS 'New role after change (NULL if role removed)';
COMMENT ON COLUMN speaker_role_history.changed_by IS 'Email of user who made the change';
COMMENT ON COLUMN speaker_role_history.changed_at IS 'When the role change occurred';
COMMENT ON COLUMN speaker_role_history.change_reason IS 'Optional reason for the role change';
COMMENT ON COLUMN speaker_role_history.metadata IS 'Additional context (e.g., changed via bulk operation, automated backfill)';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_speaker_role_history_speaker ON speaker_role_history(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_role_history_changed_at ON speaker_role_history(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_speaker_role_history_changed_by ON speaker_role_history(changed_by);
CREATE INDEX IF NOT EXISTS idx_speaker_role_history_new_role ON speaker_role_history(new_role);

-- Create function to automatically log role changes
CREATE OR REPLACE FUNCTION log_speaker_role_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        -- Only log if role is not NULL (skip initial NULL assignments)
        IF NEW.role IS NOT NULL THEN
            INSERT INTO speaker_role_history (
                speaker_id, old_role, new_role, changed_by, change_reason, metadata
            ) VALUES (
                NEW.id,
                NULL,
                NEW.role,
                COALESCE(current_setting('app.current_user', true), 'system'),
                'Initial role assignment',
                jsonb_build_object('trigger', 'INSERT')
            );
        END IF;
        RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN
        -- Only log if role actually changed
        IF (OLD.role IS DISTINCT FROM NEW.role) THEN
            INSERT INTO speaker_role_history (
                speaker_id, old_role, new_role, changed_by, change_reason, metadata
            ) VALUES (
                NEW.id,
                OLD.role,
                NEW.role,
                COALESCE(current_setting('app.current_user', true), 'system'),
                CASE
                    WHEN NEW.role IS NULL THEN 'Role removed'
                    WHEN OLD.role IS NULL THEN 'Role assigned'
                    ELSE 'Role changed'
                END,
                jsonb_build_object(
                    'trigger', 'UPDATE',
                    'old_role', OLD.role::text,
                    'new_role', NEW.role::text
                )
            );
        END IF;
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on speakers table
DO $$ BEGIN
    CREATE TRIGGER trigger_log_speaker_role_changes
        AFTER INSERT OR UPDATE ON speakers
        FOR EACH ROW
        EXECUTE FUNCTION log_speaker_role_change();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON FUNCTION log_speaker_role_change IS 'Automatically logs all role changes to speakers table for audit trail';

-- Show summary
DO $$
DECLARE
    speaker_count INTEGER;
    role_assigned_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO speaker_count FROM speakers WHERE company_side = true;
    SELECT COUNT(*) INTO role_assigned_count FROM speakers WHERE company_side = true AND role IS NOT NULL;

    RAISE NOTICE '=== Speaker Role History Table Created ===';
    RAISE NOTICE 'Table: speaker_role_history';
    RAISE NOTICE 'Indexes: speaker_id, changed_at, changed_by, new_role';
    RAISE NOTICE 'Trigger: Automatic logging of all speaker role changes';
    RAISE NOTICE 'Features: Track role assignments, changes, and removals';
    RAISE NOTICE '';
    RAISE NOTICE 'Current state:';
    RAISE NOTICE '  Total company speakers: %', speaker_count;
    RAISE NOTICE '  Speakers with roles: %', role_assigned_count;
    RAISE NOTICE '  Speakers needing roles: %', speaker_count - role_assigned_count;
END $$;
