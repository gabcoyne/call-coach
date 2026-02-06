"use client";

import { useState, useEffect } from "react";
import { X, AlertCircle, TrendingUp, MessageSquare, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Annotation } from "./AnnotationMarker";

interface CoachingOverlayProps {
  annotation: Annotation | null;
  isVisible: boolean;
  onClose: () => void;
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left";
}

const dimensionConfig = {
  product_knowledge: {
    color: "bg-blue-500",
    bgLight: "bg-blue-50",
    borderColor: "border-blue-300",
    textColor: "text-blue-700",
    icon: AlertCircle,
    label: "Product Knowledge",
  },
  discovery: {
    color: "bg-green-500",
    bgLight: "bg-green-50",
    borderColor: "border-green-300",
    textColor: "text-green-700",
    icon: Search,
    label: "Discovery",
  },
  objection_handling: {
    color: "bg-orange-500",
    bgLight: "bg-orange-50",
    borderColor: "border-orange-300",
    textColor: "text-orange-700",
    icon: MessageSquare,
    label: "Objection Handling",
  },
  engagement: {
    color: "bg-purple-500",
    bgLight: "bg-purple-50",
    borderColor: "border-purple-300",
    textColor: "text-purple-700",
    icon: TrendingUp,
    label: "Engagement",
  },
};

export function CoachingOverlay({
  annotation,
  isVisible,
  onClose,
  position = "bottom-right",
}: CoachingOverlayProps) {
  const [displayAnnotation, setDisplayAnnotation] = useState<Annotation | null>(
    annotation
  );

  useEffect(() => {
    if (annotation) {
      setDisplayAnnotation(annotation);
    }
  }, [annotation]);

  if (!isVisible || !displayAnnotation) {
    return null;
  }

  const config = dimensionConfig[displayAnnotation.dimension];
  const Icon = config.icon;

  const positionClasses = {
    "bottom-right": "bottom-4 right-4",
    "bottom-left": "bottom-4 left-4",
    "top-right": "top-4 right-4",
    "top-left": "top-4 left-4",
  };

  const severityStyles = {
    positive: "border-green-200 bg-green-50",
    neutral: "border-gray-200 bg-white",
    improvement: "border-yellow-200 bg-yellow-50",
  };

  return (
    <div
      className={`fixed z-40 w-80 rounded-lg border-2 shadow-xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-2 ${positionClasses[position]} ${
        severityStyles[displayAnnotation.severity || "neutral"]
      }`}
    >
      {/* Header with icon */}
      <div className="flex items-start gap-3 p-4 border-b">
        <div className={`${config.color} p-2 rounded-lg flex-shrink-0`}>
          <Icon className="h-5 w-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-bold text-gray-900">{config.label}</h3>
          <p className="text-xs text-gray-600 mt-0.5">
            {displayAnnotation.severity === "positive"
              ? "Strength Identified"
              : displayAnnotation.severity === "improvement"
                ? "Development Opportunity"
                : "Coaching Insight"}
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-6 w-6 p-0 flex-shrink-0"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900">
            {displayAnnotation.title}
          </h4>
        </div>

        {/* Main insight */}
        <div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {displayAnnotation.insight}
          </p>
        </div>

        {/* Coaching suggestion */}
        {displayAnnotation.severity === "improvement" && (
          <div className={`${config.bgLight} p-3 rounded-lg border-l-4 ${config.borderColor}`}>
            <p className="text-xs font-semibold text-gray-900 mb-1">
              Coaching Suggestion:
            </p>
            <p className="text-xs text-gray-700">
              Focus on deepening your approach in this area. Consider practicing
              this technique in upcoming calls.
            </p>
          </div>
        )}

        {displayAnnotation.severity === "positive" && (
          <div className={`${config.bgLight} p-3 rounded-lg border-l-4 ${config.borderColor}`}>
            <p className="text-xs font-semibold text-gray-900 mb-1">
              Keep it up:
            </p>
            <p className="text-xs text-gray-700">
              This is an excellent demonstration. Continue applying this approach
              in similar situations.
            </p>
          </div>
        )}

        {/* Timestamp indicator */}
        <div className="text-xs text-gray-600 pt-1 border-t">
          This occurs at{" "}
          <span className="font-mono font-semibold text-gray-900">
            {Math.floor(displayAnnotation.timestamp / 60)}:
            {String(Math.floor(displayAnnotation.timestamp % 60)).padStart(2, "0")}
          </span>
        </div>
      </div>
    </div>
  );
}
