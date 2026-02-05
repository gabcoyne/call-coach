"use client";

import { useState, useMemo } from "react";
import { useUser } from "@clerk/nextjs";
import { SearchCallsRequest, CallSearchResult } from "@/types/coaching";
import { useSearchCalls } from "@/lib/hooks/use-search-calls";

// Search components
import { MultiCriteriaFilterForm } from "@/components/search/multi-criteria-filter-form";
import { ScoreThresholdFilters } from "@/components/search/score-threshold-filters";
import { ObjectionTypeFilter } from "@/components/search/objection-type-filter";
import { TopicKeywordFilter } from "@/components/search/topic-keyword-filter";
import { SearchResults } from "@/components/search/search-results";
import { SortingOptions, SortField, SortDirection } from "@/components/search/sorting-options";
import { PaginationControls } from "@/components/search/pagination-controls";
import { SaveSearchButton } from "@/components/search/save-search-button";
import { LoadSavedSearches } from "@/components/search/load-saved-searches";
import { ExportResults } from "@/components/search/export-results";
import { QuickFilterPresets } from "@/components/search/quick-filter-presets";

// UI components
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Search, Filter } from "lucide-react";

export default function CallSearchPage() {
  const { user } = useUser();
  const userEmail = user?.emailAddresses[0]?.emailAddress;

  // Filter state
  const [filters, setFilters] = useState<Partial<SearchCallsRequest>>({
    limit: 20,
  });

  // Sorting state
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Search trigger - only search when user clicks search button
  const [searchFilters, setSearchFilters] = useState<SearchCallsRequest | null>(
    null
  );

  // Fetch data using SWR hook
  const { data, error, isLoading } = useSearchCalls(searchFilters);

  // Handle search submission
  const handleSearch = () => {
    setSearchFilters({
      ...filters,
      limit: 100, // Fetch more results for client-side pagination
    } as SearchCallsRequest);
    setCurrentPage(1); // Reset to first page
  };

  // Handle filter changes
  const handleFiltersChange = (newFilters: Partial<SearchCallsRequest>) => {
    setFilters(newFilters);
  };

  // Handle filter reset
  const handleReset = () => {
    setFilters({ limit: 20 });
    setSearchFilters(null);
    setCurrentPage(1);
  };

  // Handle preset selection
  const handlePresetSelect = (presetFilters: Partial<SearchCallsRequest>) => {
    setFilters(presetFilters);
    // Auto-search when preset is selected
    setSearchFilters(presetFilters as SearchCallsRequest);
    setCurrentPage(1);
  };

  // Handle load saved search
  const handleLoadSavedSearch = (savedFilters: Partial<SearchCallsRequest>) => {
    setFilters(savedFilters);
    // Auto-search when loading saved search
    setSearchFilters(savedFilters as SearchCallsRequest);
    setCurrentPage(1);
  };

  // Handle page size change
  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // Reset to first page
  };

  // Sort and paginate results
  const processedResults = useMemo(() => {
    if (!data) return [];

    let sorted = [...data];

    // Sort
    sorted.sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case "date":
          const dateA = a.date ? new Date(a.date).getTime() : 0;
          const dateB = b.date ? new Date(b.date).getTime() : 0;
          comparison = dateA - dateB;
          break;
        case "score":
          const scoreA = a.overall_score ?? -1;
          const scoreB = b.overall_score ?? -1;
          comparison = scoreA - scoreB;
          break;
        case "duration":
          comparison = a.duration_seconds - b.duration_seconds;
          break;
      }

      return sortDirection === "asc" ? comparison : -comparison;
    });

    // Paginate
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sorted.slice(startIndex, endIndex);
  }, [data, sortField, sortDirection, currentPage, pageSize]);

  const totalPages = Math.ceil((data?.length || 0) / pageSize);

  return (
    <div className="container mx-auto py-8 px-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Call Search</h1>
          <p className="text-muted-foreground mt-1">
            Search and filter coaching call analyses
          </p>
        </div>
      </div>

      {/* Quick Filter Presets */}
      <QuickFilterPresets
        onPresetSelect={handlePresetSelect}
        currentUserEmail={userEmail}
      />

      {/* Load Saved Searches */}
      <Card>
        <CardContent className="pt-6">
          <LoadSavedSearches onLoad={handleLoadSavedSearch} />
        </CardContent>
      </Card>

      {/* Filter Forms */}
      <div className="space-y-4">
        <MultiCriteriaFilterForm
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onReset={handleReset}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ScoreThresholdFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />
          <ObjectionTypeFilter
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />
        </div>

        <TopicKeywordFilter
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      </div>

      {/* Search Actions */}
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={handleSearch} variant="prefect" size="lg">
          <Search className="h-4 w-4 mr-2" />
          Search Calls
        </Button>
        <SaveSearchButton filters={filters} />
        {data && data.length > 0 && <ExportResults results={data} />}
      </div>

      {/* Results Section */}
      {searchFilters && (
        <div className="space-y-4">
          {/* Sorting and Actions Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <SortingOptions
              sortField={sortField}
              sortDirection={sortDirection}
              onSortChange={(field, direction) => {
                setSortField(field);
                setSortDirection(direction);
              }}
            />
          </div>

          {/* Error State */}
          {error && (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-destructive">
                  <p className="text-lg font-medium">Error loading results</p>
                  <p className="mt-2">{error.message}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {!error && (
            <>
              <SearchResults results={processedResults} isLoading={isLoading} />

              {/* Pagination */}
              {data && data.length > 0 && (
                <PaginationControls
                  currentPage={currentPage}
                  totalPages={totalPages}
                  pageSize={pageSize}
                  totalResults={data.length}
                  onPageChange={setCurrentPage}
                  onPageSizeChange={handlePageSizeChange}
                />
              )}
            </>
          )}
        </div>
      )}

      {/* Initial State - No Search Yet */}
      {!searchFilters && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <Filter className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">
                Configure filters and click Search to find calls
              </p>
              <p className="mt-2">
                Or select a quick filter preset above to get started
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
