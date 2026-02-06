"use client";

import { getPriorityColor } from "@/lib/colors";

export interface ActionItemProps {
  /** Action item text/description */
  text: string;
  /** Priority level (high, medium, low) */
  priority: "high" | "medium" | "low";
  /** Optional completion status */
  completed?: boolean;
  /** Optional callback when checkbox is toggled */
  onComplete?: (completed: boolean) => void;
  /** Optional className for additional styling */
  className?: string;
}

/**
 * ActionItem Component
 *
 * Displays an actionable coaching recommendation with priority badge and optional checkbox.
 * - High priority: Red badge
 * - Medium priority: Yellow badge
 * - Low priority: Blue badge
 */
export function ActionItem({
  text,
  priority,
  completed = false,
  onComplete,
  className = "",
}: ActionItemProps) {
  const priorityColors = getPriorityColor(priority);
  const showCheckbox = typeof onComplete === "function";

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onComplete) {
      onComplete(e.target.checked);
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-3 border rounded-lg ${
        completed ? "bg-gray-50" : "bg-white"
      } ${className}`}
    >
      {/* Optional Checkbox */}
      {showCheckbox && (
        <input
          type="checkbox"
          checked={completed}
          onChange={handleCheckboxChange}
          className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
          aria-label={`Mark "${text}" as ${completed ? "incomplete" : "complete"}`}
        />
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {/* Priority Badge */}
          <span
            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold"
            style={{
              backgroundColor: priorityColors.bg,
              color: priorityColors.text,
              borderColor: priorityColors.border,
              borderWidth: "1px",
            }}
          >
            {priority.charAt(0).toUpperCase() + priority.slice(1)}
          </span>
        </div>

        {/* Action Text */}
        <p className={`text-sm ${completed ? "line-through text-gray-500" : "text-gray-700"}`}>
          {text}
        </p>
      </div>
    </div>
  );
}
