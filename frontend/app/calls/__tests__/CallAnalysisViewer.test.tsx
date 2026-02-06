import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { CallAnalysisViewer } from "../[callId]/CallAnalysisViewer";
import * as hooks from "@/lib/hooks";

// Mock the useCallAnalysis hook
jest.mock("@/lib/hooks", () => ({
  useCallAnalysis: jest.fn(),
}));

// Mock child components
jest.mock("@/components/ui/button", () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
}));

jest.mock("@/components/coaching/ScoreCard", () => ({
  ScoreCard: ({ score, title, subtitle }: any) => (
    <div data-testid="score-card">
      {title}: {score}
      {subtitle && ` - ${subtitle}`}
    </div>
  ),
}));

jest.mock("@/components/coaching/InsightCard", () => ({
  InsightCard: ({ title, strengths, improvements }: any) => (
    <div data-testid="insight-card">
      <h3>{title}</h3>
      {strengths?.map((s: string, i: number) => <div key={i}>Strength: {s}</div>)}
      {improvements?.map((imp: string, i: number) => <div key={i}>Improvement: {imp}</div>)}
    </div>
  ),
}));

jest.mock("@/components/coaching/ActionItem", () => ({
  ActionItem: ({ text, priority }: any) => (
    <div data-testid="action-item">
      {text} (Priority: {priority})
    </div>
  ),
}));

jest.mock("@/components/coaching/EnhancedCallPlayer", () => ({
  EnhancedCallPlayer: ({ gongUrl, duration }: any) => (
    <div data-testid="call-player">
      Player: {gongUrl} - Duration: {duration}s
    </div>
  ),
}));

jest.mock("@/components/coaching/TranscriptSearch", () => ({
  TranscriptSearch: ({ transcript }: any) => (
    <div data-testid="transcript-search">Transcript items: {transcript.length}</div>
  ),
}));

jest.mock("@/components/coaching/ExportCoachingReport", () => ({
  ExportCoachingReport: () => <button>Export Report</button>,
}));

jest.mock("@/components/coaching/ShareLink", () => ({
  ShareLink: () => <button>Share Link</button>,
}));

jest.mock("@/components/coaching/CoachingSessionFeedback", () => ({
  CoachingSessionFeedback: ({ callId }: any) => <div>Feedback for {callId}</div>,
}));

jest.mock("@/components/RubricBadge", () => ({
  RubricBadge: ({ role }: any) => <div>Rubric: {role}</div>,
}));

