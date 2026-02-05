"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SearchCallsRequest } from "@/types/coaching";
import { Save, Check } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface SaveSearchButtonProps {
  filters: Partial<SearchCallsRequest>;
  onSave?: (name: string) => void;
}

export interface SavedSearch {
  id: string;
  name: string;
  filters: Partial<SearchCallsRequest>;
  createdAt: string;
}

const STORAGE_KEY = "coaching-saved-searches";

export function SaveSearchButton({ filters, onSave }: SaveSearchButtonProps) {
  const [open, setOpen] = useState(false);
  const [searchName, setSearchName] = useState("");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    if (!searchName.trim()) return;

    // Get existing saved searches
    const existingSearches = getSavedSearches();

    // Create new saved search
    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name: searchName.trim(),
      filters,
      createdAt: new Date().toISOString(),
    };

    // Save to localStorage
    const updatedSearches = [...existingSearches, newSearch];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSearches));

    // Show success state
    setSaved(true);
    onSave?.(searchName.trim());

    // Reset after delay
    setTimeout(() => {
      setOpen(false);
      setSearchName("");
      setSaved(false);
    }, 1500);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Save className="h-4 w-4 mr-2" />
          Save Search
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save Current Search</DialogTitle>
          <DialogDescription>
            Give this search configuration a name to quickly access it later.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="search-name">Search Name</Label>
            <Input
              id="search-name"
              placeholder="e.g., Low Performers This Month"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSave();
                }
              }}
            />
          </div>
          <div className="text-sm text-muted-foreground">
            <p className="font-medium mb-1">Current Filters:</p>
            <ul className="list-disc list-inside space-y-1">
              {Object.entries(filters).map(([key, value]) => {
                if (value === undefined || value === null) return null;
                return (
                  <li key={key} className="truncate">
                    {key}: {JSON.stringify(value)}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setOpen(false);
              setSearchName("");
              setSaved(false);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!searchName.trim() || saved}>
            {saved ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Saved!
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Utility functions for managing saved searches
export function getSavedSearches(): SavedSearch[] {
  if (typeof window === "undefined") return [];

  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return [];

  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

export function deleteSavedSearch(id: string): void {
  const searches = getSavedSearches();
  const updated = searches.filter((s) => s.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}
