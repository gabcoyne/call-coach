"use client";

/**
 * OpportunityDetail Component
 *
 * Shows opportunity header and timeline of calls/emails.
 */
import useSWR from "swr";
import { OpportunityHeader } from "./OpportunityHeader";
import { OpportunityTimeline } from "./OpportunityTimeline";
import { OpportunityInsights } from "./OpportunityInsights";
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

interface Opportunity {
  id: string;
  name: string;
  account_name: string;
  owner_email: string;
  stage: string;
  close_date: string;
  amount: number;
  health_score: number;
  call_count: number;
  email_count: number;
  metadata: any;
  created_at: string;
  updated_at: string;
}

interface OpportunityResponse {
  opportunity: Opportunity;
}

async function fetcher(url: string): Promise<OpportunityResponse> {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Opportunity not found");
    }
    throw new Error("Failed to fetch opportunity");
  }
  return response.json();
}

interface OpportunityDetailProps {
  opportunityId: string;
}

export function OpportunityDetail({ opportunityId }: OpportunityDetailProps) {
  const router = useRouter();
  const { data, error, isLoading } = useSWR<OpportunityResponse>(
    `/api/opportunities/${opportunityId}`,
    fetcher,
    {
      revalidateOnFocus: false,
    }
  );

  if (error) {
    return (
      <div className="space-y-4">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/opportunities")}
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Opportunities
          </Button>
        </div>

        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <span>{error.message}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading || !data) {
    return null; // Show skeleton from parent
  }

  const { opportunity } = data;

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/opportunities")}
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Opportunities
        </Button>
        <span>/</span>
        <span className="text-foreground">{opportunity.name}</span>
      </div>

      {/* Header */}
      <OpportunityHeader opportunity={opportunity} />

      {/* Insights */}
      <OpportunityInsights opportunityId={opportunityId} />

      {/* Timeline */}
      <OpportunityTimeline opportunityId={opportunityId} />
    </div>
  );
}
