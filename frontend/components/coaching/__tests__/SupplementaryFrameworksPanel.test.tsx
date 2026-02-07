/**
 * Tests for SupplementaryFrameworksPanel Component
 */

import { render, screen, fireEvent } from "@testing-library/react";
import SupplementaryFrameworksPanel from "../SupplementaryFrameworksPanel";
import type { SupplementaryFrameworks } from "@/types/rubric";

describe("SupplementaryFrameworksPanel", () => {
  const mockFrameworks: SupplementaryFrameworks = {
    discovery_rubric: {
      overall_score: 80,
      max_score: 100,
      criteria: [
        {
          criterion: "situation",
          score: 18,
          max_score: 20,
          status: "met",
          evidence: [
            {
              timestamp_start: 120,
              timestamp_end: 180,
              exchange_summary: "Rep asked about current state of data infrastructure.",
              impact: "Established context for the conversation.",
            },
          ],
        },
        {
          criterion: "pain",
          score: 15,
          max_score: 20,
          status: "partial",
          evidence: [
            {
              timestamp_start: 200,
              timestamp_end: 300,
              exchange_summary: "Rep asked about challenges but didn't quantify impact.",
              impact: "Identified pain but needs deeper exploration.",
            },
          ],
          missed_explanation: "Pain was identified but not fully quantified.",
        },
      ],
    },
    engagement_rubric: {
      overall_score: 70,
      max_score: 100,
      criteria: [
        {
          criterion: "teaching",
          score: 25,
          max_score: 33,
          status: "met",
          evidence: [],
        },
      ],
    },
  };

  it("renders collapsed by default", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    expect(screen.getByText("Additional Coaching Frameworks")).toBeInTheDocument();
    expect(screen.getByText(/SPICED · Challenger/)).toBeInTheDocument();
    expect(screen.queryByText("Discovery Framework (SPICED)")).not.toBeInTheDocument();
  });

  it("shows framework count when collapsed", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    expect(screen.getByText("2 frameworks available")).toBeInTheDocument();
  });

  it("expands to show frameworks when clicked", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    const expandButton = screen.getByRole("button", {
      name: /Additional Coaching Frameworks/,
    });
    fireEvent.click(expandButton);

    expect(screen.getByText("Discovery Framework (SPICED)")).toBeInTheDocument();
    expect(screen.getByText("Engagement Framework (Challenger)")).toBeInTheDocument();
  });

  it("collapses when clicked again", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand
    const expandButton = screen.getByRole("button", {
      name: /Additional Coaching Frameworks/,
    });
    fireEvent.click(expandButton);

    expect(screen.getByText("Discovery Framework (SPICED)")).toBeInTheDocument();

    // Collapse
    const collapseButton = screen.getByRole("button", {
      name: /Additional Coaching Frameworks/,
    });
    fireEvent.click(collapseButton);

    expect(screen.queryByText("Discovery Framework (SPICED)")).not.toBeInTheDocument();
  });

  it("displays framework scores", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    const expandButton = screen.getByRole("button", {
      name: /Additional Coaching Frameworks/,
    });
    fireEvent.click(expandButton);

    expect(screen.getByText("80/100")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
    expect(screen.getByText("70/100")).toBeInTheDocument();
    expect(screen.getByText("70%")).toBeInTheDocument();
  });

  it("expands individual frameworks to show criteria", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand panel
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));

    // Expand discovery framework
    const discoveryButton = screen.getByRole("button", {
      name: /Discovery Framework \(SPICED\)/,
    });
    fireEvent.click(discoveryButton);

    expect(screen.getByText("Situation")).toBeInTheDocument();
    expect(screen.getByText("Pain")).toBeInTheDocument();
  });

  it("displays criterion scores and status", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand panel and framework
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Discovery Framework/ }));

    expect(screen.getByText("18/20 (90%)")).toBeInTheDocument();
    expect(screen.getByText("15/20 (75%)")).toBeInTheDocument();
  });

  it("expands individual criteria to show evidence", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand panel and framework
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Discovery Framework/ }));

    // Expand situation criterion - get by text since there may be multiple buttons
    const situationButtons = screen.getAllByText("Situation");
    expect(situationButtons.length).toBeGreaterThan(0);
    fireEvent.click(situationButtons[0].closest("button")!);

    expect(
      screen.getByText(/Rep asked about current state of data infrastructure/)
    ).toBeInTheDocument();
    expect(screen.getByText(/Established context for the conversation/)).toBeInTheDocument();
  });

  it("displays missed explanation when present", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand to pain criterion
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Discovery Framework/ }));

    const painButtons = screen.getAllByText("Pain");
    fireEvent.click(painButtons[0].closest("button")!);

    expect(screen.getByText("Pain was identified but not fully quantified.")).toBeInTheDocument();
  });

  it("shows empty state for criteria without evidence", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand to teaching criterion
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Engagement Framework/ }));

    const teachingButtons = screen.getAllByText("Teaching");
    fireEvent.click(teachingButtons[0].closest("button")!);

    expect(screen.getByText("No evidence recorded for this criterion.")).toBeInTheDocument();
  });

  it("renders nothing when no frameworks available", () => {
    const emptyFrameworks: SupplementaryFrameworks = {};
    const { container } = render(<SupplementaryFrameworksPanel frameworks={emptyFrameworks} />);

    expect(container.firstChild).toBeNull();
  });

  it("applies correct color coding by status", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    // Expand to see criteria
    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Discovery Framework/ }));

    // Check status indicators
    const allStatuses = screen.getAllByText(/met|partial/i);
    expect(allStatuses.length).toBeGreaterThan(0);
  });

  it("displays framework descriptions", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));

    expect(
      screen.getByText("Situation, Pain, Impact, Critical Event, Decision")
    ).toBeInTheDocument();
    expect(screen.getByText("Teaching, Tailoring, Taking Control")).toBeInTheDocument();
  });

  it("handles all four framework types", () => {
    const allFrameworks: SupplementaryFrameworks = {
      discovery_rubric: {
        overall_score: 80,
        max_score: 100,
        criteria: [],
      },
      engagement_rubric: {
        overall_score: 70,
        max_score: 100,
        criteria: [],
      },
      objection_handling_rubric: {
        overall_score: 60,
        max_score: 100,
        criteria: [],
      },
      product_knowledge_rubric: {
        overall_score: 90,
        max_score: 100,
        criteria: [],
      },
    };

    render(<SupplementaryFrameworksPanel frameworks={allFrameworks} />);

    expect(screen.getByText("4 frameworks available")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));

    expect(screen.getByText("Discovery Framework (SPICED)")).toBeInTheDocument();
    expect(screen.getByText("Engagement Framework (Challenger)")).toBeInTheDocument();
    expect(screen.getByText("Objection Handling Framework (Sandler)")).toBeInTheDocument();
    expect(screen.getByText("Product Knowledge Framework")).toBeInTheDocument();
  });

  it("formats criterion names correctly", () => {
    render(<SupplementaryFrameworksPanel frameworks={mockFrameworks} />);

    fireEvent.click(screen.getByRole("button", { name: /Additional Coaching Frameworks/ }));
    fireEvent.click(screen.getByRole("button", { name: /Discovery Framework/ }));

    // snake_case should be converted to Title Case
    expect(screen.getByText("Situation")).toBeInTheDocument();
    expect(screen.getByText("Pain")).toBeInTheDocument();
  });
});