describe("CallAnalysisViewer", () => {
  const mockCallId = "call-123";
  const mockUserRole = "rep";

  const mockAnalysis = {
    call_metadata: {
      title: "Sales Call with Acme Corp",
      date: "2026-01-15T10:00:00Z",
      duration_seconds: 1800,
      call_type: "Discovery",
      participants: [
        { name: "John Doe", email: "john@example.com", role: "Rep" },
        { name: "Jane Smith", email: "jane@acme.com", role: "Prospect" },
      ],
      gong_url: "https://gong.io/call/123",
      recording_url: "https://example.com/recording.mp3",
    },
    scores: {
      overall: 85,
      product_knowledge: 88,
      discovery: 82,
      objection_handling: 80,
      engagement: 90,
    },
    strengths: ["Excellent rapport building", "Strong product knowledge"],
    areas_for_improvement: ["Ask more discovery questions", "Handle objections earlier"],
    dimension_details: {
      product_knowledge: {
        strengths: ["Knew all product features"],
        improvements: ["Could mention pricing tiers"],
      },
      discovery: {
        strengths: ["Asked about budget"],
        improvements: ["Dig deeper into pain points"],
      },
    },
    transcript: [
      { timestamp: 0, speaker: "Rep", text: "Hello, how are you?" },
      { timestamp: 5, speaker: "Prospect", text: "I'm good, thanks." },
    ],
    action_items: ["Follow up with pricing proposal", "Schedule demo for next week"],
    specific_examples: {
      good: ["Great opening question"],
      needs_work: ["Missed opportunity to address pricing concern"],
    },
    rep_analyzed: {
      evaluated_as_role: "AE",
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Loading State", () => {
    it("should render loading skeletons when data is loading", () => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: undefined,
        error: undefined,
        isLoading: true,
        mutate: jest.fn(),
      });

      const { container } = render(
        <CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />
      );

      // Check for skeleton loaders
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it("should render metadata skeleton", () => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: undefined,
        error: undefined,
        isLoading: true,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      // Metadata section should have skeleton
      const skeletons = document.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe("Error State", () => {
    it("should render error message when error occurs", () => {
      const mockError = { message: "Failed to load analysis" };
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: undefined,
        error: mockError,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      expect(screen.getByText("Failed to Load Analysis")).toBeInTheDocument();
      expect(screen.getByText(mockError.message)).toBeInTheDocument();
    });

    it("should render retry button on error", () => {
      const mockMutate = jest.fn();
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: undefined,
        error: { message: "Network error" },
        isLoading: false,
        mutate: mockMutate,
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      const retryButton = screen.getByText("Retry");
      expect(retryButton).toBeInTheDocument();
    });

    it("should call mutate when retry button is clicked", () => {
      const mockMutate = jest.fn();
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: undefined,
        error: { message: "Network error" },
        isLoading: false,
        mutate: mockMutate,
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      const retryButton = screen.getByText("Retry");
      fireEvent.click(retryButton);

      expect(mockMutate).toHaveBeenCalledTimes(1);
    });
  });

  describe("Not Analyzed State", () => {
    it("should show analyze button when analysis is null", () => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: null,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      expect(screen.getByText("Call Not Yet Analyzed")).toBeInTheDocument();
      expect(screen.getByText("Analyze This Call")).toBeInTheDocument();
    });

    it("should call mutate when analyze button is clicked", () => {
      const mockMutate = jest.fn();
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: null,
        error: undefined,
        isLoading: false,
        mutate: mockMutate,
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      const analyzeButton = screen.getByText("Analyze This Call");
      fireEvent.click(analyzeButton);

      expect(mockMutate).toHaveBeenCalledTimes(1);
    });
  });

  describe("Call Metadata Display", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render call title", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Sales Call with Acme Corp")).toBeInTheDocument();
    });

    it("should render call date", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Date")).toBeInTheDocument();
    });

    it("should render call duration", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Duration")).toBeInTheDocument();
      expect(screen.getByText("30m 0s")).toBeInTheDocument(); // 1800 seconds = 30 minutes
    });

    it("should render call type", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Type")).toBeInTheDocument();
      expect(screen.getByText("Discovery")).toBeInTheDocument();
    });

    it("should render participant count", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Participants")).toBeInTheDocument();
      expect(screen.getByText("2 people")).toBeInTheDocument();
    });

    it("should render participant details", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    });
  });

  describe("Score Display", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render overall score", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText(/Overall Score.*85/)).toBeInTheDocument();
    });

    it("should render all dimension scores", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText(/Product Knowledge.*88/)).toBeInTheDocument();
      expect(screen.getByText(/Discovery.*82/)).toBeInTheDocument();
      expect(screen.getByText(/Objection Handling.*80/)).toBeInTheDocument();
      expect(screen.getByText(/Engagement.*90/)).toBeInTheDocument();
    });

    it("should not render null scores", () => {
      const analysisWithNullScores = {
        ...mockAnalysis,
        scores: {
          ...mockAnalysis.scores,
          product_knowledge: null,
        },
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: analysisWithNullScores,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.queryByText(/Product Knowledge/)).not.toBeInTheDocument();
    });
  });

  describe("Insights Display", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render strengths section", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Strengths")).toBeInTheDocument();
      expect(screen.getByText(/Strength:.*Excellent rapport building/)).toBeInTheDocument();
    });

    it("should render improvements section", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Areas for Improvement")).toBeInTheDocument();
      expect(screen.getByText(/Improvement:.*Ask more discovery questions/)).toBeInTheDocument();
    });

    it("should render dimension details", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Dimension Details")).toBeInTheDocument();
      expect(screen.getByText("Product Knowledge")).toBeInTheDocument();
      expect(screen.getByText("Discovery")).toBeInTheDocument();
    });
  });

  describe("Transcript Display", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render transcript when available", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Transcript & Search")).toBeInTheDocument();
      expect(screen.getByTestId("transcript-search")).toBeInTheDocument();
    });

    it("should show not available message when transcript is null", () => {
      const analysisWithoutTranscript = {
        ...mockAnalysis,
        transcript: null,
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: analysisWithoutTranscript,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Transcript not available for this call")).toBeInTheDocument();
    });

    it("should display specific examples when transcript is unavailable", () => {
      const analysisWithExamples = {
        ...mockAnalysis,
        transcript: null,
        specific_examples: {
          good: ["Great opening question"],
          needs_work: ["Missed pricing concern"],
        },
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: analysisWithExamples,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Excellent Moments")).toBeInTheDocument();
      expect(screen.getByText("Moments to Improve")).toBeInTheDocument();
    });
  });

  describe("Action Items Display", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render action items section", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Action Items")).toBeInTheDocument();
    });

    it("should render all action items", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(
        screen.getByText(/Follow up with pricing proposal.*Priority: high/)
      ).toBeInTheDocument();
      expect(screen.getByText(/Schedule demo for next week.*Priority: high/)).toBeInTheDocument();
    });

    it("should not render action items section when none exist", () => {
      const analysisWithoutActions = {
        ...mockAnalysis,
        action_items: [],
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: analysisWithoutActions,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.queryByText("Action Items")).not.toBeInTheDocument();
    });
  });

  describe("Call Player", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render call player with correct props", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      const player = screen.getByTestId("call-player");
      expect(player).toBeInTheDocument();
      expect(player.textContent).toContain("https://gong.io/call/123");
      expect(player.textContent).toContain("1800s");
    });
  });

  describe("Rubric Badge", () => {
    it("should display rubric badge when evaluated_as_role is present", () => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Rubric: AE")).toBeInTheDocument();
    });

    it("should not display rubric badge when evaluated_as_role is missing", () => {
      const analysisWithoutRole = {
        ...mockAnalysis,
        rep_analyzed: {},
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: analysisWithoutRole,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.queryByText(/Rubric:/)).not.toBeInTheDocument();
    });
  });

  describe("Action Buttons", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render back to dashboard button", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Back to Dashboard")).toBeInTheDocument();
    });

    it("should render refresh button", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Refresh")).toBeInTheDocument();
    });

    it("should render export report button", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Export Report")).toBeInTheDocument();
    });

    it("should render share link button", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Share Link")).toBeInTheDocument();
    });

    it("should call mutate when refresh button is clicked", () => {
      const mockMutate = jest.fn();
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: mockMutate,
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);

      const refreshButton = screen.getByText("Refresh");
      fireEvent.click(refreshButton);

      expect(mockMutate).toHaveBeenCalledTimes(1);
    });
  });

  describe("Coaching Feedback", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render coaching feedback component", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText(`Feedback for ${mockCallId}`)).toBeInTheDocument();
    });
  });

  describe("Responsive Layout", () => {
    beforeEach(() => {
      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: mockAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });
    });

    it("should render with proper spacing classes", () => {
      const { container } = render(
        <CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />
      );
      const mainContainer = container.querySelector(".space-y-6");
      expect(mainContainer).toBeInTheDocument();
    });

    it("should use grid layout for score cards", () => {
      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Performance Scores")).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle analysis with minimal data", () => {
      const minimalAnalysis = {
        call_metadata: {
          title: "Test Call",
          date: null,
          duration_seconds: 0,
          call_type: null,
          participants: [],
          gong_url: null,
          recording_url: null,
        },
        scores: {
          overall: 75,
        },
        strengths: [],
        areas_for_improvement: [],
        transcript: null,
        action_items: [],
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: minimalAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("Test Call")).toBeInTheDocument();
      expect(screen.getByText(/Overall Score.*75/)).toBeInTheDocument();
    });

    it("should handle very long call titles", () => {
      const longTitleAnalysis = {
        ...mockAnalysis,
        call_metadata: {
          ...mockAnalysis.call_metadata,
          title: "This is a very long call title that should wrap properly on all devices",
        },
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: longTitleAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(
        screen.getByText("This is a very long call title that should wrap properly on all devices")
      ).toBeInTheDocument();
    });

    it("should handle many participants", () => {
      const manyParticipantsAnalysis = {
        ...mockAnalysis,
        call_metadata: {
          ...mockAnalysis.call_metadata,
          participants: Array.from({ length: 10 }, (_, i) => ({
            name: `Person ${i + 1}`,
            email: `person${i + 1}@example.com`,
            role: i % 2 === 0 ? "Rep" : "Prospect",
          })),
        },
      };

      (hooks.useCallAnalysis as jest.Mock).mockReturnValue({
        data: manyParticipantsAnalysis,
        error: undefined,
        isLoading: false,
        mutate: jest.fn(),
      });

      render(<CallAnalysisViewer callId={mockCallId} userRole={mockUserRole} />);
      expect(screen.getByText("10 people")).toBeInTheDocument();
      expect(screen.getByText("Person 1")).toBeInTheDocument();
      expect(screen.getByText("Person 10")).toBeInTheDocument();
    });
  });
});
