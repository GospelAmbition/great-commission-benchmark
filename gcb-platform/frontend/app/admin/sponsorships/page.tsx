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
import Link from "next/link";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";
import { apiClient } from "@/lib/api";
import { User, Mail, Clock, CheckCircle2, XCircle } from "lucide-react";

interface SponsorshipItem {
  id: string;
  request_type: string;
  model_name: string;
  user_id: string;
  user_name: string;
  user_email: string;
  message?: string;
  status: string;
  payment_id?: string;
  payment_status?: string;
  created_at: string;
  reviewed_at?: string;
  reviewer_notes?: string;
  assigned_moderator_id?: string;
  assigned_moderator_name?: string;
  assigned_at?: string;
}

interface Moderator {
  id: string;
  name?: string;
  email: string;
}

export default function AdminSponsorshipsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();

  const [sponsorships, setSponsorships] = useState<SponsorshipItem[]>([]);
  const [sponsorshipsLoading, setSponsorshipsLoading] = useState(true);
  const [sponsorshipsTotal, setSponsorshipsTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [requestTypeFilter, setRequestTypeFilter] = useState<string>("all");
  const [moderators, setModerators] = useState<Moderator[]>([]);
  const [moderatorsLoading, setModeratorsLoading] = useState(true);
  const [assigning, setAssigning] = useState<string | null>(null);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && !profileLoading) {
      if (!canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadSponsorships();
      loadModerators();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router]);

  useEffect(() => {
    if (user) {
      loadSponsorships();
    }
  }, [statusFilter, requestTypeFilter]);

  async function loadSponsorships() {
    setSponsorshipsLoading(true);
    try {
      const params: any = {};
      if (statusFilter !== "all") {
        params.status = statusFilter;
      }
      if (requestTypeFilter !== "all") {
        params.request_type = requestTypeFilter;
      }
      const data = await apiClient.getAdminSponsorships(params);
      setSponsorships(data.items);
      setSponsorshipsTotal(data.total);
    } catch (error: any) {
      console.error("Failed to load sponsorships:", error);
      toast.error(error.message || "Failed to load sponsorships");
    } finally {
      setSponsorshipsLoading(false);
    }
  }

  async function loadModerators() {
    setModeratorsLoading(true);
    try {
      const data = await apiClient.getAvailableModerators();
      setModerators(data.moderators);
    } catch (error: any) {
      console.error("Failed to load moderators:", error);
      toast.error(error.message || "Failed to load moderators");
    } finally {
      setModeratorsLoading(false);
    }
  }

  async function handleAssignModerator(sponsorshipId: string, moderatorId: string) {
    if (!moderatorId) {
      toast.error("Please select a moderator");
      return;
    }

    setAssigning(sponsorshipId);
    try {
      const result = await apiClient.assignSponsorshipModerator(sponsorshipId, moderatorId);
      toast.success(result.message || "Moderator assigned successfully");
      await loadSponsorships(); // Refresh list
    } catch (error: any) {
      console.error("Failed to assign moderator:", error);
      toast.error(error.message || "Failed to assign moderator");
    } finally {
      setAssigning(null);
    }
  }

  if (userLoading || profileLoading || (sponsorshipsLoading && !user)) {
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

  if (!canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <h1 className="text-4xl font-bold">Sponsorship Management</h1>
        <p className="mt-2 text-muted-foreground">
          Manage sponsorship requests and assign moderators
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-2 block">Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending_payment">Pending Payment</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Request Type</label>
              <Select value={requestTypeFilter} onValueChange={setRequestTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="sponsorship">Sponsorship ($20)</SelectItem>
                  <SelectItem value="request">Model Request (Free)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sponsorships Table */}
      <Card>
        <CardHeader>
          <CardTitle>Sponsorship Requests</CardTitle>
          <CardDescription>
            {sponsorshipsTotal} total request{sponsorshipsTotal !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sponsorshipsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16" />
              ))}
            </div>
          ) : sponsorships.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Payment</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Assigned Moderator</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sponsorships.map((sponsorship) => (
                  <TableRow key={sponsorship.id}>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(sponsorship.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={sponsorship.request_type === "sponsorship" ? "default" : "outline"}>
                        {sponsorship.request_type === "sponsorship" ? "Paid ($20)" : "Request"}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate">{sponsorship.model_name}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span>{sponsorship.user_name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {sponsorship.request_type === "sponsorship" ? (
                        <Badge variant={sponsorship.payment_status === "succeeded" ? "default" : "destructive"}>
                          {sponsorship.payment_status || "pending"}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          sponsorship.status === "pending" || sponsorship.status === "pending_payment"
                            ? "destructive"
                            : sponsorship.status === "approved"
                            ? "default"
                            : "outline"
                        }
                      >
                        {sponsorship.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {sponsorship.assigned_moderator_name ? (
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span className="text-sm">{sponsorship.assigned_moderator_name}</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-sm">Unassigned</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Select
                          value={sponsorship.assigned_moderator_id || ""}
                          onValueChange={(value) => handleAssignModerator(sponsorship.id, value)}
                          disabled={assigning === sponsorship.id || moderatorsLoading}
                        >
                          <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Assign moderator" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Unassign</SelectItem>
                            {moderators.map((mod) => (
                              <SelectItem key={mod.id} value={mod.id}>
                                {mod.name || mod.email}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/moderator/sponsorship/${sponsorship.id}`}>
                            Review
                          </Link>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No sponsorship requests found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
