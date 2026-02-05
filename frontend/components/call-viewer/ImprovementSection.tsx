import { AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ImprovementSectionProps {
  improvements: string[];
  className?: string;
}

export function ImprovementSection({
  improvements,
  className,
}: ImprovementSectionProps) {
  if (!improvements || improvements.length === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-amber-700">
          <AlertCircle className="h-5 w-5" />
          Areas for Improvement
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {improvements.map((improvement, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-amber-600 mt-1">•</span>
              <span className="text-sm">{improvement}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
