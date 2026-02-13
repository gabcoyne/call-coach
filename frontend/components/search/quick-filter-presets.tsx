"use client";

import { useUser } from "@/lib/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SearchCallsRequest } from "@/types/coaching";
import { Zap, TrendingDown, Calendar, Star, Users } from "lucide-react";

interface QuickFilterPresetsProps {
  onPresetSelect: (filters: Partial<SearchCallsRequest>) => void;
  currentUserEmail?: string;
}

interface Preset {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  filters: Partial<SearchCallsRequest>;
  requiresManager?: boolean;
}

export function QuickFilterPresets({ onPresetSelect, currentUserEmail }: QuickFilterPresetsProps) {
  const { user } = useUser();
  const userRole = user?.publicMetadata?.role as string | undefined;
  const isManager = userRole === "manager";
  const userEmail = currentUserEmail || user?.emailAddresses[0]?.emailAddress;

  // Get date ranges
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const weekAgo = new Date(today);
  weekAgo.setDate(today.getDate() - 7);
  const monthAgo = new Date(today);
  monthAgo.setMonth(today.getMonth() - 1);

  const presets: Preset[] = [
    {
      id: "my-calls-week",
      name: "My Calls This Week",
      description: "All your calls from the last 7 days",
      icon: <Calendar className="h-4 w-4" />,
      filters: {
        rep_email: userEmail,
        date_range: {
          start: weekAgo.toISOString(),
          end: now.toISOString(),
        },
        limit: 20,
      },
    },
    {
      id: "my-high-performers",
      name: "My High Performers",
      description: "Your calls scoring 80 or above",
      icon: <Star className="h-4 w-4" />,
      filters: {
        rep_email: userEmail,
        min_score: 80,
        limit: 20,
      },
    },
    {
      id: "low-performers",
      name: "Low Performers",
      description: "Calls scoring below 60 that need attention",
      icon: <TrendingDown className="h-4 w-4" />,
      filters: {
        max_score: 60,
        limit: 20,
      },
    },
    {
      id: "discovery-calls",
      name: "Discovery Calls",
      description: "All discovery calls",
      icon: <Zap className="h-4 w-4" />,
      filters: {
        call_type: "discovery",
        limit: 20,
      },
    },
    {
      id: "recent-all",
      name: "Recent All Calls",
      description: "All calls from the last 30 days",
      icon: <Calendar className="h-4 w-4" />,
      filters: {
        date_range: {
          start: monthAgo.toISOString(),
          end: now.toISOString(),
        },
        limit: 50,
      },
      requiresManager: true,
    },
    {
      id: "team-top-performers",
      name: "Team Top Performers",
      description: "All calls scoring 85+ across the team",
      icon: <Users className="h-4 w-4" />,
      filters: {
        min_score: 85,
        limit: 50,
      },
      requiresManager: true,
    },
  ];

  // Filter presets based on user role
  const availablePresets = presets.filter((preset) => !preset.requiresManager || isManager);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Quick Filter Presets
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {availablePresets.map((preset) => (
            <Button
              key={preset.id}
              variant="outline"
              className="h-auto flex flex-col items-start p-4 hover:bg-accent"
              onClick={() => onPresetSelect(preset.filters)}
            >
              <div className="flex items-center gap-2 mb-1">
                {preset.icon}
                <span className="font-medium text-sm">{preset.name}</span>
                {preset.requiresManager && (
                  <Badge variant="secondary" className="text-xs">
                    Manager
                  </Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground text-left">{preset.description}</p>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
