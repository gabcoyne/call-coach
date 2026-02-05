"use client";

import { FeedItem } from "@/types/coaching";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Bookmark,
  Share2,
  X,
  TrendingUp,
  Award,
  Bell,
  FileText,
  Star
} from "lucide-react";
import Link from "next/link";
import { useFeedActions } from "@/lib/hooks";
import { useState } from "react";

interface FeedItemCardProps {
  item: FeedItem;
  onAction?: () => void;
}

export function FeedItemCard({ item, onAction }: FeedItemCardProps) {
  const { bookmarkItem, dismissItem, shareItem, isProcessing } = useFeedActions();
  const [isBookmarked, setIsBookmarked] = useState(item.is_bookmarked || false);
  const [isDismissed, setIsDismissed] = useState(false);

  const handleBookmark = async () => {
    await bookmarkItem(item.id);
    setIsBookmarked(!isBookmarked);
    onAction?.();
  };

  const handleDismiss = async () => {
    await dismissItem(item.id);
    setIsDismissed(true);
    onAction?.();
  };

  const handleShare = async () => {
    const shareUrl = await shareItem(item.id);
    navigator.clipboard.writeText(shareUrl);
    // TODO: Show toast notification
  };

  if (isDismissed) {
    return null;
  }

  const getIcon = () => {
    switch (item.type) {
      case 'call_analysis':
        return <FileText className="h-5 w-5" />;
      case 'team_insight':
        return <TrendingUp className="h-5 w-5" />;
      case 'highlight':
        return <Award className="h-5 w-5" />;
      case 'milestone':
        return <Bell className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getTypeColor = () => {
    switch (item.type) {
      case 'call_analysis':
        return 'text-prefect-blue-600 bg-prefect-blue-50';
      case 'team_insight':
        return 'text-prefect-purple-600 bg-prefect-purple-50';
      case 'highlight':
        return 'text-prefect-sunrise1 bg-orange-50';
      case 'milestone':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} min ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      });
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow relative">
      {item.is_new && (
        <div className="absolute top-2 right-2">
          <Badge variant="destructive" className="text-xs">New</Badge>
        </div>
      )}

      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${getTypeColor()}`}>
            {getIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="text-xs">
                {item.type.replace('_', ' ')}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {formatTimestamp(item.timestamp)}
              </span>
            </div>
            <h3 className="text-base font-semibold text-foreground line-clamp-2">
              {item.title}
            </h3>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {item.description}
        </p>

        {/* Metadata */}
        {item.metadata.call_id && (
          <Link href={`/calls/${item.metadata.call_id}`}>
            <Button variant="link" size="sm" className="p-0 h-auto text-prefect-blue-600">
              View Call Analysis →
            </Button>
          </Link>
        )}

        {item.metadata.rep_name && (
          <div className="text-xs text-muted-foreground">
            Rep: {item.metadata.rep_name}
          </div>
        )}

        {item.metadata.highlight_snippet && (
          <div className="bg-muted/50 rounded-lg p-3 text-sm italic border-l-2 border-prefect-blue-500">
            "{item.metadata.highlight_snippet}"
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2 border-t">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBookmark}
            disabled={isProcessing}
            className="gap-1"
          >
            <Bookmark
              className={`h-4 w-4 ${isBookmarked ? 'fill-current text-prefect-blue-600' : ''}`}
            />
            <span className="text-xs">{isBookmarked ? 'Bookmarked' : 'Bookmark'}</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleShare}
            disabled={isProcessing}
            className="gap-1"
          >
            <Share2 className="h-4 w-4" />
            <span className="text-xs">Share</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            disabled={isProcessing}
            className="gap-1 ml-auto"
          >
            <X className="h-4 w-4" />
            <span className="text-xs">Dismiss</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
