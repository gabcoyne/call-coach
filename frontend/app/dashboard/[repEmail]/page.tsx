"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useRepInsights } from "@/lib/hooks";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { ScoreTrendsChart } from "@/components/dashboard/ScoreTrendsChart";
import { TimePeriodSelector, TimePeriod } from "@/components/dashboard/TimePeriodSelector";
import { SkillGapCards } from "@/components/dashboard/SkillGapCards";
import { DimensionRadarChart } from "@/components/dashboard/DimensionRadarChart";
import { ImprovementAreas } from "@/components/dashboard/ImprovementAreas";
import { CoachingPlanSection } from "@/components/dashboard/CoachingPlanSection";
import { CallHistoryTable } from "@/components/dashboard/CallHistoryTable";
import { RepSelector } from "@/components/dashboard/RepSelector";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

interface DashboardPageProps {
  params: {
    repEmail: string;
  };
}

export default function RepDashboardPage({ params }: DashboardPageProps) {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [timePeriod, setTimePeriod] = useState<TimePeriod>('last_30_days');

  // Decode the email from URL
  const repEmail = decodeURIComponent(params.repEmail);

  // Check if current user is a manager
  const isManager = user?.publicMetadata?.role === 'manager';
  const currentUserEmail = user?.emailAddresses[0]?.emailAddress;

  // Check authorization
  const canViewData = isManager || currentUserEmail === repEmail;

  // Fetch insights
  const { data: insights, isLoading, error } = useRepInsights(
    canViewData ? repEmail : null,
    { time_period: timePeriod }
  );

  useEffect(() => {
    if (isLoaded && !canViewData) {
      // Redirect to own dashboard if trying to view someone else's data
      if (currentUserEmail) {
        router.push(`/dashboard/${encodeURIComponent(currentUserEmail)}`);
      } else {
        router.push('/sign-in');
      }
    }
  }, [isLoaded, canViewData, currentUserEmail, router]);

  // Calculate overall score from trends
  const calculateOverallScore = () => {
    if (!insights?.score_trends.overall?.scores) return undefined;
    const scores = insights.score_trends.overall.scores.filter((s): s is number => s !== null);
    if (scores.length === 0) return undefined;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  const handleCallClick = (callId: string) => {
    router.push(`/calls/${callId}`);
  };

  const handleExportPlan = () => {
    if (!insights) return;

    const content = `
Personalized Coaching Plan
Rep: ${insights.rep_info.name} (${insights.rep_info.email})
Generated: ${new Date().toLocaleDateString()}

${insights.coaching_plan}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coaching-plan-${repEmail}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSharePlan = () => {
    if (!insights) return;

    const shareText = `Coaching Plan for ${insights.rep_info.name}`;
    const shareUrl = window.location.href;

    if (navigator.share) {
      navigator.share({
        title: shareText,
        url: shareUrl,
      }).catch(() => {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareUrl);
        alert('Link copied to clipboard!');
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      alert('Link copied to clipboard!');
    }
  };

  if (!isLoaded) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!canViewData) {
    return null; // Will redirect in useEffect
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-red-600 mb-2">Error Loading Dashboard</h2>
          <p className="text-sm text-muted-foreground">{error.message || 'Failed to load rep insights'}</p>
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="mt-4 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </Button>
        </Card>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-2">No Data Available</h2>
          <p className="text-sm text-muted-foreground">
            No insights available for this rep. Make sure calls have been analyzed.
          </p>
        </Card>
      </div>
    );
  }

  // Mock call history - in production this would come from the API
  const callHistory = insights.score_trends.overall?.dates.map((date, index) => ({
    call_id: `call-${index}`,
    title: `Sales Call ${index + 1}`,
    date,
    duration_seconds: 1800 + Math.random() * 1800,
    call_type: ['discovery', 'demo', 'technical_deep_dive'][Math.floor(Math.random() * 3)],
    product: ['prefect', 'horizon'][Math.floor(Math.random() * 2)],
    overall_score: insights.score_trends.overall?.scores[index] ?? null,
  })) || [];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header with period selector */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>
        <TimePeriodSelector value={timePeriod} onChange={setTimePeriod} />
      </div>

      {/* Manager-only Rep Selector */}
      {isManager && (
        <Card className="p-4">
          <RepSelector
            reps={[
              { email: repEmail, name: insights.rep_info.name },
              // In production, this would be fetched from an API
            ]}
            selectedRepEmail={repEmail}
            onChange={(email) => router.push(`/dashboard/${encodeURIComponent(email)}`)}
            currentUserEmail={currentUserEmail}
          />
        </Card>
      )}

      {/* Dashboard Header */}
      <DashboardHeader
        repInfo={insights.rep_info}
        overallScore={calculateOverallScore()}
      />

      {/* Score Trends Chart */}
      <ScoreTrendsChart
        scoreTrends={insights.score_trends}
        showTeamAverage={isManager}
      />

      {/* Radar Chart */}
      <DimensionRadarChart
        scoreTrends={insights.score_trends}
        showTeamAverage={isManager}
      />

      {/* Skill Gaps */}
      <SkillGapCards skillGaps={insights.skill_gaps} />

      {/* Improvement Areas and Recent Wins */}
      <ImprovementAreas
        improvementAreas={insights.improvement_areas}
        recentWins={insights.recent_wins}
      />

      {/* Coaching Plan */}
      <CoachingPlanSection
        coachingPlan={insights.coaching_plan}
        onExport={handleExportPlan}
        onShare={handleSharePlan}
      />

      {/* Call History */}
      <CallHistoryTable
        calls={callHistory}
        onCallClick={handleCallClick}
      />
    </div>
  );
}
