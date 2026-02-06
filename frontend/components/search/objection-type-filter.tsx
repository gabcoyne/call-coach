"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchCallsRequest } from "@/types/coaching";

const OBJECTION_TYPES = [
  { value: "pricing", label: "Pricing" },
  { value: "timing", label: "Timing" },
  { value: "technical", label: "Technical" },
  { value: "competitor", label: "Competitor" },
] as const;

interface ObjectionTypeFilterProps {
  filters: Partial<SearchCallsRequest>;
  onFiltersChange: (filters: Partial<SearchCallsRequest>) => void;
}

export function ObjectionTypeFilter({ filters, onFiltersChange }: ObjectionTypeFilterProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Objection Type</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Label htmlFor="objection-type">Filter by Objection Handled</Label>
          <Select
            value={filters.has_objection_type || ""}
            onValueChange={(value) =>
              onFiltersChange({
                ...filters,
                has_objection_type: value || undefined,
              })
            }
          >
            <SelectTrigger id="objection-type">
              <SelectValue placeholder="All Objection Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Objection Types</SelectItem>
              {OBJECTION_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            Find calls where specific objection types were handled
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
