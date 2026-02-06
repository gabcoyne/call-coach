"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { CallSearchResult } from "@/types/coaching";
import { Download, FileSpreadsheet, FileText } from "lucide-react";

interface ExportResultsProps {
  results: CallSearchResult[];
}

export function ExportResults({ results }: ExportResultsProps) {
  const exportToCSV = () => {
    if (!results || results.length === 0) return;

    // Create CSV header
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

    // Create CSV rows
    const rows = results.map((result) => [
      result.call_id,
      `"${result.title.replace(/"/g, '""')}"`, // Escape quotes
      result.date || "",
      result.duration_seconds,
      result.call_type || "",
      result.product || "",
      result.overall_score ?? "",
      `"${result.customer_names.join(", ")}"`,
      `"${result.prefect_reps.join(", ")}"`,
    ]);

    // Combine headers and rows
    const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    downloadBlob(blob, "call-search-results.csv");
  };

  const exportToExcel = () => {
    // For Excel, we'll use the same CSV format but with .xlsx extension
    // In a production app, you'd use a library like xlsx or exceljs
    exportToCSV();
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const disabled = !results || results.length === 0;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={disabled}>
          <Download className="h-4 w-4 mr-2" />
          Export Results
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={exportToCSV}>
          <FileText className="h-4 w-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToExcel}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Export as Excel
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
