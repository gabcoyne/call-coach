"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Filter,
  Calendar,
  Users,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { DateRange } from "react-day-picker";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DateRangePicker } from "@/components/ui/date-range-picker";

interface Call {
  call_id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  overall_score: number | null;
  customer_names: string[];
  prefect_reps: string[];
}

interface SearchResponse {
  data: {
    items: Call[];
    total: number;
  };
}

const PAGE_SIZE = 20;

export default function CallsPage() {
  const router = useRouter();
  const [calls, setCalls] = useState<Call[]>([]);
  const [totalCalls, setTotalCalls] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [callTypeFilter, setCallTypeFilter] = useState<string>("all");
  const [productFilter, setProductFilter] = useState<string>("all");
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined);
  const [page, setPage] = useState(1);

  const totalPages = Math.ceil(totalCalls / PAGE_SIZE);

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // Format call title with fallback
  const formatCallTitle = (call: Call): string => {
    if (call.title) return call.title;
    const customer = call.customer_names?.[0] || "Unknown";
    const dateStr = call.date
      ? new Date(call.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })
      : "Unknown date";
    return `Call with ${customer} on ${dateStr}`;
  };

  const handleSearch = useCallback(
    async (pageNum: number = 1) => {
      setIsLoading(true);
      setError(null);

      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

      try {
        const requestBody: Record<string, any> = {
          limit: PAGE_SIZE,
          offset: (pageNum - 1) * PAGE_SIZE,
        };

        // Add search query if present
        if (searchQuery.trim()) {
          requestBody.search = searchQuery.trim();
        }
        if (callTypeFilter !== "all") requestBody.call_type = callTypeFilter;
        if (productFilter !== "all") requestBody.product = productFilter;

        // Add date range if selected
        if (dateRange?.from) {
          requestBody.start_date = dateRange.from.toISOString().split("T")[0];
        }
        if (dateRange?.to) {
          requestBody.end_date = dateRange.to.toISOString().split("T")[0];
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_MCP_BACKEND_URL}/api/v1/tools/search_calls`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
            signal: controller.signal,
          }
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result: SearchResponse = await response.json();
        setCalls(result.data.items);
        setTotalCalls(result.data.total || result.data.items.length);
        setPage(pageNum);
      } catch (err) {
        if (err instanceof Error) {
          if (err.name === "AbortError") {
            setError("Request timed out. Please try again.");
          } else {
            setError(err.message || "Failed to load calls");
          }
        } else {
          setError("An unexpected error occurred");
        }
        console.error("Failed to search calls:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [searchQuery, callTypeFilter, productFilter, dateRange]
  );

  // Load calls on component mount
  useEffect(() => {
    handleSearch(1);
  }, []);

  // Handle filter changes - reset to page 1
  const handleFilterChange = () => {
    handleSearch(1);
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setCallTypeFilter("all");
    setProductFilter("all");
    setDateRange(undefined);
    setCalls([]);
    setTotalCalls(0);
    setPage(1);
  };

  const handleRetry = () => {
    handleSearch(page);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Call Library</h1>
        <p className="text-muted-foreground mt-1">Browse and analyze sales calls</p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {/* Search Input */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by title, customer, or rep..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleFilterChange()}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Date Range Picker */}
            <DateRangePicker
              value={dateRange}
              onChange={setDateRange}
              placeholder="Select dates"
              className="w-full"
            />

            {/* Call Type Filter */}
            <Select value={callTypeFilter} onValueChange={setCallTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="discovery">Discovery</SelectItem>
                <SelectItem value="demo">Demo</SelectItem>
                <SelectItem value="negotiation">Negotiation</SelectItem>
                <SelectItem value="technical_deep_dive">Technical Deep Dive</SelectItem>
                <SelectItem value="follow_up">Follow Up</SelectItem>
                <SelectItem value="executive_briefing">Executive Briefing</SelectItem>
              </SelectContent>
            </Select>

            {/* Product Filter */}
            <Select value={productFilter} onValueChange={setProductFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Products" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Products</SelectItem>
                <SelectItem value="prefect">Prefect</SelectItem>
                <SelectItem value="horizon">Horizon</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleFilterChange} disabled={isLoading}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
            <Button variant="outline" onClick={handleClearFilters}>
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-8 w-8 text-destructive" />
              <div className="flex-1">
                <p className="font-medium text-destructive">Failed to load calls</p>
                <p className="text-sm text-muted-foreground">{error}</p>
              </div>
              <Button onClick={handleRetry} variant="outline">
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Calls Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex gap-4">
                  <Skeleton className="h-12 flex-1" />
                  <Skeleton className="h-12 w-24" />
                  <Skeleton className="h-12 w-24" />
                  <Skeleton className="h-12 w-16" />
                </div>
              ))}
            </div>
          ) : calls.length === 0 && !error ? (
            <div className="p-12 text-center">
              <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No calls found</h3>
              <p className="text-sm text-muted-foreground">
                Try adjusting your search filters or search for calls using the form above.
              </p>
            </div>
          ) : calls.length > 0 ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Call Title</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Product</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Reps</TableHead>
                    <TableHead>Customers</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {calls.map((call) => (
                    <TableRow
                      key={call.call_id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => router.push(`/calls/${call.call_id}`)}
                    >
                      <TableCell className="font-medium max-w-xs truncate">
                        {formatCallTitle(call)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(call.date)}
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
                      <TableCell>
                        {call.overall_score !== null && <ScoreBadge score={call.overall_score} />}
                      </TableCell>
                      <TableCell className="text-sm">
                        <div className="flex items-center gap-1 max-w-xs truncate">
                          <Users className="h-3 w-3 flex-shrink-0" />
                          <span className="truncate">{call.prefect_reps.join(", ") || "N/A"}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm max-w-xs truncate">
                        {call.customer_names.join(", ") || "N/A"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t">
                  <div className="text-sm text-muted-foreground">
                    Showing {(page - 1) * PAGE_SIZE + 1} to {Math.min(page * PAGE_SIZE, totalCalls)}{" "}
                    of {totalCalls} calls
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSearch(page - 1)}
                      disabled={page === 1 || isLoading}
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                    <span className="text-sm text-muted-foreground px-2">
                      Page {page} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSearch(page + 1)}
                      disabled={page === totalPages || isLoading}
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </CardContent>
      </Card>

      {/* Stats Footer */}
      {calls.length > 0 && totalPages <= 1 && (
        <div className="text-sm text-muted-foreground text-center">
          Showing {calls.length} calls
        </div>
      )}
    </div>
  );
}
