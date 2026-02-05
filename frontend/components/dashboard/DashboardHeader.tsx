"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RepInfo } from "@/types/coaching";
import { User, Calendar, TrendingUp } from "lucide-react";

interface DashboardHeaderProps {
  repInfo: RepInfo;
  overallScore?: number;
}

export function DashboardHeader({ repInfo, overallScore }: DashboardHeaderProps) {
  const formatDateRange = (start: string, end: string, period: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);

    const formatter = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });

    return `${formatter.format(startDate)} - ${formatter.format(endDate)}`;
  };

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-prefect-blue-light flex items-center justify-center">
            <User className="w-8 h-8 text-prefect-blue" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-prefect-dark">{repInfo.name}</h1>
            <p className="text-sm text-muted-foreground">{repInfo.email}</p>
            <p className="text-sm text-muted-foreground mt-1">
              <Badge variant="secondary">{repInfo.role}</Badge>
            </p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          {overallScore !== undefined && (
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-prefect-blue" />
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Average Score</p>
                <p className="text-3xl font-bold text-prefect-blue">{overallScore}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Period</p>
            <p className="text-sm font-medium">
              {formatDateRange(repInfo.date_range.start, repInfo.date_range.end, repInfo.date_range.period)}
            </p>
          </div>
        </div>

        <div>
          <p className="text-xs text-muted-foreground">Calls Analyzed</p>
          <p className="text-sm font-medium">{repInfo.calls_analyzed}</p>
        </div>

        {repInfo.product_filter && (
          <div>
            <p className="text-xs text-muted-foreground">Product Filter</p>
            <p className="text-sm font-medium capitalize">{repInfo.product_filter}</p>
          </div>
        )}
      </div>
    </Card>
  );
}
