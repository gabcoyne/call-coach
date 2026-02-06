"use client";

import * as Accordion from "@radix-ui/react-accordion";
import { CheckCircle, AlertCircle, ChevronDown } from "lucide-react";

export interface InsightCardProps {
  /** Title of the insight (e.g., "Discovery Quality", "Objection Handling") */
  title: string;
  /** Array of strength items to display */
  strengths?: string[];
  /** Array of improvement area items to display */
  improvements?: string[];
  /** Optional default open state (default: false) */
  defaultOpen?: boolean;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * InsightCard Component
 *
 * Displays coaching insights with collapsible content using Radix Accordion.
 * Shows strengths with checkmark icons and improvement areas with alert icons.
 */
export function InsightCard({
  title,
  strengths = [],
  improvements = [],
  defaultOpen = false,
  className = "",
}: InsightCardProps) {
  const hasContent = strengths.length > 0 || improvements.length > 0;

  return (
    <Accordion.Root
      type="single"
      collapsible
      defaultValue={defaultOpen ? "content" : undefined}
      className={`border rounded-lg ${className}`}
    >
      <Accordion.Item value="content">
        <Accordion.Header>
          <Accordion.Trigger className="flex w-full items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors">
            <h3 className="text-base font-semibold text-gray-900">{title}</h3>
            <ChevronDown
              className="h-5 w-5 text-gray-500 transition-transform duration-200 [&[data-state=open]]:rotate-180"
              aria-hidden="true"
            />
          </Accordion.Trigger>
        </Accordion.Header>

        <Accordion.Content className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
          <div className="p-4 pt-0 space-y-4">
            {!hasContent && <p className="text-sm text-gray-500">No insights available</p>}

            {/* Strengths Section */}
            {strengths.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Strengths
                </h4>
                <ul className="space-y-2">
                  {strengths.map((strength, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-green-600 mt-0.5">•</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvement Areas Section */}
            {improvements.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                  Areas for Improvement
                </h4>
                <ul className="space-y-2">
                  {improvements.map((improvement, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-amber-600 mt-0.5">•</span>
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Accordion.Content>
      </Accordion.Item>
    </Accordion.Root>
  );
}
