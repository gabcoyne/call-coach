/**
 * Rubric Utility Functions
 *
 * Helper functions for displaying and working with Five Wins evaluation data.
 */

import type { FiveWinsEvaluation, WinEvaluation } from "@/types/rubric";

/**
 * Format a time range from seconds to MM:SS format
 *
 * @param start - Start time in seconds
 * @param end - End time in seconds
 * @returns Formatted string like "5:20 - 10:15"
 *
 * @example
 * formatTimeRange(320, 615) // "5:20 - 10:15"
 * formatTimeRange(45, 90)   // "0:45 - 1:30"
 */
export function formatTimeRange(start: number, end: number): string {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return `${formatTime(start)} - ${formatTime(end)}`;
}

/**
 * Get status icon for win/criterion status
 *
 * @param status - Status value ("met", "partial", "missed")
 * @returns Icon string (✅ for met, ⚠️ for partial, ❌ for missed)
 *
 * @example
 * getStatusIcon("met")     // "✅"
 * getStatusIcon("partial") // "⚠️"
 * getStatusIcon("missed")  // "❌"
 */
export function getStatusIcon(status: "met" | "partial" | "missed"): string {
  const icons = {
    met: "✅",
    partial: "⚠️",
    missed: "❌",
  };
  return icons[status];
}

/**
 * Get status color class for win/criterion status
 *
 * @param status - Status value ("met", "partial", "missed")
 * @returns Tailwind color class prefix (green, amber, red)
 *
 * @example
 * getStatusColor("met")     // "green"
 * getStatusColor("partial") // "amber"
 * getStatusColor("missed")  // "red"
 */
export function getStatusColor(status: "met" | "partial" | "missed"): string {
  const colors = {
    met: "green",
    partial: "amber",
    missed: "red",
  };
  return colors[status];
}

/**
 * Count wins that have been secured (status = "met")
 *
 * @param evaluation - Five Wins evaluation object
 * @returns Count of wins with status "met"
 *
 * @example
 * countWinsSecured(evaluation) // 3 (if 3 wins have status="met")
 */
export function countWinsSecured(evaluation: FiveWinsEvaluation): number {
  const wins: WinEvaluation[] = [
    evaluation.business_win,
    evaluation.technical_win,
    evaluation.security_win,
    evaluation.commercial_win,
    evaluation.legal_win,
  ];

  return wins.filter((win) => win.status === "met").length;
}

/**
 * Get wins that are at risk (status = "partial" or "missed")
 *
 * @param evaluation - Five Wins evaluation object
 * @returns Array of win names that are at risk
 *
 * @example
 * getAtRiskWins(evaluation)
 * // ["Business Win", "Security Win"] if those two have status "partial" or "missed"
 */
export function getAtRiskWins(evaluation: FiveWinsEvaluation): string[] {
  const winEntries: [string, WinEvaluation][] = [
    ["business_win", evaluation.business_win],
    ["technical_win", evaluation.technical_win],
    ["security_win", evaluation.security_win],
    ["commercial_win", evaluation.commercial_win],
    ["legal_win", evaluation.legal_win],
  ];

  return winEntries
    .filter(([_, win]) => win.status === "partial" || win.status === "missed")
    .map(([name, _]) => formatWinName(name));
}

/**
 * Format win name from snake_case to Title Case
 *
 * @param key - Win name in snake_case (e.g., "business_win")
 * @returns Formatted name in Title Case (e.g., "Business Win")
 *
 * @example
 * formatWinName("business_win")   // "Business Win"
 * formatWinName("technical_win")  // "Technical Win"
 * formatWinName("security_win")   // "Security Win"
 */
export function formatWinName(key: string): string {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
