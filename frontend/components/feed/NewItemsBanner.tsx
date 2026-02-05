"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw } from "lucide-react";

interface NewItemsBannerProps {
  count: number;
  onRefresh: () => void;
}

export function NewItemsBanner({ count, onRefresh }: NewItemsBannerProps) {
  if (count === 0) {
    return null;
  }

  return (
    <div className="sticky top-0 z-10 animate-in slide-in-from-top duration-300">
      <div className="bg-prefect-blue-600 text-white rounded-lg shadow-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <RefreshCw className="h-5 w-5 animate-pulse" />
          <div>
            <p className="font-semibold">
              {count} new {count === 1 ? 'item' : 'items'} available
            </p>
            <p className="text-xs text-blue-100">
              Click to refresh and see the latest updates
            </p>
          </div>
        </div>
        <Button
          onClick={onRefresh}
          variant="secondary"
          size="sm"
          className="gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Feed
        </Button>
      </div>
    </div>
  );
}
