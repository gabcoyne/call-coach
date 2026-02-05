import type { DimensionScores } from "@/types/coaching";
import { DimensionScoreCard } from "@/components/ui/score-badge";

interface DimensionScoreCardsProps {
  scores: DimensionScores;
  className?: string;
}

const DIMENSION_LABELS: Record<string, string> = {
  product_knowledge: "Product Knowledge",
  discovery: "Discovery",
  objection_handling: "Objection Handling",
  engagement: "Engagement",
};

const DIMENSION_DESCRIPTIONS: Record<string, string> = {
  product_knowledge:
    "Understanding of Prefect features, benefits, and technical details",
  discovery: "Ability to uncover customer needs, pain points, and requirements",
  objection_handling:
    "Effectiveness in addressing concerns and overcoming obstacles",
  engagement: "Rapport building, active listening, and conversational flow",
};

export function DimensionScoreCards({
  scores,
  className,
}: DimensionScoreCardsProps) {
  const dimensions = [
    "product_knowledge",
    "discovery",
    "objection_handling",
    "engagement",
  ] as const;

  return (
    <div className={className}>
      <h3 className="text-lg font-semibold mb-4">Dimension Scores</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dimensions.map((dimension) => {
          const score = scores[dimension];
          if (score === null || score === undefined) return null;

          return (
            <DimensionScoreCard
              key={dimension}
              dimension={DIMENSION_LABELS[dimension]}
              score={score}
              description={DIMENSION_DESCRIPTIONS[dimension]}
            />
          );
        })}
      </div>
    </div>
  );
}
