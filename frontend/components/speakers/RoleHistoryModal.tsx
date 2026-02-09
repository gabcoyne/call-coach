"use client";

import { useEffect, useState } from "react";
import { X, Clock, User, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface RoleHistoryEntry {
  id: string;
  speaker_id: string;
  old_role: string | null;
  new_role: string | null;
  changed_by: string;
  changed_at: string;
  reason: string | null;
}

interface RoleHistoryModalProps {
  speakerId: string;
  speakerName: string;
  speakerEmail: string;
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
}

const ROLE_LABELS: Record<string, string> = {
  ae: "Account Executive",
  se: "Sales Engineer",
  csm: "Customer Success Manager",
  support: "Support Engineer",
};

const ROLE_COLORS: Record<string, string> = {
  ae: "bg-blue-100 text-blue-800 border-blue-200",
  se: "bg-purple-100 text-purple-800 border-purple-200",
  csm: "bg-green-100 text-green-800 border-green-200",
  support: "bg-orange-100 text-orange-800 border-orange-200",
};

export function RoleHistoryModal({
  speakerId,
  speakerName,
  speakerEmail,
  isOpen,
  onClose,
  userEmail,
}: RoleHistoryModalProps) {
  const [history, setHistory] = useState<RoleHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && speakerId) {
      fetchHistory();
    }
  }, [isOpen, speakerId]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(
        `${MCP_BACKEND_URL}/api/v1/speakers/${speakerId}/history?limit=50`,
        {
          headers: {
            "X-User-Email": userEmail,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch history");
      }

      const data = await response.json();
      setHistory(data);
    } catch (err) {
      console.error("Error fetching role history:", err);
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).format(date);
  };

  const getRoleBadge = (role: string | null) => {
    if (!role) {
      return (
        <Badge variant="outline" className="bg-gray-100 text-gray-600 border-gray-200">
          None
        </Badge>
      );
    }

    return (
      <Badge variant="outline" className={ROLE_COLORS[role] || "bg-gray-100 text-gray-600"}>
        {ROLE_LABELS[role] || role.toUpperCase()}
      </Badge>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Role Change History</DialogTitle>
          <DialogDescription>
            {speakerName || speakerEmail}
            {speakerName && <span className="text-xs text-gray-500 ml-2">({speakerEmail})</span>}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto pr-2">
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-start gap-4 p-4 border rounded-lg">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-600 mb-2">Failed to load history</div>
              <p className="text-sm text-gray-600">{error}</p>
              <Button variant="outline" size="sm" onClick={fetchHistory} className="mt-4">
                Retry
              </Button>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No role changes recorded</p>
              <p className="text-sm text-gray-500 mt-2">
                Role assignments and changes will appear here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((entry, index) => (
                <div
                  key={entry.id}
                  className="relative p-4 border rounded-lg bg-white hover:bg-gray-50 transition-colors"
                >
                  {/* Timeline connector */}
                  {index < history.length - 1 && (
                    <div className="absolute left-8 top-16 w-px h-6 bg-gray-200" />
                  )}

                  <div className="flex items-start gap-4">
                    {/* Timeline dot */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mt-1">
                      <Clock className="h-4 w-4 text-blue-600" />
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Role change */}
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        {getRoleBadge(entry.old_role)}
                        <ArrowRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                        {getRoleBadge(entry.new_role)}
                      </div>

                      {/* Metadata */}
                      <div className="flex items-center gap-3 text-sm text-gray-600 flex-wrap">
                        <div className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span>{entry.changed_by}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>{formatDate(entry.changed_at)}</span>
                        </div>
                      </div>

                      {/* Reason (if provided) */}
                      {entry.reason && (
                        <div className="mt-2 text-sm text-gray-700 bg-gray-50 p-2 rounded">
                          <span className="font-medium">Reason:</span> {entry.reason}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
