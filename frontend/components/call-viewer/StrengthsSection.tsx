import { CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StrengthsSectionProps {
  strengths: string[];
  className?: string;
}

export function StrengthsSection({ strengths, className }: StrengthsSectionProps) {
  if (!strengths || strengths.length === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-700">
          <CheckCircle2 className="h-5 w-5" />
          Strengths
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {strengths.map((strength, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-green-600 mt-1">•</span>
              <span className="text-sm">{strength}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
