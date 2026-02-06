"use client";

import { useState, useEffect } from "react";
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
import { Bell, Loader, Slack } from "lucide-react";

type NotificationPreferences = {
  weeklyReports: boolean;
  coachingUpdates: boolean;
  callAnalysis: boolean;
  opportunityInsights: boolean;
  slackIntegration: boolean;
  notificationFrequency: "daily" | "weekly" | "monthly";
};

export default function NotificationsPage() {
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    weeklyReports: true,
    coachingUpdates: true,
    callAnalysis: true,
    opportunityInsights: true,
    slackIntegration: false,
    notificationFrequency: "weekly",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    // Load preferences from API
    const loadPreferences = async () => {
      try {
        const response = await fetch("/api/user/preferences", {
          method: "GET",
        });

        if (response.ok) {
          const data = await response.json();
          setPreferences({
            weeklyReports: data.weeklyReports ?? true,
            coachingUpdates: data.coachingUpdates ?? true,
            callAnalysis: data.callAnalysis ?? true,
            opportunityInsights: data.opportunityInsights ?? true,
            slackIntegration: data.slackIntegration ?? false,
            notificationFrequency: data.notificationFrequency ?? "weekly",
          });
        }
      } catch (error) {
        console.error("Failed to load preferences:", error);
      } finally {
        setLoading(false);
      }
    };

    loadPreferences();
  }, []);

  const handleToggle = (key: keyof NotificationPreferences) => {
    setPreferences((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleFrequencyChange = (value: string) => {
    setPreferences((prev) => ({
      ...prev,
      notificationFrequency: value as "daily" | "weekly" | "monthly",
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch("/api/user/preferences", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) throw new Error("Failed to save preferences");

      setMessage({ type: "success", text: "Notification preferences saved" });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error("Failed to save preferences:", error);
      setMessage({ type: "error", text: "Failed to save preferences" });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Notification Settings</h1>
        <p className="text-muted-foreground mt-1">Manage how and when you receive notifications</p>
      </div>

      {/* Status Message */}
      {message && (
        <div
          className={`p-4 rounded-lg ${
            message.type === "success"
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-red-50 text-red-700 border border-red-200"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Notification Frequency */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Frequency
          </CardTitle>
          <CardDescription>How often you want to receive summary notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="frequency">Summary Frequency</Label>
            <Select value={preferences.notificationFrequency} onValueChange={handleFrequencyChange}>
              <SelectTrigger id="frequency" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="text-sm text-muted-foreground">
            Select how often you'd like to receive summary emails with all your updates.
          </p>
        </CardContent>
      </Card>

      {/* Email Notification Types */}
      <Card>
        <CardHeader>
          <CardTitle>Email Notifications</CardTitle>
          <CardDescription>
            Choose which notifications you want to receive via email
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
            <Checkbox
              id="weeklyReports"
              checked={preferences.weeklyReports}
              onCheckedChange={() => handleToggle("weeklyReports")}
            />
            <div className="flex-1 min-w-0">
              <Label htmlFor="weeklyReports" className="font-semibold cursor-pointer">
                Weekly Summary Reports
              </Label>
              <p className="text-sm text-muted-foreground mt-1">
                Get a comprehensive summary of your coaching sessions and progress each week
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
            <Checkbox
              id="coachingUpdates"
              checked={preferences.coachingUpdates}
              onCheckedChange={() => handleToggle("coachingUpdates")}
            />
            <div className="flex-1 min-w-0">
              <Label htmlFor="coachingUpdates" className="font-semibold cursor-pointer">
                Coaching Updates
              </Label>
              <p className="text-sm text-muted-foreground mt-1">
                Receive notifications when new coaching insights and feedback are available
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
            <Checkbox
              id="callAnalysis"
              checked={preferences.callAnalysis}
              onCheckedChange={() => handleToggle("callAnalysis")}
            />
            <div className="flex-1 min-w-0">
              <Label htmlFor="callAnalysis" className="font-semibold cursor-pointer">
                Call Analysis Results
              </Label>
              <p className="text-sm text-muted-foreground mt-1">
                Get notified when AI analysis of your recorded calls is complete
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
            <Checkbox
              id="opportunityInsights"
              checked={preferences.opportunityInsights}
              onCheckedChange={() => handleToggle("opportunityInsights")}
            />
            <div className="flex-1 min-w-0">
              <Label htmlFor="opportunityInsights" className="font-semibold cursor-pointer">
                Opportunity Insights
              </Label>
              <p className="text-sm text-muted-foreground mt-1">
                Receive coaching suggestions related to specific sales opportunities
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Slack Integration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Slack className="h-5 w-5" />
            Slack Integration
          </CardTitle>
          <CardDescription>Connect Call Coach to your Slack workspace</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors">
            <Checkbox
              id="slackIntegration"
              checked={preferences.slackIntegration}
              onCheckedChange={() => handleToggle("slackIntegration")}
            />
            <div className="flex-1 min-w-0">
              <Label htmlFor="slackIntegration" className="font-semibold cursor-pointer">
                Enable Slack Notifications
              </Label>
              <p className="text-sm text-muted-foreground mt-1">
                Receive coaching updates and insights directly in your Slack workspace
              </p>
            </div>
          </div>

          {preferences.slackIntegration && (
            <div className="p-4 bg-muted rounded-lg space-y-3">
              <p className="text-sm font-medium text-foreground">Slack Setup Instructions</p>
              <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                <li>Click the "Connect Slack" button below</li>
                <li>Authorize Call Coach in your Slack workspace</li>
                <li>Select the channels where you want to receive notifications</li>
              </ol>
              <Button className="w-full mt-4">Connect Slack</Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex gap-3">
        <Button onClick={handleSave} disabled={saving} className="flex-1 md:w-auto">
          {saving ? (
            <>
              <Loader className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            "Save Preferences"
          )}
        </Button>
        <Button variant="outline" className="flex-1 md:w-auto">
          Reset to Defaults
        </Button>
      </div>
    </div>
  );
}
