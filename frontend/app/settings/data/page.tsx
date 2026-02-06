"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Download, Loader, AlertCircle, CheckCircle } from "lucide-react";

type DataExportFormat = "csv" | "json";
type DataRetention = "30" | "90" | "180" | "365" | "indefinite";

export default function DataPage() {
  const [exportFormat, setExportFormat] = useState<DataExportFormat>("csv");
  const [includeCallRecordings, setIncludeCallRecordings] = useState(false);
  const [includeTranscripts, setIncludeTranscripts] = useState(true);
  const [includeCoachingFeedback, setIncludeCoachingFeedback] = useState(true);
  const [retentionDays, setRetentionDays] = useState<DataRetention>("180");
  const [exporting, setExporting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleExportData = async () => {
    setExporting(true);
    try {
      const response = await fetch("/api/user/data/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          format: exportFormat,
          includeCallRecordings,
          includeTranscripts,
          includeCoachingFeedback,
        }),
      });

      if (!response.ok) throw new Error("Export failed");

      // Create download link
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `call-coach-data-export.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setMessage({
        type: "success",
        text: `Data exported successfully as ${exportFormat.toUpperCase()}`,
      });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error("Export failed:", error);
      setMessage({ type: "error", text: "Failed to export data" });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setExporting(false);
    }
  };

  const handleRetentionUpdate = async () => {
    try {
      const response = await fetch("/api/user/preferences", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataRetentionDays: retentionDays === "indefinite" ? null : parseInt(retentionDays),
        }),
      });

      if (!response.ok) throw new Error("Failed to update retention policy");

      setMessage({ type: "success", text: "Data retention policy updated" });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error("Update failed:", error);
      setMessage({ type: "error", text: "Failed to update retention policy" });
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const getRetentionDescription = (days: DataRetention) => {
    const descriptions: Record<DataRetention, string> = {
      "30": "Your data will be automatically deleted after 30 days",
      "90": "Your data will be automatically deleted after 90 days",
      "180": "Your data will be automatically deleted after 6 months",
      "365": "Your data will be automatically deleted after 1 year",
      indefinite: "Your data will be retained indefinitely",
    };
    return descriptions[days];
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Data & Privacy</h1>
        <p className="text-muted-foreground mt-1">
          Export your data and manage your privacy preferences
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center gap-2 ${message.type === "success" ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
          {message.type === "success" ? (
            <CheckCircle className="h-5 w-5 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
          )}
          {message.text}
        </div>
      )}

      {/* Data Export Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Your Data
          </CardTitle>
          <CardDescription>
            Download all your personal data and coaching history (GDPR compliant)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Export Format */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="format">Export Format</Label>
              <Select value={exportFormat} onValueChange={(value) => setExportFormat(value as DataExportFormat)}>
                <SelectTrigger id="format" className="w-full mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV (Spreadsheet compatible)</SelectItem>
                  <SelectItem value="json">JSON (Complete data structure)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Data Includes */}
            <div className="space-y-3 pt-4 border-t border-border">
              <Label className="font-semibold">Include in Export</Label>

              <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
                <Checkbox
                  id="transcripts"
                  checked={includeTranscripts}
                  onCheckedChange={(checked) => setIncludeTranscripts(checked as boolean)}
                />
                <div className="flex-1 min-w-0">
                  <Label htmlFor="transcripts" className="font-medium cursor-pointer">
                    Call Transcripts
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Transcripts of all your recorded coaching calls
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
                <Checkbox
                  id="feedback"
                  checked={includeCoachingFeedback}
                  onCheckedChange={(checked) => setIncludeCoachingFeedback(checked as boolean)}
                />
                <div className="flex-1 min-w-0">
                  <Label htmlFor="feedback" className="font-medium cursor-pointer">
                    Coaching Feedback
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    All coaching insights and feedback from AI analysis
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
                <Checkbox
                  id="recordings"
                  checked={includeCallRecordings}
                  onCheckedChange={(checked) => setIncludeCallRecordings(checked as boolean)}
                />
                <div className="flex-1 min-w-0">
                  <Label htmlFor="recordings" className="font-medium cursor-pointer">
                    Call Recordings
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Audio files of your recorded calls (may be large)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Button onClick={handleExportData} disabled={exporting} className="w-full">
            {exporting ? (
              <>
                <Loader className="h-4 w-4 mr-2 animate-spin" />
                Preparing Export...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Download Your Data
              </>
            )}
          </Button>

          <p className="text-xs text-muted-foreground">
            Your export will contain all your personal data and coaching history. This complies
            with GDPR and other data protection regulations.
          </p>
        </CardContent>
      </Card>

      {/* Data Retention Policy */}
      <Card>
        <CardHeader>
          <CardTitle>Data Retention Policy</CardTitle>
          <CardDescription>
            Automatically delete your data after a specified period
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="retention">Retention Period</Label>
            <Select value={retentionDays} onValueChange={(value) => setRetentionDays(value as DataRetention)}>
              <SelectTrigger id="retention" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="30">30 Days</SelectItem>
                <SelectItem value="90">90 Days (3 Months)</SelectItem>
                <SelectItem value="180">180 Days (6 Months)</SelectItem>
                <SelectItem value="365">365 Days (1 Year)</SelectItem>
                <SelectItem value="indefinite">Indefinite (Keep Forever)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-foreground font-medium">
              {getRetentionDescription(retentionDays)}
            </p>
          </div>

          <Button onClick={handleRetentionUpdate} variant="outline" className="w-full">
            Update Retention Policy
          </Button>

          <p className="text-xs text-muted-foreground">
            After the retention period expires, your coaching sessions, transcripts, and feedback
            will be automatically and permanently deleted.
          </p>
        </CardContent>
      </Card>

      {/* Privacy Information */}
      <Card>
        <CardHeader>
          <CardTitle>Privacy Information</CardTitle>
          <CardDescription>How we handle your data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div>
              <h4 className="font-semibold text-sm text-foreground mb-1">Data Encryption</h4>
              <p className="text-sm text-muted-foreground">
                All your data is encrypted in transit and at rest using industry-standard encryption.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-foreground mb-1">Access Controls</h4>
              <p className="text-sm text-muted-foreground">
                Only authorized personnel can access your data, and all access is logged for audit purposes.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-foreground mb-1">No Third-Party Sharing</h4>
              <p className="text-sm text-muted-foreground">
                We never share your personal data with third parties without your explicit consent.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-foreground mb-1">GDPR Compliance</h4>
              <p className="text-sm text-muted-foreground">
                We comply with GDPR and other data protection regulations. You can request data deletion
                at any time.
              </p>
            </div>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              For more information about our privacy practices, please review our{" "}
              <a href="/privacy" className="font-semibold underline hover:no-underline">
                Privacy Policy
              </a>
              .
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-red-600">Danger Zone</CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-900 font-medium mb-3">
              Delete All Your Data
            </p>
            <p className="text-sm text-red-800 mb-4">
              This action will permanently delete all your personal data, coaching sessions, transcripts,
              and feedback. This cannot be undone.
            </p>
            <Button variant="destructive" className="w-full">
              Delete All My Data
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
