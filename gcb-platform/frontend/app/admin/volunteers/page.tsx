"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { Shield, Mail, Calendar, ChevronRight } from "lucide-react";
import Link from "next/link";
import { useUserProfile } from "@/lib/useUserProfile";

interface VolunteerApplication {
  id: string;
  user_id: string | null;
  email: string;
  name: string;
  role: string;
  background: string | null;
  motivation: string | null;
  status: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export default function AdminVolunteersPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [applications, setApplications] = useState<VolunteerApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [roleFilter, setRoleFilter] = useState<string>("all");

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    // Check if user is admin
    if (user && !profileLoading) {
      if (!canAdmin && !isAdmin) {
        // User is not an admin, redirect to dashboard
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadApplications();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router, statusFilter, roleFilter]);

  async function loadApplications() {
    setLoading(true);
    try {
      const response = await apiClient.getVolunteerApplications({
        status: statusFilter !== "all" ? statusFilter : undefined,
        role: roleFilter !== "all" ? roleFilter : undefined,
      });
      setApplications(response.applications);
    } catch (error) {
      console.error("Failed to load volunteer applications:", error);
      toast.error("Failed to load volunteer applications");
    } finally {
      setLoading(false);
    }
  }

  if (userLoading || profileLoading || loading) {
    return (
      <div className="container py-8 max-w-7xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Double-check admin permission before rendering
  if (!canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="container py-8 max-w-7xl">
      {/* Breadcrumb */}
      <nav className="mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/admin" className="hover:text-primary transition-colors">
              Admin
            </Link>
          </li>
          <li>
            <ChevronRight className="h-4 w-4" />
          </li>
          <li className="text-foreground font-medium">
            Volunteer Applications
          </li>
        </ol>
      </nav>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Volunteer Applications</h1>
        </div>
        <p className="mt-2 text-muted-foreground">
          Review and manage volunteer applications for moderation and advisory roles
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Role</label>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="moderator">Moderator</SelectItem>
                  <SelectItem value="advisor">Advisor</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Applications Table */}
      <Card>
        <CardHeader>
          <CardTitle>Applications ({applications.length})</CardTitle>
          <CardDescription>
            All volunteer applications submitted through the volunteer page
          </CardDescription>
        </CardHeader>
        <CardContent>
          {applications.length > 0 ? (
            <div className="rounded-lg border border-white/[0.08] overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-white/[0.02]">
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Submitted</TableHead>
                    <TableHead>Background</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {applications.map((app) => (
                    <TableRow key={app.id}>
                      <TableCell className="font-medium">{app.name}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-muted-foreground" />
                          {app.email}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {app.role === "moderator" ? "Moderator" : "Advisor"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            app.status === "approved"
                              ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                              : app.status === "rejected"
                              ? "bg-red-500/20 text-red-400 border-red-500/30"
                              : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                          }
                        >
                          {app.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          {new Date(app.created_at).toLocaleDateString()}
                        </div>
                      </TableCell>
                      <TableCell>
                        {app.background ? (
                          <div className="max-w-xs truncate text-sm text-muted-foreground">
                            {app.background}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-12">
              <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-foreground mb-2">No volunteer applications found</p>
              <p className="text-sm text-muted-foreground">
                {statusFilter !== "all" || roleFilter !== "all"
                  ? "Try adjusting your filters"
                  : "Applications will appear here when submitted"}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
