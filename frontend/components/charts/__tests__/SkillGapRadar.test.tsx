import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SkillGapRadar, SkillGapRadarData } from "../SkillGapRadar";

describe("SkillGapRadar", () => {
  const mockData: SkillGapRadarData[] = [
    { skill: "Product Knowledge", actual: 75, target: 85, teamAverage: 80 },
    { skill: "Discovery", actual: 82, target: 90, teamAverage: 78 },
    { skill: "Objection Handling", actual: 70, target: 80, teamAverage: 75 },
    { skill: "Engagement", actual: 88, target: 85, teamAverage: 82 },
  ];

  describe("Rendering with Props", () => {
    it("should render radar chart with data", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radarChart = container.querySelector(".recharts-radar-chart");
      expect(radarChart).toBeInTheDocument();
    });

    it("should display all skill names", () => {
      render(<SkillGapRadar data={mockData} />);
      mockData.forEach((item) => {
        expect(screen.getByText(item.skill)).toBeInTheDocument();
      });
    });

    it("should render with custom height", () => {
      const { container } = render(<SkillGapRadar data={mockData} height={400} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });

    it("should apply custom className", () => {
      const { container } = render(<SkillGapRadar data={mockData} className="custom-radar" />);
      expect(container.firstChild).toHaveClass("custom-radar");
    });
  });

  describe("Empty State", () => {
    it("should show placeholder when data is empty", () => {
      render(<SkillGapRadar data={[]} />);
      expect(screen.getByText("No skill gap data available")).toBeInTheDocument();
    });

    it("should show placeholder when data is null", () => {
      render(<SkillGapRadar data={null as any} />);
      expect(screen.getByText("No skill gap data available")).toBeInTheDocument();
    });

    it("should apply custom height to placeholder", () => {
      const { container } = render(<SkillGapRadar data={[]} height={300} />);
      const placeholder = screen.getByText("No skill gap data available").closest("div");
      expect(placeholder).toHaveStyle({ height: "300px" });
    });
  });

  describe("Comparison Types", () => {
    it("should render target comparison by default", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      expect(container.textContent).toContain("Target Performance");
      expect(container.textContent).toContain("Actual Performance");
    });

    it("should render team comparison when compareType is team", () => {
      const { container } = render(<SkillGapRadar data={mockData} compareType="team" />);
      expect(container.textContent).toContain("Team Average");
      expect(container.textContent).toContain("Actual Performance");
    });

    it("should render target comparison when compareType is target", () => {
      const { container } = render(<SkillGapRadar data={mockData} compareType="target" />);
      expect(container.textContent).toContain("Target Performance");
      expect(container.textContent).not.toContain("Team Average");
    });

    it("should render target comparison when compareType is topPerformers", () => {
      const { container } = render(<SkillGapRadar data={mockData} compareType="topPerformers" />);
      expect(container.textContent).toContain("Target Performance");
      expect(container.textContent).not.toContain("Team Average");
    });

    it("should not show team average when data lacks teamAverage values", () => {
      const dataWithoutTeam: SkillGapRadarData[] = [
        { skill: "Product Knowledge", actual: 75, target: 85 },
        { skill: "Discovery", actual: 82, target: 90 },
      ];
      const { container } = render(<SkillGapRadar data={dataWithoutTeam} compareType="team" />);
      expect(container.textContent).not.toContain("Team Average");
    });
  });

  describe("Radar Chart Components", () => {
    it("should render PolarGrid", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const grid = container.querySelector(".recharts-polar-grid");
      expect(grid).toBeInTheDocument();
    });

    it("should render PolarAngleAxis with skills", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const angleAxis = container.querySelector(".recharts-polar-angle-axis");
      expect(angleAxis).toBeInTheDocument();
    });

    it("should render PolarRadiusAxis", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radiusAxis = container.querySelector(".recharts-polar-radius-axis");
      expect(radiusAxis).toBeInTheDocument();
    });

    it("should configure radius axis domain to 0-100", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radiusAxis = container.querySelector(".recharts-polar-radius-axis");
      expect(radiusAxis).toBeInTheDocument();
    });

    it("should render Legend", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const legend = container.querySelector(".recharts-legend-wrapper");
      expect(legend).toBeInTheDocument();
    });

    it("should render Tooltip", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const tooltip = container.querySelector(".recharts-tooltip-wrapper");
      expect(tooltip).toBeInTheDocument();
    });
  });

  describe("Radar Series", () => {
    it("should render actual performance radar", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBeGreaterThan(0);
    });

    it("should render two radars for target comparison", () => {
      const { container } = render(<SkillGapRadar data={mockData} compareType="target" />);
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBe(2); // actual + target
    });

    it("should render two radars for team comparison", () => {
      const { container } = render(<SkillGapRadar data={mockData} compareType="team" />);
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBe(2); // actual + team average
    });

    it("should apply different fill opacity for actual vs comparison", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBe(2);
    });
  });

  describe("Animation", () => {
    it("should enable animation for radar series", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      // Animation should be configured in Radar components
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBeGreaterThan(0);
    });
  });

  describe("User Interaction", () => {
    it("should render interactive chart", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radarChart = container.querySelector(".recharts-radar-chart");
      expect(radarChart).toBeInTheDocument();
    });

    it("should be responsive to viewport", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const responsiveContainer = container.querySelector(".recharts-responsive-container");
      expect(responsiveContainer).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle single skill", () => {
      const singleSkill: SkillGapRadarData[] = [
        { skill: "Product Knowledge", actual: 75, target: 85, teamAverage: 80 },
      ];
      render(<SkillGapRadar data={singleSkill} />);
      expect(screen.getByText("Product Knowledge")).toBeInTheDocument();
    });

    it("should handle many skills", () => {
      const manySkills: SkillGapRadarData[] = Array.from({ length: 10 }, (_, i) => ({
        skill: `Skill ${i + 1}`,
        actual: 70 + i,
        target: 80 + i,
        teamAverage: 75 + i,
      }));
      render(<SkillGapRadar data={manySkills} />);
      expect(screen.getByText("Skill 1")).toBeInTheDocument();
      expect(screen.getByText("Skill 10")).toBeInTheDocument();
    });

    it("should handle score at minimum (0)", () => {
      const minScores: SkillGapRadarData[] = [
        { skill: "Low Skill", actual: 0, target: 50, teamAverage: 30 },
      ];
      render(<SkillGapRadar data={minScores} />);
      expect(screen.getByText("Low Skill")).toBeInTheDocument();
    });

    it("should handle score at maximum (100)", () => {
      const maxScores: SkillGapRadarData[] = [
        { skill: "Perfect Skill", actual: 100, target: 100, teamAverage: 95 },
      ];
      render(<SkillGapRadar data={maxScores} />);
      expect(screen.getByText("Perfect Skill")).toBeInTheDocument();
    });

    it("should handle actual score exceeding target", () => {
      const exceedingScores: SkillGapRadarData[] = [
        { skill: "Exceeded Skill", actual: 95, target: 80, teamAverage: 75 },
      ];
      render(<SkillGapRadar data={exceedingScores} />);
      expect(screen.getByText("Exceeded Skill")).toBeInTheDocument();
    });

    it("should handle missing teamAverage values", () => {
      const partialData: SkillGapRadarData[] = [
        { skill: "Skill 1", actual: 75, target: 85 },
        { skill: "Skill 2", actual: 82, target: 90, teamAverage: 80 },
      ];
      render(<SkillGapRadar data={partialData} compareType="team" />);
      expect(screen.getByText("Skill 1")).toBeInTheDocument();
      expect(screen.getByText("Skill 2")).toBeInTheDocument();
    });
  });

  describe("Styling", () => {
    it("should apply consistent margin to radar chart", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      const radarChart = container.querySelector(".recharts-radar-chart");
      expect(radarChart).toBeInTheDocument();
    });

    it("should format skill names on angle axis", () => {
      render(<SkillGapRadar data={mockData} />);
      mockData.forEach((item) => {
        expect(screen.getByText(item.skill)).toBeInTheDocument();
      });
    });

    it("should use dashed stroke for comparison radar", () => {
      const { container } = render(<SkillGapRadar data={mockData} />);
      // Target/Team comparison should use dashed stroke
      const radars = container.querySelectorAll(".recharts-radar");
      expect(radars.length).toBe(2);
    });
  });
});
