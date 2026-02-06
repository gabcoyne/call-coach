"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { CallSearchResult } from "@/types/coaching";
import {
  CheckSquare2,
  Download,
  BarChart3,
  Trash2,
  FileText,
  AlertCircle,
} from "lucide-react";

interface BulkActionsProps {
  results: CallSearchResult[];
  selectedCount: number;
  onSelectAll: (selected: boolean) => void;
  onBulkAnalyze?: (callIds: string[]) => void;
  onBulkExport?: (results: CallSearchResult[]) => void;
}

export function BulkActions({
  results,
  selectedCount,
  onSelectAll,
  onBulkAnalyze,
  onBulkExport,
}: BulkActionsProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const allSelected = selectedIds.size === results.length && results.length > 0;

  const handleSelectAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
      onSelectAll(false);
    } else {
      const newSelected = new Set(results.map((r) => r.call_id));
      setSelectedIds(newSelected);
      onSelectAll(true);
    }
  };

  const handleSelectResult = (callId: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(callId)) {
      newSelected.delete(callId);
    } else {
      newSelected.add(callId);
    }
    setSelectedIds(newSelected);
  };

  const selectedCallIds = Array.from(selectedIds);
  const selectedResults = results.filter((r) => selectedIds.has(r.call_id));

  const exportToCSV = () => {
    if (selectedResults.length === 0) return;

    const headers = [
      "Call ID",
      "Title",
      "Date",
      "Duration (seconds)",
      "Call Type",
      "Product",
      "Overall Score",
      "Customer Names",
      "Prefect Reps",
    ];

    const rows = selectedResults.map((result) => [
      result.call_id,
      `"${result.title.replace(/"/g, '""')}"`,
      result.date || "",
      result.duration_seconds,
      result.call_type || "",
      result.product || "",
      result.overall_score ?? "",
      `"${result.customer_names.join(", ")}"`,
      `"${result.prefect_reps.join(", ")}"`,
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = `call-analysis-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToJSON = () => {
    if (selectedResults.length === 0) return;

    const jsonContent = JSON.stringify(selectedResults, null, 2);
    const blob = new Blob([jsonContent], {
      type: "application/json;charset=utf-8;",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = `call-analysis-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Bulk Selection Bar */}
      {results.length > 0 && (
        <Card className="bg-muted/50">
          <CardContent className="py-4">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={handleSelectAll}
                  aria-label="Select all results"
                />
                <span className="text-sm font-medium">
                  {allSelected
                    ? `All ${results.length} selected`
                    : `${selectedIds.size} of ${results.length} selected`}
                </span>
              </div>

              {selectedIds.size > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {onBulkAnalyze && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onBulkAnalyze(selectedCallIds)}
                      className="gap-2"
                    >
                      <BarChart3 className="h-4 w-4" />
                      Analyze ({selectedIds.size})
                    </Button>
                  )}

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-2"
                        disabled={selectedIds.size === 0}
                      >
                        <Download className="h-4 w-4" />
                        Export ({selectedIds.size})
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={exportToCSV}>
                        <FileText className="h-4 w-4 mr-2" />
                        Export as CSV
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={exportToJSON}>
                        <FileText className="h-4 w-4 mr-2" />
                        Export as JSON
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results with Selection Checkboxes */}
      {results.length > 0 && (
        <div className="space-y-2">
          {results.map((result) => (
            <Card key={result.call_id} className="hover:shadow-sm transition-shadow">
              <CardContent className="py-3">
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={selectedIds.has(result.call_id)}
                    onCheckedChange={() => handleSelectResult(result.call_id)}
                    aria-label={`Select ${result.title}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{result.title}</div>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div>
                        {result.date &&
                          new Date(result.date).toLocaleDateString()}{" "}
                        • {result.call_type}
                      </div>
                      <div>
                        {result.prefect_reps.join(", ")} •{" "}
                        {result.duration_seconds
                          ? `${Math.round(result.duration_seconds / 60)} min`
                          : "N/A"}
                      </div>
                    </div>
                  </div>
                  {result.overall_score !== null && (
                    <div className="text-right">
                      <div className="font-semibold text-lg">
                        {result.overall_score}
                      </div>
                      <div className="text-xs text-muted-foreground">Score</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {results.length === 0 && (
        <Card>
          <CardContent className="py-8">
            <div className="text-center text-muted-foreground">
              <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No results to display</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
