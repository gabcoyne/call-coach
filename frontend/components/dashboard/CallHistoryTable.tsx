"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScoreBadge } from "@/components/ui/score-badge";
import { ArrowUpDown, ExternalLink } from "lucide-react";

interface CallHistoryItem {
  call_id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  overall_score: number | null;
}

interface CallHistoryTableProps {
  calls: CallHistoryItem[];
  onCallClick?: (callId: string) => void;
}

type SortField = 'date' | 'score' | 'duration';
type SortDirection = 'asc' | 'desc';

export function CallHistoryTable({ calls, onCallClick }: CallHistoryTableProps) {
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedCalls = [...calls].sort((a, b) => {
    let comparison = 0;

    switch (sortField) {
      case 'date':
        const dateA = a.date ? new Date(a.date).getTime() : 0;
        const dateB = b.date ? new Date(b.date).getTime() : 0;
        comparison = dateA - dateB;
        break;
      case 'score':
        comparison = (a.overall_score ?? 0) - (b.overall_score ?? 0);
        break;
      case 'duration':
        comparison = a.duration_seconds - b.duration_seconds;
        break;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (calls.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Call History</h3>
        <p className="text-sm text-muted-foreground">No calls found</p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Call History</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4 font-medium text-sm">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('date')}
                  className="gap-1 -ml-4"
                >
                  Date
                  <ArrowUpDown className="w-4 h-4" />
                </Button>
              </th>
              <th className="text-left py-3 px-4 font-medium text-sm">Title</th>
              <th className="text-left py-3 px-4 font-medium text-sm">Type</th>
              <th className="text-left py-3 px-4 font-medium text-sm">Product</th>
              <th className="text-left py-3 px-4 font-medium text-sm">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('duration')}
                  className="gap-1 -ml-4"
                >
                  Duration
                  <ArrowUpDown className="w-4 h-4" />
                </Button>
              </th>
              <th className="text-left py-3 px-4 font-medium text-sm">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('score')}
                  className="gap-1 -ml-4"
                >
                  Score
                  <ArrowUpDown className="w-4 h-4" />
                </Button>
              </th>
              <th className="text-left py-3 px-4 font-medium text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedCalls.map((call) => (
              <tr
                key={call.call_id}
                className="border-b hover:bg-gray-50 transition-colors"
              >
                <td className="py-3 px-4 text-sm text-muted-foreground">
                  {formatDate(call.date)}
                </td>
                <td className="py-3 px-4 text-sm font-medium max-w-xs truncate">
                  {call.title}
                </td>
                <td className="py-3 px-4 text-sm">
                  {call.call_type ? (
                    <Badge variant="outline" className="capitalize">
                      {call.call_type.replace('_', ' ')}
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground">N/A</span>
                  )}
                </td>
                <td className="py-3 px-4 text-sm">
                  {call.product ? (
                    <Badge variant="secondary" className="capitalize">
                      {call.product}
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground">N/A</span>
                  )}
                </td>
                <td className="py-3 px-4 text-sm text-muted-foreground">
                  {formatDuration(call.duration_seconds)}
                </td>
                <td className="py-3 px-4">
                  {call.overall_score !== null ? (
                    <ScoreBadge score={call.overall_score} />
                  ) : (
                    <span className="text-sm text-muted-foreground">N/A</span>
                  )}
                </td>
                <td className="py-3 px-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onCallClick?.(call.call_id)}
                    className="gap-1"
                  >
                    View
                    <ExternalLink className="w-3 h-3" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
