import { CalendarDays, Clock, Users, VideoIcon } from "lucide-react";
import type { CallMetadata } from "@/types/coaching";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CallMetadataHeaderProps {
  metadata: CallMetadata;
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

function formatDate(dateString: string | null): string {
  if (!dateString) return "Unknown date";

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "Unknown date";
  }
}

function calculateTalkTimePercentage(
  talkTimeSeconds: number,
  totalDuration: number
): number {
  if (totalDuration === 0) return 0;
  return Math.round((talkTimeSeconds / totalDuration) * 100);
}

export function CallMetadataHeader({ metadata }: CallMetadataHeaderProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl">{metadata.title}</CardTitle>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <CalendarDays className="h-4 w-4" />
                <span>{formatDate(metadata.date)}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{formatDuration(metadata.duration_seconds)}</span>
              </div>
              {metadata.call_type && (
                <div className="flex items-center gap-1">
                  <VideoIcon className="h-4 w-4" />
                  <span className="capitalize">
                    {metadata.call_type.replace(/_/g, " ")}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-semibold text-sm">Participants</h4>
          </div>
          <div className="grid gap-2">
            {metadata.participants.map((participant, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/50"
              >
                <div className="flex items-center gap-3">
                  <div>
                    <p className="font-medium text-sm">{participant.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {participant.role}
                      {participant.is_internal ? " (Internal)" : " (External)"}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">
                    {calculateTalkTimePercentage(
                      participant.talk_time_seconds,
                      metadata.duration_seconds
                    )}
                    %
                  </p>
                  <p className="text-xs text-muted-foreground">talk time</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
