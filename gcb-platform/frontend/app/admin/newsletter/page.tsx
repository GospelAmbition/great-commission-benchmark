"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { useUserProfile } from "@/lib/useUserProfile";
import {
  Mail,
  ChevronRight,
  RefreshCw,
  Trash2,
  Eye,
  Calendar,
  CheckCircle,
  XCircle,
  CloudOff,
  Users,
  UserCheck,
  UserX,
  Link2,
  Download,
} from "lucide-react";

// ---- Types ----

interface NewsletterStats {
  total: number;
  active: number;
  unsubscribed: number;
  synced_to_mailerlite: number;
  mailerlite_configured: boolean;
}

interface SubscriberItem {
  id: string;
  email: string;
  is_active: boolean;
  mailerlite_subscriber_id: string | null;
  subscribed_at: string | null;
  unsubscribed_at: string | null;
}

interface SubscriberDetail extends SubscriberItem {
  mailerlite_status: string | null;
  mailerlite_subscribed_at: string | null;
  mailerlite_opens_count: number | null;
  mailerlite_clicks_count: number | null;
}

interface MailerLiteSubscriber {
  id: string;
  email: string;
  status: string;
  subscribed_at: string | null;
  opens_count: number | null;
  clicks_count: number | null;
}

// ---- Component ----

