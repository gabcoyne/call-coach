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
import { Loader, Moon, Sun, LayoutGrid } from "lucide-react";

type UserPreferences = {
  theme: "light" | "dark" | "system";
  defaultCoachingDimensions: string[];
  dashboardLayout: "grid" | "list";
  compactMode: boolean;
  autoRefreshEnabled: boolean;
};

const coachingDimensions = [
  { id: "opening", label: "Opening" },
  { id: "discovery", label: "Discovery" },
  { id: "pitch", label: "Pitch/Demo" },
  { id: "objection_handling", label: "Objection Handling" },
  { id: "closing", label: "Closing" },
  { id: "rapport", label: "Rapport Building" },
  { id: "questioning", label: "Questioning" },
  { id: "listening", label: "Active Listening" },
];

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState<UserPreferences>({
    theme: "system",
    defaultCoachingDimensions: ["opening", "discovery", "pitch"],
    dashboardLayout: "grid",
    compactMode: false,
    autoRefreshEnabled: true,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    // Load preferences from API or localStorage
    const loadPreferences = async () => {
      try {
        const response = await fetch("/api/user/preferences", {
          method: "GET",
        });

        if (response.ok) {
          const data = await response.json();
          setPreferences({
            theme: data.theme ?? "system",
            defaultCoachingDimensions: data.defaultCoachingDimensions ?? ["opening", "discovery", "pitch"],
            dashboardLayout: data.dashboardLayout ?? "grid",
            compactMode: data.compactMode ?? false,
            autoRefreshEnabled: data.autoRefreshEnabled ?? true,
          });
        }
      } catch (error) {
        console.error("Failed to load preferences:", error);
        // Fall back to localStorage
        const stored = localStorage.getItem("userPreferences");
        if (stored) {
          setPreferences(JSON.parse(stored));
        }
      } finally {
        setLoading(false);
      }
    };

    loadPreferences();
  }, []);

  const handleThemeChange = (value: string) => {
    setPreferences((prev) => ({
      ...prev,
      theme: value as "light" | "dark" | "system",
    }));

    // Apply theme immediately
    const html = document.documentElement;
    if (value === "dark") {
      html.classList.add("dark");
    } else if (value === "light") {
      html.classList.remove("dark");
    } else {
      // System preference
      if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        html.classList.add("dark");
      } else {
        html.classList.remove("dark");
      }
    }
  };

  const handleDimensionToggle = (dimensionId: string) => {
    setPreferences((prev) => ({
      ...prev,
      defaultCoachingDimensions: prev.defaultCoachingDimensions.includes(dimensionId)
        ? prev.defaultCoachingDimensions.filter((id) => id !== dimensionId)
        : [...prev.defaultCoachingDimensions, dimensionId],
    }));
  };

  const handleLayoutChange = (value: string) => {
    setPreferences((prev) => ({
      ...prev,
      dashboardLayout: value as "grid" | "list",
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

      // Also save to localStorage as backup
      localStorage.setItem("userPreferences", JSON.stringify(preferences));

      setMessage({ type: "success", text: "Preferences saved successfully" });
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
        <h1 className="text-3xl font-bold text-foreground">Preferences</h1>
        <p className="text-muted-foreground mt-1">
          Customize your experience with Call Coach
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`p-4 rounded-lg ${message.type === "success" ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
          {message.text}
        </div>
      )}

      {/* Theme Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sun className="h-5 w-5" />
            Appearance
          </CardTitle>
          <CardDescription>Customize how Call Coach looks</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="theme">Theme</Label>
            <Select value={preferences.theme} onValueChange={handleThemeChange}>
              <SelectTrigger id="theme" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">
                  <div className="flex items-center gap-2">
                    <Sun className="h-4 w-4" />
                    Light
                  </div>
                </SelectItem>
                <SelectItem value="dark">
                  <div className="flex items-center gap-2">
                    <Moon className="h-4 w-4" />
                    Dark
                  </div>
                </SelectItem>
                <SelectItem value="system">
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 rounded-full border border-foreground" />
                    System
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="text-sm text-muted-foreground">
            Choose how the interface looks. "System" follows your device settings.
          </p>

          <div className="mt-4 pt-4 border-t border-border space-y-3">
            <div className="flex items-center space-x-3">
              <Checkbox
                id="compactMode"
                checked={preferences.compactMode}
                onCheckedChange={(checked) =>
                  setPreferences((prev) => ({ ...prev, compactMode: checked as boolean }))
                }
              />
              <Label htmlFor="compactMode" className="font-normal cursor-pointer">
                Compact Mode
              </Label>
            </div>
            <p className="text-sm text-muted-foreground ml-7">
              Reduce spacing and text sizes for a more compact interface.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Dashboard Layout */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LayoutGrid className="h-5 w-5" />
            Dashboard Layout
          </CardTitle>
          <CardDescription>Choose how your dashboard displays content</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="layout">Default Layout</Label>
            <Select value={preferences.dashboardLayout} onValueChange={handleLayoutChange}>
              <SelectTrigger id="layout" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="grid">Grid View</SelectItem>
                <SelectItem value="list">List View</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="text-sm text-muted-foreground">
            Select your preferred way to view coaching sessions and insights.
          </p>

          <div className="mt-4 pt-4 border-t border-border space-y-3">
            <div className="flex items-center space-x-3">
              <Checkbox
                id="autoRefresh"
                checked={preferences.autoRefreshEnabled}
                onCheckedChange={(checked) =>
                  setPreferences((prev) => ({ ...prev, autoRefreshEnabled: checked as boolean }))
                }
              />
              <Label htmlFor="autoRefresh" className="font-normal cursor-pointer">
                Auto-refresh Data
              </Label>
            </div>
            <p className="text-sm text-muted-foreground ml-7">
              Automatically refresh coaching data every 5 minutes.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Default Coaching Dimensions */}
      <Card>
        <CardHeader>
          <CardTitle>Default Coaching Dimensions</CardTitle>
          <CardDescription>
            Select which coaching dimensions to focus on by default
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            These dimensions will be highlighted in your coaching insights and reports.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {coachingDimensions.map((dimension) => (
              <div
                key={dimension.id}
                className="flex items-center space-x-3 p-3 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                <Checkbox
                  id={dimension.id}
                  checked={preferences.defaultCoachingDimensions.includes(dimension.id)}
                  onCheckedChange={() => handleDimensionToggle(dimension.id)}
                />
                <Label htmlFor={dimension.id} className="font-normal cursor-pointer">
                  {dimension.label}
                </Label>
              </div>
            ))}
          </div>
          {preferences.defaultCoachingDimensions.length === 0 && (
            <p className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
              Please select at least one coaching dimension.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex gap-3">
        <Button
          onClick={handleSave}
          disabled={saving || preferences.defaultCoachingDimensions.length === 0}
          className="flex-1 md:w-auto"
        >
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
