"use client";

import { useState } from "react";
import { CheckSquare, Square } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ActionItemsListProps {
  actionItems: string[];
  className?: string;
}

export function ActionItemsList({ actionItems, className }: ActionItemsListProps) {
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

  if (!actionItems || actionItems.length === 0) {
    return null;
  }

  const toggleItem = (index: number) => {
    setCheckedItems((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const completedCount = checkedItems.size;
  const totalCount = actionItems.length;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">Action Items</CardTitle>
          <span className="text-sm text-muted-foreground">
            {completedCount} / {totalCount} completed
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {actionItems.map((item, index) => {
            const isChecked = checkedItems.has(index);
            return (
              <li key={index}>
                <button
                  onClick={() => toggleItem(index)}
                  className="flex items-start gap-3 w-full text-left p-2 rounded-md hover:bg-muted/50 transition-colors"
                >
                  {isChecked ? (
                    <CheckSquare className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <Square className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  )}
                  <span
                    className={cn(
                      "text-sm flex-1",
                      isChecked && "line-through text-muted-foreground"
                    )}
                  >
                    {item}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
