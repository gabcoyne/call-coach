/**
 * Supplementary Frameworks Panel Component
 *
 * Displays additional coaching frameworks (SPICED, Challenger, Sandler) below
 * the primary Five Wins scorecard. Collapsed by default to keep focus on Five Wins.
 *
 * Features:
 * - Collapsed-by-default state with expand button
 * - Shows discovery_rubric (SPICED), engagement_rubric (Challenger),
 *   objection_handling_rubric (Sandler), and product_knowledge_rubric
 * - Uses same criterion breakdown pattern as Five Wins
 * - Reuses ExchangeEvidenceCard for evidence display
 * - Secondary/supplementary visual styling to differentiate from primary scorecard
 */

"use client";

import { useState } from "react";
import type { SupplementaryFrameworks, CriterionEvaluation } from "@/types/rubric";
import { getStatusIcon, getStatusColor, formatWinName } from "@/lib/rubric-utils";
import { ChevronDown, ChevronRight } from "lucide-react";
import ExchangeEvidenceCard from "./ExchangeEvidenceCard";

interface SupplementaryFrameworksPanelProps {
  frameworks: SupplementaryFrameworks;
}

// Framework display configurations
const FRAMEWORK_CONFIG = {
  discovery_rubric: {
    title: "Discovery Framework (SPICED)",
    description: "Situation, Pain, Impact, Critical Event, Decision",
    color: "purple",
  },
  engagement_rubric: {
    title: "Engagement Framework (Challenger)",
    description: "Teaching, Tailoring, Taking Control",
    color: "indigo",
  },
  objection_handling_rubric: {
    title: "Objection Handling Framework (Sandler)",
    description: "Pain-Budget-Decision qualification",
    color: "blue",
  },
  product_knowledge_rubric: {
    title: "Product Knowledge Framework",
    description: "Feature knowledge, use case alignment, competitive positioning",
    color: "teal",
  },
} as const;

type FrameworkKey = keyof typeof FRAMEWORK_CONFIG;

