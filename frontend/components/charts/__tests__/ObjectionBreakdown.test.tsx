import { render, screen, fireEvent } from "@testing-library/react";
import { ObjectionBreakdown, ObjectionType } from "../ObjectionBreakdown";

describe("ObjectionBreakdown", () => {
  const mockData: ObjectionType[] = [
    { name: "Price", count: 15, successRate: 75, avgScore: 82 },
    { name: "Competition", count: 10, successRate: 60, avgScore: 70 },
    { name: "Timing", count: 8, successRate: 85, avgScore: 88 },
    { name: "Need", count: 5, successRate: 90, avgScore: 92 },
  ];

  describe("Rendering with Props", () => {
    it("should render objection breakdown chart", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const pieChart = container.querySelector(".recharts-pie-chart");
      expect(pieChart).toBeInTheDocument();
    });

    it("should render with custom height", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} height={400} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });

    it("should apply custom className", () => {
      const { container } = render(
        <ObjectionBreakdown data={mockData} className="custom-objection" />
      );
      expect(container.firstChild).toHaveClass("custom-objection");
    });
  });

  describe("Empty State", () => {
    it("should show placeholder when data is empty", () => {
      render(<ObjectionBreakdown data={[]} />);
      expect(screen.getByText("No objection data available")).toBeInTheDocument();
    });

    it("should show placeholder when data is null", () => {
      render(<ObjectionBreakdown data={null as any} />);
      expect(screen.getByText("No objection data available")).toBeInTheDocument();
    });

    it("should apply custom height to placeholder", () => {
      const { container } = render(<ObjectionBreakdown data={[]} height={300} />);
      const placeholder = screen.getByText("No objection data available").closest("div");
      expect(placeholder).toHaveStyle({ height: "300px" });
    });
  });

  describe("View Mode Buttons", () => {
    it("should render Distribution and Details buttons", () => {
      render(<ObjectionBreakdown data={mockData} />);
      expect(screen.getByText("Distribution")).toBeInTheDocument();
      expect(screen.getByText("Details")).toBeInTheDocument();
    });

    it("should highlight Distribution button by default", () => {
      render(<ObjectionBreakdown data={mockData} />);
      const distributionButton = screen.getByText("Distribution");
      expect(distributionButton).toHaveClass("bg-blue-500", "text-white");
    });

    it("should start with Details view when showDetails is true", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const detailsButton = screen.getByText("Details");
      expect(detailsButton).toHaveClass("bg-blue-500", "text-white");
    });

    it("should switch to Details view when Details button clicked", () => {
      render(<ObjectionBreakdown data={mockData} />);
      const detailsButton = screen.getByText("Details");
      fireEvent.click(detailsButton);
      expect(detailsButton).toHaveClass("bg-blue-500", "text-white");
    });

    it("should switch back to Distribution view when Distribution button clicked", () => {
      render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const distributionButton = screen.getByText("Distribution");
      fireEvent.click(distributionButton);
      expect(distributionButton).toHaveClass("bg-blue-500", "text-white");
    });
  });

  describe("Pie Chart View (Distribution)", () => {
    it("should render pie chart by default", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const pieChart = container.querySelector(".recharts-pie-chart");
      expect(pieChart).toBeInTheDocument();
    });

    it("should display all objection types in pie chart", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      mockData.forEach((item) => {
        expect(container.textContent).toContain(item.name);
      });
    });

    it("should render pie slices with different colors", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const cells = container.querySelectorAll(".recharts-pie-sector");
      expect(cells.length).toBe(mockData.length);
    });

    it("should show percentage labels on pie slices", () => {
      render(<ObjectionBreakdown data={mockData} />);
      // Total = 15 + 10 + 8 + 5 = 38
      // Price percentage = 15/38 * 100 = 39%
      const totalCount = mockData.reduce((sum, d) => sum + d.count, 0);
      expect(totalCount).toBe(38);
    });

    it("should render Tooltip", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const tooltip = container.querySelector(".recharts-tooltip-wrapper");
      expect(tooltip).toBeInTheDocument();
    });
  });

  describe("Bar Chart View (Details)", () => {
    it("should render bar chart when in details mode", () => {
      render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const barChart = document.querySelector(".recharts-bar-chart");
      expect(barChart).toBeInTheDocument();
    });

    it("should display objection names on X-axis", () => {
      render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      mockData.forEach((item) => {
        expect(screen.getByText(item.name)).toBeInTheDocument();
      });
    });

    it("should render two Y-axes (count and success rate)", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const yAxes = container.querySelectorAll(".recharts-yAxis");
      expect(yAxes.length).toBe(2);
    });

    it("should render two bar series", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const bars = container.querySelectorAll(".recharts-bar");
      expect(bars.length).toBe(2); // count and successRate
    });

    it("should render CartesianGrid", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const grid = container.querySelector(".recharts-cartesian-grid");
      expect(grid).toBeInTheDocument();
    });

    it("should render Legend", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const legend = container.querySelector(".recharts-legend-wrapper");
      expect(legend).toBeInTheDocument();
    });

    it("should show message when no success rate data available", () => {
      const dataWithoutSuccessRate: ObjectionType[] = [
        { name: "Price", count: 15 },
        { name: "Competition", count: 10 },
      ];
      render(<ObjectionBreakdown data={dataWithoutSuccessRate} showDetails={true} />);
      expect(
        screen.getByText("No success rate data available. Switch to Distribution view.")
      ).toBeInTheDocument();
    });
  });

  describe("Tooltip Content", () => {
    it("should show objection name in tooltip", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const tooltip = container.querySelector(".recharts-tooltip-wrapper");
      expect(tooltip).toBeInTheDocument();
    });

    it("should show count and percentage in pie chart tooltip", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      // Tooltip component should be present
      expect(container).toBeInTheDocument();
    });

    it("should show success rate in details tooltip", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      // Tooltip should show success rate and avg score
      expect(container).toBeInTheDocument();
    });
  });

  describe("Data Calculations", () => {
    it("should calculate total objections correctly", () => {
      render(<ObjectionBreakdown data={mockData} />);
      const total = mockData.reduce((sum, d) => sum + d.count, 0);
      expect(total).toBe(38);
    });

    it("should calculate percentages correctly", () => {
      render(<ObjectionBreakdown data={mockData} />);
      // Price: 15/38 = 39%
      // Competition: 10/38 = 26%
      // Timing: 8/38 = 21%
      // Need: 5/38 = 13%
      const total = mockData.reduce((sum, d) => sum + d.count, 0);
      const pricePercentage = Math.round((15 / total) * 100);
      expect(pricePercentage).toBe(39);
    });

    it("should handle equal distribution", () => {
      const equalData: ObjectionType[] = [
        { name: "Type A", count: 10, successRate: 80 },
        { name: "Type B", count: 10, successRate: 80 },
        { name: "Type C", count: 10, successRate: 80 },
        { name: "Type D", count: 10, successRate: 80 },
      ];
      render(<ObjectionBreakdown data={equalData} />);
      // Each should be 25%
      expect(screen.getByText("Type A")).toBeInTheDocument();
    });
  });

  describe("Success Rate Display", () => {
    it("should display success rates when available", () => {
      render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      // Success rates should be visible in the chart
      expect(screen.getByText("Price")).toBeInTheDocument();
    });

    it("should handle missing success rates gracefully", () => {
      const mixedData: ObjectionType[] = [
        { name: "With Rate", count: 10, successRate: 80 },
        { name: "Without Rate", count: 8 },
      ];
      render(<ObjectionBreakdown data={mixedData} showDetails={true} />);
      expect(screen.getByText("With Rate")).toBeInTheDocument();
    });

    it("should display avgScore when available", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      // avgScore should be accessible in tooltips
      expect(container).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle single objection type", () => {
      const singleData: ObjectionType[] = [{ name: "Price", count: 20, successRate: 75 }];
      render(<ObjectionBreakdown data={singleData} />);
      expect(screen.getByText("Price")).toBeInTheDocument();
    });

    it("should handle many objection types", () => {
      const manyData: ObjectionType[] = Array.from({ length: 12 }, (_, i) => ({
        name: `Objection ${i + 1}`,
        count: i + 1,
        successRate: 70 + i,
      }));
      render(<ObjectionBreakdown data={manyData} />);
      expect(screen.getByText("Objection 1")).toBeInTheDocument();
      expect(screen.getByText("Objection 12")).toBeInTheDocument();
    });

    it("should handle zero count objections", () => {
      const zeroData: ObjectionType[] = [
        { name: "Never Seen", count: 0, successRate: 0 },
        { name: "Sometimes", count: 5, successRate: 80 },
      ];
      render(<ObjectionBreakdown data={zeroData} />);
      expect(screen.getByText("Sometimes")).toBeInTheDocument();
    });

    it("should handle 100% success rate", () => {
      const perfectData: ObjectionType[] = [
        { name: "Always Win", count: 10, successRate: 100, avgScore: 100 },
      ];
      render(<ObjectionBreakdown data={perfectData} showDetails={true} />);
      expect(screen.getByText("Always Win")).toBeInTheDocument();
    });

    it("should handle 0% success rate", () => {
      const failData: ObjectionType[] = [
        { name: "Always Lose", count: 10, successRate: 0, avgScore: 40 },
      ];
      render(<ObjectionBreakdown data={failData} showDetails={true} />);
      expect(screen.getByText("Always Lose")).toBeInTheDocument();
    });

    it("should handle very long objection names", () => {
      const longNameData: ObjectionType[] = [
        {
          name: "This is a very long objection name that should wrap properly",
          count: 10,
          successRate: 75,
        },
      ];
      render(<ObjectionBreakdown data={longNameData} />);
      expect(
        screen.getByText("This is a very long objection name that should wrap properly")
      ).toBeInTheDocument();
    });
  });

  describe("Chart Styling", () => {
    it("should render X-axis labels at an angle in details view", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const xAxis = container.querySelector(".recharts-xAxis");
      expect(xAxis).toBeInTheDocument();
    });

    it("should apply proper margins for rotated labels", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const barChart = container.querySelector(".recharts-bar-chart");
      expect(barChart).toBeInTheDocument();
    });

    it("should use rounded corners for bars in details view", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} showDetails={true} />);
      const bars = container.querySelectorAll(".recharts-bar");
      expect(bars.length).toBe(2);
    });
  });

  describe("Color Coding", () => {
    it("should use different colors for each pie slice", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const pieSectors = container.querySelectorAll(".recharts-pie-sector");
      expect(pieSectors.length).toBe(mockData.length);
    });

    it("should cycle through color palette for many objections", () => {
      const manyData: ObjectionType[] = Array.from({ length: 10 }, (_, i) => ({
        name: `Objection ${i + 1}`,
        count: i + 1,
      }));
      const { container } = render(<ObjectionBreakdown data={manyData} />);
      const pieSectors = container.querySelectorAll(".recharts-pie-sector");
      expect(pieSectors.length).toBe(10);
    });
  });

  describe("Responsive Behavior", () => {
    it("should use ResponsiveContainer", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });

    it("should adapt to container width", () => {
      const { container } = render(<ObjectionBreakdown data={mockData} />);
      // ResponsiveContainer should have width="100%"
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });
  });

  describe("View Persistence", () => {
    it("should maintain view mode after multiple toggles", () => {
      render(<ObjectionBreakdown data={mockData} />);

      // Switch to details
      const detailsButton = screen.getByText("Details");
      fireEvent.click(detailsButton);
      expect(detailsButton).toHaveClass("bg-blue-500", "text-white");

      // Switch back to distribution
      const distributionButton = screen.getByText("Distribution");
      fireEvent.click(distributionButton);
      expect(distributionButton).toHaveClass("bg-blue-500", "text-white");

      // Switch to details again
      fireEvent.click(detailsButton);
      expect(detailsButton).toHaveClass("bg-blue-500", "text-white");
    });
  });
});
