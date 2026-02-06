"use client";

import { useState, useMemo, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useSearchCalls, SearchFilters } from "@/lib/hooks/use-search-calls-new";
import { CallSearchResult, SearchCallsRequest } from "@/types/coaching";
import Link from "next/link";

// UI components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Search, Filter, AlertCircle, Clock, Users } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

// Search components
import { MultiCriteriaFilterForm } from "@/components/search/multi-criteria-filter-form";
import { QuickFilterPresets } from "@/components/search/quick-filter-presets";
import { SaveSearchButton } from "@/components/search/save-search-button";
import { LoadSavedSearches } from "@/components/search/load-saved-searches";
import { SearchResults } from "@/components/search/search-results";
import { ExportResults } from "@/components/search/export-results";
import { PaginationControls } from "@/components/search/pagination-controls";
import { SortingOptions, SortField, SortDirection } from "@/components/search/sorting-options";
import { ScoreThresholdFilters } from "@/components/search/score-threshold-filters";
import { TopicKeywordFilter } from "@/components/search/topic-keyword-filter";
import { ObjectionTypeFilter } from "@/components/search/objection-type-filter";
import { AdvancedFilterBuilder } from "@/components/search/advanced-filter-builder";
import { BulkActions } from "@/components/search/bulk-actions";

// Storage key for recent searches
const RECENT_SEARCHES_KEY = "coaching-recent-searches";
const MAX_RECENT_SEARCHES = 10;

interface RecentSearch {
  id: string;
  filters: Partial<SearchCallsRequest>;
  timestamp: string;
}

