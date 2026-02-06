/**
 * GET /api/coaching-sessions/feedback-stats
 *
 * Get aggregated feedback statistics for coaching quality issues.
 *
 * Query parameters:
 * - dimension?: string (e.g., 'product_knowledge', 'discovery')
 * - time_period?: string (e.g., 'last_7_days', 'last_30_days', 'all_time')
 * - rep_email?: string
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

interface FeedbackStats {
  total_feedback: number;
  accurate_count: number;
  inaccurate_count: number;
  missing_context_count: number;
  helpful_count: number;
  not_helpful_count: number;
  accuracy_rate: number;
  helpfulness_rate: number;
}

interface DimensionStats extends FeedbackStats {
  dimension: string;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const dimension = searchParams.get("dimension");
    const timePeriod = searchParams.get("time_period") || "all_time";
    const repEmail = searchParams.get("rep_email");

    // Build the date filter
    let dateFilter = "";
    let dateParam: string | null = null;

    switch (timePeriod) {
      case "last_7_days":
        dateFilter = "cf.created_at >= NOW() - INTERVAL '7 days'";
        break;
      case "last_30_days":
        dateFilter = "cf.created_at >= NOW() - INTERVAL '30 days'";
        break;
      case "last_90_days":
        dateFilter = "cf.created_at >= NOW() - INTERVAL '90 days'";
        break;
      case "all_time":
      default:
        dateFilter = "1=1";
    }

    // Build query for overall feedback stats
    let overallQuery = `
      SELECT
        COUNT(*) as total_feedback,
        SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) as accurate_count,
        SUM(CASE WHEN cf.feedback_type = 'inaccurate' THEN 1 ELSE 0 END) as inaccurate_count,
        SUM(CASE WHEN cf.feedback_type = 'missing_context' THEN 1 ELSE 0 END) as missing_context_count,
        SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) as helpful_count,
        SUM(CASE WHEN cf.feedback_type = 'not_helpful' THEN 1 ELSE 0 END) as not_helpful_count,
        ROUND(
          100.0 * SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) /
          NULLIF(COUNT(*), 0),
          2
        ) as accuracy_rate,
        ROUND(
          100.0 * SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) /
          NULLIF(COUNT(*), 0),
          2
        ) as helpfulness_rate
      FROM coaching_feedback cf
      JOIN coaching_sessions cs ON cf.coaching_session_id = cs.id
    `;

    const params: any[] = [];

    // Add rep filter if provided
    if (repEmail) {
      overallQuery += `
        JOIN speakers s ON cf.rep_id = s.id
        WHERE s.email = $1 AND ${dateFilter}
      `;
      params.push(repEmail);
    } else {
      overallQuery += `WHERE ${dateFilter}`;
    }

    const overallResult = await query(overallQuery, params);
    const overallStats = overallResult.rows[0] || {
      total_feedback: 0,
      accurate_count: 0,
      inaccurate_count: 0,
      missing_context_count: 0,
      helpful_count: 0,
      not_helpful_count: 0,
      accuracy_rate: 0,
      helpfulness_rate: 0,
    };

    // Build query for dimension-specific stats
    let dimensionQuery = `
      SELECT
        cs.coaching_dimension as dimension,
        COUNT(*) as total_feedback,
        SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) as accurate_count,
        SUM(CASE WHEN cf.feedback_type = 'inaccurate' THEN 1 ELSE 0 END) as inaccurate_count,
        SUM(CASE WHEN cf.feedback_type = 'missing_context' THEN 1 ELSE 0 END) as missing_context_count,
        SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) as helpful_count,
        SUM(CASE WHEN cf.feedback_type = 'not_helpful' THEN 1 ELSE 0 END) as not_helpful_count,
        ROUND(
          100.0 * SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) /
          NULLIF(COUNT(*), 0),
          2
        ) as accuracy_rate,
        ROUND(
          100.0 * SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) /
          NULLIF(COUNT(*), 0),
          2
        ) as helpfulness_rate
      FROM coaching_feedback cf
      JOIN coaching_sessions cs ON cf.coaching_session_id = cs.id
    `;

    const dimensionParams: any[] = [];

    if (repEmail) {
      dimensionQuery += `
        JOIN speakers s ON cf.rep_id = s.id
        WHERE s.email = $1 AND ${dateFilter}
      `;
      dimensionParams.push(repEmail);
    } else {
      dimensionQuery += `WHERE ${dateFilter}`;
    }

    // Add dimension filter if provided
    if (dimension) {
      dimensionQuery += ` AND cs.coaching_dimension = $${dimensionParams.length + 1}`;
      dimensionParams.push(dimension);
    }

    dimensionQuery += ` GROUP BY cs.coaching_dimension ORDER BY total_feedback DESC`;

    const dimensionResult = await query(dimensionQuery, dimensionParams);
    const dimensionStats = dimensionResult.rows;

    // Calculate quality issues (low accuracy or helpfulness)
    const qualityIssues = [];

    // Issue 1: Low accuracy
    if (overallStats.total_feedback > 0 && overallStats.accuracy_rate < 80) {
      qualityIssues.push({
        type: "low_accuracy",
        severity: "high",
        message: `Coaching accuracy is ${overallStats.accuracy_rate}% (target: 90%+)`,
        metric: overallStats.accuracy_rate,
        affected_count: overallStats.inaccurate_count,
      });
    }

    // Issue 2: Low helpfulness
    if (overallStats.total_feedback > 0 && overallStats.helpfulness_rate < 70) {
      qualityIssues.push({
        type: "low_helpfulness",
        severity: "medium",
        message: `Coaching helpfulness is ${overallStats.helpfulness_rate}% (target: 80%+)`,
        metric: overallStats.helpfulness_rate,
        affected_count: overallStats.not_helpful_count,
      });
    }

    // Issue 3: High missing context
    const missingContextRate =
      overallStats.total_feedback > 0
        ? Math.round((100 * overallStats.missing_context_count) / overallStats.total_feedback)
        : 0;

    if (missingContextRate > 20) {
      qualityIssues.push({
        type: "missing_context",
        severity: "medium",
        message: `${missingContextRate}% of feedback indicates missing context in coaching`,
        metric: missingContextRate,
        affected_count: overallStats.missing_context_count,
      });
    }

    return NextResponse.json({
      overall_stats: overallStats,
      dimension_stats: dimensionStats,
      quality_issues: qualityIssues,
      time_period: timePeriod,
    });
  } catch (error) {
    console.error("Error fetching feedback stats:", error);
    return NextResponse.json({ error: "Failed to fetch feedback statistics" }, { status: 500 });
  }
}
