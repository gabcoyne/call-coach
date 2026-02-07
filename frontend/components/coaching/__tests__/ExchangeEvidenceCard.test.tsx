/**
 * Tests for ExchangeEvidenceCard Component
 */

import { render, screen, fireEvent } from "@testing-library/react";
import ExchangeEvidenceCard from "../ExchangeEvidenceCard";
import type { ExchangeEvidence } from "@/types/rubric";

describe("ExchangeEvidenceCard", () => {
  const mockEvidence: ExchangeEvidence = {
    timestamp_start: 320, // 5:20
    timestamp_end: 615, // 10:15
    exchange_summary:
      "Rep asked about current data infrastructure challenges and quantified the cost of manual data processing.",
    impact: "Identified $50K/year savings opportunity, aligned with Q1 strategic initiative.",
  };

  it("renders timestamp range badge correctly", () => {
    render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    expect(screen.getByText("5:20 - 10:15")).toBeInTheDocument();
  });

  it("renders exchange summary text", () => {
    render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    expect(
      screen.getByText(/Rep asked about current data infrastructure challenges/)
    ).toBeInTheDocument();
  });

  it("renders impact statement", () => {
    render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    expect(screen.getByText("Impact:")).toBeInTheDocument();
    expect(screen.getByText(/Identified \$50K\/year savings opportunity/)).toBeInTheDocument();
  });

  it("timestamp badge is clickable when onTimestampClick provided", () => {
    const handleClick = jest.fn();
    render(<ExchangeEvidenceCard evidence={mockEvidence} onTimestampClick={handleClick} />);

    const timestampButton = screen.getByRole("button", {
      name: /Jump to timestamp 5:20 - 10:15/,
    });

    fireEvent.click(timestampButton);

    expect(handleClick).toHaveBeenCalledWith(320);
  });

  it("timestamp badge is not clickable when onTimestampClick not provided", () => {
    render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    const timestampButton = screen.getByRole("button", {
      name: /Jump to timestamp 5:20 - 10:15/,
    });

    expect(timestampButton).toBeDisabled();
  });

  it("handles very long exchange summaries", () => {
    const longEvidence: ExchangeEvidence = {
      ...mockEvidence,
      exchange_summary:
        "Rep asked detailed questions about their current data infrastructure, including questions about data sources, ETL processes, data quality issues, manual data processing workflows, reporting bottlenecks, team size, and current tooling. The prospect shared that they have 15 data sources, manual SQL queries taking 2-3 hours per report, and a team of 3 analysts spending 60% of their time on data preparation instead of analysis.",
    };

    render(<ExchangeEvidenceCard evidence={longEvidence} />);

    expect(screen.getByText(/Rep asked detailed questions/)).toBeInTheDocument();
  });

  it("handles very long impact statements", () => {
    const longImpactEvidence: ExchangeEvidence = {
      ...mockEvidence,
      impact:
        "Identified significant cost savings opportunity of $50K/year in manual processing time, aligned with their Q1 strategic initiative to improve data team efficiency, validated ROI calculation with prospect's own numbers, and secured commitment to include in business case for executive review.",
    };

    render(<ExchangeEvidenceCard evidence={longImpactEvidence} />);

    expect(screen.getByText(/Identified significant cost savings/)).toBeInTheDocument();
  });

  it("formats timestamps correctly at boundary values", () => {
    const boundaryEvidence: ExchangeEvidence = {
      timestamp_start: 0, // 0:00
      timestamp_end: 3599, // 59:59
      exchange_summary: "Start to end",
      impact: "Full call",
    };

    render(<ExchangeEvidenceCard evidence={boundaryEvidence} />);

    expect(screen.getByText("0:00 - 59:59")).toBeInTheDocument();
  });

  it("applies hover styles to card", () => {
    const { container } = render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    const card = container.querySelector(".hover\\:border-gray-300");
    expect(card).toBeInTheDocument();
  });

  it("applies correct styling when clickable", () => {
    const handleClick = jest.fn();
    render(<ExchangeEvidenceCard evidence={mockEvidence} onTimestampClick={handleClick} />);

    const timestampButton = screen.getByRole("button", {
      name: /Jump to timestamp/,
    });

    expect(timestampButton).toHaveClass("hover:bg-blue-100");
    expect(timestampButton).toHaveClass("cursor-pointer");
  });

  it("applies correct styling when not clickable", () => {
    render(<ExchangeEvidenceCard evidence={mockEvidence} />);

    const timestampButton = screen.getByRole("button", {
      name: /Jump to timestamp/,
    });

    expect(timestampButton).toHaveClass("cursor-default");
    expect(timestampButton).not.toHaveClass("cursor-pointer");
  });

  it("renders with minimal evidence data", () => {
    const minimalEvidence: ExchangeEvidence = {
      timestamp_start: 0,
      timestamp_end: 1,
      exchange_summary: "Short.",
      impact: "Minimal.",
    };

    render(<ExchangeEvidenceCard evidence={minimalEvidence} />);

    expect(screen.getByText("0:00 - 0:01")).toBeInTheDocument();
    expect(screen.getByText("Short.")).toBeInTheDocument();
    expect(screen.getByText("Minimal.")).toBeInTheDocument();
  });
});
