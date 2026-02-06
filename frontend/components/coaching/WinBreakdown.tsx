/**
 * Win Breakdown Component
 *
 * Displays detailed breakdown of a single win including:
 * - Win name and description
 * - Score with visual progress bar
 * - Status indicator (met/partial/missed)
 * - Exchange evidence list
 * - Explanation for partial/missed wins
 */

"use client";

import type { WinEvaluation, ExchangeEvidence } from "@/types/rubric";
import { getStatusIcon, getStatusColor, formatTimeRange } from "@/lib/rubric-utils";
import ExchangeEvidenceCard from "./ExchangeEvidenceCard";

interface WinBreakdownProps {
  winName: string;
  winDescription: string;
  evaluation: WinEvaluation;
}

// Win descriptions for the Five Wins framework
const WIN_DESCRIPTIONS: Record<string, string> = {
  business_win:
    "Identified business pain/problem, quantified impact of solving it, and connected to strategic initiatives.",
  technical_win:
    "Technical requirements understood, solution fit validated, and technical champion identified.",
  security_win:
    "Security requirements captured, compliance needs understood, and security/IT stakeholder engaged.",
  commercial_win:
    "Budget/pricing discussed, procurement process understood, and economic buyer identified.",
  legal_win:
    "Legal requirements captured, contract/MSA needs understood, and legal stakeholder engaged.",
};

export default function WinBreakdown({ winName, winDescription, evaluation }: WinBreakdownProps) {
  const statusColor = getStatusColor(evaluation.status);
  const statusIcon = getStatusIcon(evaluation.status);
  const percentage = Math.round((evaluation.score / evaluation.max_score) * 100);

  // Color classes for different status states
  const colorClasses = {
    green: {
      bg: "bg-green-50",
      border: "border-green-200",
      text: "text-green-900",
      progress: "bg-green-500",
      badge: "bg-green-100 text-green-800",
    },
    amber: {
      bg: "bg-amber-50",
      border: "border-amber-200",
      text: "text-amber-900",
      progress: "bg-amber-500",
      badge: "bg-amber-100 text-amber-800",
    },
    red: {
      bg: "bg-red-50",
      border: "border-red-200",
      text: "text-red-900",
      progress: "bg-red-500",
      badge: "bg-red-100 text-red-800",
    },
  };

  const colors = colorClasses[statusColor as keyof typeof colorClasses];

  return (
    <div className={`border rounded-lg ${colors.bg} ${colors.border}`}>
      {/* Header: Win Name and Status */}
      <div className="p-6 border-b">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{statusIcon}</span>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{winName}</h3>
              <p
                className={`text-sm font-medium capitalize ${colors.badge} px-2 py-1 rounded mt-1 inline-block`}
              >
                {evaluation.status}
              </p>
            </div>
          </div>
        </div>

        {/* Win Description */}
        <p className="text-sm text-gray-600 mb-4">{winDescription}</p>

        {/* Score with Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Score</span>
            <span className="text-sm font-bold text-gray-900">
              {evaluation.score}/{evaluation.max_score} points ({percentage}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full ${colors.progress} transition-all duration-300`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Evidence Section */}
      {evaluation.evidence.length > 0 && (
        <div className="p-6">
          <h4 className={`text-sm font-semibold ${colors.text} mb-4`}>
            Evidence ({evaluation.evidence.length})
          </h4>
          <div className="space-y-3">
            {evaluation.evidence.map((evidence: ExchangeEvidence, idx: number) => (
              <ExchangeEvidenceCard key={idx} evidence={evidence} />
            ))}
          </div>
        </div>
      )}

      {/* Missed/Partial Explanation */}
      {(evaluation.status === "partial" || evaluation.status === "missed") && (
        <div className={`p-6 border-t ${colors.bg}`}>
          <h4 className={`text-sm font-semibold ${colors.text} mb-2`}>
            {evaluation.status === "missed" ? "Why This Win Was Missed" : "Areas to Improve"}
          </h4>
          <p className="text-sm text-gray-700">
            {evaluation.status === "missed"
              ? `This win requires ${winName.toLowerCase()} to be clearly addressed during the call. No evidence was found of ${winDescription.toLowerCase()}`
              : `While some progress was made on ${winName.toLowerCase()}, there are gaps in ${winDescription.toLowerCase()}. Review the evidence above and focus on strengthening these areas.`}
          </p>
        </div>
      )}
    </div>
  );
}

// Export WIN_DESCRIPTIONS for use in parent components
export { WIN_DESCRIPTIONS };
