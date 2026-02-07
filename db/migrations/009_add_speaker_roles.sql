-- Migration: 009_add_speaker_roles.sql
-- Purpose: Add business role column to speakers table for role-based coaching analysis
-- Date: 2026-02-07

-- Create speaker role enum (different from user_role - this is for business function)
-- Make idempotent: only create if not exists
DO $$ BEGIN
    CREATE TYPE speaker_role AS ENUM ('ae', 'se', 'csm', 'support');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add role column to speakers table (nullable to allow gradual assignment)
-- Make idempotent: only add if not exists
DO $$ BEGIN
    ALTER TABLE speakers ADD COLUMN role speaker_role DEFAULT NULL;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Add comment explaining the purpose
COMMENT ON COLUMN speakers.role IS 'Business role for coaching rubric selection: ae=Account Executive, se=Sales Engineer, csm=Customer Success Manager, support=Support Engineer';

-- Create index for role-based queries (idempotent)
CREATE INDEX IF NOT EXISTS idx_speakers_role ON speakers(role);

-- Create index for company-side speakers with roles (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_speakers_company_role ON speakers(company_side, role) WHERE company_side = true;

-- Optional: Backfill some obvious roles based on email patterns
-- (Can be expanded later with manual assignments)
UPDATE speakers
SET role = 'ae'
WHERE company_side = true
  AND email LIKE '%@prefect.io'
  AND (
    email LIKE '%ae%' OR
    email IN ('george@prefect.io', 'mason@prefect.io') -- Known AEs
  );

UPDATE speakers
SET role = 'se'
WHERE company_side = true
  AND email LIKE '%@prefect.io'
  AND (
    email LIKE '%se%' OR
    email LIKE '%engineer%'
  );

UPDATE speakers
SET role = 'csm'
WHERE company_side = true
  AND email LIKE '%@prefect.io'
  AND (
    email LIKE '%csm%' OR
    email LIKE '%success%'
  );

UPDATE speakers
SET role = 'support'
WHERE company_side = true
  AND email LIKE '%@prefect.io'
  AND email LIKE '%support%';

-- Show summary of role assignments
DO $$
DECLARE
    total_speakers INTEGER;
    assigned_roles INTEGER;
    ae_count INTEGER;
    se_count INTEGER;
    csm_count INTEGER;
    support_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_speakers FROM speakers WHERE company_side = true;
    SELECT COUNT(*) INTO assigned_roles FROM speakers WHERE company_side = true AND role IS NOT NULL;
    SELECT COUNT(*) INTO ae_count FROM speakers WHERE role = 'ae';
    SELECT COUNT(*) INTO se_count FROM speakers WHERE role = 'se';
    SELECT COUNT(*) INTO csm_count FROM speakers WHERE role = 'csm';
    SELECT COUNT(*) INTO support_count FROM speakers WHERE role = 'support';

    RAISE NOTICE '=== Speaker Role Migration Summary ===';
    RAISE NOTICE 'Total company speakers: %', total_speakers;
    RAISE NOTICE 'Speakers with roles assigned: % (%.0f%%)', assigned_roles, (assigned_roles::float / NULLIF(total_speakers, 0) * 100);
    RAISE NOTICE '  - AE: %', ae_count;
    RAISE NOTICE '  - SE: %', se_count;
    RAISE NOTICE '  - CSM: %', csm_count;
    RAISE NOTICE '  - Support: %', support_count;
    RAISE NOTICE 'Speakers needing manual assignment: %', total_speakers - assigned_roles;
END $$;
