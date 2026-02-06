/**
 * Database query functions for Next.js API routes.
 *
 * This module provides TypeScript wrappers around database queries
 * for use in Next.js API routes and server components.
 */
import { query } from "./connection";

/**
 * Get all Prefect staff emails from speakers table.
 *
 * Returns unique @prefect.io email addresses with names from call transcripts.
 */
export async function get_prefect_staff() {
  const result = await query(
    `
    SELECT DISTINCT
      email,
      name
    FROM speakers
    WHERE email LIKE '%@prefect.io'
      AND email IS NOT NULL
    ORDER BY name
    `
  );

  return result.rows;
}

/**
 * List all staff role assignments.
 *
 * Returns all rows from staff_roles table with metadata.
 */
export async function list_all_staff_roles() {
  const result = await query(
    `
    SELECT
      email,
      role,
      assigned_by,
      assigned_at,
      updated_at
    FROM staff_roles
    ORDER BY updated_at DESC
    `
  );

  return result.rows;
}

/**
 * Get role assignment for a specific staff member.
 *
 * @param email - Staff email address
 * @returns Role string ('ae', 'se', 'csm') or null if no assignment
 */
export async function get_staff_role(email: string): Promise<string | null> {
  const result = await query(
    `SELECT role FROM staff_roles WHERE email = $1`,
    [email]
  );

  return result.rows.length > 0 ? result.rows[0].role : null;
}

/**
 * Create or update role assignment for a staff member.
 *
 * @param email - Staff email address (must be @prefect.io)
 * @param role - Role to assign ('ae', 'se', 'csm')
 * @param assigned_by - Manager email making the assignment
 */
export async function upsert_staff_role(
  email: string,
  role: string,
  assigned_by: string
): Promise<void> {
  await query(
    `
    INSERT INTO staff_roles (email, role, assigned_by, assigned_at, updated_at)
    VALUES ($1, $2, $3, NOW(), NOW())
    ON CONFLICT (email)
    DO UPDATE SET
      role = EXCLUDED.role,
      assigned_by = EXCLUDED.assigned_by,
      updated_at = NOW()
    `,
    [email, role, assigned_by]
  );
}

/**
 * Delete role assignment for a staff member.
 *
 * @param email - Staff email address
 */
export async function delete_staff_role(email: string): Promise<void> {
  await query(`DELETE FROM staff_roles WHERE email = $1`, [email]);
}

// Re-export from opportunities module
export * from "./opportunities";
