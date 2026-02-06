"use client";

import { useState } from "react";
import { Download, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { AnalyzeCallResponse } from "@/types/coaching";

interface ExportCoachingReportProps {
  analysis: AnalyzeCallResponse;
  callTitle: string;
}

export function ExportCoachingReport({
  analysis,
  callTitle,
}: ExportCoachingReportProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const handleExportPDF = async () => {
    setIsExporting(true);
    setExportError(null);

    try {
      // Dynamically import html2pdf
      const html2pdf = (await import("html2pdf.js")).default;

      const element = document.createElement("div");
      element.style.padding = "20px";
      element.style.fontFamily = "Arial, sans-serif";

      // Build HTML content
      const metadata = analysis.call_metadata;
      const scores = analysis.scores;

      element.innerHTML = `
        <html>
          <head>
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; }
              h1 { color: #1f2937; font-size: 28px; margin-bottom: 20px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
              h2 { color: #374151; font-size: 18px; margin-top: 20px; margin-bottom: 12px; }
              .metadata { background: #f3f4f6; padding: 12px; border-radius: 8px; margin-bottom: 20px; }
              .metadata-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
              .metadata-label { font-weight: bold; color: #6b7280; }
              .metadata-value { color: #1f2937; }
              .scores { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
              .score-card { background: #f9fafb; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; }
              .score-value { font-size: 32px; font-weight: bold; color: #3b82f6; }
              .score-label { color: #6b7280; font-size: 14px; margin-top: 4px; }
              .strengths, .improvements, .action-items { margin-bottom: 20px; }
              .strengths h3 { color: #059669; margin-bottom: 8px; }
              .improvements h3 { color: #d97706; margin-bottom: 8px; }
              .action-items h3 { color: #1f2937; margin-bottom: 8px; }
              ul { margin-left: 20px; }
              li { margin-bottom: 6px; }
              .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #d1d5db; color: #6b7280; font-size: 12px; }
            </style>
          </head>
          <body>
            <h1>Coaching Report: ${callTitle}</h1>

            <div class="metadata">
              <div class="metadata-row">
                <span class="metadata-label">Date:</span>
                <span class="metadata-value">${formatDate(metadata.date)}</span>
              </div>
              <div class="metadata-row">
                <span class="metadata-label">Duration:</span>
                <span class="metadata-value">${formatDuration(metadata.duration_seconds)}</span>
              </div>
              <div class="metadata-row">
                <span class="metadata-label">Call Type:</span>
                <span class="metadata-value">${metadata.call_type || "N/A"}</span>
              </div>
              <div class="metadata-row">
                <span class="metadata-label">Product:</span>
                <span class="metadata-value">${metadata.product || "N/A"}</span>
              </div>
              <div class="metadata-row">
                <span class="metadata-label">Participants:</span>
                <span class="metadata-value">${metadata.participants.length} people</span>
              </div>
            </div>

            <h2>Performance Scores</h2>
            <div class="scores">
              <div class="score-card">
                <div class="score-value">${scores.overall}</div>
                <div class="score-label">Overall Score</div>
              </div>
              ${scores.product_knowledge !== null && scores.product_knowledge !== undefined ? `
                <div class="score-card">
                  <div class="score-value">${scores.product_knowledge}</div>
                  <div class="score-label">Product Knowledge</div>
                </div>
              ` : ""}
              ${scores.discovery !== null && scores.discovery !== undefined ? `
                <div class="score-card">
                  <div class="score-value">${scores.discovery}</div>
                  <div class="score-label">Discovery</div>
                </div>
              ` : ""}
              ${scores.objection_handling !== null && scores.objection_handling !== undefined ? `
                <div class="score-card">
                  <div class="score-value">${scores.objection_handling}</div>
                  <div class="score-label">Objection Handling</div>
                </div>
              ` : ""}
              ${scores.engagement !== null && scores.engagement !== undefined ? `
                <div class="score-card">
                  <div class="score-value">${scores.engagement}</div>
                  <div class="score-label">Engagement</div>
                </div>
              ` : ""}
            </div>

            ${analysis.strengths && analysis.strengths.length > 0 ? `
              <div class="strengths">
                <h2>Strengths</h2>
                <ul>
                  ${analysis.strengths.map((s) => `<li>${s}</li>`).join("")}
                </ul>
              </div>
            ` : ""}

            ${analysis.areas_for_improvement && analysis.areas_for_improvement.length > 0 ? `
              <div class="improvements">
                <h2>Areas for Improvement</h2>
                <ul>
                  ${analysis.areas_for_improvement.map((a) => `<li>${a}</li>`).join("")}
                </ul>
              </div>
            ` : ""}

            ${analysis.action_items && analysis.action_items.length > 0 ? `
              <div class="action-items">
                <h2>Action Items</h2>
                <ul>
                  ${analysis.action_items.map((item) => `<li>${item}</li>`).join("")}
                </ul>
              </div>
            ` : ""}

            <div class="footer">
              <p>Generated on ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })} at ${new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}</p>
            </div>
          </body>
        </html>
      `;

      const options = {
        margin: 10,
        filename: `${callTitle.replace(/\s+/g, "_")}_coaching_report.pdf`,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { orientation: "portrait", unit: "mm", format: "a4" },
      };

      html2pdf().set(options).from(element).save();
    } catch (error) {
      console.error("Error exporting PDF:", error);
      setExportError("Failed to export PDF. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div>
      <Button
        onClick={handleExportPDF}
        disabled={isExporting}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        {isExporting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Exporting...
          </>
        ) : (
          <>
            <Download className="h-4 w-4" />
            Export as PDF
          </>
        )}
      </Button>
      {exportError && (
        <p className="text-xs text-red-600 mt-2">{exportError}</p>
      )}
    </div>
  );
}
