import { render, screen, within } from "@testing-library/react";
import { ActivityTimeline, ActivityDay } from "../ActivityTimeline";

describe("ActivityTimeline", () => {
  const mockData: ActivityDay[] = [
    { date: "2026-01-01", count: 3, isHighActivity: false },
    { date: "2026-01-02", count: 5, isHighActivity: false },
    { date: "2026-01-03", count: 0, isHighActivity: false },
    { date: "2026-01-04", count: 8, isHighActivity: true },
    { date: "2026-01-05", count: 2, isHighActivity: false },
    { date: "2026-01-06", count: 10, isHighActivity: true },
    { date: "2026-01-07", count: 4, isHighActivity: false },
  ];

  describe("Rendering with Props", () => {
    it("should render activity timeline with data", () => {
      render(<ActivityTimeline data={mockData} />);
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
    });

    it("should display title based on metric", () => {
      render(<ActivityTimeline data={mockData} metric="calls" />);
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
    });

    it("should display coaching sessions title when metric is coachingSessions", () => {
      render(<ActivityTimeline data={mockData} metric="coachingSessions" />);
      expect(screen.getByText("Coaching Sessions Timeline")).toBeInTheDocument();
    });

    it("should apply custom className", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} className="custom-timeline" />
      );
      expect(container.firstChild).toHaveClass("custom-timeline");
    });
  });

  describe("Empty State", () => {
    it("should show placeholder when data is empty", () => {
      render(<ActivityTimeline data={[]} />);
      expect(screen.getByText("No activity data available")).toBeInTheDocument();
    });

    it("should show placeholder when data is null", () => {
      render(<ActivityTimeline data={null as any} />);
      expect(screen.getByText("No activity data available")).toBeInTheDocument();
    });

    it("should render placeholder in a card", () => {
      const { container } = render(<ActivityTimeline data={[]} />);
      const placeholder = screen.getByText("No activity data available").closest("div");
      expect(placeholder).toHaveClass("h-40");
    });
  });

  describe("Date Range", () => {
    it("should use last 12 weeks by default when no dates provided", () => {
      const { container } = render(<ActivityTimeline data={mockData} />);
      // Should render calendar grid
      expect(container.querySelector(".overflow-x-auto")).toBeInTheDocument();
    });

    it("should use provided startDate and endDate", () => {
      render(<ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-31" />);
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
    });

    it("should handle single day range", () => {
      const singleDayData: ActivityDay[] = [{ date: "2026-01-01", count: 5 }];
      render(<ActivityTimeline data={singleDayData} startDate="2026-01-01" endDate="2026-01-01" />);
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
    });
  });

  describe("Calendar Grid", () => {
    it("should render day labels", () => {
      render(<ActivityTimeline data={mockData} />);
      expect(screen.getByText("Sun")).toBeInTheDocument();
      expect(screen.getByText("Mon")).toBeInTheDocument();
      expect(screen.getByText("Tue")).toBeInTheDocument();
      expect(screen.getByText("Wed")).toBeInTheDocument();
      expect(screen.getByText("Thu")).toBeInTheDocument();
      expect(screen.getByText("Fri")).toBeInTheDocument();
      expect(screen.getByText("Sat")).toBeInTheDocument();
    });

    it("should render month labels", () => {
      const janData: ActivityDay[] = [
        { date: "2026-01-01", count: 3 },
        { date: "2026-01-15", count: 5 },
      ];
      render(<ActivityTimeline data={janData} startDate="2026-01-01" endDate="2026-01-31" />);
      expect(screen.getByText("Jan")).toBeInTheDocument();
    });

    it("should organize days by week", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-31" />
      );
      // Should have multiple week columns
      const weeks = container.querySelectorAll(".flex.flex-col");
      expect(weeks.length).toBeGreaterThan(0);
    });

    it("should render individual day cells", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-07" />
      );
      // Should have day cells with border and rounded corners
      const dayCells = container.querySelectorAll(".w-5.h-5");
      expect(dayCells.length).toBeGreaterThan(0);
    });
  });

  describe("Activity Color Coding", () => {
    it("should use gray for zero activity days", () => {
      const zeroActivityData: ActivityDay[] = [{ date: "2026-01-01", count: 0 }];
      const { container } = render(
        <ActivityTimeline data={zeroActivityData} startDate="2026-01-01" endDate="2026-01-01" />
      );
      const dayCell = container.querySelector(".bg-gray-100");
      expect(dayCell).toBeInTheDocument();
    });

    it("should use blue shades for activity levels", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-07" />
      );
      // Should have various blue shades based on activity intensity
      const blueCells = container.querySelectorAll('[class*="bg-blue"]');
      expect(blueCells.length).toBeGreaterThan(0);
    });

    it("should use darker blue for higher activity", () => {
      const highActivityData: ActivityDay[] = [
        { date: "2026-01-01", count: 1 },
        { date: "2026-01-02", count: 10 },
      ];
      const { container } = render(
        <ActivityTimeline data={highActivityData} startDate="2026-01-01" endDate="2026-01-02" />
      );
      // Should have different shades
      const cells = container.querySelectorAll('[class*="bg-blue"]');
      expect(cells.length).toBeGreaterThan(0);
    });
  });

  describe("High Activity Highlighting", () => {
    it("should highlight high activity days with ring", () => {
      const highActivityData: ActivityDay[] = [
        { date: "2026-01-01", count: 10, isHighActivity: true },
      ];
      const { container } = render(
        <ActivityTimeline data={highActivityData} startDate="2026-01-01" endDate="2026-01-01" />
      );
      // High activity should have orange ring
      const ringElement = container.querySelector(".ring-2.ring-orange-400");
      expect(ringElement).toBeInTheDocument();
    });

    it("should not highlight normal activity days", () => {
      const normalActivityData: ActivityDay[] = [
        { date: "2026-01-01", count: 3, isHighActivity: false },
      ];
      const { container } = render(
        <ActivityTimeline data={normalActivityData} startDate="2026-01-01" endDate="2026-01-01" />
      );
      // Should not have ring
      const ringElement = container.querySelector(".ring-2.ring-orange-400");
      expect(ringElement).not.toBeInTheDocument();
    });
  });

  describe("Legend", () => {
    it("should render legend with color scale", () => {
      render(<ActivityTimeline data={mockData} />);
      expect(screen.getByText("Less")).toBeInTheDocument();
      expect(screen.getByText("More")).toBeInTheDocument();
    });

    it("should show five color intensity levels in legend", () => {
      const { container } = render(<ActivityTimeline data={mockData} />);
      // Legend should have 5 color boxes
      const legendBoxes = container.querySelectorAll(".w-4.h-4");
      expect(legendBoxes.length).toBeGreaterThanOrEqual(5);
    });
  });

  describe("Summary Statistics", () => {
    it("should display total activity count", () => {
      render(<ActivityTimeline data={mockData} />);
      const total = mockData.reduce((sum, d) => sum + d.count, 0);
      expect(screen.getByText("Total Activity")).toBeInTheDocument();
      expect(screen.getByText(total.toString())).toBeInTheDocument();
    });

    it("should display average per day", () => {
      render(<ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-07" />);
      expect(screen.getByText("Average per Day")).toBeInTheDocument();
    });

    it("should display peak activity", () => {
      render(<ActivityTimeline data={mockData} />);
      const maxActivity = Math.max(...mockData.map((d) => d.count));
      expect(screen.getByText("Peak Activity")).toBeInTheDocument();
      expect(screen.getByText(maxActivity.toString())).toBeInTheDocument();
    });

    it("should calculate correct average", () => {
      const testData: ActivityDay[] = [
        { date: "2026-01-01", count: 4 },
        { date: "2026-01-02", count: 6 },
        { date: "2026-01-03", count: 8 },
      ];
      render(<ActivityTimeline data={testData} startDate="2026-01-01" endDate="2026-01-03" />);
      // Average should be (4+6+8)/3 = 6
      expect(screen.getByText("6")).toBeInTheDocument();
    });
  });

  describe("Hover Interaction", () => {
    it("should add hover effect to day cells", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-07" />
      );
      const dayCells = container.querySelectorAll(".hover\\:border-gray-500");
      expect(dayCells.length).toBeGreaterThan(0);
    });

    it("should display tooltip title with date and count", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-01-07" />
      );
      // Day cells should have title attribute
      const dayCell = container.querySelector('[title*="2026-01-01"]');
      expect(dayCell).toBeInTheDocument();
    });
  });

  describe("Metric Display", () => {
    it("should show calls in tooltip when metric is calls", () => {
      const { container } = render(<ActivityTimeline data={mockData} metric="calls" />);
      const cellWithTitle = container.querySelector('[title*="calls"]');
      expect(cellWithTitle).toBeInTheDocument();
    });

    it("should show coachingSessions in tooltip when metric is coachingSessions", () => {
      const { container } = render(<ActivityTimeline data={mockData} metric="coachingSessions" />);
      const cellWithTitle = container.querySelector('[title*="coachingSessions"]');
      expect(cellWithTitle).toBeInTheDocument();
    });
  });

  describe("Card Styling", () => {
    it("should render inside a Card component", () => {
      const { container } = render(<ActivityTimeline data={mockData} />);
      // Card should have padding and rounded corners
      const card = container.querySelector(".p-6");
      expect(card).toBeInTheDocument();
    });

    it("should have scrollable overflow for large date ranges", () => {
      const { container } = render(<ActivityTimeline data={mockData} />);
      const scrollContainer = container.querySelector(".overflow-x-auto");
      expect(scrollContainer).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle single day of activity", () => {
      const singleDay: ActivityDay[] = [{ date: "2026-01-01", count: 5 }];
      render(<ActivityTimeline data={singleDay} startDate="2026-01-01" endDate="2026-01-01" />);
      expect(screen.getByText("Total Activity")).toBeInTheDocument();
      expect(screen.getByText("5")).toBeInTheDocument();
    });

    it("should handle all zero activity days", () => {
      const zeroData: ActivityDay[] = [
        { date: "2026-01-01", count: 0 },
        { date: "2026-01-02", count: 0 },
        { date: "2026-01-03", count: 0 },
      ];
      render(<ActivityTimeline data={zeroData} startDate="2026-01-01" endDate="2026-01-03" />);
      expect(screen.getByText("0")).toBeInTheDocument();
      expect(screen.getByText("Peak Activity")).toBeInTheDocument();
    });

    it("should handle very high activity counts", () => {
      const highData: ActivityDay[] = [{ date: "2026-01-01", count: 100 }];
      render(<ActivityTimeline data={highData} startDate="2026-01-01" endDate="2026-01-01" />);
      expect(screen.getByText("100")).toBeInTheDocument();
    });

    it("should handle sparse activity data", () => {
      const sparseData: ActivityDay[] = [
        { date: "2026-01-01", count: 5 },
        { date: "2026-01-15", count: 3 },
      ];
      render(<ActivityTimeline data={sparseData} startDate="2026-01-01" endDate="2026-01-31" />);
      // Should still render full calendar with gaps
      expect(screen.getByText("Total Activity")).toBeInTheDocument();
    });

    it("should handle leap year dates", () => {
      const leapYearData: ActivityDay[] = [{ date: "2024-02-29", count: 5 }];
      render(<ActivityTimeline data={leapYearData} startDate="2024-02-29" endDate="2024-02-29" />);
      expect(screen.getByText("5")).toBeInTheDocument();
    });

    it("should handle year transitions", () => {
      const yearTransitionData: ActivityDay[] = [
        { date: "2025-12-30", count: 3 },
        { date: "2025-12-31", count: 5 },
        { date: "2026-01-01", count: 4 },
      ];
      render(
        <ActivityTimeline data={yearTransitionData} startDate="2025-12-30" endDate="2026-01-01" />
      );
      expect(screen.getByText("Dec")).toBeInTheDocument();
      expect(screen.getByText("Jan")).toBeInTheDocument();
    });
  });

  describe("Data Mapping", () => {
    it("should correctly map dates to activity counts", () => {
      const specificData: ActivityDay[] = [
        { date: "2026-01-05", count: 7 },
        { date: "2026-01-06", count: 9 },
      ];
      const { container } = render(
        <ActivityTimeline data={specificData} startDate="2026-01-05" endDate="2026-01-06" />
      );
      // Dates should be mapped correctly
      const dayCells = container.querySelectorAll('[title*="2026-01-05"]');
      expect(dayCells[0]).toHaveAttribute("title", "2026-01-05: 7 calls");
    });

    it("should show zero for unmapped dates in range", () => {
      const partialData: ActivityDay[] = [{ date: "2026-01-01", count: 5 }];
      const { container } = render(
        <ActivityTimeline data={partialData} startDate="2026-01-01" endDate="2026-01-07" />
      );
      // Days without data should show 0
      const zeroDayCell = container.querySelector('[title*="2026-01-02"]');
      expect(zeroDayCell).toHaveAttribute("title", "2026-01-02: 0 calls");
    });
  });

  describe("Responsive Design", () => {
    it("should have full width", () => {
      const { container } = render(<ActivityTimeline data={mockData} />);
      const wrapper = container.querySelector(".w-full");
      expect(wrapper).toBeInTheDocument();
    });

    it("should maintain structure with many weeks", () => {
      const { container } = render(
        <ActivityTimeline data={mockData} startDate="2026-01-01" endDate="2026-12-31" />
      );
      // Should render without breaking layout
      expect(container.querySelector(".overflow-x-auto")).toBeInTheDocument();
    });
  });
});
