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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";
import { MessageSquare, ChevronRight, Mail, Calendar, Eye, CheckCircle, Clock } from "lucide-react";

interface ContactSubmission {
  id: string;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: string;
  admin_notes: string | null;
  responded_at: string | null;
  responded_by: string | null;
  created_at: string;
  updated_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
  new: {
    label: "New",
    className: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    icon: <Clock className="h-3 w-3" />,
  },
  read: {
    label: "Read",
    className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    icon: <Eye className="h-3 w-3" />,
  },
  responded: {
    label: "Responded",
    className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    icon: <CheckCircle className="h-3 w-3" />,
  },
};

const SUBJECT_LABELS: Record<string, string> = {
  general: "General Inquiry",
  technical: "Technical Support",
  partnership: "Partnership",
  media: "Media Inquiry",
  feedback: "Feedback",
  other: "Other",
};

export default function AdminContactsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [contacts, setContacts] = useState<ContactSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedContact, setSelectedContact] = useState<ContactSubmission | null>(null);
  const [newStatus, setNewStatus] = useState<string>("");
  const [adminNotes, setAdminNotes] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [total, setTotal] = useState(0);

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
      loadContacts();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router, statusFilter]);

  async function loadContacts() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "all") {
        params.append("status", statusFilter);
      }
      params.append("limit", "100");

      const response = await fetch(`/api/admin/contacts?${params}`);
      if (response.ok) {
        const data = await response.json();
        setContacts(data.items || []);
        setTotal(data.total || 0);
      } else {
        toast.error("Failed to load contact submissions");
      }
    } catch (error) {
      console.error("Failed to load contacts:", error);
      toast.error("Failed to load contact submissions");
    } finally {
      setLoading(false);
    }
  }

  function openContactDialog(contact: ContactSubmission) {
    setSelectedContact(contact);
    setNewStatus(contact.status);
    setAdminNotes(contact.admin_notes || "");
  }

  async function handleUpdateStatus() {
    if (!selectedContact) return;

    setSaving(true);
    try {
      const response = await fetch(`/api/admin/contacts/${selectedContact.id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: newStatus,
          admin_notes: adminNotes || null,
        }),
      });

      if (response.ok) {
        toast.success("Contact status updated");
        setSelectedContact(null);
        loadContacts();
      } else {
        const error = await response.json().catch(() => ({}));
        toast.error(error.detail || "Failed to update status");
      }
    } catch (error) {
      console.error("Failed to update status:", error);
      toast.error("Failed to update contact status");
    } finally {
      setSaving(false);
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

  if (!user || (!canAdmin && !isAdmin)) {
    return null;
  }

  const newCount = contacts.filter((c) => c.status === "new").length;

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
            Contact Submissions
          </li>
        </ol>
      </nav>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <MessageSquare className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Contact Submissions</h1>
          {newCount > 0 && (
            <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
              {newCount} New
            </Badge>
          )}
        </div>
        <p className="mt-2 text-muted-foreground">
          View and manage contact form submissions from the website
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 max-w-xs">
              <label className="text-sm font-medium mb-2 block">Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="read">Read</SelectItem>
                  <SelectItem value="responded">Responded</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contacts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Submissions ({total})</CardTitle>
          <CardDescription>
            All contact form submissions from the website
          </CardDescription>
        </CardHeader>
        <CardContent>
          {contacts.length > 0 ? (
            <div className="rounded-lg border border-white/[0.08] overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-white/[0.02]">
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contacts.map((contact) => {
                    const statusConfig = STATUS_CONFIG[contact.status] || STATUS_CONFIG.new;
                    return (
                      <TableRow key={contact.id}>
                        <TableCell className="font-medium">{contact.name}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <a 
                              href={`mailto:${contact.email}`}
                              className="hover:text-primary transition-colors"
                            >
                              {contact.email}
                            </a>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {SUBJECT_LABELS[contact.subject] || contact.subject}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={statusConfig.className}>
                            <span className="flex items-center gap-1">
                              {statusConfig.icon}
                              {statusConfig.label}
                            </span>
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Calendar className="h-4 w-4" />
                            {new Date(contact.created_at).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openContactDialog(contact)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-12">
              <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-foreground mb-2">No contact submissions found</p>
              <p className="text-sm text-muted-foreground">
                {statusFilter !== "all"
                  ? "Try adjusting your filters"
                  : "Submissions will appear here when received"}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Contact Detail Dialog */}
      <Dialog open={!!selectedContact} onOpenChange={(open) => !open && setSelectedContact(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Contact Submission</DialogTitle>
            <DialogDescription>
              {selectedContact && (
                <>
                  From {selectedContact.name} on{" "}
                  {new Date(selectedContact.created_at).toLocaleString()}
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          {selectedContact && (
            <div className="space-y-4 py-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label className="text-muted-foreground">Name</Label>
                  <p className="font-medium">{selectedContact.name}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Email</Label>
                  <p>
                    <a
                      href={`mailto:${selectedContact.email}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {selectedContact.email}
                    </a>
                  </p>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Subject</Label>
                <p className="font-medium">
                  {SUBJECT_LABELS[selectedContact.subject] || selectedContact.subject}
                </p>
              </div>

              <div>
                <Label className="text-muted-foreground">Message</Label>
                <div className="mt-1 p-4 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                  <p className="whitespace-pre-wrap">{selectedContact.message}</p>
                </div>
              </div>

              <div className="border-t border-white/[0.06] pt-4">
                <Label htmlFor="status">Update Status</Label>
                <Select value={newStatus} onValueChange={setNewStatus}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="read">Read</SelectItem>
                    <SelectItem value="responded">Responded</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="admin-notes">Admin Notes</Label>
                <Textarea
                  id="admin-notes"
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Add notes about this submission..."
                  className="mt-1"
                  rows={3}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedContact(null)}>
              Close
            </Button>
            <Button onClick={handleUpdateStatus} disabled={saving}>
              {saving ? "Saving..." : "Update Status"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
