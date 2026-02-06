"use client";

/**
 * CallTimelineCard Component
 *
 * Collapsible card for a call in the opportunity timeline.
 * Lazy loads transcript when expanded.
 */
import { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Phone,
  ChevronDown,
  ChevronUp,
  Clock,
  AlertCircle,
} from "lucide-react";

interface CallDetail {
  id: string;
  gong_call_id: string;
  title: string;
  scheduled_at: string;
  duration: number;
  participants: string[];
  transcript?: string;
  summary?: string;
  metadata?: any;
}

async function fetcher(url: string): Promise<{ call: CallDetail }> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch call details");
  }
  return response.json();
}

interface CallTimelineCardProps {
  callId: string;
  gongCallId: string;
  title: string;
  timestamp: string;
  duration: number;
}

export function CallTimelineCard({
  callId,
  gongCallId,
  title,
  timestamp,
  duration,
}: CallTimelineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Only fetch details when expanded
  const { data, error, isLoading } = useSWR<{ call: CallDetail }>(
    isExpanded ? `/api/calls/${callId}` : null,
    fetcher,
    {
      revalidateOnFocus: false,
    }
  );

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

  const formatTimestamp = (ts: string) => {
    const date = new Date(ts);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  return (
    <Card className="border-l-4 border-l-blue-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="p-2 rounded-full bg-blue-500/10">
              <Phone className="h-4 w-4 text-blue-500" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-foreground">{title}</div>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span>{formatTimestamp(timestamp)}</span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDuration(duration)}
                </span>
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleExpanded}
            className="ml-2"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0 border-t">
          {isLoading ? (
            <div className="space-y-3 pt-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 text-destructive pt-4">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Failed to load call details</span>
            </div>
          ) : data ? (
            <div className="space-y-4 pt-4">
              {/* Participants */}
              {data.call.participants && data.call.participants.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                    Participants
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {data.call.participants.map((participant, i) => (
                      <Badge key={i} variant="outline">
                        {participant}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary */}
              {data.call.summary && (
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                    Summary
                  </div>
                  <p className="text-sm text-foreground">
                    {data.call.summary}
                  </p>
                </div>
              )}

              {/* Transcript Preview */}
              {data.call.transcript && (
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                    Transcript Preview
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <p className="text-sm text-foreground whitespace-pre-wrap">
                      {data.call.transcript.substring(0, 500)}
                      {data.call.transcript.length > 500 && "..."}
                    </p>
                  </div>
                  <Button
                    variant="link"
                    size="sm"
                    className="mt-2"
                    onClick={() =>
                      window.open(`/calls/${callId}`, "_blank")
                    }
                  >
                    View Full Call Analysis
                  </Button>
                </div>
              )}

              {/* Gong Call ID */}
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Gong Call ID: {gongCallId}
              </div>
            </div>
          ) : null}
        </CardContent>
      )}
    </Card>
  );
}
