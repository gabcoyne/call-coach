"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/lib/hooks/use-auth";
import { Users, UserPlus, Shield, Edit, Trash2, Save, X, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { RoleBadge } from "@/components/ui/role-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCurrentUser } from "@/lib/hooks/use-current-user";
import { isManager } from "@/lib/rbac";

interface StaffRole {
  email: string;
  role: string;
  assigned_by: string;
  assigned_at: string;
  updated_at: string;
}

export default function TeamManagementPage() {
  const router = useRouter();
  const { user: clerkUser } = useUser();
  const { data: currentUser, isLoading: userLoading } = useCurrentUser();
  const [staff, setStaff] = useState<StaffRole[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingEmail, setEditingEmail] = useState<string | null>(null);
  const [editingRole, setEditingRole] = useState<string>("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserRole, setNewUserRole] = useState("rep");
  const [isAddingUser, setIsAddingUser] = useState(false);

  const userIsManager = isManager(currentUser);

  useEffect(() => {
    if (!userLoading && !userIsManager) {
      router.push("/dashboard");
      return;
    }

    if (userIsManager) {
      loadStaff();
    }
  }, [userIsManager, userLoading, router]);

  const loadStaff = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/users/staff-roles");
      if (!response.ok) {
        throw new Error("Failed to load staff");
      }
      const data = await response.json();
      setStaff(data);
    } catch (err) {
      console.error("Failed to load staff:", err);
      setError(err instanceof Error ? err.message : "Failed to load staff");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditRole = (email: string, currentRole: string) => {
    setEditingEmail(email);
    setEditingRole(currentRole);
  };

  const handleSaveRole = async (email: string) => {
    try {
      const response = await fetch("/api/users/staff-roles", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": clerkUser?.primaryEmailAddress?.emailAddress || "",
        },
        body: JSON.stringify({
          email,
          role: editingRole,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update role");
      }

      await loadStaff();
      setEditingEmail(null);
    } catch (err) {
      console.error("Failed to update role:", err);
      setError(err instanceof Error ? err.message : "Failed to update role");
    }
  };

  const handleDeleteRole = async (email: string) => {
    if (!confirm(`Remove role assignment for ${email}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/users/staff-roles?email=${encodeURIComponent(email)}`, {
        method: "DELETE",
        headers: {
          "X-User-Email": clerkUser?.primaryEmailAddress?.emailAddress || "",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete role");
      }

      await loadStaff();
    } catch (err) {
      console.error("Failed to delete role:", err);
      setError(err instanceof Error ? err.message : "Failed to delete role");
    }
  };

  const handleAddUser = async () => {
    if (!newUserEmail || !newUserRole) {
      setError("Please provide both email and role");
      return;
    }

    try {
      const response = await fetch("/api/users/staff-roles", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": clerkUser?.primaryEmailAddress?.emailAddress || "",
        },
        body: JSON.stringify({
          email: newUserEmail,
          role: newUserRole,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add user");
      }

      await loadStaff();
      setNewUserEmail("");
      setNewUserRole("rep");
      setIsAddingUser(false);
    } catch (err) {
      console.error("Failed to add user:", err);
      setError(err instanceof Error ? err.message : "Failed to add user");
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  if (userLoading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96" />
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
          <h1 className="text-3xl font-bold text-foreground">Team Management</h1>
          <p className="text-muted-foreground mt-1">Manage users, roles, and permissions</p>
        </div>
        <Button onClick={() => setIsAddingUser(true)} disabled={isAddingUser}>
          <UserPlus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Card className="border-destructive bg-destructive/10">
          <CardContent className="pt-6 flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            {error}
          </CardContent>
        </Card>
      )}

      {/* Add User Form */}
      {isAddingUser && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserPlus className="h-5 w-5" />
              Add New User
            </CardTitle>
            <CardDescription>Assign a role to a new team member</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Input
                placeholder="user@prefect.io"
                value={newUserEmail}
                onChange={(e) => setNewUserEmail(e.target.value)}
                className="flex-1"
              />
              <Select value={newUserRole} onValueChange={setNewUserRole}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rep">Rep</SelectItem>
                  <SelectItem value="manager">Manager</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleAddUser}>
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setIsAddingUser(false);
                  setNewUserEmail("");
                  setNewUserRole("rep");
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{staff.length}</div>
            <p className="text-xs text-muted-foreground">Assigned roles</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Managers</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {staff.filter((s) => s.role === "manager").length}
            </div>
            <p className="text-xs text-muted-foreground">Team leaders</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sales Reps</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{staff.filter((s) => s.role === "rep").length}</div>
            <p className="text-xs text-muted-foreground">Individual contributors</p>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Members & Roles
          </CardTitle>
          <CardDescription>Manage user roles and permissions</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : staff.length === 0 ? (
            <div className="p-12 text-center">
              <Users className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">No staff roles assigned yet</p>
              <Button className="mt-4" onClick={() => setIsAddingUser(true)}>
                <UserPlus className="h-4 w-4 mr-2" />
                Add First User
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Assigned By</TableHead>
                  <TableHead>Assigned On</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {staff.map((member) => (
                  <TableRow key={member.email}>
                    <TableCell className="font-medium">{member.email}</TableCell>
                    <TableCell>
                      {editingEmail === member.email ? (
                        <Select value={editingRole} onValueChange={setEditingRole}>
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="rep">Rep</SelectItem>
                            <SelectItem value="manager">Manager</SelectItem>
                            <SelectItem value="admin">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <RoleBadge role={member.role as "rep" | "manager" | "admin"} />
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {member.assigned_by}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(member.assigned_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex gap-2 justify-end">
                        {editingEmail === member.email ? (
                          <>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleSaveRole(member.email)}
                            >
                              <Save className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => setEditingEmail(null)}>
                              <X className="h-4 w-4" />
                            </Button>
                          </>
                        ) : (
                          <>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleEditRole(member.email, member.role)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDeleteRole(member.email)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Role Descriptions */}
      <Card>
        <CardHeader>
          <CardTitle>Role Descriptions</CardTitle>
          <CardDescription>Understanding team permissions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3 p-3 border rounded-lg">
            <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="font-semibold">Admin</p>
              <p className="text-sm text-muted-foreground">
                Full access to all features, user management, and system configuration
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 border rounded-lg">
            <Users className="h-5 w-5 text-purple-600 mt-0.5" />
            <div>
              <p className="font-semibold">Manager</p>
              <p className="text-sm text-muted-foreground">
                Can view team performance, manage team members, and access coaching insights
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 border rounded-lg">
            <Users className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <p className="font-semibold">Rep</p>
              <p className="text-sm text-muted-foreground">
                Can view their own calls, receive coaching, and track their performance
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
