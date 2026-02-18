import { notFound } from "next/navigation";
import { getAuthContext } from "@/lib/auth-middleware";
import { CallAnalysisViewer } from "./CallAnalysisViewer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

interface PageProps {
  params: Promise<{
    callId: string;
  }>;
}

export default async function CallDetailPage({ params }: PageProps) {
  const { callId } = await params;

  let authContext;
  try {
    authContext = await getAuthContext();
  } catch {
    notFound();
  }

  const userRole = authContext.role || "rep";

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <ErrorBoundary>
        <CallAnalysisViewer callId={callId} userRole={userRole} />
      </ErrorBoundary>
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
