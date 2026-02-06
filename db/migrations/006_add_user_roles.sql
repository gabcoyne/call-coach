-- Migration: 006_add_user_roles.sql
-- Purpose: Add user roles and permissions for RBAC (admin, manager, rep)
-- Date: 2026-02-06

-- Create role enum
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'rep');

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    role user_role NOT NULL DEFAULT 'rep',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add manager_id to speakers table (links rep to their manager)
ALTER TABLE speakers ADD COLUMN manager_id UUID REFERENCES users(id);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_speakers_manager ON speakers(manager_id);

-- Seed initial users from speakers (Prefect employees only)
INSERT INTO users (email, name, role)
SELECT DISTINCT ON (email) email, name, 'rep'
FROM speakers
WHERE company_side = true AND email IS NOT NULL
ORDER BY email;

-- Promote specific users to manager (based on known managers)
UPDATE users SET role = 'manager'
WHERE email IN ('george@prefect.io', 'ann@prefect.io');

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with role-based access control';
COMMENT ON COLUMN users.role IS 'User role: admin (full access), manager (team access), rep (own calls only)';
COMMENT ON COLUMN speakers.manager_id IS 'References the manager assigned to this rep';

-- Create function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER users_updated_at_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();
