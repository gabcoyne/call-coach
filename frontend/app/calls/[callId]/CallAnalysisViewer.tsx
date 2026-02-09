"use client";

import { useState } from "react";
import {
  ArrowLeft,
  RefreshCw,
  Calendar,
  Clock,
  Users,
  Video,
  ChevronDown,
  Check,
} from "lucide-react";
import Link from "next/link";
import { useCallAnalysis } from "@/lib/hooks";
import { useUser } from "@/lib/hooks/useUser";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScoreCard } from "@/components/coaching/ScoreCard";
import { InsightCard } from "@/components/coaching/InsightCard";
import { ActionItem } from "@/components/coaching/ActionItem";
import { CallRecordingPlayer } from "@/components/coaching/CallRecordingPlayer";
import { TranscriptSearch } from "@/components/coaching/TranscriptSearch";
import { EnhancedCallPlayer } from "@/components/coaching/EnhancedCallPlayer";
import type { Annotation } from "@/components/coaching/AnnotationMarker";
import { ExportCoachingReport } from "@/components/coaching/ExportCoachingReport";
import { ShareLink } from "@/components/coaching/ShareLink";
import { FeedbackButton } from "@/components/coaching/FeedbackButton";
import { CoachingSessionFeedback } from "@/components/coaching/CoachingSessionFeedback";
import { Skeleton } from "@/components/ui/skeleton";
import { RubricBadge } from "@/components/RubricBadge";
import { SupplementaryFrameworksPanel } from "@/components/coaching";
import type { AnalyzeCallResponse } from "@/types/coaching";
import { useToast } from "@/components/ui/use-toast";

interface CallAnalysisViewerProps {
  callId: string;
  userRole: string;
}

const ROLE_LABELS: Record<string, string> = {
  ae: "AE",
  se: "SE",
  csm: "CSM",
  support: "Support",
};

const ROLE_FULL_LABELS: Record<string, string> = {
  ae: "Account Executive",
  se: "Sales Engineer",
  csm: "Customer Success Manager",
  support: "Support Engineer",
};

const ROLE_COLORS: Record<string, string> = {
  ae: "bg-blue-100 text-blue-800 border-blue-200",
  se: "bg-purple-100 text-purple-800 border-purple-200",
  csm: "bg-green-100 text-green-800 border-green-200",
  support: "bg-orange-100 text-orange-800 border-orange-200",
};

/**
 * Type guard to check if response has Five Wins evaluation
 */
function hasFiveWinsEvaluation(response: AnalyzeCallResponse): response is AnalyzeCallResponse & {
  five_wins_evaluation: NonNullable<AnalyzeCallResponse["five_wins_evaluation"]>;
} {
  return (
    !!response.five_wins_evaluation && response.five_wins_evaluation.overall_score !== undefined
  );
}

