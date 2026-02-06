"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchCallsRequest } from "@/types/coaching";
import { Plus, X } from "lucide-react";

interface TopicKeywordFilterProps {
  filters: Partial<SearchCallsRequest>;
  onFiltersChange: (filters: Partial<SearchCallsRequest>) => void;
}

export function TopicKeywordFilter({ filters, onFiltersChange }: TopicKeywordFilterProps) {
  const [inputValue, setInputValue] = useState("");

  const topics = filters.topics || [];

  const addTopic = () => {
    if (inputValue.trim() && !topics.includes(inputValue.trim())) {
      onFiltersChange({
        ...filters,
        topics: [...topics, inputValue.trim()],
      });
      setInputValue("");
    }
  };

  const removeTopic = (topicToRemove: string) => {
    const newTopics = topics.filter((topic) => topic !== topicToRemove);
    onFiltersChange({
      ...filters,
      topics: newTopics.length > 0 ? newTopics : undefined,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addTopic();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Topics & Keywords</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 space-y-2">
              <Label htmlFor="topic-input">Add Topic or Keyword</Label>
              <Input
                id="topic-input"
                type="text"
                placeholder="e.g., migration, scalability, pricing"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
              />
            </div>
            <div className="flex items-end">
              <Button
                type="button"
                onClick={addTopic}
                variant="outline"
                size="default"
                className="h-10"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add
              </Button>
            </div>
          </div>

          {topics.length > 0 && (
            <div className="space-y-2">
              <Label>Active Topics ({topics.length})</Label>
              <div className="flex flex-wrap gap-2">
                {topics.map((topic) => (
                  <Badge key={topic} variant="secondary" className="pl-2 pr-1 py-1">
                    {topic}
                    <button
                      onClick={() => removeTopic(topic)}
                      className="ml-1 rounded-full hover:bg-muted p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <p className="text-sm text-muted-foreground">
            Search for calls containing specific topics or keywords in transcripts and analysis
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
