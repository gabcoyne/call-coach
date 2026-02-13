"use client";

import { useState, useEffect, useRef } from "react";
import { useUser } from "@clerk/nextjs";
import { useInfiniteFeed } from "@/lib/hooks";
import {
  FeedItemCard,
  TeamInsightCard,
  CoachingHighlightCard,
  FeedFilters,
  NewItemsBanner,
  type FeedFilterState,
} from "@/components/feed";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Inbox } from "lucide-react";
import { isManager } from "@/lib/auth-utils";

export default function FeedPage() {
  const { user } = useUser();
  const [filters, setFilters] = useState<FeedFilterState>({
    typeFilter: "all",
    timeFilter: "this_week",
  });
  const [newItemsCount, setNewItemsCount] = useState(0);
  const loaderRef = useRef<HTMLDivElement>(null);

  // Check if user is manager using client-safe utility
  const userIsManager = isManager(user);

  // Build filter options for the hook
  const filterOptions = {
    type_filter: filters.typeFilter,
    time_filter: filters.timeFilter,
    start_date: filters.startDate,
    end_date: filters.endDate,
    limit: 20,
  };

  const { data, error, size, setSize, isLoading, isLoadingMore, isEmpty, isReachingEnd, mutate } =
    useInfiniteFeed(filterOptions);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoadingMore && !isReachingEnd) {
          setSize(size + 1);
        }
      },
      { threshold: 0.1 }
    );

    const currentLoader = loaderRef.current;
    if (currentLoader) {
      observer.observe(currentLoader);
    }

    return () => {
      if (currentLoader) {
        observer.unobserve(currentLoader);
      }
    };
  }, [isLoadingMore, isReachingEnd, size, setSize]);

  // Check for new items periodically
  useEffect(() => {
    const interval = setInterval(() => {
      mutate();
    }, 60000); // Check every 60 seconds

    return () => clearInterval(interval);
  }, [mutate]);

  // Calculate new items count (mock implementation)
  useEffect(() => {
    if (data && data[0]) {
      const newCount = data[0].new_items_count || 0;
      setNewItemsCount(newCount);
    }
  }, [data]);

  const handleRefresh = () => {
    setNewItemsCount(0);
    mutate();
  };

  // Flatten all feed items from paginated data
  const allItems = data ? data.flatMap((page) => page?.items || []) : [];
  const teamInsights = data?.[0]?.team_insights || [];
  const highlights = data?.[0]?.highlights || [];

  // Calculate item counts for filters
  const itemCounts = allItems.reduce(
    (acc, item) => {
      acc.all++;
      const type = item.type as keyof typeof acc;
      if (type in acc) {
        acc[type]++;
      }
      return acc;
    },
    {
      all: 0,
      call_analysis: 0,
      team_insight: 0,
      highlight: 0,
      milestone: 0,
    }
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Coaching Feed</h1>
        <p className="text-muted-foreground mt-1">Latest insights, highlights, and team updates</p>
      </div>

      {/* New Items Banner */}
      {newItemsCount > 0 && <NewItemsBanner count={newItemsCount} onRefresh={handleRefresh} />}

      {/* Filters */}
      <FeedFilters
        filters={filters}
        onFiltersChange={setFilters}
        itemCounts={itemCounts}
        isManager={userIsManager}
      />

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Feed Column */}
        <div className="lg:col-span-2 space-y-4">
          {isLoading && (
            <Card>
              <CardContent className="py-12">
                <div className="flex flex-col items-center justify-center text-center">
                  <Loader2 className="h-8 w-8 animate-spin text-prefect-blue-600 mb-4" />
                  <p className="text-muted-foreground">Loading feed...</p>
                </div>
              </CardContent>
            </Card>
          )}

          {error && (
            <Card>
              <CardContent className="py-12">
                <div className="flex flex-col items-center justify-center text-center max-w-md mx-auto">
                  <Inbox className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground mb-2">
                    Coaching Feed Coming Soon
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    This page will display personalized coaching insights, team performance
                    patterns, and high-impact moments from your calls. The backend endpoint is
                    currently being developed.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                    <p className="text-sm font-medium text-blue-900 mb-2">In the meantime:</p>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>
                        • Browse all calls at{" "}
                        <a href="/calls" className="underline font-medium">
                          /calls
                        </a>
                      </li>
                      <li>• Click any call to view detailed coaching analysis</li>
                      <li>• Search and filter calls by type, date, and participants</li>
                    </ul>
                  </div>
                  <p className="text-xs text-muted-foreground mt-4">
                    Tracked in:{" "}
                    <a
                      href="https://github.com/gabcoyne/call-coach/issues/1"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-foreground"
                    >
                      GitHub Issue #1
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {isEmpty && !isLoading && (
            <Card>
              <CardContent className="py-12">
                <div className="flex flex-col items-center justify-center text-center max-w-md mx-auto">
                  <Inbox className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground mb-2">
                    Coaching Feed Coming Soon
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    This page will display personalized coaching insights, team performance
                    patterns, and high-impact moments from your calls. The backend endpoint is
                    currently being developed.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                    <p className="text-sm font-medium text-blue-900 mb-2">In the meantime:</p>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>
                        • Browse all calls at{" "}
                        <a href="/calls" className="underline font-medium">
                          /calls
                        </a>
                      </li>
                      <li>• Click any call to view detailed coaching analysis</li>
                      <li>• Search and filter calls by type, date, and participants</li>
                    </ul>
                  </div>
                  <p className="text-xs text-muted-foreground mt-4">
                    Tracked in:{" "}
                    <a
                      href="https://github.com/gabcoyne/call-coach/issues/1"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-foreground"
                    >
                      GitHub Issue #1
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Feed Items */}
          {allItems.map((item) => (
            <FeedItemCard key={item.id} item={item} onAction={() => mutate()} />
          ))}

          {/* Loading More Indicator */}
          <div ref={loaderRef}>
            {isLoadingMore && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-prefect-blue-600" />
                <span className="ml-2 text-sm text-muted-foreground">Loading more...</span>
              </div>
            )}
            {isReachingEnd && allItems.length > 0 && (
              <div className="text-center py-8 text-sm text-muted-foreground">
                You've reached the end of the feed
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Column */}
        <div className="space-y-6">
          {/* Team Insights - Manager Only */}
          {userIsManager && teamInsights.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-foreground">Team Insights</h2>
              {teamInsights.slice(0, 3).map((insight) => (
                <TeamInsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          )}

          {/* Coaching Highlights */}
          {highlights.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-foreground">Coaching Highlights</h2>
              {highlights.slice(0, 3).map((highlight) => (
                <CoachingHighlightCard key={highlight.id} highlight={highlight} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
