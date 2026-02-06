"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getScoreColor } from "@/lib/colors";
import { Phone, Calendar, TrendingUp } from "lucide-react";
import Link from "next/link";

export interface ActivityItem {
  call_id: string;
  date: string;
  call_type: string;
  overall_score: number | null;
  customer_name?: string;
  duration_seconds?: number;
}

export interface RecentActivityFeedProps {
  /** Array of recent calls/activities (typically last 10) */
  activities: ActivityItem[];
  /** Optional max number of items to display */
  limit?: number;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * RecentActivityFeed Component
 *
 * Displays a scrollable feed of recent calls with quick score indicators.
 * Each item shows date, call type, duration, and performance score.
 */
export function RecentActivityFeed({
  activities,
  limit = 10,
  className = "",
}: RecentActivityFeedProps) {
  const displayActivities = activities.slice(0, limit);

  if (!displayActivities || displayActivities.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="w-5 h-5" />
            Recent Activity
          </CardTitle>
          <CardDescription>Last 10 calls</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 text-center py-8">No recent activity available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Phone className="w-5 h-5" />
          Recent Activity
        </CardTitle>
        <CardDescription>Last {Math.min(limit, displayActivities.length)} calls</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {displayActivities.map((activity, index) => {
            const scoreColor = activity.overall_score
              ? getScoreColor(activity.overall_score)
              : null;
            const formattedDate = new Date(activity.date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "2-digit",
            });
            const formattedTime = new Date(activity.date).toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
            });

            // Calculate duration display
            const durationMinutes = activity.duration_seconds
              ? Math.round(activity.duration_seconds / 60)
              : null;

            return (
              <div
                key={activity.call_id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                {/* Left: Call info */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100">
                    <span className="text-xs font-semibold text-blue-700">{index + 1}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {activity.call_type || "Call"}
                      </p>
                      {activity.customer_name && (
                        <span className="text-xs text-gray-500 truncate">
                          with {activity.customer_name}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      <span>{formattedDate}</span>
                      <span>·</span>
                      <span>{formattedTime}</span>
                      {durationMinutes && (
                        <>
                          <span>·</span>
                          <span>{durationMinutes}m</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: Score badge */}
                <div className="flex items-center gap-3 ml-2">
                  {activity.overall_score !== null ? (
                    <div
                      className="px-3 py-1 rounded-full text-sm font-semibold whitespace-nowrap"
                      style={{
                        backgroundColor: scoreColor?.bg,
                        color: scoreColor?.text,
                      }}
                    >
                      {activity.overall_score}
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400 whitespace-nowrap">N/A</span>
                  )}
                  <Link
                    href={`/calls/${activity.call_id}`}
                    className="text-sm text-blue-600 hover:text-blue-800 hover:underline whitespace-nowrap"
                  >
                    View
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
