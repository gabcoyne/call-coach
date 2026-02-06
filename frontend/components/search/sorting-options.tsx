"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { ArrowUpDown } from "lucide-react";

export type SortField = "date" | "score" | "duration";
export type SortDirection = "asc" | "desc";

interface SortingOptionsProps {
  sortField: SortField;
  sortDirection: SortDirection;
  onSortChange: (field: SortField, direction: SortDirection) => void;
}

export function SortingOptions({ sortField, sortDirection, onSortChange }: SortingOptionsProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
        <Label htmlFor="sort-field" className="text-sm">
          Sort by:
        </Label>
      </div>
      <div className="flex gap-2">
        <Select
          value={sortField}
          onValueChange={(value) => onSortChange(value as SortField, sortDirection)}
        >
          <SelectTrigger id="sort-field" className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="score">Score</SelectItem>
            <SelectItem value="duration">Duration</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={sortDirection}
          onValueChange={(value) => onSortChange(sortField, value as SortDirection)}
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Descending</SelectItem>
            <SelectItem value="asc">Ascending</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
