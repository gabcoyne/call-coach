-- Migration: 004_staff_roles.sql
-- Purpose: Add staff_roles table for role-based coaching rubrics (AE, SE, CSM)
-- Date: 2026-02-05

-- Create staff_roles table with email as primary key
CREATE TABLE IF NOT EXISTS staff_roles (
    email VARCHAR PRIMARY KEY,  -- e.g., sarah.chen@prefect.io
    role VARCHAR NOT NULL CHECK (role IN ('ae', 'se', 'csm')),
    assigned_by VARCHAR NOT NULL,  -- Manager email who made assignment
    assigned_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add index on role column for filtering queries
CREATE INDEX IF NOT EXISTS idx_staff_roles_role ON staff_roles(role);

-- Add comment for documentation
COMMENT ON TABLE staff_roles IS 'Stores role assignments (AE/SE/CSM) for Prefect staff identified by @prefect.io email domain';
COMMENT ON COLUMN staff_roles.email IS 'Staff member email address (must end in @prefect.io)';
COMMENT ON COLUMN staff_roles.role IS 'Assigned role: ae (Account Executive), se (Sales Engineer), csm (Customer Success Manager)';
COMMENT ON COLUMN staff_roles.assigned_by IS 'Email of manager who assigned/updated the role';
COMMENT ON COLUMN staff_roles.assigned_at IS 'Timestamp when role was first assigned';
COMMENT ON COLUMN staff_roles.updated_at IS 'Timestamp when role assignment was last updated';