export default function CallSearchPage() {
  const { userId } = useAuth();
  const { toast } = useToast();

  // Filter state
  const [filters, setFilters] = useState<Partial<SearchCallsRequest>>({});
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);

  // Pagination and sorting state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  // Show advanced filters state
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showAdvancedBuilder, setShowAdvancedBuilder] = useState(false);

  // Bulk actions state
  const [useBulkActionsView, setUseBulkActionsView] = useState(false);

  // Load recent searches on mount
  useEffect(() => {
    loadRecentSearches();
  }, []);

  // Load recent searches from localStorage
  const loadRecentSearches = () => {
    if (typeof window === "undefined") return;
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load recent searches", error);
    }
  };

  // Save search to recent searches
  const addToRecentSearches = (newFilters: Partial<SearchCallsRequest>) => {
    const newSearch: RecentSearch = {
      id: Date.now().toString(),
      filters: newFilters,
      timestamp: new Date().toISOString(),
    };

    const updated = [newSearch, ...recentSearches].slice(0, MAX_RECENT_SEARCHES);
    setRecentSearches(updated);

    if (typeof window !== "undefined") {
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    }
  };

  // Build search query based on filters
  const searchFilters: SearchFilters | null = useMemo(() => {
    if (Object.keys(filters).length === 0) {
      return null;
    }
    return filters as SearchFilters;
  }, [filters]);

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchFilters]);

  // Fetch data using hook
  const { data, error, isLoading } = useSearchCalls(searchFilters);

  // Sort and paginate results
  const processedResults = useMemo(() => {
    if (!data) return [];

    let sorted = [...data];

    // Apply sorting
    sorted.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case "date":
          comparison = new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime();
          break;
        case "score":
          comparison = (b.overall_score ?? 0) - (a.overall_score ?? 0);
          break;
        case "duration":
          comparison = b.duration_seconds - a.duration_seconds;
          break;
      }
      return sortDirection === "asc" ? -comparison : comparison;
    });

    return sorted;
  }, [data, sortField, sortDirection]);

  // Paginate results
  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return processedResults.slice(startIndex, startIndex + pageSize);
  }, [processedResults, currentPage, pageSize]);

  const totalPages = Math.ceil((processedResults?.length || 0) / pageSize);

  // Handle filter changes
  const handleFiltersChange = (newFilters: Partial<SearchCallsRequest>) => {
    setFilters(newFilters);
    addToRecentSearches(newFilters);
  };

  // Handle preset selection
  const handlePresetSelect = (presetFilters: Partial<SearchCallsRequest>) => {
    setFilters(presetFilters);
    addToRecentSearches(presetFilters);
    toast({
      title: "Preset Applied",
      description: "Search filters have been updated",
    });
  };

  // Handle saved search load
  const handleLoadSavedSearch = (savedFilters: Partial<SearchCallsRequest>) => {
    setFilters(savedFilters);
    addToRecentSearches(savedFilters);
    toast({
      title: "Search Loaded",
      description: "Saved search filters have been applied",
    });
  };

  // Handle save search
  const handleSaveSearch = (name: string) => {
    toast({
      title: "Search Saved",
      description: `'${name}' has been saved to your search presets`,
    });
  };

  // Handle retry
  const handleRetry = () => {
    window.location.reload();
  };

  // Get total results count
  const totalResults = processedResults?.length || 0;

  return (
    <div className="container mx-auto py-8 px-4 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Call Search & Advanced Filters</h1>
        <p className="text-muted-foreground mt-1">
          Search, filter, and analyze coaching calls with advanced options
        </p>
      </div>

      {/* Quick Filter Presets */}
      <QuickFilterPresets onPresetSelect={handlePresetSelect} />

      {/* Saved Searches Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Saved & Recent Searches
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Load Saved Searches */}
            <div>
              <h3 className="font-medium mb-3">My Saved Searches</h3>
              <LoadSavedSearches onLoad={handleLoadSavedSearch} />
            </div>

            {/* Recent Searches */}
            <div>
              <h3 className="font-medium mb-3">Recent Searches</h3>
              {recentSearches.length > 0 ? (
                <div className="space-y-2">
                  {recentSearches.slice(0, 5).map((search) => (
                    <Button
                      key={search.id}
                      variant="outline"
                      size="sm"
                      className="w-full justify-start text-left"
                      onClick={() => {
                        setFilters(search.filters);
                        toast({
                          title: "Search Restored",
                          description: "Recent search has been applied",
                        });
                      }}
                    >
                      <Clock className="h-3 w-3 mr-2" />
                      <span className="truncate text-xs">
                        {Object.entries(search.filters)
                          .filter(([_, v]) => v !== undefined && v !== null)
                          .map(([k, v]) => `${k}: ${JSON.stringify(v).substring(0, 20)}`)
                          .join(", ") || "Empty search"}
                      </span>
                    </Button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No recent searches yet</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Filter Card with Expandable Advanced Options */}
      <div className="space-y-4">
        {/* Basic Filters */}
        <MultiCriteriaFilterForm
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onReset={() => {
            setFilters({});
            setCurrentPage(1);
          }}
        />

        {/* Toggle Advanced Filters and Advanced Builder */}
        <div className="flex justify-center gap-2 flex-wrap">
          <Button
            variant="outline"
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="gap-2"
          >
            {showAdvancedFilters ? "Hide" : "Show"} Advanced Filters
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowAdvancedBuilder(!showAdvancedBuilder)}
            className="gap-2"
          >
            {showAdvancedBuilder ? "Hide" : "Show"} Filter Builder
          </Button>
        </div>

        {/* Advanced Filter Sections */}
        {showAdvancedFilters && (
          <div className="space-y-4">
            <ScoreThresholdFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
            <TopicKeywordFilter
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
            <ObjectionTypeFilter
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
          </div>
        )}

        {/* Advanced Filter Builder */}
        {showAdvancedBuilder && (
          <AdvancedFilterBuilder
            onApplyFilters={handleFiltersChange}
            onClose={() => setShowAdvancedBuilder(false)}
          />
        )}
      </div>

      {/* Results Section */}
      {searchFilters && (
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Search Results
                  {totalResults > 0 && (
                    <span className="text-sm font-normal text-muted-foreground">
                      ({totalResults} {totalResults === 1 ? "call" : "calls"} found)
                    </span>
                  )}
                </CardTitle>
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={useBulkActionsView ? "default" : "outline"}
                  onClick={() => setUseBulkActionsView(!useBulkActionsView)}
                  size="sm"
                >
                  {useBulkActionsView ? "Normal View" : "Bulk Actions"}
                </Button>
                <SaveSearchButton
                  filters={filters}
                  onSave={handleSaveSearch}
                />
                <ExportResults results={paginatedResults} />
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Sorting Options */}
            {!isLoading && totalResults > 0 && (
              <div className="border-b pb-4">
                <SortingOptions
                  sortField={sortField}
                  sortDirection={sortDirection}
                  onSortChange={(field, direction) => {
                    setSortField(field);
                    setSortDirection(direction);
                    setCurrentPage(1);
                  }}
                />
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="space-y-3">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            )}

            {/* Error State */}
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

            {/* Empty State */}
            {!isLoading && !error && totalResults === 0 && (
              <div className="text-center py-12">
                <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4 opacity-50" />
                <p className="text-lg font-medium text-muted-foreground">
                  No calls match your filters
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Try adjusting your search criteria or clearing some filters
                </p>
              </div>
            )}

            {/* Results Display */}
            {!isLoading && !error && totalResults > 0 && (
              <>
                {useBulkActionsView ? (
                  <BulkActions
                    results={paginatedResults}
                    selectedCount={0}
                    onSelectAll={() => {}}
                    onBulkAnalyze={(callIds) => {
                      toast({
                        title: "Bulk Analysis",
                        description: `Analyzing ${callIds.length} calls...`,
                      });
                    }}
                    onBulkExport={(results) => {
                      toast({
                        title: "Export Started",
                        description: `Exporting ${results.length} calls...`,
                      });
                    }}
                  />
                ) : (
                  <SearchResults results={paginatedResults} />
                )}

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="border-t pt-4">
                    <PaginationControls
                      currentPage={currentPage}
                      totalPages={totalPages}
                      pageSize={pageSize}
                      totalResults={totalResults}
                      onPageChange={setCurrentPage}
                      onPageSizeChange={(newSize) => {
                        setPageSize(newSize);
                        setCurrentPage(1);
                      }}
                    />
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Initial State - No Filters Set */}
      {!searchFilters && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <Filter className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">
                Set filters above or choose a quick filter preset to search for calls
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
