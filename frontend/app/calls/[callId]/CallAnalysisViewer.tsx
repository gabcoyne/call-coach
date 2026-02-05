"use client";

import { ArrowLeft, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useCallAnalysis } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import {
  CallMetadataHeader,
  OverallScoreBadge,
  DimensionScoreCards,
  StrengthsSection,
  ImprovementSection,
  TranscriptSnippet,
  ActionItemsList,
  CoachingNotes,
  ShareAnalysis,
  ExportPDF,
} from "@/components/call-viewer";

interface CallAnalysisViewerProps {
  callId: string;
  userRole: string;
}

export function CallAnalysisViewer({
  callId,
  userRole,
}: CallAnalysisViewerProps) {
  const { data: analysis, error, isLoading, mutate } = useCallAnalysis(callId);
  const isManager = userRole === "manager";

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="animate-spin h-8 w-8 border-4 border-prefect-blue-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-sm text-muted-foreground">
            Loading call analysis...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-destructive">
            Failed to Load Analysis
          </h2>
          <p className="text-muted-foreground">{error.message}</p>
        </div>
        <Button onClick={() => mutate()} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-muted-foreground">No analysis data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <ExportPDF
            callId={callId}
            callTitle={analysis.call_metadata.title}
          />
          <Button onClick={() => mutate()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Call Metadata */}
      <CallMetadataHeader metadata={analysis.call_metadata} />

      {/* Overall Score and Dimension Scores */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <OverallScoreBadge score={analysis.scores.overall} />
        </div>
        <div className="lg:col-span-2">
          <DimensionScoreCards scores={analysis.scores} />
        </div>
      </div>

      {/* Strengths and Improvements */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StrengthsSection strengths={analysis.strengths} />
        <ImprovementSection improvements={analysis.areas_for_improvement} />
      </div>

      {/* Transcript Snippets */}
      {analysis.specific_examples && (
        <TranscriptSnippet
          examples={analysis.specific_examples}
          callId={callId}
        />
      )}

      {/* Action Items */}
      <ActionItemsList actionItems={analysis.action_items} />

      {/* Manager-Only: Coaching Notes */}
      <CoachingNotes callId={callId} isManager={isManager} />

      {/* Share and Export */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ShareAnalysis callId={callId} />
        <div className="flex items-center justify-center md:justify-end">
          <p className="text-sm text-muted-foreground">
            Analysis generated on{" "}
            {new Date().toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
