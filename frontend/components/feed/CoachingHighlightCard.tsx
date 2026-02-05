"use client";

import { CoachingHighlight } from "@/types/coaching";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Award, ExternalLink } from "lucide-react";
import Link from "next/link";

interface CoachingHighlightCardProps {
  highlight: CoachingHighlight;
}

export function CoachingHighlightCard({ highlight }: CoachingHighlightCardProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  return (
    <Card className="border-l-4 border-l-prefect-sunrise1 hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-orange-50 text-prefect-sunrise1">
            <Award className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="text-xs bg-orange-50 text-prefect-sunrise1 border-prefect-sunrise1">
                Exemplary Moment
              </Badge>
              <ScoreBadge score={highlight.score} size="sm" />
            </div>
            <CardTitle className="text-base">
              {highlight.dimension.replace('_', ' ').charAt(0).toUpperCase() +
               highlight.dimension.replace('_', ' ').slice(1)} Excellence
            </CardTitle>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Rep Info */}
        <div className="flex items-center justify-between text-sm">
          <div>
            <p className="font-medium text-foreground">{highlight.rep_name}</p>
            <p className="text-xs text-muted-foreground">{highlight.call_title}</p>
          </div>
          <p className="text-xs text-muted-foreground">
            {formatTimestamp(highlight.timestamp)}
          </p>
        </div>

        {/* Highlight Snippet */}
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4 border border-prefect-sunrise1/20">
          <p className="text-sm italic text-foreground leading-relaxed">
            "{highlight.snippet}"
          </p>
        </div>

        {/* Context */}
        <div className="space-y-2">
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
              Context
            </p>
            <p className="text-sm text-foreground">{highlight.context}</p>
          </div>

          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
              Why This Is Exemplary
            </p>
            <p className="text-sm text-foreground">{highlight.why_exemplary}</p>
          </div>
        </div>

        {/* Action */}
        <Link href={`/calls/${highlight.call_id}`}>
          <Button variant="outline" size="sm" className="w-full mt-2">
            View Full Call Analysis
            <ExternalLink className="h-3 w-3 ml-1" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
