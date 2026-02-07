"use client";

import { useState } from "react";
import { getScoreColor } from "@/lib/colors";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { FiveWinsEvaluation } from "@/types/rubric";
import FiveWinsScoreCard from "./FiveWinsScoreCard";

export interface ScoreCardProps {
  /** Numeric score value (0-100) */
  score: number;
  /** Main title displayed above the score */
  title: string;
  /** Optional subtitle or description */
  subtitle?: string;
  /** Optional className for additional styling */
  className?: string;
  /** Optional Five Wins evaluation data for expandable breakdown */
  fiveWinsEvaluation?: FiveWinsEvaluation;
  /** Optional callback for "Show All Frameworks" button */
  onShowAllFrameworks?: () => void;
}

/**
 * ScoreCard Component
 *
 * Displays a coaching dimension score with color-coded visual indicator.
 * - Green (>=80): Excellent performance
 * - Yellow (60-79): Good performance
 * - Red (<60): Needs improvement
 *
 * When fiveWinsEvaluation is provided, displays an expandable button to show
 * detailed Five Wins breakdown. Maintains backward compatibility when used without
 * the expand/collapse feature.
 */
export function ScoreCard({
  score,
  title,
  subtitle,
  className = "",
  fiveWinsEvaluation,
  onShowAllFrameworks,
}: ScoreCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { bg, text, label } = getScoreColor(score);
  const hasExpandableContent = !!fiveWinsEvaluation;

  return (
    <div className={`rounded-lg border overflow-hidden ${className}`}>
      {/* Main Score Card */}
      <div className="p-4" style={{ backgroundColor: bg, borderColor: text }}>
        {/* Title */}
        <h3 className="text-sm font-medium mb-2" style={{ color: text }}>
          {title}
        </h3>

        {/* Score Display */}
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold" style={{ color: text }}>
            {score}
          </span>
          <span className="text-lg font-medium" style={{ color: text }}>
            / 100
          </span>
        </div>

        {/* Performance Label */}
        <p className="text-xs font-semibold mt-1" style={{ color: text }}>
          {label}
        </p>

        {/* Optional Subtitle */}
        {subtitle && (
          <p className="text-sm mt-2" style={{ color: text }}>
            {subtitle}
          </p>
        )}

        {/* Expandable Button */}
        {hasExpandableContent && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-white/90 hover:bg-white rounded-lg transition-colors text-sm font-medium"
            style={{ color: text }}
          >
            {isExpanded ? (
              <>
                <ChevronDown className="h-4 w-4" />
                Hide Score Breakdown
              </>
            ) : (
              <>
                <ChevronRight className="h-4 w-4" />
                Show How This Score Was Calculated
              </>
            )}
          </button>
        )}
      </div>

      {/* Expanded Content - Five Wins Breakdown */}
      {hasExpandableContent && isExpanded && (
        <div
          className="border-t animate-fadeIn"
          style={{
            animation: "fadeIn 0.3s ease-in-out",
          }}
        >
          <FiveWinsScoreCard
            evaluation={fiveWinsEvaluation}
            onShowAllFrameworks={onShowAllFrameworks}
          />
        </div>
      )}

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
