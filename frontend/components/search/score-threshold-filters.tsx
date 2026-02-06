"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchCallsRequest } from "@/types/coaching";

interface ScoreThresholdFiltersProps {
  filters: Partial<SearchCallsRequest>;
  onFiltersChange: (filters: Partial<SearchCallsRequest>) => void;
}

export function ScoreThresholdFilters({ filters, onFiltersChange }: ScoreThresholdFiltersProps) {
  const updateFilter = (key: keyof SearchCallsRequest, value: string) => {
    const numValue = value ? Number(value) : undefined;
    onFiltersChange({
      ...filters,
      [key]: numValue,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Score Filters</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Minimum Score */}
          <div className="space-y-2">
            <Label htmlFor="min-score">Minimum Overall Score (0-100)</Label>
            <Input
              id="min-score"
              type="number"
              min="0"
              max="100"
              placeholder="0"
              value={filters.min_score ?? ""}
              onChange={(e) => updateFilter("min_score", e.target.value)}
            />
          </div>

          {/* Maximum Score */}
          <div className="space-y-2">
            <Label htmlFor="max-score">Maximum Overall Score (0-100)</Label>
            <Input
              id="max-score"
              type="number"
              min="0"
              max="100"
              placeholder="100"
              value={filters.max_score ?? ""}
              onChange={(e) => updateFilter("max_score", e.target.value)}
            />
          </div>
        </div>

        <div className="mt-4 text-sm text-muted-foreground">
          <p>Filter calls by overall performance score. Leave blank for no restriction.</p>
          {filters.min_score !== undefined && filters.max_score !== undefined && (
            <p className="mt-2 font-medium text-foreground">
              Showing calls with scores between {filters.min_score} and {filters.max_score}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
