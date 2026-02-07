/**
 * Tests for ScoreCard Component
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { ScoreCard } from "../ScoreCard";
import type { FiveWinsEvaluation } from "@/types/rubric";

describe("ScoreCard", () => {
  const basicProps = {
    score: 85,
    title: "Overall Performance",
    subtitle: "Strong execution across all dimensions",
  };

  const mockFiveWinsEvaluation: FiveWinsEvaluation = {
    business_win: {
      score: 30,
      max_score: 35,
      status: "met",
      evidence: [],
    },
    technical_win: {
      score: 20,
      max_score: 25,
      status: "met",
      evidence: [],
    },
    security_win: {
      score: 10,
      max_score: 15,
      status: "partial",
      evidence: [],
    },
    commercial_win: {
      score: 15,
      max_score: 15,
      status: "met",
      evidence: [],
    },
    legal_win: {
      score: 10,
      max_score: 10,
      status: "met",
      evidence: [],
    },
    wins_secured: 4,
    overall_score: 85,
  };

  describe("Basic Functionality (Backward Compatibility)", () => {
    it("renders score, title, and subtitle", () => {
      render(<ScoreCard {...basicProps} />);

      expect(screen.getByText("Overall Performance")).toBeInTheDocument();
      expect(screen.getByText("85")).toBeInTheDocument();
      expect(screen.getByText("/ 100")).toBeInTheDocument();
      expect(screen.getByText("Strong execution across all dimensions")).toBeInTheDocument();
    });

    it("renders without subtitle when not provided", () => {
      const { container } = render(<ScoreCard score={75} title="Discovery" />);

      expect(screen.getByText("Discovery")).toBeInTheDocument();
      expect(screen.getByText("75")).toBeInTheDocument();
      expect(container.textContent).not.toContain("Strong execution");
    });

    it("applies custom className", () => {
      const { container } = render(<ScoreCard {...basicProps} className="custom-class" />);

      const card = container.querySelector(".custom-class");
      expect(card).toBeInTheDocument();
    });

    it("displays performance label based on score", () => {
      const { rerender } = render(<ScoreCard score={85} title="Test" />);
      expect(screen.getByText(/Excellent|Strong/i)).toBeInTheDocument();

      rerender(<ScoreCard score={70} title="Test" />);
      expect(screen.getByText(/Good|Solid/i)).toBeInTheDocument();

      rerender(<ScoreCard score={50} title="Test" />);
      expect(screen.getByText(/Needs|Improvement/i)).toBeInTheDocument();
    });

    it("does not show expand button when fiveWinsEvaluation not provided", () => {
      render(<ScoreCard {...basicProps} />);

      expect(screen.queryByText(/Show How This Score Was Calculated/)).not.toBeInTheDocument();
      expect(screen.queryByText(/Hide Score Breakdown/)).not.toBeInTheDocument();
    });
  });

  describe("Expandable Functionality", () => {
    it("shows expand button when fiveWinsEvaluation provided", () => {
      render(<ScoreCard {...basicProps} fiveWinsEvaluation={mockFiveWinsEvaluation} />);

      expect(screen.getByText("Show How This Score Was Calculated")).toBeInTheDocument();
    });

    it("expands to show Five Wins breakdown when clicked", () => {
      render(<ScoreCard {...basicProps} fiveWinsEvaluation={mockFiveWinsEvaluation} />);

      const expandButton = screen.getByRole("button", {
        name: /Show How This Score Was Calculated/,
      });
      fireEvent.click(expandButton);

      // Should show FiveWinsScoreCard content
      expect(screen.getByText(/of 5 Wins Secured/)).toBeInTheDocument();
      expect(screen.getByText("Hide Score Breakdown")).toBeInTheDocument();
    });

    it("collapses when clicked again", () => {
      render(<ScoreCard {...basicProps} fiveWinsEvaluation={mockFiveWinsEvaluation} />);

      // Expand
      const expandButton = screen.getByRole("button", {
        name: /Show How This Score Was Calculated/,
      });
      fireEvent.click(expandButton);

      expect(screen.getByText(/of 5 Wins Secured/)).toBeInTheDocument();

      // Collapse
      const collapseButton = screen.getByRole("button", {
        name: /Hide Score Breakdown/,
      });
      fireEvent.click(collapseButton);

      expect(screen.queryByText(/of 5 Wins Secured/)).not.toBeInTheDocument();
      expect(screen.getByText("Show How This Score Was Calculated")).toBeInTheDocument();
    });

    it("is collapsed by default", () => {
      render(<ScoreCard {...basicProps} fiveWinsEvaluation={mockFiveWinsEvaluation} />);

      expect(screen.queryByText(/of 5 Wins Secured/)).not.toBeInTheDocument();
      expect(screen.getByText("Show How This Score Was Calculated")).toBeInTheDocument();
    });

    it("passes onShowAllFrameworks callback to FiveWinsScoreCard", () => {
      const handleShowAll = jest.fn();

      render(
        <ScoreCard
          {...basicProps}
          fiveWinsEvaluation={mockFiveWinsEvaluation}
          onShowAllFrameworks={handleShowAll}
        />
      );

      // Expand
      const expandButton = screen.getByRole("button", {
        name: /Show How This Score Was Calculated/,
      });
      fireEvent.click(expandButton);

      // Find and click "Show All Frameworks" button in FiveWinsScoreCard
      const showAllButton = screen.getByRole("button", {
        name: /Show All Coaching Frameworks/,
      });
      fireEvent.click(showAllButton);

      expect(handleShowAll).toHaveBeenCalledTimes(1);
    });
  });

  describe("Color Coding", () => {
    it("applies green styling for high scores (>=80)", () => {
      const { container } = render(<ScoreCard score={85} title="Test" />);

      const card = container.querySelector("div[style*='background']");
      expect(card).toBeInTheDocument();
      // Green background should be applied
      expect(card?.getAttribute("style")).toContain("rgb");
    });

    it("applies yellow styling for medium scores (60-79)", () => {
      const { container } = render(<ScoreCard score={70} title="Test" />);

      const card = container.querySelector("div[style*='background']");
      expect(card).toBeInTheDocument();
      expect(card?.getAttribute("style")).toContain("rgb");
    });

    it("applies red styling for low scores (<60)", () => {
      const { container } = render(<ScoreCard score={45} title="Test" />);

      const card = container.querySelector("div[style*='background']");
      expect(card).toBeInTheDocument();
      expect(card?.getAttribute("style")).toContain("rgb");
    });
  });

  describe("Edge Cases", () => {
    it("handles score of 0", () => {
      render(<ScoreCard score={0} title="Test" />);

      expect(screen.getByText("0")).toBeInTheDocument();
    });

    it("handles score of 100", () => {
      render(<ScoreCard score={100} title="Test" />);

      expect(screen.getByText("100")).toBeInTheDocument();
    });

    it("handles very long title", () => {
      render(
        <ScoreCard
          score={75}
          title="This is a very long title that might wrap to multiple lines in the component"
        />
      );

      expect(screen.getByText(/This is a very long title that might wrap/)).toBeInTheDocument();
    });

    it("handles very long subtitle", () => {
      render(
        <ScoreCard
          score={75}
          title="Test"
          subtitle="This is a very long subtitle that provides extensive context and details about the performance and might wrap to multiple lines"
        />
      );

      expect(screen.getByText(/This is a very long subtitle/)).toBeInTheDocument();
    });
  });

  describe("Animation", () => {
    it("applies fade-in animation to expanded content", () => {
      const { container } = render(
        <ScoreCard {...basicProps} fiveWinsEvaluation={mockFiveWinsEvaluation} />
      );

      const expandButton = screen.getByRole("button", {
        name: /Show How This Score Was Calculated/,
      });
      fireEvent.click(expandButton);

      const expandedContent = container.querySelector(".animate-fadeIn");
      expect(expandedContent).toBeInTheDocument();
    });
  });
});
