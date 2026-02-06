"use client";

import { useState } from "react";
import { AlertCircle, TrendingUp, MessageSquare, Search } from "lucide-react";

export interface Annotation {
  id: string;
  timestamp: number;
  dimension: "product_knowledge" | "discovery" | "objection_handling" | "engagement";
  title: string;
  insight: string;
  severity?: "positive" | "neutral" | "improvement";
}

interface AnnotationMarkerProps {
  annotation: Annotation;
  duration: number;
  isHovered: boolean;
  onHover: (id: string | null) => void;
  onClick: (timestamp: number) => void;
}

const dimensionConfig = {
  product_knowledge: {
    color: "bg-blue-500",
    borderColor: "border-blue-500",
    bgLight: "bg-blue-50",
    icon: AlertCircle,
    label: "Product Knowledge",
  },
  discovery: {
    color: "bg-green-500",
    borderColor: "border-green-500",
    bgLight: "bg-green-50",
    icon: Search,
    label: "Discovery",
  },
  objection_handling: {
    color: "bg-orange-500",
    borderColor: "border-orange-500",
    bgLight: "bg-orange-50",
    icon: MessageSquare,
    label: "Objection Handling",
  },
  engagement: {
    color: "bg-purple-500",
    borderColor: "border-purple-500",
    bgLight: "bg-purple-50",
    icon: TrendingUp,
    label: "Engagement",
  },
};

export function AnnotationMarker({
  annotation,
  duration,
  isHovered,
  onHover,
  onClick,
}: AnnotationMarkerProps) {
  const config = dimensionConfig[annotation.dimension];
  const Icon = config.icon;
  const percentPosition = (annotation.timestamp / duration) * 100;

  return (
    <div className="relative group">
      {/* Marker on timeline */}
      <div
        className={`absolute top-0 transform -translate-x-1/2 cursor-pointer transition-all ${
          isHovered ? "z-50" : "z-10"
        }`}
        style={{ left: `${percentPosition}%` }}
        onMouseEnter={() => onHover(annotation.id)}
        onMouseLeave={() => onHover(null)}
      >
        {/* Vertical line */}
        <div
          className={`w-1 h-full ${config.color} transition-all ${
            isHovered ? "w-2 shadow-lg" : ""
          }`}
        />

        {/* Dot at top */}
        <div
          className={`absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-3 ${config.color} rounded-full border-2 border-white shadow-md transition-all ${
            isHovered ? "w-4 h-4 -translate-y-2" : ""
          }`}
        />

        {/* Popover on hover */}
        {isHovered && (
          <div className="absolute left-1/2 transform -translate-x-1/2 -top-32 z-50 w-48 bg-white rounded-lg shadow-lg border border-gray-200 p-3 pointer-events-auto">
            <div className="flex items-start gap-2">
              <Icon className={`h-4 w-4 ${config.color.replace("bg-", "text-")} flex-shrink-0 mt-0.5`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-gray-900">
                  {config.label}
                </p>
                <p className="text-xs font-medium text-gray-700 mt-0.5">
                  {annotation.title}
                </p>
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                  {annotation.insight}
                </p>
              </div>
            </div>
            <button
              onClick={() => onClick(annotation.timestamp)}
              className="w-full mt-2 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 py-1 rounded transition-colors font-medium"
            >
              Jump to moment
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
