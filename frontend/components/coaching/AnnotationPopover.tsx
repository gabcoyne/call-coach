"use client";

import { useState } from "react";
import {
  AlertCircle,
  TrendingUp,
  MessageSquare,
  Search,
  X,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Annotation } from "./AnnotationMarker";

interface AnnotationPopoverProps {
  annotation: Annotation;
  position: "top" | "bottom";
  onClose: () => void;
  onJumpToMoment: (timestamp: number) => void;
}

const dimensionConfig = {
  product_knowledge: {
    color: "bg-blue-500",
    borderColor: "border-blue-500",
    bgLight: "bg-blue-50",
    textColor: "text-blue-700",
    icon: AlertCircle,
    label: "Product Knowledge",
    description: "Knowledge and accuracy about product features and capabilities",
  },
  discovery: {
    color: "bg-green-500",
    borderColor: "border-green-500",
    bgLight: "bg-green-50",
    textColor: "text-green-700",
    icon: Search,
    label: "Discovery",
    description: "Effectiveness in uncovering customer needs and pain points",
  },
  objection_handling: {
    color: "bg-orange-500",
    borderColor: "border-orange-500",
    bgLight: "bg-orange-50",
    textColor: "text-orange-700",
    icon: MessageSquare,
    label: "Objection Handling",
    description: "Skills in addressing and overcoming customer objections",
  },
  engagement: {
    color: "bg-purple-500",
    borderColor: "border-purple-500",
    bgLight: "bg-purple-50",
    textColor: "text-purple-700",
    icon: TrendingUp,
    label: "Engagement",
    description: "Ability to build rapport and keep customer interested",
  },
};

export function AnnotationPopover({
  annotation,
  position,
  onClose,
  onJumpToMoment,
}: AnnotationPopoverProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = dimensionConfig[annotation.dimension];
  const Icon = config.icon;

  const severityStyles = {
    positive: "border-green-200 bg-green-50",
    neutral: "border-gray-200 bg-gray-50",
    improvement: "border-yellow-200 bg-yellow-50",
  };

  const severityLabel = {
    positive: "Strength",
    neutral: "Observation",
    improvement: "Area for Improvement",
  };

  return (
    <div
      className={`fixed z-50 w-96 rounded-lg border shadow-lg ${
        severityStyles[annotation.severity || "neutral"]
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 p-4 border-b">
        <div className="flex items-start gap-3 flex-1">
          <div
            className={`${config.color} p-2 rounded-lg flex-shrink-0`}
          >
            <Icon className="h-4 w-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900">
              {config.label}
            </h3>
            <p className="text-xs text-gray-600 mt-1">
              {severityLabel[annotation.severity || "neutral"]}
            </p>
          </div>
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
        {/* Main insight */}
        <div>
          <p className="text-sm font-medium text-gray-900">
            {annotation.title}
          </p>
          <p className="text-sm text-gray-700 mt-2">
            {annotation.insight}
          </p>
        </div>

        {/* Expandable dimension details */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-xs font-medium text-gray-600 hover:text-gray-900 transition-colors"
        >
          {isExpanded ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          About {config.label}
        </button>

        {isExpanded && (
          <div className={`${config.bgLight} p-3 rounded-md text-xs text-gray-700`}>
            <p>{config.description}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2 pt-2">
          <Button
            size="sm"
            onClick={() => onJumpToMoment(annotation.timestamp)}
            className="flex-1 text-xs h-8"
          >
            Play this moment
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={onClose}
            className="flex-1 text-xs h-8"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
