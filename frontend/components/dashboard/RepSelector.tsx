"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { User } from "lucide-react";

interface RepOption {
  email: string;
  name: string;
}

interface RepSelectorProps {
  reps: RepOption[];
  selectedRepEmail: string;
  onChange: (repEmail: string) => void;
  currentUserEmail?: string;
}

export function RepSelector({
  reps,
  selectedRepEmail,
  onChange,
  currentUserEmail,
}: RepSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <User className="w-4 h-4 text-muted-foreground" />
      <Select value={selectedRepEmail} onValueChange={onChange}>
        <SelectTrigger className="w-[280px]">
          <SelectValue placeholder="Select a rep" />
        </SelectTrigger>
        <SelectContent>
          {reps.map((rep) => (
            <SelectItem key={rep.email} value={rep.email}>
              <div className="flex items-center gap-2">
                <span>{rep.name}</span>
                {rep.email === currentUserEmail && (
                  <span className="text-xs text-muted-foreground">(You)</span>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