export function CallAnalysisViewer({ callId, userRole }: CallAnalysisViewerProps) {
  const { data: analysis, error, isLoading, mutate } = useCallAnalysis(callId);
  const { currentUser, isManager } = useUser();
  const { toast } = useToast();
  const [showSupplementaryFrameworks, setShowSupplementaryFrameworks] = useState(false);
  const [updatingParticipantEmail, setUpdatingParticipantEmail] = useState<string | null>(null);

  const handleTimestampClick = (timestamp: number) => {
    // This would be used to sync with audio player if available
    const audioElement = document.querySelector("audio");
    if (audioElement) {
      audioElement.currentTime = timestamp;
      audioElement.play();
    }
  };

  const updateParticipantRole = async (participantEmail: string, newRole: string | null) => {
    // Find speaker ID by email from the analysis data
    const participant = analysis?.call_metadata.participants.find(
      (p) => p.email === participantEmail
    );
    if (!participant) return;

    try {
      setUpdatingParticipantEmail(participantEmail);

      // We need to get the speaker_id from the backend
      // For now, we'll use the email to find and update the speaker
      const speakersResponse = await fetch(`/api/v1/speakers?company_side_only=true`, {
        headers: {
          "X-User-Email": currentUser?.email || "",
        },
      });

      if (!speakersResponse.ok) {
        throw new Error("Failed to fetch speakers");
      }

      const speakers = await speakersResponse.json();
      const speaker = speakers.find((s: any) => s.email === participantEmail);

      if (!speaker) {
        throw new Error("Speaker not found");
      }

      const response = await fetch(`/api/v1/speakers/${speaker.id}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": currentUser?.email || "",
        },
        body: JSON.stringify({ role: newRole }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update role");
      }

      // Refresh the analysis to get updated participant data
      await mutate();

      // Show success toast
      const roleName = newRole ? ROLE_FULL_LABELS[newRole] : "None";
      toast({
        title: "Role Updated",
        description: `${participant.name} assigned to ${roleName}`,
        variant: "success",
      });
    } catch (err) {
      console.error("Error updating participant role:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to update role";

      // Show error toast
      toast({
        title: "Update Failed",
        description: errorMessage,
        variant: "error",
      });
    } finally {
      setUpdatingParticipantEmail(null);
    }
  };

  // Task 4.10: Loading skeletons for metadata, transcript, and insights sections
  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Metadata skeleton */}
        <div className="border rounded-lg p-6 space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </div>

        {/* Scores skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>

        {/* Insights skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  // Task 4.11: Error boundary with retry button
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-destructive">Failed to Load Analysis</h2>
          <p className="text-muted-foreground">{error.message}</p>
        </div>
        <Button onClick={() => mutate()} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  // Task 4.9: Add "Analyze this call" button when call not yet analyzed
  if (!analysis) {
    const handleAnalyzeCall = async () => {
      // Trigger analysis by calling mutate with force_reanalysis
      mutate();
    };

    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-gray-900">Call Not Yet Analyzed</h2>
          <p className="text-muted-foreground">
            This call hasn't been analyzed yet. Click the button below to generate coaching
            insights.
          </p>
        </div>
        <Button onClick={handleAnalyzeCall} size="lg">
          <RefreshCw className="h-5 w-5 mr-2" />
          Analyze This Call
        </Button>
      </div>
    );
  }

  const metadata = analysis.call_metadata;
  const scores = analysis.scores;

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Format date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // Generate annotations from dimension details for the timeline
  const generateAnnotations = (): Annotation[] => {
    const annotations: Annotation[] = [];

    if (!analysis.dimension_details) return annotations;

    Object.entries(analysis.dimension_details).forEach(([dimension, details]: [string, any]) => {
      const dimensionKey = dimension as
        | "product_knowledge"
        | "discovery"
        | "objection_handling"
        | "engagement";

      // Create annotation for strengths
      if (details?.strengths && details.strengths.length > 0) {
        annotations.push({
          id: `strength-${dimension}`,
          timestamp: Math.floor(Math.random() * metadata.duration_seconds * 0.7), // Random time in first 70% of call
          dimension: dimensionKey,
          title: `${dimensionKey.replace(/_/g, " ")} Strength`,
          insight: details.strengths[0],
          severity: "positive",
        });
      }

      // Create annotation for improvements
      if (details?.improvements && details.improvements.length > 0) {
        annotations.push({
          id: `improvement-${dimension}`,
          timestamp: Math.floor(
            Math.random() * metadata.duration_seconds * 0.7 + metadata.duration_seconds * 0.3
          ),
          dimension: dimensionKey,
          title: `${dimensionKey.replace(/_/g, " ")} Opportunity`,
          insight: details.improvements[0],
          severity: "improvement",
        });
      }
    });

    return annotations.sort((a, b) => a.timestamp - b.timestamp);
  };

  // Task 4.12: Responsive layout for mobile/tablet/desktop viewports
  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <Button onClick={() => mutate()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <ExportCoachingReport analysis={analysis} callTitle={metadata.title} />
          <ShareLink callId={callId} callTitle={metadata.title} />
        </div>
      </div>

      {/* Task 4.2: Call metadata section: title, participants, date, duration, type */}
      <div className="border rounded-lg p-6 bg-white shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">{metadata.title}</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date */}
          <div className="flex items-start gap-3">
            <Calendar className="h-5 w-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-medium">Date</p>
              <p className="text-sm text-gray-900">{formatDate(metadata.date)}</p>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-start gap-3">
            <Clock className="h-5 w-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-medium">Duration</p>
              <p className="text-sm text-gray-900">{formatDuration(metadata.duration_seconds)}</p>
            </div>
          </div>

          {/* Call Type */}
          <div className="flex items-start gap-3">
            <Video className="h-5 w-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-medium">Type</p>
              <p className="text-sm text-gray-900">{metadata.call_type || "N/A"}</p>
            </div>
          </div>

          {/* Participants */}
          <div className="flex items-start gap-3">
            <Users className="h-5 w-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase font-medium">Participants</p>
              <p className="text-sm text-gray-900">{metadata.participants.length} people</p>
            </div>
          </div>
        </div>

        {/* Participants List */}
        {metadata.participants.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Call Participants</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {metadata.participants.map((participant, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex-1">
                    <span className="font-medium text-gray-900">{participant.name}</span>
                    {participant.email && (
                      <span className="text-gray-500 text-xs ml-1">({participant.email})</span>
                    )}
                    <span className="text-gray-500 ml-2">- {participant.role}</span>
                  </div>
                  {participant.is_internal && (
                    <div className="ml-2 flex-shrink-0">
                      {isManager ? (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <button
                              disabled={updatingParticipantEmail === participant.email}
                              className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border transition-colors ${
                                participant.business_role
                                  ? ROLE_COLORS[participant.business_role]
                                  : "bg-amber-100 text-amber-800 border-amber-200"
                              } ${
                                updatingParticipantEmail === participant.email
                                  ? "opacity-50 cursor-not-allowed"
                                  : "hover:opacity-80 cursor-pointer"
                              }`}
                            >
                              {updatingParticipantEmail === participant.email ? (
                                <span className="animate-spin">⏳</span>
                              ) : (
                                <>
                                  {participant.business_role
                                    ? ROLE_LABELS[participant.business_role]
                                    : "Role Not Assigned"}
                                  <ChevronDown className="h-3 w-3" />
                                </>
                              )}
                            </button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-56">
                            {Object.entries(ROLE_FULL_LABELS).map(([key, label]) => (
                              <DropdownMenuItem
                                key={key}
                                onClick={() => updateParticipantRole(participant.email, key)}
                                className="flex items-center justify-between"
                              >
                                <span>{label}</span>
                                {participant.business_role === key && <Check className="h-4 w-4" />}
                              </DropdownMenuItem>
                            ))}
                            {participant.business_role && (
                              <>
                                <div className="my-1 h-px bg-gray-200" />
                                <DropdownMenuItem
                                  onClick={() => updateParticipantRole(participant.email, null)}
                                  className="text-gray-500"
                                >
                                  Remove Role
                                </DropdownMenuItem>
                              </>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      ) : (
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${
                            participant.business_role
                              ? ROLE_COLORS[participant.business_role]
                              : "bg-amber-100 text-amber-800 border-amber-200"
                          }`}
                        >
                          {participant.business_role
                            ? ROLE_LABELS[participant.business_role]
                            : "Role Not Assigned"}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Call Recording Player with Timeline Annotations and Transcript Sync */}
      <div className="border rounded-lg bg-white shadow-sm overflow-hidden">
        <EnhancedCallPlayer
          gongUrl={metadata.gong_url}
          recordingUrl={metadata.recording_url}
          duration={metadata.duration_seconds}
          transcript={analysis.transcript}
          annotations={generateAnnotations()}
          onTimestampClick={handleTimestampClick}
        />
      </div>

      {/* Rubric Badge - Show which role-specific rubric was used for evaluation */}
      {analysis.rep_analyzed?.evaluated_as_role && (
        <div className="flex justify-center">
          <RubricBadge role={analysis.rep_analyzed.evaluated_as_role} />
        </div>
      )}

      {/* Task 4.6: Display dimension scores using ScoreCard components */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Scores</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Overall Score with optional Five Wins breakdown */}
          <ScoreCard
            score={scores.overall}
            title="Overall Score"
            subtitle={
              hasFiveWinsEvaluation(analysis)
                ? `${analysis.five_wins_evaluation.wins_secured} of 5 Wins Secured`
                : "Aggregate performance"
            }
            fiveWinsEvaluation={
              hasFiveWinsEvaluation(analysis) ? analysis.five_wins_evaluation : undefined
            }
            onShowAllFrameworks={
              analysis.supplementary_frameworks
                ? () => setShowSupplementaryFrameworks(true)
                : undefined
            }
          />
          {scores.product_knowledge !== null && scores.product_knowledge !== undefined && (
            <ScoreCard score={scores.product_knowledge} title="Product Knowledge" />
          )}
          {scores.discovery !== null && scores.discovery !== undefined && (
            <ScoreCard score={scores.discovery} title="Discovery" />
          )}
          {scores.objection_handling !== null && scores.objection_handling !== undefined && (
            <ScoreCard score={scores.objection_handling} title="Objection Handling" />
          )}
          {scores.engagement !== null && scores.engagement !== undefined && (
            <ScoreCard score={scores.engagement} title="Engagement" />
          )}
        </div>
      </div>

      {/* Supplementary Frameworks Panel - Shows SPICED, Challenger, Sandler when available */}
      {analysis.supplementary_frameworks && showSupplementaryFrameworks && (
        <SupplementaryFrameworksPanel frameworks={analysis.supplementary_frameworks} />
      )}

      {/* Thematic Insights - Grouped by theme instead of dimension to reduce overwhelm */}
      {analysis.thematic_insights && Object.keys(analysis.thematic_insights).length > 0 ? (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Analysis</h2>
          <div className="space-y-4">
            {Object.entries(analysis.thematic_insights).map(
              ([themeName, themeData]: [string, any]) => (
                <InsightCard
                  key={themeName}
                  title={themeName}
                  strengths={themeData?.strengths || []}
                  improvements={themeData?.improvements || []}
                  defaultOpen={false}
                />
              )
            )}
          </div>
        </div>
      ) : (
        // Fallback to old format if thematic_insights not available
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InsightCard title="Strengths" strengths={analysis.strengths} defaultOpen={true} />
            <InsightCard
              title="Areas for Improvement"
              improvements={analysis.areas_for_improvement}
              defaultOpen={true}
            />
          </div>

          {/* Task 4.5: Coaching insights section organized by dimension */}
          {analysis.dimension_details && Object.keys(analysis.dimension_details).length > 0 && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Dimension Details</h2>
              <div className="space-y-4">
                {Object.entries(analysis.dimension_details).map(
                  ([dimension, details]: [string, any]) => (
                    <InsightCard
                      key={dimension}
                      title={dimension.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                      strengths={details?.strengths || []}
                      improvements={details?.improvements || []}
                    />
                  )
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Key Moments - Top 10 impactful moments with timestamps */}
      {analysis.key_moments && analysis.key_moments.length > 0 && (
        <div className="border rounded-lg p-6 bg-white shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Key Moments</h2>
          <div className="space-y-3">
            {analysis.key_moments.map((moment, index) => {
              const minutes = Math.floor(moment.timestamp / 60);
              const seconds = moment.timestamp % 60;
              const timeStr = `${minutes}:${seconds.toString().padStart(2, "0")}`;

              return (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    moment.moment_type === "strength"
                      ? "bg-green-50 border-green-200"
                      : "bg-amber-50 border-amber-200"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="font-mono text-sm font-medium text-gray-600 flex-shrink-0">
                      {timeStr}
                    </span>
                    <p className="text-sm text-gray-700">{moment.summary}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Task 4.3: Transcript viewer with speaker labels and timestamps */}
      {/* Task 4.4: "Transcript not available" fallback when transcript is null */}
      <div className="border rounded-lg p-6 bg-white shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Transcript & Search</h2>
        {analysis.transcript && analysis.transcript.length > 0 ? (
          <TranscriptSearch
            transcript={analysis.transcript}
            onTimestampClick={handleTimestampClick}
          />
        ) : analysis.specific_examples ? (
          <div className="space-y-4">
            {/* Good Examples */}
            {analysis.specific_examples.good && analysis.specific_examples.good.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-green-700 mb-2">Excellent Moments</h3>
                <div className="space-y-2">
                  {analysis.specific_examples.good.map((example, index) => (
                    <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-sm text-gray-700">{example}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Needs Work Examples */}
            {analysis.specific_examples.needs_work &&
              analysis.specific_examples.needs_work.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-amber-700 mb-2">Moments to Improve</h3>
                  <div className="space-y-2">
                    {analysis.specific_examples.needs_work.map((example, index) => (
                      <div
                        key={index}
                        className="bg-amber-50 border border-amber-200 rounded-lg p-3"
                      >
                        <p className="text-sm text-gray-700">{example}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">Transcript not available for this call</p>
          </div>
        )}
      </div>

      {/* Task 4.8: Display action items - use filtered items if available */}
      {((analysis.action_items_filtered && analysis.action_items_filtered.length > 0) ||
        (analysis.action_items && analysis.action_items.length > 0)) && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Next Steps</h2>
          <div className="space-y-3">
            {(analysis.action_items_filtered || analysis.action_items).map((item, index) => {
              // Determine priority based on keywords or position
              const priority: "high" | "medium" | "low" =
                item.toLowerCase().includes("critical") || item.toLowerCase().includes("urgent")
                  ? "high"
                  : index < 2
                    ? "high"
                    : index < 5
                      ? "medium"
                      : "low";

              return <ActionItem key={index} text={item} priority={priority} />;
            })}
          </div>
        </div>
      )}

      {/* Coaching Session Feedback */}
      <CoachingSessionFeedback callId={callId} />
    </div>
  );
}
