"use client";

import { useEffect, useState } from "react";
import { FeedbackButton } from "./FeedbackButton";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface CoachingSession {
  id: string;
  coaching_dimension: string;
  session_type: string;
  score: number | null;
  created_at: string;
}

interface CoachingSessionFeedbackProps {
  callId: string;
}

export function CoachingSessionFeedback({ callId }: CoachingSessionFeedbackProps) {
  const [sessions, setSessions] = useState<CoachingSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/calls/${callId}/coaching-sessions`);

        if (!response.ok) {
          throw new Error("Failed to fetch coaching sessions");
        }

        const data = await response.json();
        setSessions(data.coaching_sessions || []);
        setError(null);
      } catch (err) {
        console.error("Error fetching coaching sessions:", err);
        setError(err instanceof Error ? err.message : "Failed to load sessions");
      } finally {
        setIsLoading(false);
      }
    };

    if (callId) {
      fetchSessions();
    }
  }, [callId]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Coaching Session Feedback</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="text-red-900">Error Loading Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-800">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (sessions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Coaching Session Feedback</CardTitle>
          <CardDescription>No coaching sessions available for this call</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Coaching Session Feedback</CardTitle>
        <CardDescription>
          Rate the quality of each coaching analysis to help us improve
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sessions.map((session) => (
            <div key={session.id} className="rounded-lg border p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold capitalize">
                    {session.coaching_dimension.replace(/_/g, " ")}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {session.session_type.replace(/_/g, " ")} •{" "}
                    {session.score !== null ? `Score: ${session.score}` : "No score"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(session.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="pt-2">
                <label className="text-sm font-medium block mb-2">
                  How would you rate this coaching feedback?
                </label>
                <FeedbackButton
                  coachingSessionId={session.id}
                  onFeedbackSubmitted={() => {
                    // Optionally refresh data or show success message
                    console.log("Feedback submitted for session", session.id);
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
