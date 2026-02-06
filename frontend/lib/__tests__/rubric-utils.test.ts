/**
 * Unit tests for rubric utility functions
 */

import {
  formatTimeRange,
  getStatusIcon,
  getStatusColor,
  countWinsSecured,
  getAtRiskWins,
  formatWinName,
} from "../rubric-utils";
import type { FiveWinsEvaluation } from "@/types/rubric";

describe("formatTimeRange", () => {
  it("should format time range correctly", () => {
    expect(formatTimeRange(320, 615)).toBe("5:20 - 10:15");
  });

  it("should handle times under 1 minute", () => {
    expect(formatTimeRange(45, 90)).toBe("0:45 - 1:30");
  });

  it("should pad seconds with leading zero", () => {
    expect(formatTimeRange(65, 125)).toBe("1:05 - 2:05");
  });

  it("should handle zero times", () => {
    expect(formatTimeRange(0, 30)).toBe("0:00 - 0:30");
  });

  it("should handle large time values", () => {
    expect(formatTimeRange(3600, 3665)).toBe("60:00 - 61:05");
  });
});

describe("getStatusIcon", () => {
  it("should return checkmark for met status", () => {
    expect(getStatusIcon("met")).toBe("✅");
  });

  it("should return warning for partial status", () => {
    expect(getStatusIcon("partial")).toBe("⚠️");
  });

  it("should return X for missed status", () => {
    expect(getStatusIcon("missed")).toBe("❌");
  });
});

describe("getStatusColor", () => {
  it("should return green for met status", () => {
    expect(getStatusColor("met")).toBe("green");
  });

  it("should return amber for partial status", () => {
    expect(getStatusColor("partial")).toBe("amber");
  });

  it("should return red for missed status", () => {
    expect(getStatusColor("missed")).toBe("red");
  });
});

describe("countWinsSecured", () => {
  it("should count all wins with met status", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 30, max_score: 35, status: "met", evidence: [] },
      technical_win: { score: 20, max_score: 25, status: "met", evidence: [] },
      security_win: { score: 12, max_score: 15, status: "met", evidence: [] },
      commercial_win: { score: 8, max_score: 15, status: "partial", evidence: [] },
      legal_win: { score: 5, max_score: 10, status: "missed", evidence: [] },
      wins_secured: 3,
      overall_score: 75,
    };

    expect(countWinsSecured(evaluation)).toBe(3);
  });

  it("should return 0 when no wins are met", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 10, max_score: 35, status: "missed", evidence: [] },
      technical_win: { score: 8, max_score: 25, status: "partial", evidence: [] },
      security_win: { score: 5, max_score: 15, status: "missed", evidence: [] },
      commercial_win: { score: 6, max_score: 15, status: "partial", evidence: [] },
      legal_win: { score: 3, max_score: 10, status: "missed", evidence: [] },
      wins_secured: 0,
      overall_score: 32,
    };

    expect(countWinsSecured(evaluation)).toBe(0);
  });

  it("should return 5 when all wins are met", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 35, max_score: 35, status: "met", evidence: [] },
      technical_win: { score: 25, max_score: 25, status: "met", evidence: [] },
      security_win: { score: 15, max_score: 15, status: "met", evidence: [] },
      commercial_win: { score: 15, max_score: 15, status: "met", evidence: [] },
      legal_win: { score: 10, max_score: 10, status: "met", evidence: [] },
      wins_secured: 5,
      overall_score: 100,
    };

    expect(countWinsSecured(evaluation)).toBe(5);
  });
});

describe("getAtRiskWins", () => {
  it("should return wins with partial or missed status", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 30, max_score: 35, status: "met", evidence: [] },
      technical_win: { score: 20, max_score: 25, status: "met", evidence: [] },
      security_win: { score: 8, max_score: 15, status: "partial", evidence: [] },
      commercial_win: { score: 5, max_score: 15, status: "missed", evidence: [] },
      legal_win: { score: 10, max_score: 10, status: "met", evidence: [] },
      wins_secured: 3,
      overall_score: 73,
    };

    const atRiskWins = getAtRiskWins(evaluation);
    expect(atRiskWins).toHaveLength(2);
    expect(atRiskWins).toContain("Security Win");
    expect(atRiskWins).toContain("Commercial Win");
  });

  it("should return empty array when all wins are met", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 35, max_score: 35, status: "met", evidence: [] },
      technical_win: { score: 25, max_score: 25, status: "met", evidence: [] },
      security_win: { score: 15, max_score: 15, status: "met", evidence: [] },
      commercial_win: { score: 15, max_score: 15, status: "met", evidence: [] },
      legal_win: { score: 10, max_score: 10, status: "met", evidence: [] },
      wins_secured: 5,
      overall_score: 100,
    };

    expect(getAtRiskWins(evaluation)).toEqual([]);
  });

  it("should return all wins when all are at risk", () => {
    const evaluation: FiveWinsEvaluation = {
      business_win: { score: 10, max_score: 35, status: "missed", evidence: [] },
      technical_win: { score: 8, max_score: 25, status: "partial", evidence: [] },
      security_win: { score: 5, max_score: 15, status: "missed", evidence: [] },
      commercial_win: { score: 6, max_score: 15, status: "partial", evidence: [] },
      legal_win: { score: 3, max_score: 10, status: "missed", evidence: [] },
      wins_secured: 0,
      overall_score: 32,
    };

    const atRiskWins = getAtRiskWins(evaluation);
    expect(atRiskWins).toHaveLength(5);
    expect(atRiskWins).toContain("Business Win");
    expect(atRiskWins).toContain("Technical Win");
    expect(atRiskWins).toContain("Security Win");
    expect(atRiskWins).toContain("Commercial Win");
    expect(atRiskWins).toContain("Legal Win");
  });
});

describe("formatWinName", () => {
  it("should format business_win correctly", () => {
    expect(formatWinName("business_win")).toBe("Business Win");
  });

  it("should format technical_win correctly", () => {
    expect(formatWinName("technical_win")).toBe("Technical Win");
  });

  it("should format security_win correctly", () => {
    expect(formatWinName("security_win")).toBe("Security Win");
  });

  it("should format commercial_win correctly", () => {
    expect(formatWinName("commercial_win")).toBe("Commercial Win");
  });

  it("should format legal_win correctly", () => {
    expect(formatWinName("legal_win")).toBe("Legal Win");
  });

  it("should handle single word without underscore", () => {
    expect(formatWinName("win")).toBe("Win");
  });

  it("should handle multiple underscores", () => {
    expect(formatWinName("this_is_a_test")).toBe("This Is A Test");
  });
});
