"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchCallsRequest } from "@/types/coaching";
import { X } from "lucide-react";

interface MultiCriteriaFilterFormProps {
  filters: Partial<SearchCallsRequest>;
  onFiltersChange: (filters: Partial<SearchCallsRequest>) => void;
  onReset: () => void;
}

export function MultiCriteriaFilterForm({
  filters,
  onFiltersChange,
  onReset,
}: MultiCriteriaFilterFormProps) {
  const updateFilter = (key: keyof SearchCallsRequest, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
    });
  };

  const updateDateRange = (field: "start" | "end", value: string) => {
    const newDateRange = {
      start: filters.date_range?.start || "",
      end: filters.date_range?.end || "",
      [field]: value,
    };

    // Only set date_range if both start and end are provided
    if (newDateRange.start && newDateRange.end) {
      onFiltersChange({
        ...filters,
        date_range: {
          start: newDateRange.start,
          end: newDateRange.end,
        },
      });
    } else if (!value) {
      // Remove date_range if field is cleared
      const { date_range, ...rest } = filters;
      onFiltersChange(rest);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Search Filters</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-8 px-2"
          >
            <X className="h-4 w-4 mr-1" />
            Reset
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Rep Email */}
          <div className="space-y-2">
            <Label htmlFor="rep-email">Rep Email</Label>
            <Input
              id="rep-email"
              type="email"
              placeholder="rep@example.com"
              value={filters.rep_email || ""}
              onChange={(e) => updateFilter("rep_email", e.target.value)}
            />
          </div>

          {/* Product Filter */}
          <div className="space-y-2">
            <Label htmlFor="product">Product</Label>
            <Select
              value={filters.product || ""}
              onValueChange={(value) => updateFilter("product", value)}
            >
              <SelectTrigger id="product">
                <SelectValue placeholder="All Products" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Products</SelectItem>
                <SelectItem value="prefect">Prefect</SelectItem>
                <SelectItem value="horizon">Horizon</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Call Type Filter */}
          <div className="space-y-2">
            <Label htmlFor="call-type">Call Type</Label>
            <Select
              value={filters.call_type || ""}
              onValueChange={(value) => updateFilter("call_type", value)}
            >
              <SelectTrigger id="call-type">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="discovery">Discovery</SelectItem>
                <SelectItem value="demo">Demo</SelectItem>
                <SelectItem value="technical_deep_dive">
                  Technical Deep Dive
                </SelectItem>
                <SelectItem value="negotiation">Negotiation</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date Range Start */}
          <div className="space-y-2">
            <Label htmlFor="date-start">Start Date</Label>
            <Input
              id="date-start"
              type="datetime-local"
              value={
                filters.date_range?.start
                  ? new Date(filters.date_range.start)
                      .toISOString()
                      .slice(0, 16)
                  : ""
              }
              onChange={(e) => {
                const value = e.target.value
                  ? new Date(e.target.value).toISOString()
                  : "";
                updateDateRange("start", value);
              }}
            />
          </div>

          {/* Date Range End */}
          <div className="space-y-2">
            <Label htmlFor="date-end">End Date</Label>
            <Input
              id="date-end"
              type="datetime-local"
              value={
                filters.date_range?.end
                  ? new Date(filters.date_range.end).toISOString().slice(0, 16)
                  : ""
              }
              onChange={(e) => {
                const value = e.target.value
                  ? new Date(e.target.value).toISOString()
                  : "";
                updateDateRange("end", value);
              }}
            />
          </div>

          {/* Results Limit */}
          <div className="space-y-2">
            <Label htmlFor="limit">Results Per Page</Label>
            <Select
              value={String(filters.limit || 20)}
              onValueChange={(value) => updateFilter("limit", Number(value))}
            >
              <SelectTrigger id="limit">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
