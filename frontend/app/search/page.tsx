"use client";

import { useState, useMemo, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useSearchCalls, SearchFilters } from "@/lib/hooks/use-search-calls-new";
import { CallSearchResult } from "@/lib/mcp-client";
import Link from "next/link";

// UI components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Search, Filter, Loader2, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";

// Call types for multi-select filter
const CALL_TYPES = ["discovery", "demo", "follow-up"] as const;

export default function CallSearchPage() {
  const { userId } = useAuth();
  const userRole = "manager"; // TODO: Extract from auth().sessionClaims.metadata.role

  // Form state - all filter inputs (Task 6.8)
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [repEmail, setRepEmail] = useState("");
  const [selectedCallTypes, setSelectedCallTypes] = useState<string[]>([]);
  const [minScore, setMinScore] = useState(0);
  const [keyword, setKeyword] = useState("");

  // Date validation error (Task 6.3)
  const [dateError, setDateError] = useState("");

  // Pagination state (Task 6.12)
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Build search filters - submit on any change (Task 6.9)
  const filters: SearchFilters | null = useMemo(() => {
    // Validate dates (Task 6.3)
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      if (end <= start) {
        setDateError("End date must be after start date");
        return null;
      } else {
        setDateError("");
      }
    }

    // Build filter object
    const hasFilters = startDate || endDate || repEmail || selectedCallTypes.length > 0 || minScore > 0 || keyword;

    if (!hasFilters) {
      return null; // No filters set, don't search
    }

    const filterObj: SearchFilters = {
      limit: 100, // Fetch more for client-side pagination
    };

    if (startDate && endDate) {
      filterObj.date_range = { start: startDate, end: endDate };
    }
    if (repEmail) {
      filterObj.rep_email = repEmail;
    }
    if (selectedCallTypes.length > 0) {
      // For simplicity, use the first selected type
      filterObj.call_type = selectedCallTypes[0];
    }
    if (minScore > 0) {
      filterObj.min_score = minScore;
    }
    if (keyword) {
      filterObj.keyword = keyword; // Will be debounced in hook (Task 6.7)
    }

    return filterObj;
  }, [startDate, endDate, repEmail, selectedCallTypes, minScore, keyword]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters]);

  // Fetch data using SWR hook (Task 6.1)
  const { data, error, isLoading } = useSearchCalls(filters);

  // Handle clear filters (Task 6.10)
  const handleClearFilters = () => {
    setStartDate("");
    setEndDate("");
    setRepEmail("");
    setSelectedCallTypes([]);
    setMinScore(0);
    setKeyword("");
    setDateError("");
    setCurrentPage(1);
  };

  // Handle call type checkbox toggle (Task 6.5)
  const handleCallTypeToggle = (callType: string) => {
    setSelectedCallTypes(prev =>
      prev.includes(callType)
        ? prev.filter(t => t !== callType)
        : [...prev, callType]
    );
  };

  // Paginate results (Task 6.12)
  const paginatedResults = useMemo(() => {
    if (!data) return [];
    const startIndex = (currentPage - 1) * pageSize;
    return data.slice(startIndex, startIndex + pageSize);
  }, [data, currentPage]);

  const totalPages = Math.ceil((data?.length || 0) / pageSize);

  // Handle retry (Task 6.15)
  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Call Search & Filter</h1>
        <p className="text-muted-foreground mt-1">
          Search and filter coaching call analyses
        </p>
      </div>

      {/* Filter Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Date Range Filter (Task 6.2) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          {/* Date validation error (Task 6.3) */}
          {dateError && (
            <p className="text-sm text-destructive">{dateError}</p>
          )}

          {/* Rep Filter - Manager only (Task 6.4) */}
          {userRole === "manager" && (
            <div className="space-y-2">
              <Label htmlFor="rep-email">Sales Rep Email</Label>
              <Input
                id="rep-email"
                type="email"
                placeholder="filter by rep email..."
                value={repEmail}
                onChange={(e) => setRepEmail(e.target.value)}
              />
            </div>
          )}

          {/* Call Type Multi-Select (Task 6.5) */}
          <div className="space-y-2">
            <Label>Call Type</Label>
            <div className="flex flex-wrap gap-4">
              {CALL_TYPES.map((callType) => (
                <div key={callType} className="flex items-center space-x-2">
                  <Checkbox
                    id={`call-type-${callType}`}
                    checked={selectedCallTypes.includes(callType)}
                    onCheckedChange={() => handleCallTypeToggle(callType)}
                  />
                  <Label
                    htmlFor={`call-type-${callType}`}
                    className="font-normal capitalize cursor-pointer"
                  >
                    {callType}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Minimum Score Filter (Task 6.6) */}
          <div className="space-y-2">
            <Label htmlFor="min-score">Minimum Score: {minScore}</Label>
            <Slider
              id="min-score"
              min={0}
              max={100}
              step={5}
              value={[minScore]}
              onValueChange={(values) => setMinScore(values[0])}
              className="w-full"
            />
          </div>

          {/* Keyword Search (Task 6.7) */}
          <div className="space-y-2">
            <Label htmlFor="keyword">Keyword Search</Label>
            <Input
              id="keyword"
              type="text"
              placeholder="search transcript or topics..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Search is debounced with 300ms delay
            </p>
          </div>

          {/* Clear Filters Button (Task 6.10) */}
          <div className="flex gap-2">
            <Button onClick={handleClearFilters} variant="outline">
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {filters && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Search Results
              {data && data.length > 0 && (
                <span className="text-sm font-normal text-muted-foreground">
                  ({data.length} {data.length === 1 ? "call" : "calls"} found)
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Loading State (Task 6.14) */}
            {isLoading && (
              <div className="space-y-3">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            )}

            {/* Error State (Task 6.15) */}
            {error && !isLoading && (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 mx-auto text-destructive mb-4" />
                <p className="text-lg font-medium text-destructive mb-2">
                  Error loading results
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  {error.message || "Something went wrong"}
                </p>
                <Button onClick={handleRetry} variant="outline">
                  Retry
                </Button>
              </div>
            )}

            {/* Empty State (Task 6.13) */}
            {!isLoading && !error && data && data.length === 0 && (
              <div className="text-center py-12">
                <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4 opacity-50" />
                <p className="text-lg font-medium text-muted-foreground">
                  No calls match your filters
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Try adjusting your search criteria
                </p>
              </div>
            )}

            {/* Results Table (Task 6.11) */}
            {!isLoading && !error && paginatedResults.length > 0 && (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium">Date</th>
                        <th className="text-left py-3 px-4 font-medium">Rep</th>
                        <th className="text-left py-3 px-4 font-medium">Type</th>
                        <th className="text-left py-3 px-4 font-medium">Score</th>
                        <th className="text-left py-3 px-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paginatedResults.map((call) => (
                        <tr key={call.call_id} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-4">
                            {call.date
                              ? new Date(call.date).toLocaleDateString()
                              : "N/A"}
                          </td>
                          <td className="py-3 px-4">
                            {call.prefect_reps.length > 0
                              ? call.prefect_reps.join(", ")
                              : "Unknown"}
                          </td>
                          <td className="py-3 px-4 capitalize">
                            {call.call_type || "N/A"}
                          </td>
                          <td className="py-3 px-4">
                            {call.overall_score !== null ? (
                              <ScoreBadge score={call.overall_score} />
                            ) : (
                              <span className="text-muted-foreground">N/A</span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <Link href={`/calls/${call.call_id}`}>
                              <Button variant="outline" size="sm">
                                View Details
                              </Button>
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls (Task 6.12) */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between pt-4">
                    <p className="text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Next
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Initial State - No Filters Set */}
      {!filters && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <Filter className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">
                Set filters above to search for calls
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
