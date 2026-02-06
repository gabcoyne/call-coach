"use client";

import { useState } from "react";
import { Copy, Download, Share2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Annotation } from "./AnnotationMarker";

interface ClipGeneratorProps {
  annotation: Annotation;
  duration: number;
  onGenerate?: (startTime: number, endTime: number) => void;
}

export function ClipGenerator({ annotation, duration, onGenerate }: ClipGeneratorProps) {
  const [copied, setCopied] = useState(false);
  const [clipDuration] = useState(30); // 30 second clips by default

  // Generate clip timestamps: 15 seconds before and after the insight
  const clipStart = Math.max(0, annotation.timestamp - 15);
  const clipEnd = Math.min(duration, annotation.timestamp + 15);

  const generateShareLink = () => {
    const baseUrl = typeof window !== "undefined" ? window.location.href.split("#")[0] : "";
    return `${baseUrl}#t=${Math.floor(clipStart)}-${Math.floor(clipEnd)}`;
  };

  const copyShareLink = () => {
    const link = generateShareLink();
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadClip = () => {
    // This would typically trigger a backend API call to generate the clip
    // For now, we'll show a placeholder
    const link = generateShareLink();
    console.log("Download clip:", link);
    alert("Clip download initiated. In production, this would generate an audio file.");
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-900">Share This Moment</h4>
        <p className="text-xs text-gray-600">
          Automatically generates a {Math.floor((clipEnd - clipStart) / 2)}-second clip around this
          insight
        </p>
      </div>

      {/* Clip Time Display */}
      <div className="bg-white border border-gray-200 rounded-lg p-3 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600">Start:</span>
          <span className="font-mono font-semibold text-gray-900">{formatTime(clipStart)}</span>
        </div>
        <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500"
            style={{
              width: `${((clipEnd - clipStart) / duration) * 100}%`,
              marginLeft: `${(clipStart / duration) * 100}%`,
            }}
          />
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600">End:</span>
          <span className="font-mono font-semibold text-gray-900">{formatTime(clipEnd)}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <Button size="sm" variant="outline" onClick={copyShareLink} className="text-xs h-8 gap-1.5">
          <Copy className="h-3 w-3" />
          {copied ? "Copied!" : "Copy Link"}
        </Button>
        <Button size="sm" variant="outline" onClick={downloadClip} className="text-xs h-8 gap-1.5">
          <Download className="h-3 w-3" />
          Download
        </Button>
      </div>

      {/* Info */}
      <div className="text-xs text-gray-600 flex items-start gap-2 pt-2 border-t">
        <Clock className="h-3 w-3 flex-shrink-0 mt-0.5" />
        <p>
          Share this link with colleagues. The recipient will hear the coaching insight in context.
        </p>
      </div>
    </div>
  );
}
