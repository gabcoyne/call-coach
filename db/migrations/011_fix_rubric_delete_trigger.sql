-- Migration: 011_fix_rubric_delete_trigger.sql
-- Purpose: Fix trigger timing for DELETE operations on rubric_criteria
-- Date: 2026-02-07
-- Issue: AFTER DELETE trigger causes FK constraint error because row is already deleted
-- Solution: Change to BEFORE DELETE for deletion logging

-- Drop existing trigger
DROP TRIGGER IF EXISTS trigger_log_rubric_changes ON rubric_criteria;

-- Recreate trigger with BEFORE DELETE for proper deletion logging
CREATE TRIGGER trigger_log_rubric_changes
    BEFORE DELETE ON rubric_criteria
    FOR EACH ROW
    EXECUTE FUNCTION log_rubric_criterion_change();

-- Recreate trigger for INSERT/UPDATE as AFTER (correct timing for these)
CREATE TRIGGER trigger_log_rubric_changes_after
    AFTER INSERT OR UPDATE ON rubric_criteria
    FOR EACH ROW
    EXECUTE FUNCTION log_rubric_criterion_change();

COMMENT ON TRIGGER trigger_log_rubric_changes ON rubric_criteria IS 'Logs deletions BEFORE they happen to avoid FK constraint issues';
COMMENT ON TRIGGER trigger_log_rubric_changes_after ON rubric_criteria IS 'Logs insertions and updates AFTER they complete';

-- Show summary
DO $$
BEGIN
    RAISE NOTICE '=== Rubric Change Trigger Fixed ===';
    RAISE NOTICE 'Split into two triggers:';
    RAISE NOTICE '  - BEFORE DELETE: trigger_log_rubric_changes';
    RAISE NOTICE '  - AFTER INSERT OR UPDATE: trigger_log_rubric_changes_after';
    RAISE NOTICE 'This prevents FK constraint violations when logging deletions';
END $$;
