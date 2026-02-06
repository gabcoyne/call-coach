/**
 * Opportunity Detail Page
 *
 * Shows opportunity details, health indicators, and chronological timeline of calls/emails.
 */
import { Suspense } from "react";
import { OpportunityDetail } from "@/components/opportunities/OpportunityDetail";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

interface PageProps {
  params: {
    id: string;
  };
}

export default function OpportunityPage({ params }: PageProps) {
  return (
    <div className="p-6 space-y-6">
      <Suspense fallback={<OpportunityDetailSkeleton />}>
        <OpportunityDetail opportunityId={params.id} />
      </Suspense>
    </div>
  );
}

function OpportunityDetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Breadcrumb skeleton */}
      <Skeleton className="h-6 w-64" />

      {/* Header skeleton */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <Skeleton className="h-8 w-96" />
          <div className="flex gap-4">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
          </div>
        </CardContent>
      </Card>

      {/* Timeline skeleton */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-20 w-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
