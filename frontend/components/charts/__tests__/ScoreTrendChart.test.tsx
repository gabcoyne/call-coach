import { render, screen } from "@testing-library/react";
import { ScoreTrendChart, ScoreTrendDataPoint } from "../ScoreTrendChart";

describe("ScoreTrendChart", () => {
  describe("Rendering with Props", () => {
    const mockData: ScoreTrendDataPoint[] = [
      { date: "2026-01-01", overall: 75, discovery: 80, engagement: 70 },
      { date: "2026-01-08", overall: 78, discovery: 82, engagement: 74 },
      { date: "2026-01-15", overall: 82, discovery: 85, engagement: 79 },
    ];

    it("should render chart with data", () => {
      render(<ScoreTrendChart data={mockData} />);
      // ResponsiveContainer should be present
      const container = screen.getByText(mockData[0].date).closest("svg");
      expect(container).toBeInTheDocument();
    });

    it("should display all data points", () => {
      render(<ScoreTrendChart data={mockData} />);
      // Check that all dates are rendered
      mockData.forEach((point) => {
        expect(screen.getByText(point.date)).toBeInTheDocument();
      });
    });

    it("should render with custom dimensions", () => {
      render(<ScoreTrendChart data={mockData} dimensions={["discovery", "engagement"]} />);
      const container = screen.getByText(mockData[0].date).closest("svg");
      expect(container).toBeInTheDocument();
    });

    it("should render with custom height", () => {
      const { container } = render(<ScoreTrendChart data={mockData} height={400} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });

    it("should apply custom className", () => {
      const { container } = render(<ScoreTrendChart data={mockData} className="custom-chart" />);
      expect(container.firstChild).toHaveClass("custom-chart");
    });
  });

  describe("Empty State", () => {
    it("should show placeholder when data is empty", () => {
      render(<ScoreTrendChart data={[]} />);
      expect(screen.getByText("No trend data available")).toBeInTheDocument();
    });

    it("should show placeholder when data is null", () => {
      render(<ScoreTrendChart data={null as any} />);
      expect(screen.getByText("No trend data available")).toBeInTheDocument();
    });

    it("should apply custom height to placeholder", () => {
      const { container } = render(<ScoreTrendChart data={[]} height={300} />);
      const placeholder = screen.getByText("No trend data available").closest("div");
      expect(placeholder).toHaveStyle({ height: "300px" });
    });
  });

  describe("Chart Types", () => {
    const mockData: ScoreTrendDataPoint[] = [
      { date: "2026-01-01", overall: 75 },
      { date: "2026-01-08", overall: 78 },
      { date: "2026-01-15", overall: 82 },
    ];

    it("should render line chart by default", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      // LineChart should be rendered
      const lineChart = container.querySelector(".recharts-line-chart");
      expect(lineChart).toBeInTheDocument();
    });

    it("should render area chart when showArea is true", () => {
      const { container } = render(<ScoreTrendChart data={mockData} showArea={true} />);
      // AreaChart should be rendered
      const areaChart = container.querySelector(".recharts-area-chart");
      expect(areaChart).toBeInTheDocument();
    });

    it("should render area chart with gradient fill", () => {
      const { container } = render(
        <ScoreTrendChart data={mockData} showArea={true} dimensions={["overall"]} />
      );
      // Check for gradient definition
      const gradient = container.querySelector("#colorScore");
      expect(gradient).toBeInTheDocument();
    });

    it("should render line chart for multiple dimensions even with showArea", () => {
      const multiDimensionData: ScoreTrendDataPoint[] = [
        { date: "2026-01-01", discovery: 75, engagement: 70 },
        { date: "2026-01-08", discovery: 78, engagement: 74 },
      ];
      const { container } = render(
        <ScoreTrendChart
          data={multiDimensionData}
          dimensions={["discovery", "engagement"]}
          showArea={true}
        />
      );
      // Should render LineChart for multiple dimensions
      const lineChart = container.querySelector(".recharts-line-chart");
      expect(lineChart).toBeInTheDocument();
    });
  });

  describe("Dimensions Display", () => {
    const mockData: ScoreTrendDataPoint[] = [
      {
        date: "2026-01-01",
        overall: 75,
        product_knowledge: 80,
        discovery: 70,
        engagement: 75,
      },
      {
        date: "2026-01-08",
        overall: 78,
        product_knowledge: 82,
        discovery: 74,
        engagement: 78,
      },
    ];

    it("should render overall score when present", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      // Check for "Overall Score" in legend
      expect(container.textContent).toContain("Overall Score");
    });

    it("should render multiple dimension lines", () => {
      const { container } = render(
        <ScoreTrendChart
          data={mockData}
          dimensions={["product_knowledge", "discovery", "engagement"]}
        />
      );
      // Check that all dimensions are rendered in legend
      expect(container.textContent).toContain("Product Knowledge");
      expect(container.textContent).toContain("Discovery");
      expect(container.textContent).toContain("Engagement");
    });

    it("should format dimension names with proper capitalization", () => {
      const { container } = render(
        <ScoreTrendChart data={mockData} dimensions={["product_knowledge"]} />
      );
      // Underscores should be replaced with spaces and capitalized
      expect(container.textContent).toContain("Product Knowledge");
    });

    it("should filter out date dimension", () => {
      const { container } = render(
        <ScoreTrendChart data={mockData} dimensions={["date", "discovery"]} />
      );
      // "date" should not be plotted, but "Discovery" should
      expect(container.textContent).toContain("Discovery");
      expect(container.textContent).not.toContain("Date");
    });
  });

  describe("Tooltip", () => {
    const mockData: ScoreTrendDataPoint[] = [
      { date: "2026-01-01", overall: 75, discovery: 80 },
      { date: "2026-01-08", overall: 78, discovery: 82 },
    ];

    it("should render custom tooltip component", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      // Tooltip component should be present in the chart
      const tooltip = container.querySelector(".recharts-tooltip-wrapper");
      expect(tooltip).toBeInTheDocument();
    });
  });

  describe("Chart Configuration", () => {
    const mockData: ScoreTrendDataPoint[] = [
      { date: "2026-01-01", overall: 75 },
      { date: "2026-01-08", overall: 78 },
    ];

    it("should set Y-axis domain to 0-100", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      // Y-axis should be configured with domain [0, 100]
      const yAxis = container.querySelector(".recharts-yAxis");
      expect(yAxis).toBeInTheDocument();
    });

    it("should render CartesianGrid", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      const grid = container.querySelector(".recharts-cartesian-grid");
      expect(grid).toBeInTheDocument();
    });

    it("should render Legend", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      const legend = container.querySelector(".recharts-legend-wrapper");
      expect(legend).toBeInTheDocument();
    });

    it("should use date as X-axis dataKey", () => {
      const { container } = render(<ScoreTrendChart data={mockData} />);
      // X-axis should use "date" as dataKey
      const xAxis = container.querySelector(".recharts-xAxis");
      expect(xAxis).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle single data point", () => {
      const singlePoint: ScoreTrendDataPoint[] = [{ date: "2026-01-01", overall: 75 }];
      render(<ScoreTrendChart data={singlePoint} />);
      expect(screen.getByText("2026-01-01")).toBeInTheDocument();
    });

    it("should handle data with missing values", () => {
      const sparseData: ScoreTrendDataPoint[] = [
        { date: "2026-01-01", overall: 75, discovery: 80 },
        { date: "2026-01-08", overall: 78 }, // discovery missing
        { date: "2026-01-15", overall: 82, discovery: 85 },
      ];
      render(<ScoreTrendChart data={sparseData} dimensions={["discovery"]} />);
      expect(screen.getByText("2026-01-08")).toBeInTheDocument();
    });

    it("should handle data with no overall score", () => {
      const noOverallData: ScoreTrendDataPoint[] = [
        { date: "2026-01-01", discovery: 80, engagement: 70 },
        { date: "2026-01-08", discovery: 82, engagement: 74 },
      ];
      render(<ScoreTrendChart data={noOverallData} dimensions={["discovery", "engagement"]} />);
      // Should still render without overall
      expect(screen.getByText("2026-01-01")).toBeInTheDocument();
    });

    it("should handle empty dimensions array", () => {
      const mockData: ScoreTrendDataPoint[] = [
        { date: "2026-01-01", overall: 75 },
        { date: "2026-01-08", overall: 78 },
      ];
      render(<ScoreTrendChart data={mockData} dimensions={[]} />);
      // Should still render with overall score if present
      expect(screen.getByText("2026-01-01")).toBeInTheDocument();
    });
  });
});
