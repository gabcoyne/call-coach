"use client";

/**
 * RoleAssignmentTable Component
 *
 * Displays Prefect staff members with their assigned roles.
 * Features:
 * - Search by name or email
 * - Filter by role (all/AE/SE/CSM/unassigned)
 * - Individual role assignment via dropdown
 * - Bulk role assignment for multiple staff members
 * - Last updated timestamp with assigned_by tooltip
 */
import { useState, useMemo } from "react";
import useSWR from "swr";
import { Search, ChevronDown, Check, X, UserCheck, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Checkbox } from "@/components/ui/checkbox";

interface StaffMember {
  email: string;
  name: string;
  role: "ae" | "se" | "csm" | null;
  assigned_by: string | null;
  assigned_at: string | null;
  updated_at: string | null;
}

interface StaffRolesResponse {
  staff: StaffMember[];
  total: number;
  with_roles: number;
}

const ROLE_OPTIONS = [
  { value: "ae", label: "Account Executive", color: "text-blue-700 bg-blue-100" },
  { value: "se", label: "Sales Engineer", color: "text-green-700 bg-green-100" },
  { value: "csm", label: "Customer Success Manager", color: "text-purple-700 bg-purple-100" },
];

const ROLE_LABELS: Record<string, string> = {
  ae: "AE",
  se: "SE",
  csm: "CSM",
};

const ROLE_COLORS: Record<string, string> = {
  ae: "text-blue-700 bg-blue-100",
  se: "text-green-700 bg-green-100",
  csm: "text-purple-700 bg-purple-100",
};

