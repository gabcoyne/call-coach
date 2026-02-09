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
      <CallAnalysisViewer callId={callId} userRole={userRole} />
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
