"use client";

import { useState, useEffect } from "react";
import { useAuthContext } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { isManager } from "@/lib/auth-utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Users, Search, Save, AlertCircle, RefreshCw } from "lucide-react";

interface StaffMember {
  email: string;
  name: string;
  role: string | null;
  assigned_by?: string;
  assigned_at?: string;
  updated_at?: string;
}

interface UserActivityMetrics {
  lastActive: string | null;
  callsAnalyzed: number;
  loginCount: number;
}

export default function AdminUsersPage() {
  const { user, isLoading: authLoading } = useAuthContext();
  const router = useRouter();
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [filteredStaff, setFilteredStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState<{ [email: string]: string }>({});
  const [saving, setSaving] = useState<{ [email: string]: boolean }>({});
  const [alertDialog, setAlertDialog] = useState<{
    open: boolean;
    email?: string;
    action?: "assign" | "revoke";
  }>({ open: false });

  // Check authorization
  const userIsManager = isManager(user);

  useEffect(() => {
    if (authLoading) return;

    if (!userIsManager) {
      router.push("/403?message=Admin access required");
      return;
    }

    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, userIsManager]);

  useEffect(() => {
    if (!searchQuery) {
      setFilteredStaff(staff);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredStaff(
        staff.filter(
          (s) => s.email.toLowerCase().includes(query) || s.name.toLowerCase().includes(query)
        )
      );
    }
  }, [searchQuery, staff]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/admin/users");
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/403?message=Admin access required");
          return;
        }
        throw new Error("Failed to fetch users");
      }

      const data = await response.json();
      setStaff(data.staff || []);

      // Initialize selected roles from current assignments
      const roleMap: { [email: string]: string } = {};
      data.staff.forEach((s: StaffMember) => {
        if (s.role) {
          roleMap[s.email] = s.role;
        }
      });
      setSelectedRole(roleMap);
    } catch (err) {
      console.error("Error fetching users:", err);
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (email: string, role: string) => {
    setSelectedRole((prev) => ({
      ...prev,
      [email]: role,
    }));
  };

  const handleSaveRole = async (email: string) => {
    const newRole = selectedRole[email];
    const currentRole = staff.find((s) => s.email === email)?.role;

    // If removing role, show confirmation
    if (!newRole && currentRole) {
      setAlertDialog({ open: true, email, action: "revoke" });
      return;
    }

    // If assigning role, show confirmation
    if (newRole && !currentRole) {
      setAlertDialog({ open: true, email, action: "assign" });
      return;
    }

    await saveRole(email, newRole);
  };

  const saveRole = async (email: string, role: string | undefined) => {
    try {
      setSaving((prev) => ({ ...prev, [email]: true }));

      const response = await fetch(`/api/admin/users/${email}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ role: role || null }),
      });

      if (!response.ok) {
        throw new Error("Failed to update role");
      }

      // Update local state
      setStaff((prev) => prev.map((s) => (s.email === email ? { ...s, role: role || null } : s)));

      // Show success
      const action = role ? `assigned ${role} role` : "role removed";
      alert(`Role ${action} for ${email}`);

      setAlertDialog({ open: false });
    } catch (err) {
      console.error("Error saving role:", err);
      alert(err instanceof Error ? err.message : "Failed to update role");
    } finally {
      setSaving((prev) => ({ ...prev, [email]: false }));
    }
  };

  const handleConfirm = () => {
    if (alertDialog.email) {
      const role = alertDialog.action === "revoke" ? undefined : selectedRole[alertDialog.email];
      saveRole(alertDialog.email, role);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">User Management</h1>
          <p className="text-muted-foreground mt-1">Loading users...</p>
        </div>
      </div>
    );
  }

  if (!userIsManager) {
    return null;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">User Management</h1>
          <p className="text-muted-foreground mt-1">Manage staff roles and permissions</p>
        </div>
        <Button onClick={fetchUsers} variant="outline" size="sm" className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Search Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Staff Members</CardTitle>
          <CardDescription>
            {filteredStaff.length} of {staff.length} users
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-sm">Name</th>
                  <th className="text-left py-3 px-4 font-medium text-sm">Email</th>
                  <th className="text-left py-3 px-4 font-medium text-sm">Current Role</th>
                  <th className="text-left py-3 px-4 font-medium text-sm">Assign Role</th>
                  <th className="text-right py-3 px-4 font-medium text-sm">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredStaff.length > 0 ? (
                  filteredStaff.map((member) => (
                    <tr key={member.email} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="font-medium">{member.name}</span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{member.email}</td>
                      <td className="py-3 px-4">
                        {member.role ? (
                          <span className="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800">
                            {member.role}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400">No role assigned</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Select
                          value={selectedRole[member.email] || ""}
                          onValueChange={(value) =>
                            handleRoleChange(member.email, value === "none" ? "" : value)
                          }
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="Select role" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">No Role</SelectItem>
                            <SelectItem value="manager">Manager</SelectItem>
                            <SelectItem value="ae">Sales Engineer</SelectItem>
                            <SelectItem value="se">Support Engineer</SelectItem>
                            <SelectItem value="csm">CSM</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={
                            selectedRole[member.email] === (member.role || "") ||
                            saving[member.email]
                          }
                          onClick={() => handleSaveRole(member.email)}
                          className="gap-1"
                        >
                          <Save className="h-4 w-4" />
                          {saving[member.email] ? "Saving..." : "Save"}
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-6 px-4 text-center text-gray-500">
                      No users found matching your search
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Alert Dialog */}
      <AlertDialog
        open={alertDialog.open}
        onOpenChange={(open) => setAlertDialog({ ...alertDialog, open })}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Confirm Role {alertDialog.action === "assign" ? "Assignment" : "Removal"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {alertDialog.action === "assign"
                ? `Are you sure you want to assign the manager role to ${alertDialog.email}?`
                : `Are you sure you want to remove the manager role from ${alertDialog.email}?`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogAction onClick={handleConfirm}>Confirm</AlertDialogAction>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