export function RoleAssignmentTable() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set());
  const [bulkRole, setBulkRole] = useState<"ae" | "se" | "csm" | "">("");
  const [updatingEmails, setUpdatingEmails] = useState<Set<string>>(new Set());

  // Fetch staff and role assignments
  const { data, error, isLoading, mutate } = useSWR<StaffRolesResponse>(
    "/api/settings/roles",
    async (url: string) => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error("Failed to fetch staff roles");
      }
      return response.json();
    }
  );

  // Filter and search staff
  const filteredStaff = useMemo(() => {
    if (!data?.staff) return [];

    let filtered = data.staff;

    // Apply role filter
    if (roleFilter !== "all") {
      if (roleFilter === "unassigned") {
        filtered = filtered.filter((s) => !s.role);
      } else {
        filtered = filtered.filter((s) => s.role === roleFilter);
      }
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.name.toLowerCase().includes(query) ||
          s.email.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [data?.staff, roleFilter, searchQuery]);

  // Update individual role
  const updateRole = async (email: string, role: "ae" | "se" | "csm" | null) => {
    setUpdatingEmails((prev) => new Set(prev).add(email));

    try {
      if (role === null) {
        // Delete role assignment
        const response = await fetch(`/api/settings/roles/${encodeURIComponent(email)}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          throw new Error("Failed to remove role assignment");
        }

        toast({
          title: "Role Removed",
          description: `Removed role assignment for ${email}`,
        });
      } else {
        // Update role assignment
        const response = await fetch(`/api/settings/roles/${encodeURIComponent(email)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ role }),
        });

        if (!response.ok) {
          throw new Error("Failed to update role");
        }

        toast({
          title: "Role Updated",
          description: `Assigned ${ROLE_LABELS[role]} role to ${email}`,
        });
      }

      // Refresh data
      mutate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUpdatingEmails((prev) => {
        const next = new Set(prev);
        next.delete(email);
        return next;
      });
    }
  };

  // Bulk role assignment
  const handleBulkAssignment = async () => {
    if (!bulkRole || selectedEmails.size === 0) return;

    const emailsToUpdate = Array.from(selectedEmails);
    setUpdatingEmails(new Set(emailsToUpdate));

    try {
      // Update all selected emails in parallel
      const updates = emailsToUpdate.map((email) =>
        fetch(`/api/settings/roles/${encodeURIComponent(email)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ role: bulkRole }),
        }).then((res) => {
          if (!res.ok) throw new Error(`Failed to update ${email}`);
          return res;
        })
      );

      await Promise.all(updates);

      toast({
        title: "Bulk Assignment Complete",
        description: `Updated ${emailsToUpdate.length} staff members to ${ROLE_LABELS[bulkRole]} role`,
      });

      // Clear selection
      setSelectedEmails(new Set());
      setBulkRole("");

      // Refresh data
      mutate();
    } catch (error: any) {
      toast({
        title: "Bulk Assignment Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUpdatingEmails(new Set());
    }
  };

  // Toggle row selection
  const toggleSelection = (email: string) => {
    setSelectedEmails((prev) => {
      const next = new Set(prev);
      if (next.has(email)) {
        next.delete(email);
      } else {
        next.add(email);
      }
      return next;
    });
  };

  // Toggle all visible rows
  const toggleSelectAll = () => {
    if (selectedEmails.size === filteredStaff.length) {
      setSelectedEmails(new Set());
    } else {
      setSelectedEmails(new Set(filteredStaff.map((s) => s.email)));
    }
  };

  // Format relative time
  const formatRelativeTime = (dateStr: string | null) => {
    if (!dateStr) return "Never";

    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  if (error) {
    return (
      <div className="border rounded-lg p-6 text-center">
        <p className="text-red-600">Failed to load staff roles: {error.message}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="border rounded-lg p-6 text-center">
        <div className="animate-spin h-8 w-8 border-4 border-prefect-blue-500 border-t-transparent rounded-full mx-auto" />
        <p className="text-sm text-gray-500 mt-2">Loading staff members...</p>
      </div>
    );
  }

  const allSelected = selectedEmails.size === filteredStaff.length && filteredStaff.length > 0;
  const someSelected = selectedEmails.size > 0 && selectedEmails.size < filteredStaff.length;

  return (
    <div className="space-y-4">
      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={roleFilter} onValueChange={setRoleFilter}>
          <SelectTrigger className="w-full sm:w-[200px]">
            <SelectValue placeholder="Filter by role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Roles</SelectItem>
            <SelectItem value="ae">AE Only</SelectItem>
            <SelectItem value="se">SE Only</SelectItem>
            <SelectItem value="csm">CSM Only</SelectItem>
            <SelectItem value="unassigned">Unassigned</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats Summary */}
      <div className="flex items-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4" />
          <span>
            {filteredStaff.length} of {data?.total || 0} staff members
          </span>
        </div>
        {data && (
          <div className="flex items-center gap-2">
            <UserCheck className="h-4 w-4" />
            <span>{data.with_roles} assigned roles</span>
          </div>
        )}
      </div>

      {/* Bulk Action Bar */}
      {selectedEmails.size > 0 && (
        <div className="border rounded-lg p-4 bg-blue-50 border-blue-200 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-blue-900">
              {selectedEmails.size} selected
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedEmails(new Set())}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <Select
              value={bulkRole}
              onValueChange={(value) => setBulkRole(value as "ae" | "se" | "csm")}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ae">Account Executive</SelectItem>
                <SelectItem value="se">Sales Engineer</SelectItem>
                <SelectItem value="csm">Customer Success Manager</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={handleBulkAssignment}
              disabled={!bulkRole || updatingEmails.size > 0}
            >
              Assign Role
            </Button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={toggleSelectAll}
                  aria-label="Select all"
                  className={someSelected ? "opacity-50" : ""}
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStaff.map((staff) => {
              const isSelected = selectedEmails.has(staff.email);
              const isUpdating = updatingEmails.has(staff.email);

              return (
                <tr
                  key={staff.email}
                  className={isSelected ? "bg-blue-50" : "hover:bg-gray-50"}
                >
                  <td className="px-6 py-4">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => toggleSelection(staff.email)}
                      disabled={isUpdating}
                      aria-label={`Select ${staff.name}`}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {staff.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {staff.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Select
                      value={staff.role || "unassigned"}
                      onValueChange={(value) => {
                        const newRole = value === "unassigned" ? null : (value as "ae" | "se" | "csm");
                        updateRole(staff.email, newRole);
                      }}
                      disabled={isUpdating}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="unassigned">
                          <span className="text-gray-500">Unassigned</span>
                        </SelectItem>
                        <SelectItem value="ae">
                          <span className="text-blue-700">Account Executive</span>
                        </SelectItem>
                        <SelectItem value="se">
                          <span className="text-green-700">Sales Engineer</span>
                        </SelectItem>
                        <SelectItem value="csm">
                          <span className="text-purple-700">Customer Success Manager</span>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div
                      className="cursor-help"
                      title={
                        staff.assigned_by
                          ? `Assigned by ${staff.assigned_by} on ${new Date(staff.updated_at!).toLocaleString()}`
                          : "Never assigned"
                      }
                    >
                      {formatRelativeTime(staff.updated_at)}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredStaff.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <Users className="h-12 w-12 mx-auto text-gray-400 mb-2" />
            <p>No staff members found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}