export default function AdminNewsletterPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();

  // Stats
  const [stats, setStats] = useState<NewsletterStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  // Platform subscribers
  const [subscribers, setSubscribers] = useState<SubscriberItem[]>([]);
  const [subscribersLoading, setSubscribersLoading] = useState(true);
  const [subscribersTotal, setSubscribersTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");

  // MailerLite subscribers
  const [mlSubscribers, setMlSubscribers] = useState<MailerLiteSubscriber[]>([]);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlNextCursor, setMlNextCursor] = useState<string | null>(null);
  const [mlHasMore, setMlHasMore] = useState(false);
  const [mlLoaded, setMlLoaded] = useState(false);

  // Detail dialog
  const [selectedSubscriber, setSelectedSubscriber] =
    useState<SubscriberDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<SubscriberItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Sync state
  const [syncingId, setSyncingId] = useState<string | null>(null);

  // Export
  const [exporting, setExporting] = useState(false);

  // Active tab
  const [activeTab, setActiveTab] = useState("platform");

  // ---- Auth checks ----

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
      loadStats();
      loadSubscribers();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router]);

  // Reload platform subscribers when filters change
  useEffect(() => {
    if (user && (canAdmin || isAdmin)) {
      loadSubscribers();
    }
  }, [statusFilter, searchQuery]);

  // ---- Data loading ----

  async function loadStats() {
    setStatsLoading(true);
    try {
      const response = await fetch("/api/admin/newsletter/stats");
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        toast.error("Failed to load newsletter stats");
      }
    } catch (error) {
      console.error("Failed to load newsletter stats:", error);
    } finally {
      setStatsLoading(false);
    }
  }

  async function loadSubscribers() {
    setSubscribersLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (searchQuery) params.append("search", searchQuery);
      params.append("limit", "50");

      const response = await fetch(
        `/api/admin/newsletter/subscribers?${params}`
      );
      if (response.ok) {
        const data = await response.json();
        setSubscribers(data.items || []);
        setSubscribersTotal(data.total || 0);
      } else {
        toast.error("Failed to load subscribers");
      }
    } catch (error) {
      console.error("Failed to load subscribers:", error);
      toast.error("Failed to load subscribers");
    } finally {
      setSubscribersLoading(false);
    }
  }

  const loadMailerLiteSubscribers = useCallback(
    async (cursor?: string | null) => {
      setMlLoading(true);
      try {
        const params = new URLSearchParams();
        if (cursor) params.append("cursor", cursor);
        params.append("limit", "50");

        const response = await fetch(
          `/api/admin/newsletter/mailerlite?${params}`
        );
        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          toast.error(err.detail || "Failed to load MailerLite subscribers");
          return;
        }
        const data = await response.json();
        if (cursor) {
          setMlSubscribers((prev) => [...prev, ...(data.items || [])]);
        } else {
          setMlSubscribers(data.items || []);
        }
        setMlNextCursor(data.next_cursor || null);
        setMlHasMore(data.has_more || false);
        setMlLoaded(true);
      } catch (error) {
        console.error("Failed to load MailerLite subscribers:", error);
        toast.error("Failed to load MailerLite subscribers");
      } finally {
        setMlLoading(false);
      }
    },
    []
  );

  // Load MailerLite data on first tab switch
  useEffect(() => {
    if (activeTab === "mailerlite" && !mlLoaded && stats?.mailerlite_configured) {
      loadMailerLiteSubscribers();
    }
  }, [activeTab, mlLoaded, stats?.mailerlite_configured, loadMailerLiteSubscribers]);

  // ---- Actions ----

  async function openDetail(sub: SubscriberItem) {
    setDetailLoading(true);
    setSelectedSubscriber(null);
    try {
      const response = await fetch(
        `/api/admin/newsletter/subscribers/${sub.id}`
      );
      if (response.ok) {
        const data: SubscriberDetail = await response.json();
        setSelectedSubscriber(data);
      } else {
        toast.error("Failed to load subscriber details");
      }
    } catch (error) {
      console.error("Failed to load subscriber detail:", error);
      toast.error("Failed to load subscriber details");
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleSync(sub: SubscriberItem) {
    setSyncingId(sub.id);
    try {
      const response = await fetch(
        `/api/admin/newsletter/subscribers/${sub.id}/sync`,
        { method: "POST" }
      );
      if (response.ok) {
        const data = await response.json();
        toast.success(data.message || "Subscriber synced to MailerLite");
        loadSubscribers();
        loadStats();
      } else {
        const err = await response.json().catch(() => ({}));
        toast.error(err.detail || "Failed to sync subscriber");
      }
    } catch (error) {
      console.error("Failed to sync subscriber:", error);
      toast.error("Failed to sync subscriber");
    } finally {
      setSyncingId(null);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      const response = await fetch(
        `/api/admin/newsletter/subscribers/${deleteTarget.id}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        toast.success(`Subscriber ${deleteTarget.email} removed`);
        setDeleteTarget(null);
        loadSubscribers();
        loadStats();
      } else {
        const err = await response.json().catch(() => ({}));
        toast.error(err.detail || "Failed to remove subscriber");
      }
    } catch (error) {
      console.error("Failed to delete subscriber:", error);
      toast.error("Failed to remove subscriber");
    } finally {
      setDeleting(false);
    }
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSearchQuery(searchInput);
  }

  async function handleExportCsv() {
    setExporting(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);

      const response = await fetch(
        `/api/admin/newsletter/subscribers/export?${params}`
      );
      if (!response.ok) {
        toast.error("Failed to export subscribers");
        return;
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "newsletter_subscribers.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success("CSV exported successfully");
    } catch (error) {
      console.error("Failed to export CSV:", error);
      toast.error("Failed to export subscribers");
    } finally {
      setExporting(false);
    }
  }

  // ---- Loading / guard ----

  if (userLoading || profileLoading) {
    return (
      <div className="container py-8 max-w-7xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!user || (!canAdmin && !isAdmin)) {
    return null;
  }

  // ---- Render ----

  return (
    <div className="container py-8 max-w-7xl">
      {/* Breadcrumb */}
      <nav className="mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link
              href="/admin"
              className="hover:text-primary transition-colors"
            >
              Admin
            </Link>
          </li>
          <li>
            <ChevronRight className="h-4 w-4" />
          </li>
          <li className="text-foreground font-medium">
            Newsletter Subscribers
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 mb-2">
            <Mail className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold">Newsletter Subscribers</h1>
          </div>
          <Button
            variant="outline"
            onClick={handleExportCsv}
            disabled={exporting}
          >
            <Download className={`h-4 w-4 mr-2 ${exporting ? "animate-pulse" : ""}`} />
            {exporting ? "Exporting..." : "Export CSV"}
          </Button>
        </div>
        <p className="mt-2 text-muted-foreground">
          Manage newsletter subscribers and view MailerLite sync status
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4" />
              Total Subscribers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div className="text-3xl font-bold">{stats?.total ?? 0}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <UserCheck className="h-4 w-4" />
              Active
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div className="text-3xl font-bold text-emerald-400">
                {stats?.active ?? 0}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <UserX className="h-4 w-4" />
              Unsubscribed
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <div className="text-3xl font-bold text-red-400">
                {stats?.unsubscribed ?? 0}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Link2 className="h-4 w-4" />
              Synced to MailerLite
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-9 w-16" />
            ) : (
              <>
                <div className="text-3xl font-bold">
                  {stats?.synced_to_mailerlite ?? 0}
                </div>
                {stats && !stats.mailerlite_configured && (
                  <p className="text-xs text-yellow-400 mt-1">
                    MailerLite not configured
                  </p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="platform">
            Platform Subscribers ({subscribersTotal})
          </TabsTrigger>
          <TabsTrigger value="mailerlite">MailerLite Subscribers</TabsTrigger>
        </TabsList>

        {/* ---- Platform Subscribers Tab ---- */}
        <TabsContent value="platform">
          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 max-w-xs">
                  <label className="text-sm font-medium mb-2 block">
                    Status
                  </label>
                  <Select
                    value={statusFilter}
                    onValueChange={setStatusFilter}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="unsubscribed">
                        Unsubscribed
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex-1 max-w-sm">
                  <label className="text-sm font-medium mb-2 block">
                    Search Email
                  </label>
                  <form
                    onSubmit={handleSearchSubmit}
                    className="flex gap-2"
                  >
                    <Input
                      placeholder="Search by email..."
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                    />
                    <Button type="submit" variant="outline" size="sm">
                      Search
                    </Button>
                  </form>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Subscribers Table */}
          <Card>
            <CardHeader>
              <CardTitle>Subscribers ({subscribersTotal})</CardTitle>
              <CardDescription>
                Newsletter subscribers stored in the platform database
              </CardDescription>
            </CardHeader>
            <CardContent>
              {subscribersLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-12" />
                  ))}
                </div>
              ) : subscribers.length > 0 ? (
                <div className="rounded-lg border border-white/[0.08] overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-white/[0.02]">
                        <TableHead>Email</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>MailerLite Sync</TableHead>
                        <TableHead>Subscribed</TableHead>
                        <TableHead>Unsubscribed</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {subscribers.map((sub) => (
                        <TableRow key={sub.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Mail className="h-4 w-4 text-muted-foreground" />
                              <span className="font-medium">{sub.email}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            {sub.is_active ? (
                              <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Active
                              </Badge>
                            ) : (
                              <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                                <XCircle className="h-3 w-3 mr-1" />
                                Unsubscribed
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            {sub.mailerlite_subscriber_id ? (
                              <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                                <Link2 className="h-3 w-3 mr-1" />
                                Synced
                              </Badge>
                            ) : (
                              <Badge
                                variant="outline"
                                className="text-muted-foreground"
                              >
                                <CloudOff className="h-3 w-3 mr-1" />
                                Not synced
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            {sub.subscribed_at ? (
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                {new Date(
                                  sub.subscribed_at
                                ).toLocaleDateString()}
                              </div>
                            ) : (
                              <span className="text-muted-foreground">
                                —
                              </span>
                            )}
                          </TableCell>
                          <TableCell>
                            {sub.unsubscribed_at ? (
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                {new Date(
                                  sub.unsubscribed_at
                                ).toLocaleDateString()}
                              </div>
                            ) : (
                              <span className="text-muted-foreground">
                                —
                              </span>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => openDetail(sub)}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                              {stats?.mailerlite_configured && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  disabled={syncingId === sub.id}
                                  onClick={() => handleSync(sub)}
                                  title="Sync to MailerLite"
                                >
                                  <RefreshCw
                                    className={`h-4 w-4 ${syncingId === sub.id ? "animate-spin" : ""}`}
                                  />
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-red-400 hover:text-red-300"
                                onClick={() => setDeleteTarget(sub)}
                                title="Remove subscriber"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-foreground mb-2">
                    No subscribers found
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {statusFilter !== "all" || searchQuery
                      ? "Try adjusting your filters"
                      : "Subscribers will appear here when they sign up"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ---- MailerLite Subscribers Tab ---- */}
        <TabsContent value="mailerlite">
          {!stats?.mailerlite_configured ? (
            <Card>
              <CardContent className="py-12 text-center">
                <CloudOff className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-foreground mb-2">
                  MailerLite Not Configured
                </p>
                <p className="text-sm text-muted-foreground">
                  Set the <code>MAILERLITE_API_KEY</code> environment variable
                  to enable MailerLite integration.
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>MailerLite Subscribers</CardTitle>
                    <CardDescription>
                      Live subscriber data fetched directly from the MailerLite
                      API
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setMlLoaded(false);
                      setMlSubscribers([]);
                      loadMailerLiteSubscribers();
                    }}
                    disabled={mlLoading}
                  >
                    <RefreshCw
                      className={`h-4 w-4 mr-2 ${mlLoading ? "animate-spin" : ""}`}
                    />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {mlLoading && mlSubscribers.length === 0 ? (
                  <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-12" />
                    ))}
                  </div>
                ) : mlSubscribers.length > 0 ? (
                  <>
                    <div className="rounded-lg border border-white/[0.08] overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-white/[0.02]">
                            <TableHead>Email</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Opens</TableHead>
                            <TableHead>Clicks</TableHead>
                            <TableHead>Subscribed</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {mlSubscribers.map((sub) => (
                            <TableRow key={sub.id}>
                              <TableCell>
                                <div className="flex items-center gap-2">
                                  <Mail className="h-4 w-4 text-muted-foreground" />
                                  <span className="font-medium">
                                    {sub.email}
                                  </span>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge
                                  className={
                                    sub.status === "active"
                                      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                      : sub.status === "unsubscribed"
                                        ? "bg-red-500/20 text-red-400 border-red-500/30"
                                        : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                                  }
                                >
                                  {sub.status}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <span className="text-sm text-muted-foreground">
                                  {sub.opens_count ?? "—"}
                                </span>
                              </TableCell>
                              <TableCell>
                                <span className="text-sm text-muted-foreground">
                                  {sub.clicks_count ?? "—"}
                                </span>
                              </TableCell>
                              <TableCell>
                                {sub.subscribed_at ? (
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Calendar className="h-4 w-4" />
                                    {new Date(
                                      sub.subscribed_at
                                    ).toLocaleDateString()}
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">
                                    —
                                  </span>
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                    {mlHasMore && (
                      <div className="mt-4 text-center">
                        <Button
                          variant="outline"
                          onClick={() =>
                            loadMailerLiteSubscribers(mlNextCursor)
                          }
                          disabled={mlLoading}
                        >
                          {mlLoading ? "Loading..." : "Load More"}
                        </Button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-12">
                    <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-foreground mb-2">
                      No subscribers in MailerLite
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Subscribers will appear here once synced to MailerLite
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* ---- Subscriber Detail Dialog ---- */}
      <Dialog
        open={!!selectedSubscriber || detailLoading}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedSubscriber(null);
          }
        }}
      >
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Subscriber Details</DialogTitle>
            <DialogDescription>
              {selectedSubscriber
                ? selectedSubscriber.email
                : "Loading subscriber details..."}
            </DialogDescription>
          </DialogHeader>
          {detailLoading ? (
            <div className="space-y-3 py-4">
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-6 w-1/2" />
            </div>
          ) : selectedSubscriber ? (
            <div className="space-y-4 py-4">
              {/* Platform data */}
              <div>
                <h4 className="text-sm font-semibold text-muted-foreground mb-2">
                  Platform Data
                </h4>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <Label className="text-muted-foreground">Email</Label>
                    <p className="font-medium">{selectedSubscriber.email}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Status</Label>
                    <p>
                      {selectedSubscriber.is_active ? (
                        <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                          Active
                        </Badge>
                      ) : (
                        <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                          Unsubscribed
                        </Badge>
                      )}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Subscribed</Label>
                    <p className="text-sm">
                      {selectedSubscriber.subscribed_at
                        ? new Date(
                            selectedSubscriber.subscribed_at
                          ).toLocaleString()
                        : "—"}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">
                      Unsubscribed
                    </Label>
                    <p className="text-sm">
                      {selectedSubscriber.unsubscribed_at
                        ? new Date(
                            selectedSubscriber.unsubscribed_at
                          ).toLocaleString()
                        : "—"}
                    </p>
                  </div>
                </div>
              </div>

              {/* MailerLite data */}
              <div className="border-t border-white/[0.06] pt-4">
                <h4 className="text-sm font-semibold text-muted-foreground mb-2">
                  MailerLite Data
                </h4>
                {selectedSubscriber.mailerlite_status ? (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <Label className="text-muted-foreground">
                        MailerLite Status
                      </Label>
                      <p>
                        <Badge
                          className={
                            selectedSubscriber.mailerlite_status === "active"
                              ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                              : "bg-red-500/20 text-red-400 border-red-500/30"
                          }
                        >
                          {selectedSubscriber.mailerlite_status}
                        </Badge>
                      </p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">
                        MailerLite ID
                      </Label>
                      <p className="text-sm font-mono">
                        {selectedSubscriber.mailerlite_subscriber_id || "—"}
                      </p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Opens</Label>
                      <p className="text-sm">
                        {selectedSubscriber.mailerlite_opens_count ?? "—"}
                      </p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Clicks</Label>
                      <p className="text-sm">
                        {selectedSubscriber.mailerlite_clicks_count ?? "—"}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {stats?.mailerlite_configured
                      ? "No MailerLite data available for this subscriber."
                      : "MailerLite is not configured."}
                  </p>
                )}
              </div>
            </div>
          ) : null}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setSelectedSubscriber(null)}
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ---- Delete Confirmation Dialog ---- */}
      <Dialog
        open={!!deleteTarget}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove Subscriber</DialogTitle>
            <DialogDescription>
              Are you sure you want to remove{" "}
              <strong>{deleteTarget?.email}</strong> from the newsletter? This
              will also unsubscribe them from MailerLite.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
            >
              {deleting ? "Removing..." : "Remove Subscriber"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
