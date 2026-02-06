"use client";

/**
 * OpportunityTimeline Component
 *
 * Chronological timeline of calls and emails with pagination and lazy loading.
 */
import { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CallTimelineCard } from "./CallTimelineCard";
import { EmailTimelineCard } from "./EmailTimelineCard";
import { AlertCircle, Clock } from "lucide-react";

interface TimelineItem {
  item_type: "call" | "email";
  id: string;
  gong_call_id?: string;
  gong_email_id?: string;
  timestamp: string;
  title?: string;
  subject?: string;
  duration?: number;
  sender_email?: string;
}

interface TimelineResponse {
  items: TimelineItem[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}

async function fetcher(url: string): Promise<TimelineResponse> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch timeline");
  }
  return response.json();
}

interface OpportunityTimelineProps {
  opportunityId: string;
}

export function OpportunityTimeline({ opportunityId }: OpportunityTimelineProps) {
  const [page, setPage] = useState(1);
  const [allItems, setAllItems] = useState<TimelineItem[]>([]);
  const limit = 20;

  const { data, error, isLoading } = useSWR<TimelineResponse>(
    `/api/opportunities/${opportunityId}/timeline?page=${page}&limit=${limit}`,
    fetcher,
    {
      revalidateOnFocus: false,
      onSuccess: (newData) => {
        if (page === 1) {
          setAllItems(newData.items);
        } else {
          setAllItems((prev) => [...prev, ...newData.items]);
        }
      },
    }
  );

  const handleLoadMore = () => {
    setPage((p) => p + 1);
  };

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span>Failed to load timeline. Please try again.</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Activity Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading && page === 1 ? (
          <TimelineLoading />
        ) : allItems.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No activity recorded for this opportunity yet.
          </div>
        ) : (
          <>
            {/* Timeline Items */}
            <div className="space-y-4">
              {allItems.map((item) =>
                item.item_type === "call" ? (
                  <CallTimelineCard
                    key={`call-${item.id}`}
                    callId={item.id}
                    gongCallId={item.gong_call_id || ""}
                    title={item.title || "Untitled Call"}
                    timestamp={item.timestamp}
                    duration={item.duration || 0}
                  />
                ) : (
                  <EmailTimelineCard
                    key={`email-${item.id}`}
                    emailId={item.id}
                    gongEmailId={item.gong_email_id || ""}
                    subject={item.subject || "No Subject"}
                    timestamp={item.timestamp}
                    senderEmail={item.sender_email || "Unknown"}
                  />
                )
              )}
            </div>

            {/* Load More */}
            {data && data.pagination.hasMore && (
              <div className="flex justify-center pt-4">
                <Button variant="outline" onClick={handleLoadMore} disabled={isLoading}>
                  {isLoading && page > 1 ? "Loading..." : "Load More"}
                </Button>
              </div>
            )}

            {/* Pagination Info */}
            {data && (
              <div className="text-sm text-center text-muted-foreground pt-2">
                Showing {allItems.length} of {data.pagination.total} items
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

function TimelineLoading() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="space-y-2 p-4 border rounded-lg">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-16 w-full" />
        </div>
      ))}
    </div>
  );
}
