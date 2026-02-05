import { Card } from "@/components/ui/card";

export default function DashboardLoading() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header skeleton */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-gray-200 animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-6 bg-gray-200 rounded animate-pulse w-48" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-64" />
          </div>
        </div>
      </Card>

      {/* Chart skeletons */}
      <Card className="p-6">
        <div className="h-6 bg-gray-200 rounded animate-pulse w-40 mb-4" />
        <div className="h-96 bg-gray-100 rounded animate-pulse" />
      </Card>

      <Card className="p-6">
        <div className="h-6 bg-gray-200 rounded animate-pulse w-40 mb-4" />
        <div className="h-96 bg-gray-100 rounded animate-pulse" />
      </Card>

      {/* Content skeletons */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4">
            <div className="h-4 bg-gray-200 rounded animate-pulse w-32 mb-2" />
            <div className="h-20 bg-gray-100 rounded animate-pulse" />
          </Card>
        ))}
      </div>
    </div>
  );
}
