/**
 * Primary Action Card - The ONE thing the rep should do
 *
 * Displays the single most important action item prominently with:
 * - Which win it relates to
 * - The specific action to take
 * - Context (why this matters, call moment reference)
 */

"use client";

import { Target, Clock, ArrowRight } from "lucide-react";

interface PrimaryActionProps {
  win: string;
  action: string;
  context: string;
  relatedMoment?: {
    timestamp_seconds: number;
    speaker: string;
    summary: string;
  } | null;
  onTimestampClick?: (timestamp: number) => void;
}

const WIN_COLORS: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  business: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-800",
    icon: "💼",
  },
  technical: {
    bg: "bg-purple-50",
    border: "border-purple-200",
    text: "text-purple-800",
    icon: "🔧",
  },
  security: {
    bg: "bg-green-50",
    border: "border-green-200",
    text: "text-green-800",
    icon: "🔒",
  },
  commercial: {
    bg: "bg-amber-50",
    border: "border-amber-200",
    text: "text-amber-800",
    icon: "💰",
  },
  legal: {
    bg: "bg-slate-50",
    border: "border-slate-200",
    text: "text-slate-800",
    icon: "📜",
  },
};

const WIN_LABELS: Record<string, string> = {
  business: "Business Win",
  technical: "Technical Win",
  security: "Security Win",
  commercial: "Commercial Win",
  legal: "Legal Win",
};

export default function PrimaryActionCard({
  win,
  action,
  context,
  relatedMoment,
  onTimestampClick,
}: PrimaryActionProps) {
  const colors = WIN_COLORS[win] || WIN_COLORS.business;
  const winLabel = WIN_LABELS[win] || "Win";

  const formatTimestamp = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className={`border-2 rounded-xl p-6 ${colors.bg} ${colors.border}`}>
      {/* Header: Priority Indicator */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Target className={`h-5 w-5 ${colors.text}`} />
          <span className={`text-sm font-semibold uppercase tracking-wide ${colors.text}`}>
            #1 Priority
          </span>
        </div>
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${colors.bg} ${colors.text} border ${colors.border}`}
        >
          <span>{colors.icon || WIN_COLORS[win]?.icon}</span>
          <span>{winLabel}</span>
        </div>
      </div>

      {/* Main Action */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 leading-snug">{action}</h3>
      </div>

      {/* Context */}
      {context && (
        <div className="mb-4">
          <p className="text-sm text-gray-700 leading-relaxed">{context}</p>
        </div>
      )}

      {/* Related Moment (if available) */}
      {relatedMoment && (
        <div
          className={`flex items-start gap-3 p-3 rounded-lg bg-white/60 border ${colors.border}`}
        >
          <Clock className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <button
                onClick={() => onTimestampClick?.(relatedMoment.timestamp_seconds)}
                className="font-mono text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
              >
                {formatTimestamp(relatedMoment.timestamp_seconds)}
              </button>
              <span className="text-sm text-gray-500">• {relatedMoment.speaker}</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{relatedMoment.summary}</p>
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
          <ArrowRight className="h-4 w-4" />
          <span>Prepare this before your next call</span>
        </div>
      </div>
    </div>
  );
}
