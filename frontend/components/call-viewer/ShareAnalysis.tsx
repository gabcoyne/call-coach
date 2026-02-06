"use client";

import { useState } from "react";
import { Share2, Check, Copy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ShareAnalysisProps {
  callId: string;
  className?: string;
}

export function ShareAnalysis({ callId, className }: ShareAnalysisProps) {
  const [copied, setCopied] = useState(false);

  const shareUrl = `${typeof window !== "undefined" ? window.location.origin : ""}/calls/${callId}`;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy link:", error);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Share2 className="h-4 w-4" />
          Share Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          <div className="flex-1 p-2 text-sm bg-muted rounded-md overflow-x-auto">
            <code className="text-xs">{shareUrl}</code>
          </div>
          <Button onClick={handleCopyLink} variant={copied ? "default" : "outline"} size="sm">
            {copied ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </>
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Anyone with this link can view the call analysis (authentication required)
        </p>
      </CardContent>
    </Card>
  );
}
