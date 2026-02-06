/**
 * RubricBadge Component
 *
 * Displays which role-specific rubric was used to evaluate a call.
 * Shows a colored badge with role name and provides a tooltip explaining
 * the role-specific evaluation criteria.
 */
import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface RubricBadgeProps {
  role: "ae" | "se" | "csm";
  className?: string;
}

const ROLE_CONFIG = {
  ae: {
    label: "Account Executive",
    shortLabel: "AE",
    color: "bg-blue-100 text-blue-800 border-blue-300",
    description:
      "Evaluated using Account Executive rubric focusing on Discovery (30%), Objection Handling (25%), Product Positioning (20%), Relationship Building (15%), and Call Control (10%)",
  },
  se: {
    label: "Sales Engineer",
    shortLabel: "SE",
    color: "bg-green-100 text-green-800 border-green-300",
    description:
      "Evaluated using Sales Engineer rubric focusing on Technical Accuracy (35%), Architecture Fit (30%), Problem-Solution Mapping (20%), Technical Objection Resolution (10%), and Collaboration with AE (5%)",
  },
  csm: {
    label: "Customer Success Manager",
    shortLabel: "CSM",
    color: "bg-purple-100 text-purple-800 border-purple-300",
    description:
      "Evaluated using Customer Success Manager rubric focusing on Value Realization (30%), Risk Identification (25%), Relationship Depth (20%), Expansion Opportunity (15%), and Product Adoption (10%)",
  },
};

export function RubricBadge({ role, className = "" }: RubricBadgeProps) {
  const config = ROLE_CONFIG[role];

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border font-medium text-sm ${config.color} ${className}`}
          >
            <span>Evaluated as: {config.label}</span>
            <Info className="h-4 w-4" />
          </div>
        </TooltipTrigger>
        <TooltipContent className="max-w-sm">
          <p className="text-sm">{config.description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
