import { Suspense } from "react";
import { notFound } from "next/navigation";
import { currentUser } from "@clerk/nextjs/server";
import { CallAnalysisViewer } from "./CallAnalysisViewer";

interface PageProps {
  params: Promise<{
    callId: string;
  }>;
}

export default async function CallDetailPage({ params }: PageProps) {
  const { callId } = await params;
  const user = await currentUser();

  if (!user) {
    notFound();
  }

  const userRole = (user.publicMetadata?.role as string) || "rep";

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <Suspense
        fallback={
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-2">
              <div className="animate-spin h-8 w-8 border-4 border-prefect-blue-500 border-t-transparent rounded-full mx-auto" />
              <p className="text-sm text-muted-foreground">Loading call analysis...</p>
            </div>
          </div>
        }
      >
        <CallAnalysisViewer callId={callId} userRole={userRole} />
      </Suspense>
    </div>
  );
}

export async function generateMetadata({ params }: PageProps) {
  const { callId } = await params;

  return {
    title: `Call Analysis - ${callId}`,
    description: "View detailed analysis and coaching insights for this call",
  };
}
