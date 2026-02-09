"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/hooks/useUser";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  Users,
  ChevronDown,
  Check,
  CheckSquare,
  Square,
  X,
  History,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { RoleHistoryModal } from "@/components/speakers/RoleHistoryModal";
import { useToast } from "@/components/ui/use-toast";

const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || "http://localhost:8000";

interface Speaker {
  id: string;
  email: string;
  name: string | null;
  role: "ae" | "se" | "csm" | "support" | null;
  company_side: boolean;
  first_seen: string | null;
  last_call_date: string | null;
  total_calls: number;
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

export default function SpeakersPage() {
  const { currentUser, isManager, loading: userLoading } = useUser();
  const { toast } = useToast();
  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterRole, setFilterRole] = useState<string | null>(null);
  const [showUnassigned, setShowUnassigned] = useState(true);
  const [updatingSpeakerId, setUpdatingSpeakerId] = useState<string | null>(null);
  const [selectedSpeakerIds, setSelectedSpeakerIds] = useState<Set<string>>(new Set());
  const [bulkUpdating, setBulkUpdating] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedSpeakerForHistory, setSelectedSpeakerForHistory] = useState<Speaker | null>(null);

  useEffect(() => {
    if (userLoading) return;

    if (!currentUser || !isManager) {
      setError("Access denied. Manager or admin role required.");
      setLoading(false);
      return;
    }

    fetchSpeakers();
  }, [currentUser, isManager, userLoading, filterRole, showUnassigned]);

  const fetchSpeakers = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        company_side_only: "true",
        include_unassigned: String(showUnassigned),
      });

      if (filterRole) {
        params.append("role", filterRole);
      }

      const response = await fetch(`${MCP_BACKEND_URL}/api/v1/speakers?${params}`, {
        headers: {
          "X-User-Email": currentUser?.email || "",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch speakers");
      }

      const data = await response.json();
      setSpeakers(data);
    } catch (err) {
      console.error("Error fetching speakers:", err);
      setError(err instanceof Error ? err.message : "Failed to load speakers");
    } finally {
      setLoading(false);
    }
  };

  const updateSpeakerRole = async (speakerId: string, newRole: string | null) => {
    try {
      setUpdatingSpeakerId(speakerId);
      setError(null);

      const response = await fetch(`${MCP_BACKEND_URL}/api/v1/speakers/${speakerId}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": currentUser?.email || "",
        },
        body: JSON.stringify({ role: newRole }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update speaker role");
      }

      // Update local state optimistically
      setSpeakers((prev) =>
        prev.map((s) => (s.id === speakerId ? { ...s, role: newRole as Speaker["role"] } : s))
      );

      // Show success toast
      const speaker = speakers.find((s) => s.id === speakerId);
      const roleName = newRole ? ROLE_LABELS[newRole] : "None";
      toast({
        title: "Role Updated",
        description: `${speaker?.name || speaker?.email} assigned to ${roleName}`,
        variant: "success",
      });
    } catch (err) {
      console.error("Error updating speaker role:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to update role";
      setError(errorMessage);

      // Show error toast
      toast({
        title: "Update Failed",
        description: errorMessage,
        variant: "error",
      });

      // Refetch to ensure consistency
      await fetchSpeakers();
    } finally {
      setUpdatingSpeakerId(null);
    }
  };

  const bulkUpdateRoles = async (role: string | null) => {
    if (selectedSpeakerIds.size === 0) return;

    try {
      setBulkUpdating(true);
      setError(null);

      const updates = Array.from(selectedSpeakerIds).map((speakerId) => ({
        speaker_id: speakerId,
        role: role,
      }));

      const response = await fetch(`${MCP_BACKEND_URL}/api/v1/speakers/bulk-update-roles`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": currentUser?.email || "",
        },
        body: JSON.stringify({ updates }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to bulk update roles");
      }

      const result = await response.json();

      // Clear selection and refetch
      setSelectedSpeakerIds(new Set());
      await fetchSpeakers();

      // Show success toast
      const roleName = role ? ROLE_LABELS[role] : "None";
      toast({
        title: "Bulk Update Successful",
        description: `Updated ${result.updated} speaker${
          result.updated !== 1 ? "s" : ""
        } to ${roleName}`,
        variant: "success",
      });
    } catch (err) {
      console.error("Error bulk updating roles:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to bulk update roles";
      setError(errorMessage);

      // Show error toast
      toast({
        title: "Bulk Update Failed",
        description: errorMessage,
        variant: "error",
      });

      await fetchSpeakers();
    } finally {
      setBulkUpdating(false);
    }
  };

  const toggleSpeakerSelection = (speakerId: string) => {
    setSelectedSpeakerIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(speakerId)) {
        newSet.delete(speakerId);
      } else {
        newSet.add(speakerId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedSpeakerIds.size === speakers.length) {
      setSelectedSpeakerIds(new Set());
    } else {
      setSelectedSpeakerIds(new Set(speakers.map((s) => s.id)));
    }
  };

  const clearSelection = () => {
    setSelectedSpeakerIds(new Set());
  };

  const openHistoryModal = (speaker: Speaker) => {
    setSelectedSpeakerForHistory(speaker);
    setHistoryModalOpen(true);
  };

  const closeHistoryModal = () => {
    setHistoryModalOpen(false);
    setSelectedSpeakerForHistory(null);
  };

  if (userLoading || loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading speakers...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const unassignedCount = speakers.filter((s) => !s.role).length;
  const assignedCount = speakers.length - unassignedCount;

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Speaker Role Management</h1>
        <p className="text-gray-600">
          Manage business roles for Prefect team members appearing in sales calls
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Speakers</CardDescription>
            <CardTitle className="text-3xl">{speakers.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Role Assigned</CardDescription>
            <CardTitle className="text-3xl text-green-600">{assignedCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Role Not Assigned</CardDescription>
            <CardTitle className="text-3xl text-amber-600">{unassignedCount}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Bulk Actions Bar */}
      {selectedSpeakerIds.size > 0 && (
        <Card className="mb-6 border-blue-200 bg-blue-50">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-gray-900">
                  {selectedSpeakerIds.size} speaker{selectedSpeakerIds.size !== 1 ? "s" : ""}{" "}
                  selected
                </span>
                <Button variant="outline" size="sm" onClick={clearSelection} className="h-8">
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 mr-2">Assign role:</span>
                {Object.entries(ROLE_LABELS).map(([key, label]) => (
                  <Button
                    key={key}
                    size="sm"
                    disabled={bulkUpdating}
                    onClick={() => bulkUpdateRoles(key)}
                    className={`h-8 ${
                      key === "ae"
                        ? "bg-blue-600 hover:bg-blue-700"
                        : key === "se"
                          ? "bg-purple-600 hover:bg-purple-700"
                          : key === "csm"
                            ? "bg-green-600 hover:bg-green-700"
                            : "bg-orange-600 hover:bg-orange-700"
                    } text-white`}
                  >
                    {bulkUpdating ? "⏳" : label}
                  </Button>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  disabled={bulkUpdating}
                  onClick={() => bulkUpdateRoles(null)}
                  className="h-8"
                >
                  Remove Role
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Filters</CardTitle>
            <Button variant="outline" size="sm" onClick={toggleSelectAll} className="h-8">
              {selectedSpeakerIds.size === speakers.length ? (
                <>
                  <CheckSquare className="h-4 w-4 mr-1" />
                  Deselect All
                </>
              ) : (
                <>
                  <Square className="h-4 w-4 mr-1" />
                  Select All
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilterRole(null)}
                  className={`px-3 py-1 rounded-md text-sm ${
                    filterRole === null
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  All
                </button>
                {Object.entries(ROLE_LABELS).map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setFilterRole(key)}
                    className={`px-3 py-1 rounded-md text-sm ${
                      filterRole === key
                        ? "bg-gray-900 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Show Unassigned
              </label>
              <button
                onClick={() => setShowUnassigned(!showUnassigned)}
                className={`px-3 py-1 rounded-md text-sm ${
                  showUnassigned
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {showUnassigned ? "Yes" : "No"}
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Speakers List */}
      {speakers.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No speakers found matching the current filters</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {speakers.map((speaker) => {
            const isSelected = selectedSpeakerIds.has(speaker.id);
            return (
              <Card
                key={speaker.id}
                className={`hover:shadow-lg transition-all ${
                  isSelected ? "ring-2 ring-blue-500 bg-blue-50" : ""
                }`}
              >
                <CardHeader>
                  <div className="flex items-start gap-3">
                    {/* Checkbox */}
                    <button
                      onClick={() => toggleSpeakerSelection(speaker.id)}
                      className="flex-shrink-0 mt-1"
                    >
                      {isSelected ? (
                        <CheckSquare className="h-5 w-5 text-blue-600" />
                      ) : (
                        <Square className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg truncate">
                        {speaker.name || speaker.email}
                      </CardTitle>
                      {speaker.name && (
                        <CardDescription className="text-xs mt-1 truncate">
                          {speaker.email}
                        </CardDescription>
                      )}
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button
                          disabled={updatingSpeakerId === speaker.id}
                          className={`ml-2 flex-shrink-0 inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium border transition-colors ${
                            speaker.role
                              ? ROLE_COLORS[speaker.role]
                              : "bg-amber-100 text-amber-800 border-amber-200"
                          } ${
                            updatingSpeakerId === speaker.id
                              ? "opacity-50 cursor-not-allowed"
                              : "hover:opacity-80 cursor-pointer"
                          }`}
                        >
                          {updatingSpeakerId === speaker.id ? (
                            <span className="animate-spin">⏳</span>
                          ) : (
                            <>
                              {speaker.role ? ROLE_LABELS[speaker.role] : "Role Not Assigned"}
                              <ChevronDown className="h-3 w-3" />
                            </>
                          )}
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-56">
                        {Object.entries(ROLE_LABELS).map(([key, label]) => (
                          <DropdownMenuItem
                            key={key}
                            onClick={() => updateSpeakerRole(speaker.id, key)}
                            className="flex items-center justify-between"
                          >
                            <span>{label}</span>
                            {speaker.role === key && <Check className="h-4 w-4" />}
                          </DropdownMenuItem>
                        ))}
                        {speaker.role && (
                          <>
                            <div className="my-1 h-px bg-gray-200" />
                            <DropdownMenuItem
                              onClick={() => updateSpeakerRole(speaker.id, null)}
                              className="text-gray-500"
                            >
                              Remove Role
                            </DropdownMenuItem>
                          </>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Total Calls:</span>
                      <span className="font-medium text-gray-900">{speaker.total_calls}</span>
                    </div>
                    {speaker.last_call_date && (
                      <div className="flex justify-between">
                        <span>Last Call:</span>
                        <span className="font-medium text-gray-900">
                          {new Date(speaker.last_call_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    {speaker.first_seen && (
                      <div className="flex justify-between">
                        <span>First Seen:</span>
                        <span className="font-medium text-gray-900">
                          {new Date(speaker.first_seen).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* View History Button */}
                  <div className="mt-4 pt-3 border-t">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openHistoryModal(speaker)}
                      className="w-full"
                    >
                      <History className="h-4 w-4 mr-2" />
                      View Role History
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Role History Modal */}
      {selectedSpeakerForHistory && (
        <RoleHistoryModal
          speakerId={selectedSpeakerForHistory.id}
          speakerName={selectedSpeakerForHistory.name || ""}
          speakerEmail={selectedSpeakerForHistory.email}
          isOpen={historyModalOpen}
          onClose={closeHistoryModal}
          userEmail={currentUser?.email || ""}
        />
      )}
    </div>
  );
}
