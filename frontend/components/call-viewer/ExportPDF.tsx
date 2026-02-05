"use client";

import { useState } from "react";
import { FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ExportPDFProps {
  callId: string;
  callTitle?: string;
  className?: string;
}

export function ExportPDF({ callId, callTitle, className }: ExportPDFProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);

    try {
      // TODO: Implement PDF export functionality
      // Options:
      // 1. Use react-pdf or jsPDF to generate client-side
      // 2. Call backend API to generate PDF server-side
      // 3. Use browser print dialog with custom CSS

      // For now, trigger browser print dialog
      if (typeof window !== "undefined") {
        window.print();
      }
    } catch (error) {
      console.error("Failed to export PDF:", error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Button
      onClick={handleExport}
      variant="outline"
      disabled={isExporting}
      className={className}
    >
      <FileDown className="h-4 w-4 mr-2" />
      {isExporting ? "Exporting..." : "Export PDF"}
    </Button>
  );
}
