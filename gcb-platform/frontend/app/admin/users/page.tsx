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
  name: string;
  role: "user" | "moderator" | "admin";
  created_at: string;
  test_count: number;
  last_login?: string;
  fee_waived?: boolean;
  fee_waived_reason?: string | null;
}

export default function AdminUsersPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [newRole, setNewRole] = useState<string>("");
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
      // In a real implementation, this would call the admin users API
      const params = new URLSearchParams({
        page: String(pagination.page),
        limit: String(pagination.limit),
        ...(search && { search }),
        ...(roleFilter !== "all" && { role: roleFilter }),
      });

      const response = await fetch(`/api/v1/admin/users?${params}`);
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setPagination((prev) => ({ ...prev, total: data.total || 0 }));
      } else {
        // Use placeholder data for demo
        setUsers([
          {
            id: "1",
            email: "admin@example.com",
            name: "Admin User",
            role: "admin",
            created_at: new Date().toISOString(),
            test_count: 5,
            last_login: new Date().toISOString(),
          },
          {
            id: "2",
            email: "moderator@example.com",
            name: "Moderator User",
            role: "moderator",
            created_at: new Date().toISOString(),
            test_count: 12,
            last_login: new Date().toISOString(),
          },
          {
            id: "3",
            email: "user@example.com",
            name: "Regular User",
            role: "user",
            created_at: new Date().toISOString(),
            test_count: 3,
          },
        ]);
        setPagination((prev) => ({ ...prev, total: 3 }));
      }
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleRoleChange() {
    if (!selectedUser || !newRole) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/v1/admin/users/${selectedUser.id}/role`, {
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
        throw new Error("Failed to update role");
      }
    } catch (error) {
      console.error("Failed to update role:", error);
      toast.error("Failed to update user role");
    } finally {
      setSaving(false);
    }
  }

  async function handleFeeWaiverToggle() {
    if (!feeWaiverUser) return;
    setFeeWaiverSaving(true);
    try {
      const waived = !feeWaiverUser.fee_waived;
      const response = await fetch(`/api/v1/admin/users/${feeWaiverUser.id}/fee-waiver`, {
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

  const filteredUsers = users.filter((u) => {
    if (search) {
      const searchLower = search.toLowerCase();
      if (
        !u.email.toLowerCase().includes(searchLower) &&
        !u.name.toLowerCase().includes(searchLower)
      ) {
        return false;
      }
    }
    if (roleFilter !== "all" && u.role !== roleFilter) {
      return false;
    }
    return true;
  });

  if (userLoading || loading) {
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
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Filter by role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="moderator">Moderator</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
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
                  <TableCell className="font-medium">{u.name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        u.role === "admin"
                          ? "default"
                          : u.role === "moderator"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {u.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {(u.role === "moderator" || u.role === "admin" || u.fee_waived) ? (
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        {u.role === "moderator" || u.role === "admin" ? "Auto-waived" : "Waived"}
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
                        }}
                      >
                        Edit Role
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

      {/* Edit Role Dialog */}
      <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User Role</DialogTitle>
            <DialogDescription>
              Change the role for {selectedUser?.name} ({selectedUser?.email})
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={newRole} onValueChange={setNewRole}>
              <SelectTrigger>
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="moderator">Moderator</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedUser(null)}>
              Cancel
            </Button>
            <Button onClick={handleRoleChange} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
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
                : `Grant fee waiver for ${feeWaiverUser?.name} (${feeWaiverUser?.email}). This waives all fees for both platform test requests and CLI submission uploads.`}
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
                Note: Moderators and admins automatically have fee waived by role.
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
