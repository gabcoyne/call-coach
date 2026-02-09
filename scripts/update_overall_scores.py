#!/usr/bin/env python3
"""
Update overall_score for all calls from their coaching_sessions.

This recalculates the average score across all dimensions for each call.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.connection import get_db_connection

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        # Update overall_score for all calls with coaching sessions
        cursor.execute(
            """
            UPDATE calls SET overall_score = (
                SELECT ROUND(AVG(cs.score))::int
                FROM coaching_sessions cs
                WHERE cs.call_id = calls.id
                AND cs.score IS NOT NULL
            )
            WHERE EXISTS (
                SELECT 1 FROM coaching_sessions cs2
                WHERE cs2.call_id = calls.id
                AND cs2.score IS NOT NULL
            )
        """
        )

        updated = cursor.rowcount
        conn.commit()

        print(f"✓ Updated overall_score for {updated} calls")

        # Show some examples
        cursor.execute(
            """
            SELECT c.title, c.overall_score, COUNT(cs.id) as session_count
            FROM calls c
            JOIN coaching_sessions cs ON cs.call_id = c.id
            WHERE c.overall_score IS NOT NULL
            GROUP BY c.id
            ORDER BY c.overall_score DESC
            LIMIT 5
        """
        )

        print("\nTop scored calls:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}/100 ({row[2]} dimensions)")
