/**
 * Exchange Evidence Card Component
 *
 * Displays a single piece of evidence from a win evaluation:
 * - Timestamp range badge (e.g., "5:20 - 10:15")
 * - Exchange summary (what happened in the conversation)
 * - Impact statement (why this matters for the win)
 * - Optional click handler for future Gong integration
 */

"use client";

import type { ExchangeEvidence } from "@/types/rubric";
import { formatTimeRange } from "@/lib/rubric-utils";

interface ExchangeEvidenceCardProps {
  evidence: ExchangeEvidence;
  onTimestampClick?: (timestamp: number) => void;
}

export default function ExchangeEvidenceCard({
  evidence,
  onTimestampClick,
}: ExchangeEvidenceCardProps) {
  const timeRange = formatTimeRange(evidence.timestamp_start, evidence.timestamp_end);
  const isClickable = !!onTimestampClick;

  const handleClick = () => {
    if (onTimestampClick) {
      onTimestampClick(evidence.timestamp_start);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
      {/* Timestamp Range Badge */}
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={handleClick}
          disabled={!isClickable}
          className={`
            text-xs font-mono px-3 py-1 rounded-full
            bg-blue-50 text-blue-700 border border-blue-200
            ${isClickable ? "hover:bg-blue-100 cursor-pointer" : "cursor-default"}
            transition-colors
          `}
          aria-label={`Jump to timestamp ${timeRange}`}
        >
          {timeRange}
        </button>
      </div>

      {/* Exchange Summary */}
      <div className="mb-3">
        <p className="text-sm text-gray-700 leading-relaxed">{evidence.exchange_summary}</p>
      </div>

      {/* Impact Statement */}
      <div className="border-t border-gray-100 pt-3">
        <div className="flex items-start gap-2">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide flex-shrink-0">
            Impact:
          </span>
          <p className="text-sm text-gray-900 font-medium">{evidence.impact}</p>
        </div>
      </div>
    </div>
  );
}
