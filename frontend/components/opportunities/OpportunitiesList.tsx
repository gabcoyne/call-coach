"use client";

/**
 * OpportunitiesList Component
 *
 * Interactive table/card view of opportunities with search, filters, sorting, and pagination.
 */
import { useState, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  TrendingDown,
  Clock,
  Target,
  RefreshCw,
} from "lucide-react";
import { useDebounce } from "@/lib/hooks/useDebounce";

interface Opportunity {
  id: string;
  name: string;
  account_name: string;
  owner_email: string;
  stage: string;
  close_date: string;
  amount: number;
  health_score: number;
  call_count: number;
  email_count: number;
  updated_at: string;
}

interface OpportunitiesResponse {
  opportunities: Opportunity[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}

const STAGES = [
  "Prospecting",
  "Qualification",
  "Proposal",
  "Negotiation",
  "Closed Won",
  "Closed Lost",
];

const SORT_OPTIONS = [
  { value: "updated_at", label: "Last Updated" },
  { value: "close_date", label: "Close Date" },
  { value: "health_score", label: "Health Score" },
  { value: "amount", label: "Amount" },
];

async function fetcher(url: string): Promise<OpportunitiesResponse> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error("Failed to fetch opportunities");
  }
  return response.json();
}

export function OpportunitiesList() {
  const router = useRouter();

  // Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStage, setSelectedStage] = useState<string>("all");
  const [healthScoreRange, setHealthScoreRange] = useState<[number, number]>([0, 100]);
  const [sortBy, setSortBy] = useState("updated_at");
  const [sortDir, setSortDir] = useState<"ASC" | "DESC">("DESC");
  const [page, setPage] = useState(1);
  const [limit] = useState(50);

  // Debounce search query
  const debouncedSearch = useDebounce(searchQuery, 300);

  // Build query string
  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    if (debouncedSearch) params.set("search", debouncedSearch);
    if (selectedStage !== "all") params.set("stage", selectedStage);
    if (healthScoreRange[0] > 0) params.set("health_score_min", String(healthScoreRange[0]));
    if (healthScoreRange[1] < 100) params.set("health_score_max", String(healthScoreRange[1]));
    params.set("sort", sortBy);
    params.set("sort_dir", sortDir);
    params.set("page", String(page));
    params.set("limit", String(limit));
    return params.toString();
  }, [debouncedSearch, selectedStage, healthScoreRange, sortBy, sortDir, page, limit]);

  // Fetch data
  const { data, error, isLoading } = useSWR<OpportunitiesResponse>(
    `/api/opportunities?${queryString}`,
    fetcher,
    {
      revalidateOnFocus: false,
      keepPreviousData: true,
    }
  );

  // Reset to page 1 when filters change
  const handleFilterChange = useCallback(() => {
    setPage(1);
  }, []);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    handleFilterChange();
  };

  const handleStageChange = (value: string) => {
    setSelectedStage(value);
    handleFilterChange();
  };

  const handleHealthScoreChange = (value: number[]) => {
    setHealthScoreRange([value[0], value[1]]);
    handleFilterChange();
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
    handleFilterChange();
  };

  const toggleSortDirection = () => {
    setSortDir((prev) => (prev === "ASC" ? "DESC" : "ASC"));
    handleFilterChange();
  };

  const handleOpportunityClick = (opportunityId: string) => {
    router.push(`/opportunities/${opportunityId}`);
  };

  // Check if opportunity is stale (14+ days since last update)
  const isStale = (updatedAt: string) => {
    const daysSinceUpdate = (Date.now() - new Date(updatedAt).getTime()) / (1000 * 60 * 60 * 24);
    return daysSinceUpdate >= 14;
  };

  // Get health score color
  const getHealthColor = (score: number) => {
    if (score >= 70) return "success";
    if (score >= 40) return "warning";
    return "destructive";
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search */}
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search opportunities or accounts..."
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="flex-1"
            />
          </div>

          {/* Stage and Sort */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Stage</Label>
              <Select value={selectedStage} onValueChange={handleStageChange}>
                <SelectTrigger>
                  <SelectValue placeholder="All Stages" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Stages</SelectItem>
                  {STAGES.map((stage) => (
                    <SelectItem key={stage} value={stage}>
                      {stage}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Sort By</Label>
              <div className="flex gap-2">
                <Select value={sortBy} onValueChange={handleSortChange}>
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SORT_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={toggleSortDirection}
                  title={sortDir === "ASC" ? "Ascending" : "Descending"}
                >
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label>
                Health Score: {healthScoreRange[0]} - {healthScoreRange[1]}
              </Label>
              <Slider
                value={healthScoreRange}
                onValueChange={handleHealthScoreChange}
                min={0}
                max={100}
                step={5}
                className="py-2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Failed to load opportunities. Please try again.</p>
          </CardContent>
        </Card>
      )}

      {isLoading && <OpportunitiesListSkeleton />}

      {data && (
        <>
          {/* Desktop Table */}
          <div className="hidden md:block">
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Opportunity</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Account</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Stage</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Close Date</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Amount</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Health</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Activity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.opportunities.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-4 py-12 text-center">
                          <div className="flex flex-col items-center gap-3">
                            <Target className="h-12 w-12 text-muted-foreground" />
                            <div>
                              <p className="text-lg font-semibold">No opportunities found</p>
                              <p className="text-sm text-muted-foreground mt-1 max-w-md mx-auto">
                                Opportunities are synced from your CRM. If you expect to see data
                                here, contact your admin to verify the data sync is configured
                                correctly.
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              className="mt-2"
                              onClick={(e) => {
                                e.stopPropagation();
                                window.location.reload();
                              }}
                            >
                              <RefreshCw className="h-4 w-4 mr-2" />
                              Refresh
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      data.opportunities.map((opp) => (
                        <tr
                          key={opp.id}
                          className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                          onClick={() => handleOpportunityClick(opp.id)}
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{opp.name}</span>
                              {isStale(opp.updated_at) && (
                                <Badge
                                  variant="warning"
                                  className="flex items-center gap-1"
                                  title="14+ days since last activity"
                                >
                                  <Clock className="h-3 w-3" />
                                  Stale
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-muted-foreground">{opp.owner_email}</div>
                          </td>
                          <td className="px-4 py-3">{opp.account_name}</td>
                          <td className="px-4 py-3">
                            <Badge variant="outline">{opp.stage}</Badge>
                          </td>
                          <td className="px-4 py-3">
                            {opp.close_date ? new Date(opp.close_date).toLocaleDateString() : "—"}
                          </td>
                          <td className="px-4 py-3">
                            {opp.amount ? `$${opp.amount.toLocaleString()}` : "—"}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              {opp.health_score != null ? (
                                <>
                                  <Badge variant={getHealthColor(opp.health_score)}>
                                    {opp.health_score}
                                  </Badge>
                                  {opp.health_score < 50 && (
                                    <TrendingDown className="h-4 w-4 text-destructive" />
                                  )}
                                </>
                              ) : (
                                <span className="text-muted-foreground text-sm">—</span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-muted-foreground">
                              {opp.call_count ?? 0} calls, {opp.email_count ?? 0} emails
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Mobile Cards */}
          <div className="md:hidden space-y-4">
            {data.opportunities.length === 0 ? (
              <Card>
                <CardContent className="pt-8 pb-8 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <Target className="h-12 w-12 text-muted-foreground" />
                    <div>
                      <p className="text-lg font-semibold">No opportunities found</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Opportunities are synced from your CRM. Contact your admin if you expect to
                        see data.
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-2"
                      onClick={() => window.location.reload()}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              data.opportunities.map((opp) => (
                <Card
                  key={opp.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => handleOpportunityClick(opp.id)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg flex items-center gap-2">
                          {opp.name}
                          {isStale(opp.updated_at) && (
                            <Badge variant="warning" className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Stale
                            </Badge>
                          )}
                        </CardTitle>
                        <div className="text-sm text-muted-foreground mt-1">{opp.account_name}</div>
                      </div>
                      {opp.health_score != null ? (
                        <Badge variant={getHealthColor(opp.health_score)}>{opp.health_score}</Badge>
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Stage:</span>
                      <Badge variant="outline">{opp.stage || "—"}</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Close Date:</span>
                      <span>
                        {opp.close_date ? new Date(opp.close_date).toLocaleDateString() : "—"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Amount:</span>
                      <span className="font-medium">
                        {opp.amount ? `$${opp.amount.toLocaleString()}` : "—"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Activity:</span>
                      <span>
                        {opp.call_count ?? 0} calls, {opp.email_count ?? 0} emails
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground pt-2 border-t">
                      Owner: {opp.owner_email}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Pagination */}
          {data.pagination.totalPages > 1 && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Showing {(page - 1) * limit + 1} to{" "}
                    {Math.min(page * limit, data.pagination.total)} of {data.pagination.total}{" "}
                    opportunities
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <div className="text-sm">
                      Page {page} of {data.pagination.totalPages}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(data.pagination.totalPages, p + 1))}
                      disabled={!data.pagination.hasMore}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

function OpportunitiesListSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6 space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between py-4">
            <div className="space-y-2 flex-1">
              <Skeleton className="h-5 w-64" />
              <Skeleton className="h-4 w-48" />
            </div>
            <Skeleton className="h-6 w-16" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
