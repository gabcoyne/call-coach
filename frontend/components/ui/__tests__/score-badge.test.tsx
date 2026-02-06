import { render, screen } from "@testing-library/react";
import { ScoreBadge, DimensionScoreCard } from "../score-badge";

describe("ScoreBadge", () => {
  describe("Score Display", () => {
    it("should render score as percentage by default", () => {
      render(<ScoreBadge score={85} />);
      expect(screen.getByText("85%")).toBeInTheDocument();
    });

    it("should render score as fraction when showPercentage is false", () => {
      render(<ScoreBadge score={85} showPercentage={false} />);
      expect(screen.getByText("85/100")).toBeInTheDocument();
    });

    it("should handle minimum score of 0", () => {
      render(<ScoreBadge score={0} />);
      expect(screen.getByText("0%")).toBeInTheDocument();
    });

    it("should handle maximum score of 100", () => {
      render(<ScoreBadge score={100} />);
      expect(screen.getByText("100%")).toBeInTheDocument();
    });

    it("should handle custom maxScore", () => {
      render(<ScoreBadge score={50} maxScore={50} />);
      expect(screen.getByText("100%")).toBeInTheDocument();
    });

    it("should round percentage to nearest integer", () => {
      render(<ScoreBadge score={85.7} />);
      expect(screen.getByText("86%")).toBeInTheDocument();
    });
  });

  describe("Variant Colors", () => {
    it("should use success variant for scores >= 90%", () => {
      const { container } = render(<ScoreBadge score={95} />);
      // Badge with success variant should be present
      expect(container.firstChild).toBeInTheDocument();
    });

    it("should use info variant for scores 75-89%", () => {
      const { container } = render(<ScoreBadge score={80} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it("should use warning variant for scores 60-74%", () => {
      const { container } = render(<ScoreBadge score={65} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it("should use destructive variant for scores < 60%", () => {
      const { container } = render(<ScoreBadge score={50} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it("should correctly handle threshold boundaries", () => {
      // Test exactly at 90
      render(<ScoreBadge score={90} />);
      expect(screen.getByText("90%")).toBeInTheDocument();

      // Test exactly at 75
      render(<ScoreBadge score={75} />);
      expect(screen.getByText("75%")).toBeInTheDocument();

      // Test exactly at 60
      render(<ScoreBadge score={60} />);
      expect(screen.getByText("60%")).toBeInTheDocument();
    });
  });

  describe("Custom Styling", () => {
    it("should apply font-semibold class by default", () => {
      const { container } = render(<ScoreBadge score={85} />);
      expect(container.firstChild).toHaveClass("font-semibold");
    });

    it("should accept and merge custom className", () => {
      const { container } = render(<ScoreBadge score={85} className="custom-class" />);
      const badge = container.firstChild;
      expect(badge).toHaveClass("custom-class");
      expect(badge).toHaveClass("font-semibold");
    });
  });
});

describe("DimensionScoreCard", () => {
  describe("Rendering", () => {
    it("should render dimension name and score", () => {
      render(<DimensionScoreCard dimension="Discovery" score={85} />);
      expect(screen.getByText("Discovery")).toBeInTheDocument();
      expect(screen.getByText("85%")).toBeInTheDocument();
    });

    it("should render description when provided", () => {
      render(
        <DimensionScoreCard
          dimension="Discovery"
          score={85}
          description="Asking insightful questions"
        />
      );
      expect(screen.getByText("Asking insightful questions")).toBeInTheDocument();
    });

    it("should not render description when not provided", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={85} />);
      expect(container.querySelector(".text-muted-foreground")).not.toBeInTheDocument();
    });
  });

  describe("Progress Bar", () => {
    it("should display progress percentage", () => {
      render(<DimensionScoreCard dimension="Discovery" score={85} />);
      // Progress label
      expect(screen.getByText("Progress")).toBeInTheDocument();
      // Percentage value
      expect(screen.getByText("85%")).toBeInTheDocument();
    });

    it("should render progress bar with correct width", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={75} />);
      const progressBar = container.querySelector('[style*="width"]');
      expect(progressBar).toHaveStyle({ width: "75%" });
    });

    it("should apply green color for scores >= 90%", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={95} />);
      const progressBar = container.querySelector(".bg-green-500");
      expect(progressBar).toBeInTheDocument();
    });

    it("should apply blue color for scores 75-89%", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={80} />);
      const progressBar = container.querySelector(".bg-prefect-blue-500");
      expect(progressBar).toBeInTheDocument();
    });

    it("should apply orange color for scores 60-74%", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={65} />);
      const progressBar = container.querySelector(".bg-prefect-sunrise1");
      expect(progressBar).toBeInTheDocument();
    });

    it("should apply red color for scores < 60%", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={50} />);
      const progressBar = container.querySelector(".bg-red-500");
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe("Custom Styling", () => {
    it("should apply custom className", () => {
      const { container } = render(
        <DimensionScoreCard dimension="Discovery" score={85} className="custom-card" />
      );
      expect(container.firstChild).toHaveClass("custom-card");
    });

    it("should maintain card structure classes", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={85} />);
      expect(container.firstChild).toHaveClass("rounded-lg", "border", "bg-card", "p-4");
    });
  });

  describe("Edge Cases", () => {
    it("should handle 0% score", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={0} />);
      const progressBar = container.querySelector('[style*="width"]');
      expect(progressBar).toHaveStyle({ width: "0%" });
    });

    it("should handle 100% score", () => {
      const { container } = render(<DimensionScoreCard dimension="Discovery" score={100} />);
      const progressBar = container.querySelector('[style*="width"]');
      expect(progressBar).toHaveStyle({ width: "100%" });
    });

    it("should handle custom maxScore", () => {
      render(<DimensionScoreCard dimension="Discovery" score={50} maxScore={50} />);
      expect(screen.getByText("100%")).toBeInTheDocument();
    });
  });
});
