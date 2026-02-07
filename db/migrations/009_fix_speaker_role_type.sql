-- Migration: 009_fix_speaker_role_type.sql
-- Purpose: Fix speakers.role column type from VARCHAR to speaker_role enum
-- Date: 2026-02-07
-- Note: This patches migration 009 which may have been run when a VARCHAR role column already existed

-- Drop any views that depend on the role column
DROP VIEW IF EXISTS rep_performance_summary CASCADE;

-- Check if column exists and has wrong type, then fix it
DO $$
DECLARE
    col_type TEXT;
BEGIN
    -- Get the current column type
    SELECT udt_name INTO col_type
    FROM information_schema.columns
    WHERE table_name = 'speakers' AND column_name = 'role';

    -- If column exists and is not the enum type, fix it
    IF col_type IS NOT NULL AND col_type != 'speaker_role' THEN
        RAISE NOTICE 'Fixing speakers.role column type from % to speaker_role', col_type;

        -- Store existing values temporarily
        ALTER TABLE speakers ADD COLUMN role_temp VARCHAR;
        UPDATE speakers SET role_temp = role::VARCHAR;

        -- Drop and recreate with correct type
        ALTER TABLE speakers DROP COLUMN role CASCADE;
        ALTER TABLE speakers ADD COLUMN role speaker_role DEFAULT NULL;

        -- Restore values (only valid enum values)
        UPDATE speakers
        SET role = role_temp::speaker_role
        WHERE role_temp IN ('ae', 'se', 'csm', 'support');

        -- Drop temp column
        ALTER TABLE speakers DROP COLUMN role_temp;

        RAISE NOTICE '✓ Fixed speakers.role column type';
    ELSIF col_type = 'speaker_role' THEN
        RAISE NOTICE '✓ speakers.role column already has correct type (speaker_role)';
    ELSE
        RAISE NOTICE '✓ speakers.role column does not exist (will be created by migration 009)';
    END IF;
END $$;

-- Recreate indexes (idempotent)
CREATE INDEX IF NOT EXISTS idx_speakers_role ON speakers(role);
CREATE INDEX IF NOT EXISTS idx_speakers_company_role ON speakers(company_side, role) WHERE company_side = true;

-- Show summary
DO $$
BEGIN
    RAISE NOTICE '=== Speaker Role Column Type Fixed ===';
    RAISE NOTICE 'Column: speakers.role now uses speaker_role enum';
    RAISE NOTICE 'Next: Run migrations 010-012 for rubric management';
END $$;
