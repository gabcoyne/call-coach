/**
 * Narrative Summary Component
 *
 * Displays the 2-3 sentence coaching narrative prominently at the top
 * of the call analysis view. This replaces the overwhelming list of
 * strengths/weaknesses with a concise, digestible summary.
 */

"use client";

import { MessageSquare, CheckCircle, AlertTriangle } from "lucide-react";

interface WinsAddressed {
  [winName: string]: string;
}

interface NarrativeSummaryProps {
  narrative: string;
  winsAddressed?: WinsAddressed;
  winsMissed?: WinsAddressed;
}

const WIN_ICONS: Record<string, string> = {
  business: "💼",
  technical: "🔧",
  security: "🔒",
  commercial: "💰",
  legal: "📜",
};

const WIN_LABELS: Record<string, string> = {
  business: "Business Win",
  technical: "Technical Win",
  security: "Security Win",
  commercial: "Commercial Win",
  legal: "Legal Win",
};

export default function NarrativeSummary({
  narrative,
  winsAddressed,
  winsMissed,
}: NarrativeSummaryProps) {
  const hasAddressed = winsAddressed && Object.keys(winsAddressed).length > 0;
  const hasMissed = winsMissed && Object.keys(winsMissed).length > 0;

  return (
    <div className="border rounded-xl p-6 bg-gradient-to-br from-white to-slate-50 shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <MessageSquare className="h-5 w-5 text-indigo-600" />
        <h2 className="text-lg font-semibold text-gray-900">Coaching Summary</h2>
      </div>

      {/* Narrative */}
      <div className="mb-6">
        <p className="text-base text-gray-800 leading-relaxed">{narrative}</p>
      </div>

      {/* Wins Summary Grid */}
      {(hasAddressed || hasMissed) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Wins Addressed */}
          {hasAddressed && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm font-semibold text-green-800">Wins Progressed</span>
              </div>
              <div className="space-y-2">
                {Object.entries(winsAddressed).map(([win, detail]) => (
                  <div key={win} className="flex items-start gap-2">
                    <span className="text-base flex-shrink-0">{WIN_ICONS[win] || "✓"}</span>
                    <div>
                      <span className="text-sm font-medium text-gray-800">
                        {WIN_LABELS[win] || win}:
                      </span>
                      <span className="text-sm text-gray-600 ml-1">{detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Wins Missed */}
          {hasMissed && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-4 w-4 text-amber-600" />
                <span className="text-sm font-semibold text-amber-800">Needs Attention</span>
              </div>
              <div className="space-y-2">
                {Object.entries(winsMissed).map(([win, detail]) => (
                  <div key={win} className="flex items-start gap-2">
                    <span className="text-base flex-shrink-0">{WIN_ICONS[win] || "⚠"}</span>
                    <div>
                      <span className="text-sm font-medium text-gray-800">
                        {WIN_LABELS[win] || win}:
                      </span>
                      <span className="text-sm text-gray-600 ml-1">{detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
