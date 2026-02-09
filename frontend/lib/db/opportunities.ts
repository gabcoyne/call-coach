/**
 * Database queries for opportunities using PostgreSQL directly from Next.js.
 */
import { query } from "./connection";

export interface Opportunity {
  id: string;
  gong_opportunity_id: string;
  name: string;
  account_name: string;
  owner_email: string;
  stage: string;
  close_date: string;
  amount: number;
  health_score: number;
  metadata: any;
  created_at: string;
  updated_at: string;
  call_count?: number;
  email_count?: number;
}

export interface TimelineItem {
  item_type: "call" | "email";
  id: string;
  gong_call_id?: string;
  gong_email_id?: string;
  timestamp: string;
  title?: string;
  subject?: string;
  duration?: number;
  sender_email?: string;
}

export async function searchOpportunities({
  filters = {},
  sort = "updated_at",
  sortDir = "DESC",
  limit = 50,
  offset = 0,
}: {
  filters?: Record<string, any>;
  sort?: string;
  sortDir?: string;
  limit?: number;
  offset?: number;
}): Promise<{ opportunities: Opportunity[]; total: number }> {
  // Build WHERE clauses
  const whereClauses: string[] = [];
  const params: any[] = [];
  let paramIndex = 1;

  if (filters.owner) {
    whereClauses.push(`o.owner_email = $${paramIndex++}`);
    params.push(filters.owner);
  }

  if (filters.stage) {
    if (Array.isArray(filters.stage)) {
      whereClauses.push(`o.stage = ANY($${paramIndex++})`);
      params.push(filters.stage);
    } else {
      whereClauses.push(`o.stage = $${paramIndex++}`);
      params.push(filters.stage);
    }
  }

  if (filters.health_score_min !== undefined) {
    whereClauses.push(`o.health_score >= $${paramIndex++}`);
    params.push(filters.health_score_min);
  }

  if (filters.health_score_max !== undefined) {
    whereClauses.push(`o.health_score <= $${paramIndex++}`);
    params.push(filters.health_score_max);
  }

  if (filters.search) {
    whereClauses.push(
      `(o.name ILIKE $${paramIndex} OR o.account_name ILIKE $${paramIndex})`
    );
    params.push(`%${filters.search}%`);
    paramIndex++;
  }

  const whereSQL = whereClauses.length > 0 ? `WHERE ${whereClauses.join(" AND ")}` : "";

  // Validate sort field
  const validSorts = new Set(["updated_at", "close_date", "health_score", "amount"]);
  const sortField = validSorts.has(sort) ? sort : "updated_at";
  const sortDirection = sortDir.toUpperCase() === "ASC" ? "ASC" : "DESC";

  // Get total count
  const countResult = await query(
    `SELECT COUNT(*) as total FROM opportunities o ${whereSQL}`,
    params
  );
  const total = parseInt(countResult.rows[0]?.total || "0", 10);

  // Get paginated results
  params.push(limit, offset);
  const result = await query(
    `
    SELECT
      o.*,
      COUNT(DISTINCT co.call_id) as call_count,
      COUNT(DISTINCT e.id) as email_count
    FROM opportunities o
    LEFT JOIN call_opportunities co ON o.id = co.opportunity_id
    LEFT JOIN emails e ON o.id = e.opportunity_id
    ${whereSQL}
    GROUP BY o.id
    ORDER BY o.${sortField} ${sortDirection} NULLS LAST
    LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `,
    params
  );

  return {
    opportunities: result.rows,
    total,
  };
}

export async function getOpportunity(id: string): Promise<Opportunity | null> {
  const result = await query(
    `
    SELECT
      o.*,
      COUNT(DISTINCT co.call_id) as call_count,
      COUNT(DISTINCT e.id) as email_count
    FROM opportunities o
    LEFT JOIN call_opportunities co ON o.id = co.opportunity_id
    LEFT JOIN emails e ON o.id = e.opportunity_id
    WHERE o.id = $1
    GROUP BY o.id
    `,
    [id]
  );

  return result.rows[0] || null;
}

export async function getOpportunityTimeline({
  opportunityId,
  limit = 20,
  offset = 0,
}: {
  opportunityId: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: TimelineItem[]; total: number }> {
  // Get total count
  const countResult = await query(
    `
    SELECT COUNT(*) as total FROM (
      SELECT c.id FROM calls c
      JOIN call_opportunities co ON c.id = co.call_id
      WHERE co.opportunity_id = $1
      UNION ALL
      SELECT e.id FROM emails e
      WHERE e.opportunity_id = $1
    ) timeline
    `,
    [opportunityId]
  );
  const total = parseInt(countResult.rows[0]?.total || "0", 10);

  // Get timeline items
  const result = await query(
    `
    SELECT
      'call' as item_type,
      c.id,
      c.gong_call_id,
      c.title,
      c.scheduled_at as timestamp,
      c.duration,
      NULL as subject,
      NULL as sender_email,
      NULL as gong_email_id
    FROM calls c
    JOIN call_opportunities co ON c.id = co.call_id
    WHERE co.opportunity_id = $1

    UNION ALL

    SELECT
      'email' as item_type,
      e.id,
      NULL as gong_call_id,
      NULL as title,
      e.sent_at as timestamp,
      NULL as duration,
      e.subject,
      e.sender_email,
      e.gong_email_id
    FROM emails e
    WHERE e.opportunity_id = $1

    ORDER BY timestamp DESC
    LIMIT $2 OFFSET $3
    `,
    [opportunityId, limit, offset]
  );

  return {
    items: result.rows,
    total,
  };
}
