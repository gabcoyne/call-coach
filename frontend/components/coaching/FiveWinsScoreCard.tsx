/**
 * Five Wins Score Card Component
 *
 * Displays the primary Five Wins evaluation with:
 * - Wins secured count header
 * - At-risk wins alert
 * - Individual win breakdown with expand/collapse
 * - "Show All Frameworks" button for supplementary frameworks
 */

"use client";

import { useState } from "react";
import type { FiveWinsEvaluation } from "@/types/rubric";
import {
  countWinsSecured,
  getAtRiskWins,
  getStatusIcon,
  getStatusColor,
  formatWinName,
} from "@/lib/rubric-utils";
import { ChevronDown, ChevronRight, AlertTriangle } from "lucide-react";

interface FiveWinsScoreCardProps {
  evaluation: FiveWinsEvaluation;
  onShowAllFrameworks?: () => void;
}

export default function FiveWinsScoreCard({
  evaluation,
  onShowAllFrameworks,
}: FiveWinsScoreCardProps) {
  const [expandedWins, setExpandedWins] = useState<Set<string>>(new Set());

  const winsSecured = countWinsSecured(evaluation);
  const atRiskWins = getAtRiskWins(evaluation);

  const toggleWin = (winKey: string) => {
    setExpandedWins((prev) => {
      const next = new Set(prev);
      if (next.has(winKey)) {
        next.delete(winKey);
      } else {
        next.add(winKey);
      }
      return next;
    });
  };

  const wins = [
    { key: "business_win", data: evaluation.business_win },
    { key: "technical_win", data: evaluation.technical_win },
    { key: "security_win", data: evaluation.security_win },
    { key: "commercial_win", data: evaluation.commercial_win },
    { key: "legal_win", data: evaluation.legal_win },
  ];

  return (
    <div className="border rounded-lg bg-white shadow-sm">
      {/* Header: Wins Secured Count */}
      <div className="border-b bg-gradient-to-r from-blue-50 to-indigo-50 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{winsSecured} of 5 Wins Secured</h2>
            <p className="text-sm text-gray-600 mt-1">
              Overall Score: {evaluation.overall_score}/100
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-indigo-600">{winsSecured}/5</div>
            <p className="text-xs text-gray-500 mt-1">Wins Met</p>
          </div>
        </div>
      </div>

      {/* At-Risk Wins Alert */}
      {atRiskWins.length > 0 && (
        <div className="border-b bg-amber-50 border-amber-200 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-amber-900">
                {atRiskWins.length} {atRiskWins.length === 1 ? "Win" : "Wins"} At Risk
              </h3>
              <p className="text-sm text-amber-800 mt-1">
                Focus on: <span className="font-medium">{atRiskWins.join(", ")}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Individual Win List */}
      <div className="divide-y">
        {wins.map(({ key, data }) => {
          const isExpanded = expandedWins.has(key);
          const statusColor = getStatusColor(data.status);
          const statusIcon = getStatusIcon(data.status);

          // Color classes for different status states
          const colorClasses = {
            green: {
              bg: "bg-green-50",
              border: "border-green-200",
              text: "text-green-900",
              badge: "bg-green-100 text-green-800",
            },
            amber: {
              bg: "bg-amber-50",
              border: "border-amber-200",
              text: "text-amber-900",
              badge: "bg-amber-100 text-amber-800",
            },
            red: {
              bg: "bg-red-50",
              border: "border-red-200",
              text: "text-red-900",
              badge: "bg-red-100 text-red-800",
            },
          };

          const colors = colorClasses[statusColor as keyof typeof colorClasses];

          return (
            <div key={key} className="p-4">
              {/* Win Header - Clickable to expand/collapse */}
              <button
                onClick={() => toggleWin(key)}
                className="w-full flex items-center justify-between hover:bg-gray-50 p-2 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                  )}
                  <span className="text-2xl">{statusIcon}</span>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">{formatWinName(key)}</h3>
                    <p className="text-sm text-gray-500 capitalize">{data.status}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
                    {data.score}/{data.max_score} points
                  </div>
                </div>
              </button>

              {/* Expanded Content - Evidence */}
              {isExpanded && (
                <div className={`mt-4 border rounded-lg p-4 ${colors.bg} ${colors.border}`}>
                  {data.evidence.length > 0 ? (
                    <div className="space-y-3">
                      <h4 className={`text-sm font-semibold ${colors.text}`}>
                        Evidence ({data.evidence.length})
                      </h4>
                      {data.evidence.map((evidence, idx) => (
                        <div key={idx} className="bg-white border rounded-lg p-3">
                          <div className="text-xs font-mono text-gray-500 mb-2">
                            {Math.floor(evidence.timestamp_start / 60)}:
                            {(evidence.timestamp_start % 60).toString().padStart(2, "0")} -{" "}
                            {Math.floor(evidence.timestamp_end / 60)}:
                            {(evidence.timestamp_end % 60).toString().padStart(2, "0")}
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{evidence.exchange_summary}</p>
                          <div className={`text-sm ${colors.text} font-medium`}>
                            Impact: {evidence.impact}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-600 italic">
                      No evidence recorded for this win.
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Show All Frameworks Button */}
      {onShowAllFrameworks && (
        <div className="border-t bg-gray-50 p-4">
          <button
            onClick={onShowAllFrameworks}
            className="w-full py-3 px-4 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 flex items-center justify-center gap-2"
          >
            <ChevronDown className="h-4 w-4" />
            Show All Coaching Frameworks (SPICED / Challenger / Sandler)
          </button>
        </div>
      )}
    </div>
  );
}
