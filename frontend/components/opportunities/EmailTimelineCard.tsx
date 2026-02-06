"use client";

/**
 * EmailTimelineCard Component
 *
 * Collapsible card for an email in the opportunity timeline.
 * Lazy loads email body when expanded.
 */
import { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Mail, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";

interface EmailDetail {
  id: string;
  gong_email_id: string;
  subject: string;
  sender_email: string;
  recipients: string[];
  sent_at: string;
  body_snippet: string;
  metadata?: any;
}

async function fetcher(url: string): Promise<{ email: EmailDetail }> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch email details");
  }
  return response.json();
}

interface EmailTimelineCardProps {
  emailId: string;
  gongEmailId: string;
  subject: string;
  timestamp: string;
  senderEmail: string;
}

export function EmailTimelineCard({
  emailId,
  gongEmailId,
  subject,
  timestamp,
  senderEmail,
}: EmailTimelineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Only fetch details when expanded
  const { data, error, isLoading } = useSWR<{ email: EmailDetail }>(
    isExpanded ? `/api/emails/${emailId}` : null,
    fetcher,
    {
      revalidateOnFocus: false,
    }
  );

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
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
    <Card className="border-l-4 border-l-purple-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="p-2 rounded-full bg-purple-500/10">
              <Mail className="h-4 w-4 text-purple-500" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-foreground">{subject}</div>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span>From: {senderEmail}</span>
                <span>{formatTimestamp(timestamp)}</span>
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
              <span className="text-sm">Failed to load email details</span>
            </div>
          ) : data ? (
            <div className="space-y-4 pt-4">
              {/* Recipients */}
              {data.email.recipients && data.email.recipients.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                    Recipients
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {data.email.recipients.map((recipient, i) => (
                      <Badge key={i} variant="outline">
                        {recipient}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Email Body */}
              {data.email.body_snippet && (
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                    Message
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <p className="text-sm text-foreground whitespace-pre-wrap">
                      {data.email.body_snippet}
                    </p>
                  </div>
                </div>
              )}

              {/* Gong Email ID */}
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Gong Email ID: {gongEmailId}
              </div>
            </div>
          ) : null}
        </CardContent>
      )}
    </Card>
  );
}
