"use client";

import { useState, useEffect } from "react";
import { useUser } from "@/lib/hooks/use-auth";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScoreCard } from "@/components/coaching/ScoreCard";
import { getScoreColor } from "@/lib/colors";
import { useSearchCalls } from "@/lib/hooks/use-search-calls";
import { ArrowRight, User, Calendar } from "lucide-react";

/**
 * Manager Dashboard Page
 *
 * For managers: Shows a list of all reps with summary performance data
 * For reps: Redirects to their individual dashboard
 */
export default function DashboardPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();

  const isManager = user?.publicMetadata?.role === "manager";
  const currentUserEmail = user?.emailAddresses[0]?.emailAddress;

  // For non-managers, redirect to their own dashboard
  useEffect(() => {
    if (isLoaded && !isManager && currentUserEmail) {
      router.push(`/dashboard/${encodeURIComponent(currentUserEmail)}`);
    }
  }, [isLoaded, isManager, currentUserEmail, router]);

  // Fetch all calls to aggregate rep data (for manager view)
  const { data: calls, isLoading, error } = useSearchCalls(isManager ? { limit: 500 } : null);

  if (!isLoaded || isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Loading...</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-100 rounded w-1/2 mt-2" />
              </CardHeader>
              <CardContent>
                <div className="h-4 bg-gray-100 rounded w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Error loading dashboard</p>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-sm text-red-800">{error.message || "Failed to load rep data"}</p>
            <Button variant="outline" onClick={() => window.location.reload()} className="mt-4">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Aggregate rep data from calls
  const repData = new Map<
    string,
    {
      name: string;
      email: string;
      totalCalls: number;
      scores: number[];
      lastActivity: string | null;
    }
  >();

  calls?.forEach((call) => {
    call.prefect_reps.forEach((repName) => {
      // Try to find email from call data, or use name as fallback
      const repEmail = repName.toLowerCase().replace(/\s+/g, ".") + "@prefect.io";

      if (!repData.has(repEmail)) {
        repData.set(repEmail, {
          name: repName,
          email: repEmail,
          totalCalls: 0,
          scores: [],
          lastActivity: null,
        });
      }

      const rep = repData.get(repEmail)!;
      rep.totalCalls++;

      if (call.overall_score !== null) {
        rep.scores.push(call.overall_score);
      }

      if (call.date) {
        if (!rep.lastActivity || call.date > rep.lastActivity) {
          rep.lastActivity = call.date;
        }
      }
    });
  });

  const reps = Array.from(repData.values())
    .map((rep) => ({
      ...rep,
      avgScore:
        rep.scores.length > 0
          ? Math.round(rep.scores.reduce((a, b) => a + b, 0) / rep.scores.length)
          : null,
    }))
    .sort((a, b) => b.totalCalls - a.totalCalls);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Team Dashboard</h1>
        <p className="text-muted-foreground mt-1">Overview of all sales reps performance</p>
      </div>

      {reps.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center">
              No rep data available. Calls need to be analyzed first.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Sales Representatives</CardTitle>
            <CardDescription>
              Click on a rep to view their detailed performance dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-sm">Rep</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Email</th>
                    <th className="text-center py-3 px-4 font-medium text-sm">Avg Score</th>
                    <th className="text-center py-3 px-4 font-medium text-sm">Total Calls</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Last Activity</th>
                    <th className="text-right py-3 px-4 font-medium text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reps.map((rep) => {
                    const scoreColor = rep.avgScore ? getScoreColor(rep.avgScore) : null;

                    return (
                      <tr
                        key={rep.email}
                        className="border-b hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => router.push(`/dashboard/${encodeURIComponent(rep.email)}`)}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-gray-400" />
                            <span className="font-medium">{rep.name}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">{rep.email}</td>
                        <td className="py-3 px-4">
                          <div className="flex justify-center">
                            {rep.avgScore !== null ? (
                              <div
                                className="px-3 py-1 rounded-full text-sm font-semibold"
                                style={{
                                  backgroundColor: scoreColor?.bg,
                                  color: scoreColor?.text,
                                }}
                              >
                                {rep.avgScore}
                              </div>
                            ) : (
                              <span className="text-sm text-gray-400">N/A</span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center text-sm">{rep.totalCalls}</td>
                        <td className="py-3 px-4">
                          {rep.lastActivity ? (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Calendar className="w-4 h-4" />
                              {new Date(rep.lastActivity).toLocaleDateString()}
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">No activity</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="gap-2"
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/dashboard/${encodeURIComponent(rep.email)}`);
                            }}
                          >
                            View Details
                            <ArrowRight className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
