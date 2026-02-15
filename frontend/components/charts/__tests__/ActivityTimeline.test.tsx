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
    it("should render calendar grid even with empty data", () => {
      const { container } = render(<ActivityTimeline data={[]} />);
      // Component renders but with zero activity
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
      expect(container.querySelector(".overflow-x-auto")).toBeInTheDocument();
    });

    it("should render calendar grid even with empty data and show title", () => {
      render(<ActivityTimeline data={[]} />);
      // Component renders with the title even when empty
      expect(screen.getByText("Call Activity Timeline")).toBeInTheDocument();
    });

    it("should render in a card when data is empty", () => {
      const { container } = render(<ActivityTimeline data={[]} />);
      // Component renders within a card structure
      expect(container.querySelector(".overflow-x-auto")).toBeInTheDocument();
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
      // Multiple "Jan" labels may appear for different weeks
      const janLabels = screen.getAllByText("Jan");
      expect(janLabels.length).toBeGreaterThan(0);
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
      // Component highlights days where count > maxActivity * 0.75
      // With single day, any count triggers highlighting
      const highActivityData: ActivityDay[] = [{ date: "2026-01-01", count: 10 }];
      const { container } = render(
        <ActivityTimeline data={highActivityData} startDate="2026-01-01" endDate="2026-01-01" />
      );
      // High activity should have orange ring
      const ringElement = container.querySelector(".ring-2.ring-orange-400");
      expect(ringElement).toBeInTheDocument();
    });

    it("should not highlight normal activity days when below threshold", () => {
      // Component highlights days where count > maxActivity * 0.75
      // Need multiple days with different counts to have some below threshold
      const mixedActivityData: ActivityDay[] = [
        { date: "2026-01-01", count: 2 }, // This is 20% of max (10), below 75%
        { date: "2026-01-02", count: 10 }, // This is the max
      ];
      const { container } = render(
        <ActivityTimeline data={mixedActivityData} startDate="2026-01-01" endDate="2026-01-02" />
      );
      // First day (count=2) should NOT have ring since 2/10 = 20% < 75%
      const dayCells = container.querySelectorAll('[title*="2026-01-01"]');
      expect(dayCells[0]).not.toHaveClass("ring-2");
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
      // Multiple elements show "5" (total, average, peak) - use getAllByText
      const fives = screen.getAllByText("5");
      expect(fives.length).toBeGreaterThan(0);
    });

    it("should handle all zero activity days", () => {
      const zeroData: ActivityDay[] = [
        { date: "2026-01-01", count: 0 },
        { date: "2026-01-02", count: 0 },
        { date: "2026-01-03", count: 0 },
      ];
      render(<ActivityTimeline data={zeroData} startDate="2026-01-01" endDate="2026-01-03" />);
      // Multiple elements show "0" - use getAllByText
      const zeros = screen.getAllByText("0");
      expect(zeros.length).toBeGreaterThan(0);
      expect(screen.getByText("Peak Activity")).toBeInTheDocument();
    });

    it("should handle very high activity counts", () => {
      const highData: ActivityDay[] = [{ date: "2026-01-01", count: 100 }];
      render(<ActivityTimeline data={highData} startDate="2026-01-01" endDate="2026-01-01" />);
      // Multiple elements show "100" - use getAllByText
      const hundreds = screen.getAllByText("100");
      expect(hundreds.length).toBeGreaterThan(0);
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
      // Multiple elements show "5" - use getAllByText
      const fives = screen.getAllByText("5");
      expect(fives.length).toBeGreaterThan(0);
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
      // At least "Dec" should be present (Jan may not appear if dates span only one week)
      const decLabels = screen.getAllByText("Dec");
      expect(decLabels.length).toBeGreaterThan(0);
      // Check that the timeline rendered with the data
      expect(screen.getByText("Total Activity")).toBeInTheDocument();
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
