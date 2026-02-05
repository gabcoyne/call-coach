"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Lightbulb, Download, Share2 } from "lucide-react";

interface CoachingPlanSectionProps {
  coachingPlan: string;
  onExport?: () => void;
  onShare?: () => void;
}

export function CoachingPlanSection({
  coachingPlan,
  onExport,
  onShare,
}: CoachingPlanSectionProps) {
  // Split coaching plan into sections if it contains bullet points or numbered lists
  const formatCoachingPlan = (plan: string) => {
    // Split by newlines and filter out empty lines
    const lines = plan.split('\n').filter(line => line.trim());

    return lines.map((line, index) => {
      // Check if line starts with a number or bullet
      const isListItem = /^[\d\-\*•]/.test(line.trim());

      return (
        <p
          key={index}
          className={`text-sm ${isListItem ? 'ml-4' : ''} ${index > 0 ? 'mt-2' : ''}`}
        >
          {line}
        </p>
      );
    });
  };

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-prefect-blue" />
          <h3 className="text-lg font-semibold">Personalized Coaching Plan</h3>
        </div>
        <div className="flex gap-2">
          {onShare && (
            <Button
              variant="outline"
              size="sm"
              onClick={onShare}
              className="gap-2"
            >
              <Share2 className="w-4 h-4" />
              Share
            </Button>
          )}
          {onExport && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExport}
              className="gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </Button>
          )}
        </div>
      </div>

      <div className="prose prose-sm max-w-none">
        {coachingPlan ? (
          <div className="text-gray-700 leading-relaxed">
            {formatCoachingPlan(coachingPlan)}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No coaching plan available. Complete more calls to generate personalized recommendations.
          </p>
        )}
      </div>
    </Card>
  );
}
