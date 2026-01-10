"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";

interface AdminUser {
  id: string;
  email: string;
  name: string | null;
  role: "user" | "moderator" | "blog_manager" | "benchmark_developer" | "benchmark_viewer" | "benchmark_administrator" | "admin";
  created_at: string;
  test_count: number;
  last_login?: string;
  fee_waived?: boolean;
  fee_waived_reason?: string | null;
  can_view_benchmark?: boolean;
  can_edit_benchmark?: boolean;
  can_moderate?: boolean;
  can_manage_blog?: boolean;
  can_admin?: boolean;
}

export default function AdminUsersPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [initialLoading, setInitialLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [newRole, setNewRole] = useState<string>("");
  const [permissions, setPermissions] = useState({
    can_view_benchmark: false,
    can_edit_benchmark: false,
    can_moderate: false,
    can_manage_blog: false,
    can_admin: false,
  });
  const [saving, setSaving] = useState(false);
  const [feeWaiverUser, setFeeWaiverUser] = useState<AdminUser | null>(null);
  const [feeWaiverReason, setFeeWaiverReason] = useState<string>("");
  const [feeWaiverSaving, setFeeWaiverSaving] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
  });

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadUsers();
    }
  }, [user, userLoading, router, search, roleFilter, pagination.page]);

  async function loadUsers() {
    setLoading(true);
    try {
      // Calculate offset from page (page is 1-based, offset is 0-based)
      const offset = (pagination.page - 1) * pagination.limit;
      const params = new URLSearchParams({
        offset: String(offset),
        limit: String(pagination.limit),
        ...(search && { search }),
        ...(roleFilter !== "all" && { role: roleFilter }),
      });

      const response = await fetch(`/api/admin/users?${params}`);
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setPagination((prev) => ({ ...prev, total: data.total || 0 }));
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to load users" }));
        console.error("Failed to load users:", error);
        toast.error(error.detail || error.error || "Failed to load users");
        setUsers([]);
        setPagination((prev) => ({ ...prev, total: 0 }));
      }
    } catch (error) {
      console.error("Failed to load users:", error);
      toast.error("Failed to load users");
      setUsers([]);
      setPagination((prev) => ({ ...prev, total: 0 }));
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  }

  async function handleRoleChange() {
    if (!selectedUser || !newRole) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/admin/users/${selectedUser.id}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });

      if (response.ok) {
        toast.success(`Role updated to ${newRole}`);
        setSelectedUser(null);
        setNewRole("");
        loadUsers();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to update role");
      }
    } catch (error: any) {
      console.error("Failed to update role:", error);
      toast.error(error.message || "Failed to update user role");
    } finally {
      setSaving(false);
    }
  }

  async function handlePermissionsChange() {
    if (!selectedUser) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/admin/users/${selectedUser.id}/permissions`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(permissions),
      });

      if (response.ok) {
        toast.success("Permissions updated successfully");
        setSelectedUser(null);
        setPermissions({
          can_view_benchmark: false,
          can_edit_benchmark: false,
          can_moderate: false,
          can_manage_blog: false,
          can_admin: false,
        });
        loadUsers();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to update permissions");
      }
    } catch (error: any) {
      console.error("Failed to update permissions:", error);
      toast.error(error.message || "Failed to update permissions");
    } finally {
      setSaving(false);
    }
  }

  function handleSetDefaultPermissions(role: string) {
    const defaults: Record<string, typeof permissions> = {
      user: {
        can_view_benchmark: false,
        can_edit_benchmark: false,
        can_moderate: false,
        can_manage_blog: false,
        can_admin: false,
      },
      moderator: {
        can_view_benchmark: false,
        can_edit_benchmark: false,
        can_moderate: true,
        can_manage_blog: false,
        can_admin: false,
      },
      benchmark_viewer: {
        can_view_benchmark: true,
        can_edit_benchmark: false,
        can_moderate: false,
        can_manage_blog: false,
        can_admin: false,
      },
      benchmark_administrator: {
        can_view_benchmark: true,
        can_edit_benchmark: true,
        can_moderate: false,
        can_manage_blog: false,
        can_admin: false,
      },
      blog_manager: {
        can_view_benchmark: false,
        can_edit_benchmark: false,
        can_moderate: false,
        can_manage_blog: true,
        can_admin: false,
      },
      admin: {
        can_view_benchmark: true,
        can_edit_benchmark: true,
        can_moderate: true,
        can_manage_blog: true,
        can_admin: true,
      },
    };
    
    if (defaults[role]) {
      setPermissions(defaults[role]);
      setNewRole(role);
    }
  }

  async function handleFeeWaiverToggle() {
    if (!feeWaiverUser) return;
    setFeeWaiverSaving(true);
    try {
      const waived = !feeWaiverUser.fee_waived;
      const response = await fetch(`/api/admin/users/${feeWaiverUser.id}/fee-waiver`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          waived,
          reason: feeWaiverReason || undefined
        }),
      });

      if (response.ok) {
        toast.success(`Fee waiver ${waived ? 'granted' : 'revoked'}`);
        setFeeWaiverUser(null);
        setFeeWaiverReason("");
        loadUsers();
      } else {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update fee waiver");
      }
    } catch (error: any) {
      console.error("Failed to update fee waiver:", error);
      toast.error(error.message || "Failed to update fee waiver");
    } finally {
      setFeeWaiverSaving(false);
    }
  }

  // Note: Backend already handles filtering, but we keep this for immediate UI feedback
  const filteredUsers = users.filter((u) => {
    if (search) {
      const searchLower = search.toLowerCase();
      const emailMatch = u.email.toLowerCase().includes(searchLower);
      const nameMatch = u.name?.toLowerCase().includes(searchLower) ?? false;
      if (!emailMatch && !nameMatch) {
        return false;
      }
    }
    if (roleFilter !== "all" && u.role !== roleFilter) {
      return false;
    }
    return true;
  });

  if (userLoading || initialLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <h1 className="text-4xl font-bold">User Management</h1>
        <p className="mt-2 text-muted-foreground">
          Manage users and their roles
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="moderator">Moderator</SelectItem>
                <SelectItem value="blog_manager">Blog Manager</SelectItem>
                <SelectItem value="benchmark_viewer">Benchmark Viewer</SelectItem>
                <SelectItem value="benchmark_administrator">Benchmark Administrator</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Users
            {loading && (
              <span className="text-sm font-normal text-muted-foreground">
                Loading...
              </span>
            )}
          </CardTitle>
          <CardDescription>
            {pagination.total} total users
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Fee Waiver</TableHead>
                <TableHead>Tests</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead>Last Login</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((u) => (
                <TableRow key={u.id}>
                  <TableCell className="font-medium">{u.name || "—"}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        u.role === "admin"
                          ? "default"
                          : u.role === "benchmark_developer"
                          ? "default"
                          : u.role === "blog_manager"
                          ? "secondary"
                          : u.role === "moderator"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {u.role === "blog_manager" ? "Blog Manager" : 
                       u.role === "benchmark_developer" ? "Benchmark Dev" :
                       u.role === "benchmark_viewer" ? "Benchmark Viewer" :
                       u.role === "benchmark_administrator" ? "Benchmark Admin" : u.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {(u.role === "moderator" || u.role === "blog_manager" || u.role === "benchmark_developer" || u.role === "admin" || u.fee_waived) ? (
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        {u.role === "moderator" || u.role === "blog_manager" || u.role === "benchmark_developer" || u.role === "admin" ? "Auto-waived" : "Waived"}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>{u.test_count}</TableCell>
                  <TableCell>
                    {new Date(u.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {u.last_login
                      ? new Date(u.last_login).toLocaleDateString()
                      : "—"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedUser(u);
                          setNewRole(u.role);
                          setPermissions({
                            can_view_benchmark: u.can_view_benchmark ?? false,
                            can_edit_benchmark: u.can_edit_benchmark ?? false,
                            can_moderate: u.can_moderate ?? false,
                            can_manage_blog: u.can_manage_blog ?? false,
                            can_admin: u.can_admin ?? false,
                          });
                        }}
                      >
                        Edit Permissions
                      </Button>
                      {(u.role === "user") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setFeeWaiverUser(u);
                            setFeeWaiverReason(u.fee_waived_reason || "");
                          }}
                        >
                          {u.fee_waived ? "Revoke Waiver" : "Grant Waiver"}
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <Button
              variant="outline"
              disabled={pagination.page === 1}
              onClick={() =>
                setPagination((prev) => ({ ...prev, page: prev.page - 1 }))
              }
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {pagination.page} of{" "}
              {Math.ceil(pagination.total / pagination.limit)}
            </span>
            <Button
              variant="outline"
              disabled={
                pagination.page >= Math.ceil(pagination.total / pagination.limit)
              }
              onClick={() =>
                setPagination((prev) => ({ ...prev, page: prev.page + 1 }))
              }
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Edit Permissions Dialog */}
      <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit User Permissions</DialogTitle>
            <DialogDescription>
              Manage permissions for {selectedUser?.name} ({selectedUser?.email})
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-6">
            {/* Role Selection (for setting defaults) */}
            <div>
              <Label className="text-sm font-medium mb-2 block">Role (for default permissions)</Label>
              <Select value={newRole} onValueChange={(value) => {
                setNewRole(value);
                handleSetDefaultPermissions(value);
              }}>
                <SelectTrigger>
                  <SelectValue placeholder="Select role to apply defaults" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="moderator">Moderator</SelectItem>
                  <SelectItem value="blog_manager">Blog Manager</SelectItem>
                  <SelectItem value="benchmark_viewer">Benchmark Viewer</SelectItem>
                  <SelectItem value="benchmark_administrator">Benchmark Administrator</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Current role: <span className="font-medium">{selectedUser?.role}</span>
              </p>
            </div>

            {/* Permissions Checkboxes */}
            <div className="space-y-4">
              <Label className="text-sm font-medium">Permissions</Label>
              <div className="space-y-3 pl-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_view_benchmark"
                    checked={permissions.can_view_benchmark}
                    onCheckedChange={(checked) =>
                      setPermissions((prev) => ({ ...prev, can_view_benchmark: checked === true }))
                    }
                    disabled={permissions.can_admin}
                  />
                  <Label htmlFor="can_view_benchmark" className="text-sm font-normal cursor-pointer">
                    View Benchmark (read-only access to Benchmark Dashboard)
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_edit_benchmark"
                    checked={permissions.can_edit_benchmark}
                    onCheckedChange={(checked) => {
                      const isChecked = checked === true;
                      setPermissions((prev) => ({
                        ...prev,
                        can_edit_benchmark: isChecked,
                        can_view_benchmark: isChecked ? true : prev.can_view_benchmark, // Editing implies viewing
                      }));
                    }}
                    disabled={permissions.can_admin}
                  />
                  <Label htmlFor="can_edit_benchmark" className="text-sm font-normal cursor-pointer">
                    Edit Benchmark (full editing access to Benchmark Dashboard)
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_moderate"
                    checked={permissions.can_moderate}
                    onCheckedChange={(checked) =>
                      setPermissions((prev) => ({ ...prev, can_moderate: checked === true }))
                    }
                    disabled={permissions.can_admin}
                  />
                  <Label htmlFor="can_moderate" className="text-sm font-normal cursor-pointer">
                    Moderate (access to Moderation Dashboard)
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_manage_blog"
                    checked={permissions.can_manage_blog}
                    onCheckedChange={(checked) =>
                      setPermissions((prev) => ({ ...prev, can_manage_blog: checked === true }))
                    }
                    disabled={permissions.can_admin}
                  />
                  <Label htmlFor="can_manage_blog" className="text-sm font-normal cursor-pointer">
                    Manage Blog (access to Blog Management Dashboard)
                  </Label>
                </div>
                <div className="flex items-center space-x-2 pt-2 border-t">
                  <Checkbox
                    id="can_admin"
                    checked={permissions.can_admin}
                    onCheckedChange={(checked) => {
                      const isChecked = checked === true;
                      setPermissions({
                        can_view_benchmark: isChecked,
                        can_edit_benchmark: isChecked,
                        can_moderate: isChecked,
                        can_manage_blog: isChecked,
                        can_admin: isChecked,
                      });
                    }}
                  />
                  <Label htmlFor="can_admin" className="text-sm font-medium cursor-pointer">
                    Administrator (grants all permissions)
                  </Label>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setSelectedUser(null);
              setPermissions({
                can_view_benchmark: false,
                can_edit_benchmark: false,
                can_moderate: false,
                can_manage_blog: false,
                can_admin: false,
              });
            }}>
              Cancel
            </Button>
            <Button onClick={handlePermissionsChange} disabled={saving}>
              {saving ? "Saving..." : "Save Permissions"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Fee Waiver Dialog */}
      <Dialog open={!!feeWaiverUser} onOpenChange={() => setFeeWaiverUser(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {feeWaiverUser?.fee_waived ? "Revoke" : "Grant"} Fee Waiver
            </DialogTitle>
            <DialogDescription>
              {feeWaiverUser?.fee_waived 
                ? `Revoke fee waiver for ${feeWaiverUser?.name} (${feeWaiverUser?.email})`
                : `Grant fee waiver for ${feeWaiverUser?.name} (${feeWaiverUser?.email}). This waives all fees for both platform test requests and GCB Runner submission uploads.`}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {feeWaiverUser?.fee_waived_reason && (
              <div className="p-3 bg-muted rounded-md">
                <p className="text-sm font-medium mb-1">Current Reason:</p>
                <p className="text-sm text-muted-foreground">{feeWaiverUser.fee_waived_reason}</p>
              </div>
            )}
            <div>
              <Label htmlFor="fee-waiver-reason">Reason (Optional)</Label>
              <Input
                id="fee-waiver-reason"
                placeholder="e.g., Stewardship team member"
                value={feeWaiverReason}
                onChange={(e) => setFeeWaiverReason(e.target.value)}
                className="mt-1"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Note: Moderators, blog managers, benchmark developers, and admins automatically have fee waived by role.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setFeeWaiverUser(null);
              setFeeWaiverReason("");
            }}>
              Cancel
            </Button>
            <Button 
              onClick={handleFeeWaiverToggle} 
              disabled={feeWaiverSaving}
              variant={feeWaiverUser?.fee_waived ? "destructive" : "default"}
            >
              {feeWaiverSaving 
                ? "Saving..." 
                : feeWaiverUser?.fee_waived 
                  ? "Revoke Waiver" 
                  : "Grant Waiver"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
