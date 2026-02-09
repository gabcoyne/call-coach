/**
 * Coaching Color Palette
 *
 * Consistent color constants for coaching-related UI components.
 * Used across ScoreCard, TrendChart, InsightCard, and ActionItem components.
 */

// Score-based colors (based on performance thresholds)
export const SCORE_COLORS = {
  // High score: 80-100 (Excellent performance)
  HIGH: '#10b981', // green-500
  HIGH_BG: '#d1fae5', // green-100
  HIGH_TEXT: '#065f46', // green-800

  // Medium score: 60-79 (Good performance)
  MEDIUM: '#f59e0b', // amber-500
  MEDIUM_BG: '#fef3c7', // amber-100
  MEDIUM_TEXT: '#78350f', // amber-900

  // Low score: 0-59 (Needs improvement)
  LOW: '#ef4444', // red-500
  LOW_BG: '#fee2e2', // red-100
  LOW_TEXT: '#991b1b', // red-800
} as const;

// Priority colors for ActionItem badges
export const PRIORITY_COLORS = {
  HIGH: {
    bg: '#ef4444', // red-500
    text: '#ffffff',
    border: '#dc2626', // red-600
  },
  MEDIUM: {
    bg: '#f59e0b', // amber-500
    text: '#ffffff',
    border: '#d97706', // amber-600
  },
  LOW: {
    bg: '#3b82f6', // blue-500
    text: '#ffffff',
    border: '#2563eb', // blue-600
  },
} as const;

// Brand colors (Prefect branding)
export const BRAND_COLORS = {
  PRIMARY: '#2D5FE3', // Prefect blue
  SECONDARY: '#6B7280', // gray-500
  ACCENT: '#8b5cf6', // purple-500
} as const;

// Chart colors for trend visualization (multiple dimension series)
export const CHART_COLORS = [
  '#2D5FE3', // Prefect blue (primary)
  '#10b981', // green-500
  '#f59e0b', // amber-500
  '#8b5cf6', // purple-500
  '#ef4444', // red-500
  '#06b6d4', // cyan-500
] as const;

/**
 * Get score color based on numeric value
 * @param score Numeric score (0-100)
 * @returns Color object with bg, text, and base colors
 */
export function getScoreColor(score: number) {
  if (score >= 80) {
    return {
      base: SCORE_COLORS.HIGH,
      bg: SCORE_COLORS.HIGH_BG,
      text: SCORE_COLORS.HIGH_TEXT,
      label: 'Excellent',
    };
  }
  if (score >= 60) {
    return {
      base: SCORE_COLORS.MEDIUM,
      bg: SCORE_COLORS.MEDIUM_BG,
      text: SCORE_COLORS.MEDIUM_TEXT,
      label: 'Good',
    };
  }
  return {
    base: SCORE_COLORS.LOW,
    bg: SCORE_COLORS.LOW_BG,
    text: SCORE_COLORS.LOW_TEXT,
    label: 'Needs Improvement',
  };
}

/**
 * Get priority color based on priority level
 * @param priority Priority level (high, medium, low)
 * @returns Color object with bg, text, and border colors
 */
export function getPriorityColor(priority: 'high' | 'medium' | 'low') {
  return PRIORITY_COLORS[priority.toUpperCase() as keyof typeof PRIORITY_COLORS];
}
