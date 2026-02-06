import { getScoreColor } from "@/lib/colors";

export interface ScoreCardProps {
  /** Numeric score value (0-100) */
  score: number;
  /** Main title displayed above the score */
  title: string;
  /** Optional subtitle or description */
  subtitle?: string;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * ScoreCard Component
 *
 * Displays a coaching dimension score with color-coded visual indicator.
 * - Green (>=80): Excellent performance
 * - Yellow (60-79): Good performance
 * - Red (<60): Needs improvement
 */
export function ScoreCard({ score, title, subtitle, className = "" }: ScoreCardProps) {
  const { bg, text, label } = getScoreColor(score);

  return (
    <div
      className={`rounded-lg border p-4 ${className}`}
      style={{ backgroundColor: bg, borderColor: text }}
    >
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
    </div>
  );
}
