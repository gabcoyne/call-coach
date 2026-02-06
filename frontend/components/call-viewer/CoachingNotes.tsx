"use client";

import { useState } from "react";
import { MessageSquarePlus, Save } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface CoachingNotesProps {
  callId: string;
  isManager: boolean;
  className?: string;
}

interface Note {
  id: string;
  content: string;
  authorName: string;
  timestamp: string;
}

export function CoachingNotes({ callId, isManager, className }: CoachingNotesProps) {
  // Manager-only feature
  if (!isManager) {
    return null;
  }

  const [notes, setNotes] = useState<Note[]>([]);
  const [newNote, setNewNote] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveNote = async () => {
    if (!newNote.trim()) return;

    setIsSaving(true);

    try {
      // TODO: Implement API call to save note
      const note: Note = {
        id: Date.now().toString(),
        content: newNote,
        authorName: "Current Manager", // TODO: Get from auth
        timestamp: new Date().toISOString(),
      };

      setNotes([note, ...notes]);
      setNewNote("");
    } catch (error) {
      console.error("Failed to save note:", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquarePlus className="h-5 w-5" />
          Coaching Notes
          <span className="text-xs font-normal text-muted-foreground ml-auto">Manager Only</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Add a private coaching note..."
            className="w-full min-h-[100px] p-3 text-sm border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-prefect-blue-500"
          />
          <div className="flex justify-end">
            <Button onClick={handleSaveNote} disabled={!newNote.trim() || isSaving} size="sm">
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? "Saving..." : "Save Note"}
            </Button>
          </div>
        </div>

        {notes.length > 0 && (
          <div className="space-y-3 mt-4">
            <h4 className="text-sm font-semibold">Previous Notes</h4>
            {notes.map((note) => (
              <div key={note.id} className="p-3 rounded-md bg-muted/50 border space-y-1">
                <p className="text-sm">{note.content}</p>
                <p className="text-xs text-muted-foreground">
                  {note.authorName} •{" "}
                  {new Date(note.timestamp).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
