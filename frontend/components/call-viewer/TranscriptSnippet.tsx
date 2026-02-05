import { Clock, User, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { SpecificExamples } from "@/types/coaching";

interface TranscriptSnippetProps {
  examples: SpecificExamples | null;
  callId?: string;
  className?: string;
}

interface SnippetItemProps {
  text: string;
  type: "good" | "needs_work";
  onClick?: () => void;
}

function SnippetItem({ text, type, onClick }: SnippetItemProps) {
  const isGood = type === "good";

  return (
    <div
      className={cn(
        "p-4 rounded-lg border-l-4 cursor-pointer hover:bg-muted/50 transition-colors",
        isGood
          ? "bg-green-50 border-l-green-500 dark:bg-green-950/20"
          : "bg-amber-50 border-l-amber-500 dark:bg-amber-950/20"
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <p className="text-sm leading-relaxed">{text}</p>
        </div>
        {onClick && (
          <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
        )}
      </div>
    </div>
  );
}

export function TranscriptSnippet({
  examples,
  callId,
  className,
}: TranscriptSnippetProps) {
  if (!examples || (!examples.good?.length && !examples.needs_work?.length)) {
    return null;
  }

  const handleSnippetClick = (snippet: string) => {
    // TODO: Extract timestamp from snippet and link to Gong
    // For now, just log for future implementation
    console.log("Clicked snippet:", snippet, "Call ID:", callId);
  };

  return (
    <div className={className}>
      <h3 className="text-lg font-semibold mb-4">Transcript Highlights</h3>

      {examples.good && examples.good.length > 0 && (
        <Card className="mb-4">
          <CardHeader>
            <h4 className="font-semibold text-green-700 text-sm flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              Effective Moments
            </h4>
          </CardHeader>
          <CardContent className="space-y-3">
            {examples.good.map((snippet, index) => (
              <SnippetItem
                key={index}
                text={snippet}
                type="good"
                onClick={() => handleSnippetClick(snippet)}
              />
            ))}
          </CardContent>
        </Card>
      )}

      {examples.needs_work && examples.needs_work.length > 0 && (
        <Card>
          <CardHeader>
            <h4 className="font-semibold text-amber-700 text-sm flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Coaching Opportunities
            </h4>
          </CardHeader>
          <CardContent className="space-y-3">
            {examples.needs_work.map((snippet, index) => (
              <SnippetItem
                key={index}
                text={snippet}
                type="needs_work"
                onClick={() => handleSnippetClick(snippet)}
              />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
