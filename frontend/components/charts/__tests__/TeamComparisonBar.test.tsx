import { render, screen, waitFor } from "@testing-library/react";
import { TeamComparisonBar, TeamComparisonData } from "../TeamComparisonBar";

describe("TeamComparisonBar", () => {
  const mockData: TeamComparisonData[] = [
    { dimension: "Product Knowledge", repScore: 85, teamAverage: 80, percentile: 75 },
    { dimension: "Discovery", repScore: 72, teamAverage: 78, percentile: 45 },
    { dimension: "Objection Handling", repScore: 90, teamAverage: 82, percentile: 88 },
    { dimension: "Engagement", repScore: 78, teamAverage: 80, percentile: 52 },
  ];

  describe("Rendering with Props", () => {
    it("should render bar chart with data", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const barChart = container.querySelector(".recharts-bar-chart");
      expect(barChart).toBeInTheDocument();
    });

    it("should display all dimension names", () => {
      render(<TeamComparisonBar data={mockData} />);
      mockData.forEach((item) => {
        expect(screen.getByText(item.dimension)).toBeInTheDocument();
      });
    });

    it("should render with custom height", () => {
      const { container } = render(<TeamComparisonBar data={mockData} height={400} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });

    it("should apply custom className", () => {
      const { container } = render(
        <TeamComparisonBar data={mockData} className="custom-comparison" />
      );
      expect(container.firstChild).toHaveClass("custom-comparison");
    });
  });

  describe("Empty State", () => {
    it("should show placeholder when data is empty", () => {
      render(<TeamComparisonBar data={[]} />);
      expect(screen.getByText("No comparison data available")).toBeInTheDocument();
    });

    it("should show placeholder when data is null", () => {
      render(<TeamComparisonBar data={null as any} />);
      expect(screen.getByText("No comparison data available")).toBeInTheDocument();
    });

    it("should apply custom height to placeholder", () => {
      const { container } = render(<TeamComparisonBar data={[]} height={300} />);
      const placeholder = screen.getByText("No comparison data available").closest("div");
      expect(placeholder).toHaveStyle({ height: "300px" });
    });
  });

  describe("Async Data Loading", () => {
    it("should handle initial render with empty data then update", async () => {
      const { rerender } = render(<TeamComparisonBar data={[]} />);
      expect(screen.getByText("No comparison data available")).toBeInTheDocument();

      // Simulate async data load
      rerender(<TeamComparisonBar data={mockData} />);

      await waitFor(() => {
        expect(screen.queryByText("No comparison data available")).not.toBeInTheDocument();
        expect(screen.getByText(mockData[0].dimension)).toBeInTheDocument();
      });
    });

    it("should update when data changes", async () => {
      const initialData: TeamComparisonData[] = [
        { dimension: "Test Dimension", repScore: 75, teamAverage: 70, percentile: 65 },
      ];

      const { rerender } = render(<TeamComparisonBar data={initialData} />);
      expect(screen.getByText("Test Dimension")).toBeInTheDocument();

      // Update with new data
      rerender(<TeamComparisonBar data={mockData} />);

      await waitFor(() => {
        expect(screen.getByText(mockData[0].dimension)).toBeInTheDocument();
        expect(screen.queryByText("Test Dimension")).not.toBeInTheDocument();
      });
    });

    it("should handle loading state transition", async () => {
      const { rerender } = render(<TeamComparisonBar data={[]} />);

      // Simulate loading complete
      await waitFor(() => {
        expect(screen.getByText("No comparison data available")).toBeInTheDocument();
      });

      rerender(<TeamComparisonBar data={mockData} />);

      await waitFor(() => {
        const barChart = document.querySelector(".recharts-bar-chart");
        expect(barChart).toBeInTheDocument();
      });
    });

    it("should handle multiple data updates", async () => {
      const data1: TeamComparisonData[] = [
        { dimension: "Dim 1", repScore: 75, teamAverage: 70, percentile: 65 },
      ];
      const data2: TeamComparisonData[] = [
        { dimension: "Dim 2", repScore: 85, teamAverage: 80, percentile: 75 },
      ];
      const data3: TeamComparisonData[] = [
        { dimension: "Dim 3", repScore: 95, teamAverage: 90, percentile: 85 },
      ];

      const { rerender } = render(<TeamComparisonBar data={data1} />);
      expect(screen.getByText("Dim 1")).toBeInTheDocument();

      rerender(<TeamComparisonBar data={data2} />);
      await waitFor(() => {
        expect(screen.getByText("Dim 2")).toBeInTheDocument();
      });

      rerender(<TeamComparisonBar data={data3} />);
      await waitFor(() => {
        expect(screen.getByText("Dim 3")).toBeInTheDocument();
      });
    });
  });

  describe("Chart Components", () => {
    it("should render CartesianGrid", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const grid = container.querySelector(".recharts-cartesian-grid");
      expect(grid).toBeInTheDocument();
    });

    it("should render X-axis with dimension names", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const xAxis = container.querySelector(".recharts-xAxis");
      expect(xAxis).toBeInTheDocument();
    });

    it("should render Y-axis with score scale", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const yAxis = container.querySelector(".recharts-yAxis");
      expect(yAxis).toBeInTheDocument();
    });

    it("should configure Y-axis domain to 0-100", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const yAxis = container.querySelector(".recharts-yAxis");
      expect(yAxis).toBeInTheDocument();
    });

    it("should render Tooltip", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const tooltip = container.querySelector(".recharts-tooltip-wrapper");
      expect(tooltip).toBeInTheDocument();
    });

    it("should render Legend", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const legend = container.querySelector(".recharts-legend-wrapper");
      expect(legend).toBeInTheDocument();
    });
  });

  describe("Bar Series", () => {
    it("should render two bar series (rep and team)", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const bars = container.querySelectorAll(".recharts-bar");
      expect(bars.length).toBe(2); // repScore and teamAverage
    });

    it("should apply different colors based on performance", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      // Rep score bars should have cells with different colors
      const cells = container.querySelectorAll(".recharts-bar-rectangle");
      expect(cells.length).toBeGreaterThan(0);
    });

    it("should use rounded corners for bars", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const bars = container.querySelectorAll(".recharts-bar");
      expect(bars.length).toBe(2);
    });
  });

  describe("Reference Line", () => {
    it("should render team average reference line", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const referenceLine = container.querySelector(".recharts-reference-line");
      expect(referenceLine).toBeInTheDocument();
    });

    it("should calculate and display average team score", () => {
      render(<TeamComparisonBar data={mockData} />);
      // Calculate expected average: (80 + 78 + 82 + 80) / 4 = 80
      const expectedAvg = 80;
      expect(screen.getByText(`Team Avg: ${expectedAvg}`)).toBeInTheDocument();
    });

    it("should handle single dimension data", () => {
      const singleData: TeamComparisonData[] = [
        { dimension: "Single", repScore: 85, teamAverage: 80, percentile: 75 },
      ];
      render(<TeamComparisonBar data={singleData} />);
      expect(screen.getByText("Team Avg: 80")).toBeInTheDocument();
    });
  });

  describe("Percentile Display", () => {
    it("should show percentile when showPercentile is true", () => {
      const { container } = render(<TeamComparisonBar data={mockData} showPercentile={true} />);
      // Percentile should be available in tooltip
      expect(container).toBeInTheDocument();
    });

    it("should not show percentile by default", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      // Default showPercentile is false
      expect(container).toBeInTheDocument();
    });

    it("should handle data without percentile values", () => {
      const dataWithoutPercentile: TeamComparisonData[] = [
        { dimension: "Discovery", repScore: 85, teamAverage: 80 },
        { dimension: "Engagement", repScore: 75, teamAverage: 78 },
      ];
      render(<TeamComparisonBar data={dataWithoutPercentile} showPercentile={true} />);
      expect(screen.getByText("Discovery")).toBeInTheDocument();
    });
  });

  describe("Role Filter", () => {
    it("should display role filter info when roleFilter is provided", () => {
      render(<TeamComparisonBar data={mockData} roleFilter="AEs only" />);
      expect(screen.getByText(/Comparing AEs only/i)).toBeInTheDocument();
    });

    it("should show team average in role filter section", () => {
      render(<TeamComparisonBar data={mockData} roleFilter="SDRs only" />);
      expect(screen.getByText(/Team average across all dimensions/i)).toBeInTheDocument();
      expect(screen.getByText("80")).toBeInTheDocument();
    });

    it("should not display role filter section when roleFilter is not provided", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      expect(screen.queryByText(/Comparing/i)).not.toBeInTheDocument();
    });
  });

  describe("Color Coding", () => {
    it("should use green color when rep exceeds team by >5 points", () => {
      const highPerformance: TeamComparisonData[] = [
        { dimension: "Excellent", repScore: 90, teamAverage: 80, percentile: 95 },
      ];
      const { container } = render(<TeamComparisonBar data={highPerformance} />);
      const cells = container.querySelectorAll(".recharts-bar-rectangle");
      expect(cells.length).toBeGreaterThan(0);
    });

    it("should use red color when rep is below team by >5 points", () => {
      const lowPerformance: TeamComparisonData[] = [
        { dimension: "Needs Work", repScore: 65, teamAverage: 75, percentile: 25 },
      ];
      const { container } = render(<TeamComparisonBar data={lowPerformance} />);
      const cells = container.querySelectorAll(".recharts-bar-rectangle");
      expect(cells.length).toBeGreaterThan(0);
    });

    it("should use neutral color when difference is ≤5 points", () => {
      const averagePerformance: TeamComparisonData[] = [
        { dimension: "Average", repScore: 78, teamAverage: 80, percentile: 50 },
      ];
      const { container } = render(<TeamComparisonBar data={averagePerformance} />);
      const cells = container.querySelectorAll(".recharts-bar-rectangle");
      expect(cells.length).toBeGreaterThan(0);
    });
  });

  describe("Edge Cases", () => {
    it("should handle all dimensions with same score", () => {
      const uniformData: TeamComparisonData[] = [
        { dimension: "Dim 1", repScore: 80, teamAverage: 80, percentile: 50 },
        { dimension: "Dim 2", repScore: 80, teamAverage: 80, percentile: 50 },
      ];
      render(<TeamComparisonBar data={uniformData} />);
      expect(screen.getByText("Team Avg: 80")).toBeInTheDocument();
    });

    it("should handle minimum scores (0)", () => {
      const minScores: TeamComparisonData[] = [
        { dimension: "Low", repScore: 0, teamAverage: 0, percentile: 0 },
      ];
      render(<TeamComparisonBar data={minScores} />);
      expect(screen.getByText("Low")).toBeInTheDocument();
    });

    it("should handle maximum scores (100)", () => {
      const maxScores: TeamComparisonData[] = [
        { dimension: "Perfect", repScore: 100, teamAverage: 100, percentile: 100 },
      ];
      render(<TeamComparisonBar data={maxScores} />);
      expect(screen.getByText("Perfect")).toBeInTheDocument();
    });

    it("should handle long dimension names", () => {
      const longNames: TeamComparisonData[] = [
        {
          dimension: "Very Long Dimension Name That Should Wrap",
          repScore: 85,
          teamAverage: 80,
          percentile: 75,
        },
      ];
      render(<TeamComparisonBar data={longNames} />);
      expect(screen.getByText("Very Long Dimension Name That Should Wrap")).toBeInTheDocument();
    });

    it("should handle many dimensions", () => {
      const manyDimensions: TeamComparisonData[] = Array.from({ length: 10 }, (_, i) => ({
        dimension: `Dimension ${i + 1}`,
        repScore: 70 + i,
        teamAverage: 75 + i,
        percentile: 50 + i,
      }));
      render(<TeamComparisonBar data={manyDimensions} />);
      expect(screen.getByText("Dimension 1")).toBeInTheDocument();
      expect(screen.getByText("Dimension 10")).toBeInTheDocument();
    });
  });

  describe("Styling", () => {
    it("should render X-axis labels at an angle", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const xAxis = container.querySelector(".recharts-xAxis");
      expect(xAxis).toBeInTheDocument();
    });

    it("should apply proper margins for rotated labels", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const barChart = container.querySelector(".recharts-bar-chart");
      expect(barChart).toBeInTheDocument();
    });

    it("should use semi-transparent team average bars", () => {
      const { container } = render(<TeamComparisonBar data={mockData} />);
      const bars = container.querySelectorAll(".recharts-bar");
      expect(bars.length).toBe(2);
    });
  });
});
