"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreBadge } from "@/components/ui/score-badge";
import { CallSearchResult } from "@/types/coaching";
import { LayoutGrid, List, ExternalLink, Clock, Users } from "lucide-react";

interface SearchResultsProps {
  results: CallSearchResult[];
  isLoading?: boolean;
}

type ViewMode = "card" | "table";

export function SearchResults({ results, isLoading }: SearchResultsProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("card");

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <div className="animate-pulse">Searching calls...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!results || results.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <p className="text-lg font-medium">No calls found</p>
            <p className="mt-2">Try adjusting your search filters</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* View Toggle */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Found {results.length} call{results.length !== 1 ? "s" : ""}
        </p>
        <div className="flex gap-1">
          <Button
            variant={viewMode === "card" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("card")}
          >
            <LayoutGrid className="h-4 w-4 mr-1" />
            Cards
          </Button>
          <Button
            variant={viewMode === "table" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("table")}
          >
            <List className="h-4 w-4 mr-1" />
            Table
          </Button>
        </div>
      </div>

      {/* Results Display */}
      {viewMode === "card" ? <CardView results={results} /> : <TableView results={results} />}
    </div>
  );
}

function CardView({ results }: { results: CallSearchResult[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {results.map((result) => (
        <Card key={result.call_id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="text-base line-clamp-2">{result.title}</CardTitle>
              {result.overall_score !== null && (
                <ScoreBadge score={result.overall_score} className="text-xs" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Metadata */}
            <div className="space-y-1 text-sm">
              {result.date && (
                <div className="flex items-center text-muted-foreground">
                  <Clock className="h-3 w-3 mr-1" />
                  {new Date(result.date).toLocaleDateString()}
                </div>
              )}
              {result.duration_seconds > 0 && (
                <div className="flex items-center text-muted-foreground">
                  <Clock className="h-3 w-3 mr-1" />
                  {Math.round(result.duration_seconds / 60)} min
                </div>
              )}
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-1">
              {result.call_type && (
                <Badge variant="outline" className="text-xs">
                  {result.call_type.replace(/_/g, " ")}
                </Badge>
              )}
              {result.product && (
                <Badge variant="secondary" className="text-xs">
                  {result.product}
                </Badge>
              )}
            </div>

            {/* Participants */}
            {result.prefect_reps.length > 0 && (
              <div className="text-xs text-muted-foreground">
                <Users className="h-3 w-3 inline mr-1" />
                {result.prefect_reps.join(", ")}
              </div>
            )}

            {/* Action */}
            <Link href={`/calls/${result.call_id}`}>
              <Button variant="outline" size="sm" className="w-full">
                View Analysis
                <ExternalLink className="h-3 w-3 ml-1" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function TableView({ results }: { results: CallSearchResult[] }) {
  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="text-left p-3 font-medium">Title</th>
                <th className="text-left p-3 font-medium">Date</th>
                <th className="text-left p-3 font-medium">Type</th>
                <th className="text-left p-3 font-medium">Duration</th>
                <th className="text-left p-3 font-medium">Reps</th>
                <th className="text-left p-3 font-medium">Score</th>
                <th className="text-left p-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.call_id} className="border-b hover:bg-muted/50 transition-colors">
                  <td className="p-3">
                    <div className="line-clamp-1 max-w-xs">{result.title}</div>
                  </td>
                  <td className="p-3 text-sm text-muted-foreground">
                    {result.date ? new Date(result.date).toLocaleDateString() : "—"}
                  </td>
                  <td className="p-3">
                    {result.call_type && (
                      <Badge variant="outline" className="text-xs">
                        {result.call_type.replace(/_/g, " ")}
                      </Badge>
                    )}
                  </td>
                  <td className="p-3 text-sm text-muted-foreground">
                    {result.duration_seconds > 0
                      ? `${Math.round(result.duration_seconds / 60)} min`
                      : "—"}
                  </td>
                  <td className="p-3 text-sm text-muted-foreground">
                    <div className="line-clamp-1 max-w-xs">
                      {result.prefect_reps.join(", ") || "—"}
                    </div>
                  </td>
                  <td className="p-3">
                    {result.overall_score !== null ? (
                      <ScoreBadge score={result.overall_score} className="text-xs" />
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="p-3">
                    <Link href={`/calls/${result.call_id}`}>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