export default function SupplementaryFrameworksPanel({
  frameworks,
}: SupplementaryFrameworksPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedFrameworks, setExpandedFrameworks] = useState<Set<string>>(new Set());
  const [expandedCriteria, setExpandedCriteria] = useState<Set<string>>(new Set());

  // Get available frameworks
  const availableFrameworks = Object.keys(FRAMEWORK_CONFIG).filter(
    (key) => frameworks[key as FrameworkKey]
  ) as FrameworkKey[];

  if (availableFrameworks.length === 0) {
    return null;
  }

  const toggleFramework = (frameworkKey: string) => {
    setExpandedFrameworks((prev) => {
      const next = new Set(prev);
      if (next.has(frameworkKey)) {
        next.delete(frameworkKey);
      } else {
        next.add(frameworkKey);
      }
      return next;
    });
  };

  const toggleCriterion = (criterionKey: string) => {
    setExpandedCriteria((prev) => {
      const next = new Set(prev);
      if (next.has(criterionKey)) {
        next.delete(criterionKey);
      } else {
        next.add(criterionKey);
      }
      return next;
    });
  };

  return (
    <div className="border rounded-lg bg-gray-50 shadow-sm">
      {/* Collapsed Header Button */}
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full p-6 flex items-center justify-between hover:bg-gray-100 transition-colors rounded-lg"
        >
          <div className="flex items-center gap-3">
            <ChevronRight className="h-5 w-5 text-gray-400" />
            <div className="text-left">
              <h3 className="text-lg font-semibold text-gray-900">
                Additional Coaching Frameworks
              </h3>
              <p className="text-sm text-gray-600">
                SPICED · Challenger · Sandler · Product Knowledge
              </p>
            </div>
          </div>
          <span className="text-sm text-gray-500 font-medium">
            {availableFrameworks.length} framework{availableFrameworks.length !== 1 ? "s" : ""}{" "}
            available
          </span>
        </button>
      )}

      {/* Expanded Content */}
      {isExpanded && (
        <div>
          {/* Expanded Header */}
          <div className="border-b bg-gradient-to-r from-gray-50 to-gray-100 p-6">
            <button
              onClick={() => setIsExpanded(false)}
              className="w-full flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <ChevronDown className="h-5 w-5 text-gray-400" />
              <div className="text-left">
                <h3 className="text-lg font-semibold text-gray-900">
                  Additional Coaching Frameworks
                </h3>
                <p className="text-sm text-gray-600">
                  Deeper insights into specific coaching dimensions
                </p>
              </div>
            </button>
          </div>

          {/* Framework List */}
          <div className="divide-y divide-gray-200">
            {availableFrameworks.map((frameworkKey) => {
              const framework = frameworks[frameworkKey];
              const config = FRAMEWORK_CONFIG[frameworkKey];
              const isFrameworkExpanded = expandedFrameworks.has(frameworkKey);

              if (!framework) return null;

              const percentage = Math.round((framework.overall_score / framework.max_score) * 100);

              return (
                <div key={frameworkKey} className="bg-white">
                  {/* Framework Header */}
                  <button
                    onClick={() => toggleFramework(frameworkKey)}
                    className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {isFrameworkExpanded ? (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      )}
                      <div className="text-left">
                        <h4 className="font-semibold text-gray-900">{config.title}</h4>
                        <p className="text-xs text-gray-500">{config.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {framework.overall_score}/{framework.max_score}
                        </div>
                        <div className="text-xs text-gray-500">{percentage}%</div>
                      </div>
                    </div>
                  </button>

                  {/* Expanded Framework Content - Criteria List */}
                  {isFrameworkExpanded && (
                    <div className="border-t bg-gray-50 p-4">
                      <div className="space-y-3">
                        {framework.criteria.map((criterion: CriterionEvaluation) => {
                          const criterionKey = `${frameworkKey}-${criterion.criterion}`;
                          const isCriterionExpanded = expandedCriteria.has(criterionKey);
                          const statusColor = getStatusColor(criterion.status);
                          const statusIcon = getStatusIcon(criterion.status);
                          const criterionPercentage = Math.round(
                            (criterion.score / criterion.max_score) * 100
                          );

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
                            <div key={criterionKey} className="bg-white border rounded-lg">
                              {/* Criterion Header */}
                              <button
                                onClick={() => toggleCriterion(criterionKey)}
                                className="w-full p-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                              >
                                <div className="flex items-center gap-2">
                                  {isCriterionExpanded ? (
                                    <ChevronDown className="h-4 w-4 text-gray-400" />
                                  ) : (
                                    <ChevronRight className="h-4 w-4 text-gray-400" />
                                  )}
                                  <span className="text-lg">{statusIcon}</span>
                                  <div className="text-left">
                                    <h5 className="text-sm font-medium text-gray-900">
                                      {formatWinName(criterion.criterion)}
                                    </h5>
                                    <p className="text-xs text-gray-500 capitalize">
                                      {criterion.status}
                                    </p>
                                  </div>
                                </div>
                                <div
                                  className={`px-2 py-1 rounded text-xs font-medium ${colors.badge}`}
                                >
                                  {criterion.score}/{criterion.max_score} ({criterionPercentage}%)
                                </div>
                              </button>

                              {/* Expanded Criterion Content - Evidence */}
                              {isCriterionExpanded && (
                                <div className={`border-t p-3 ${colors.bg} ${colors.border}`}>
                                  {criterion.evidence.length > 0 ? (
                                    <div className="space-y-3">
                                      <h6 className={`text-xs font-semibold ${colors.text}`}>
                                        Evidence ({criterion.evidence.length})
                                      </h6>
                                      {criterion.evidence.map((evidence, idx) => (
                                        <ExchangeEvidenceCard key={idx} evidence={evidence} />
                                      ))}
                                    </div>
                                  ) : (
                                    <p className="text-sm text-gray-600 italic">
                                      No evidence recorded for this criterion.
                                    </p>
                                  )}

                                  {/* Missed Explanation */}
                                  {criterion.missed_explanation && (
                                    <div className="mt-3 pt-3 border-t border-gray-200">
                                      <p className="text-sm text-gray-700">
                                        {criterion.missed_explanation}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
