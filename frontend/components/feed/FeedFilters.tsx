"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  FileText,
  TrendingUp,
  Award,
  Bell,
  Calendar,
  Filter,
} from "lucide-react";

export interface FeedFilterState {
  typeFilter: 'all' | 'call_analysis' | 'team_insight' | 'highlight' | 'milestone';
  timeFilter: 'today' | 'this_week' | 'this_month' | 'custom';
  startDate?: string;
  endDate?: string;
}

interface FeedFiltersProps {
  filters: FeedFilterState;
  onFiltersChange: (filters: FeedFilterState) => void;
  itemCounts?: {
    all: number;
    call_analysis: number;
    team_insight: number;
    highlight: number;
    milestone: number;
  };
  isManager?: boolean;
}

export function FeedFilters({
  filters,
  onFiltersChange,
  itemCounts,
  isManager = false,
}: FeedFiltersProps) {
  const [showCustomDateRange, setShowCustomDateRange] = useState(false);

  const typeFilters = [
    { value: 'all' as const, label: 'All', icon: Filter },
    { value: 'call_analysis' as const, label: 'Analyses', icon: FileText },
    ...(isManager ? [{ value: 'team_insight' as const, label: 'Insights', icon: TrendingUp }] : []),
    { value: 'highlight' as const, label: 'Highlights', icon: Award },
    { value: 'milestone' as const, label: 'Milestones', icon: Bell },
  ];

  const timeFilters = [
    { value: 'today' as const, label: 'Today' },
    { value: 'this_week' as const, label: 'This Week' },
    { value: 'this_month' as const, label: 'This Month' },
    { value: 'custom' as const, label: 'Custom Range' },
  ];

  const handleTypeChange = (type: FeedFilterState['typeFilter']) => {
    onFiltersChange({ ...filters, typeFilter: type });
  };

  const handleTimeChange = (time: FeedFilterState['timeFilter']) => {
    setShowCustomDateRange(time === 'custom');
    onFiltersChange({ ...filters, timeFilter: time });
  };

  const handleCustomDateChange = (startDate?: string, endDate?: string) => {
    onFiltersChange({ ...filters, startDate, endDate });
  };

  return (
    <Card>
      <CardContent className="pt-6 space-y-6">
        {/* Type Filter */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">Feed Type</Label>
          <div className="flex flex-wrap gap-2">
            {typeFilters.map((type) => {
              const Icon = type.icon;
              const count = itemCounts?.[type.value] ?? 0;
              const isActive = filters.typeFilter === type.value;

              return (
                <Button
                  key={type.value}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleTypeChange(type.value)}
                  className="gap-2"
                >
                  <Icon className="h-4 w-4" />
                  <span>{type.label}</span>
                  {itemCounts && (
                    <Badge
                      variant={isActive ? "secondary" : "outline"}
                      className="ml-1 text-xs"
                    >
                      {count}
                    </Badge>
                  )}
                </Button>
              );
            })}
          </div>
        </div>

        {/* Time Filter */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">Time Period</Label>
          <div className="flex flex-wrap gap-2">
            {timeFilters.map((time) => (
              <Button
                key={time.value}
                variant={filters.timeFilter === time.value ? "default" : "outline"}
                size="sm"
                onClick={() => handleTimeChange(time.value)}
                className="gap-2"
              >
                <Calendar className="h-4 w-4" />
                <span>{time.label}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Custom Date Range */}
        {showCustomDateRange && filters.timeFilter === 'custom' && (
          <div className="p-4 bg-muted/50 rounded-lg space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <Label htmlFor="start-date" className="text-xs mb-2 block">
                  Start Date
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={filters.startDate || ''}
                  onChange={(e) =>
                    handleCustomDateChange(e.target.value, filters.endDate)
                  }
                />
              </div>
              <div>
                <Label htmlFor="end-date" className="text-xs mb-2 block">
                  End Date
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={filters.endDate || ''}
                  onChange={(e) =>
                    handleCustomDateChange(filters.startDate, e.target.value)
                  }
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
