"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { SearchCallsRequest } from "@/types/coaching";
import { getSavedSearches, deleteSavedSearch, SavedSearch } from "./save-search-button";
import { FolderOpen, Trash2 } from "lucide-react";

interface LoadSavedSearchesProps {
  onLoad: (filters: Partial<SearchCallsRequest>) => void;
}

export function LoadSavedSearches({ onLoad }: LoadSavedSearchesProps) {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");

  // Load saved searches on mount and when storage changes
  useEffect(() => {
    loadSearches();

    // Listen for storage events (updates from other tabs)
    const handleStorageChange = () => {
      loadSearches();
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const loadSearches = () => {
    setSavedSearches(getSavedSearches());
  };

  const handleLoad = () => {
    const search = savedSearches.find((s) => s.id === selectedId);
    if (search) {
      onLoad(search.filters);
    }
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteSavedSearch(id);
    loadSearches();
    if (selectedId === id) {
      setSelectedId("");
    }
  };

  if (savedSearches.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        <FolderOpen className="h-4 w-4 inline mr-1" />
        No saved searches yet
      </div>
    );
  }

  return (
    <div className="flex items-end gap-2">
      <div className="flex-1 space-y-2">
        <Label htmlFor="saved-searches">Load Saved Search</Label>
        <Select value={selectedId} onValueChange={setSelectedId}>
          <SelectTrigger id="saved-searches">
            <SelectValue placeholder="Select a saved search..." />
          </SelectTrigger>
          <SelectContent>
            {savedSearches.map((search) => (
              <SelectItem key={search.id} value={search.id}>
                <div className="flex items-center justify-between w-full">
                  <span>{search.name}</span>
                  <span className="text-xs text-muted-foreground ml-2">
                    {new Date(search.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <Button
        onClick={handleLoad}
        disabled={!selectedId}
        variant="outline"
      >
        Load
      </Button>
      {selectedId && (
        <Button
          onClick={(e) => handleDelete(selectedId, e)}
          variant="destructive"
          size="icon"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
