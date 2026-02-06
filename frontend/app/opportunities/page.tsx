/**
 * Opportunities List Page
 *
 * Server component that renders the opportunities listing with search, filters, and pagination.
 */
import { Suspense } from "react";
import { OpportunitiesList } from "@/components/opportunities/OpportunitiesList";
import { Skeleton } from "@/components/ui/skeleton";

export default function OpportunitiesPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Opportunities</h1>
        <p className="text-muted-foreground mt-1">
          Track and analyze sales opportunities with holistic coaching insights
        </p>
      </div>

      <Suspense fallback={<OpportunitiesListSkeleton />}>
        <OpportunitiesList />
      </Suspense>
    </div>
  );
}

function OpportunitiesListSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-10 w-48" />
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
