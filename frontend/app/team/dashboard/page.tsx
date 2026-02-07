"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import {
  Users,
  TrendingUp,
  Phone,
  Calendar,
  Clock,
  BarChart3,
  ArrowRight,
  Activity,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/lib/hooks/use-current-user";
import { isManager } from "@/lib/rbac";

interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface TeamCall {
  id: string;
  gong_call_id: string;
  title: string;
  scheduled_at: string;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
}

export default function TeamDashboardPage() {
  const router = useRouter();
  const { user: clerkUser } = useUser();
  const { data: currentUser, isLoading: userLoading } = useCurrentUser();
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [recentCalls, setRecentCalls] = useState<TeamCall[]>([]);
  const [isLoadingMembers, setIsLoadingMembers] = useState(true);
  const [isLoadingCalls, setIsLoadingCalls] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const userIsManager = isManager(currentUser);

  useEffect(() => {
    if (!userLoading && !userIsManager) {
      // Redirect non-managers
      router.push("/dashboard");
      return;
    }

    if (userIsManager && clerkUser?.primaryEmailAddress?.emailAddress) {
      loadTeamData();
    }
  }, [userIsManager, userLoading, clerkUser, router]);

  const loadTeamData = async () => {
    const userEmail = clerkUser?.primaryEmailAddress?.emailAddress;
    if (!userEmail) return;

    try {
      // Load team members
      setIsLoadingMembers(true);
      const membersResponse = await fetch(
        `${process.env.NEXT_PUBLIC_MCP_BACKEND_URL}/api/v1/team/reps`,
        {
          headers: {
            "X-User-Email": userEmail,
          },
        }
      );

      if (membersResponse.ok) {
        const members = await membersResponse.json();
        setTeamMembers(members);
      }

      // Load recent team calls
      setIsLoadingCalls(true);
      const callsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_MCP_BACKEND_URL}/api/v1/team/calls?limit=10`,
        {
          headers: {
            "X-User-Email": userEmail,
          },
        }
      );

      if (callsResponse.ok) {
        const calls = await callsResponse.json();
        setRecentCalls(calls);
      }
    } catch (err) {
      console.error("Failed to load team data:", err);
      setError("Failed to load team data");
    } finally {
      setIsLoadingMembers(false);
      setIsLoadingCalls(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  };

  if (userLoading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  if (!userIsManager) {
    return null; // Will redirect
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">My Team</h1>
        <p className="text-muted-foreground mt-1">Team performance and activity overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamMembers.length}</div>
            <p className="text-xs text-muted-foreground">Active sales reps</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Calls</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{recentCalls.length}</div>
            <p className="text-xs text-muted-foreground">Last 10 team calls</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Activity</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <TrendingUp className="h-6 w-6 text-green-500 inline" />
            </div>
            <p className="text-xs text-muted-foreground">Team is active</p>
          </CardContent>
        </Card>
      </div>

      {/* Team Members */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Members
          </CardTitle>
          <CardDescription>View and manage your sales team</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingMembers ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : teamMembers.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">No team members found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors cursor-pointer"
                  onClick={() => router.push(`/dashboard/${member.email}`)}
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-r from-prefect-pink to-prefect-sunrise1 flex items-center justify-center text-white font-medium">
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-sm text-muted-foreground">{member.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{member.role}</Badge>
                    <Button variant="ghost" size="sm">
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Team Calls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5" />
            Recent Team Calls
          </CardTitle>
          <CardDescription>Latest calls from your team members</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoadingCalls ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : recentCalls.length === 0 ? (
            <div className="p-12 text-center">
              <Phone className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">No recent calls</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Call Title</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Product</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentCalls.map((call) => (
                  <TableRow
                    key={call.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => router.push(`/calls/${call.gong_call_id}`)}
                  >
                    <TableCell className="font-medium max-w-xs truncate">{call.title}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(call.scheduled_at)}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDuration(call.duration_seconds)}
                      </div>
                    </TableCell>
                    <TableCell>
                      {call.call_type && (
                        <Badge variant="outline">{call.call_type.replace(/_/g, " ")}</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {call.product && <Badge variant="secondary">{call.product}</Badge>}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Team Analytics
            </CardTitle>
            <CardDescription>View detailed team performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => router.push("/calls?view=team")}
            >
              View All Team Calls
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Individual Reviews
            </CardTitle>
            <CardDescription>Deep dive into individual rep performance</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" onClick={() => router.push("/search")}>
              Search Rep Calls
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
