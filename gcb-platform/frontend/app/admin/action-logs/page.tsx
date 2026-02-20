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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";
import {
  ScrollText,
  ChevronRight,
  Calendar,
  RefreshCw,
  User,
  Key,
  Globe,
  Cpu,
} from "lucide-react";

interface ActionLogActor {
  id: string;
  name: string | null;
  email: string;
}

interface ActionLogItem {
  id: string;
  action: string;
  actor_type: string;
  actor_user: ActionLogActor | null;
  actor_api_key_id: string | null;
  entity_type: string | null;
  entity_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

const ACTOR_TYPE_CONFIG: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
  user: {
    label: "User",
    className: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    icon: <User className="h-3 w-3" />,
  },
  api_key: {
    label: "API Key",
    className: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    icon: <Key className="h-3 w-3" />,
  },
  anonymous: {
    label: "Anonymous",
    className: "bg-slate-500/20 text-slate-400 border-slate-500/30",
    icon: <Globe className="h-3 w-3" />,
  },
  system: {
    label: "System",
    className: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    icon: <Cpu className="h-3 w-3" />,
  },
};

function formatAction(action: string): string {
  return action
    .replace(/_/g, " ")
    .replace(/\./g, " · ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function AdminActionLogsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [logs, setLogs] = useState<ActionLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>("all");
  const [limit] = useState(100);
  const [offset, setOffset] = useState(0);

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
      loadLogs();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router, actionFilter, entityTypeFilter, limit, offset]);

  async function loadLogs() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (actionFilter !== "all") {
        params.append("action", actionFilter);
      }
      if (entityTypeFilter !== "all") {
        params.append("entity_type", entityTypeFilter);
      }
      params.append("limit", String(limit));
      params.append("offset", String(offset));

      const response = await fetch(`/api/admin/action-logs?${params}`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.items || []);
        setTotal(data.total || 0);
      } else {
        toast.error("Failed to load action logs");
      }
    } catch (error) {
      console.error("Failed to load action logs:", error);
      toast.error("Failed to load action logs");
    } finally {
      setLoading(false);
    }
  }

  function renderActor(log: ActionLogItem) {
    if (log.actor_user) {
      return (
        <span title={log.actor_user.email}>
          {log.actor_user.name || log.actor_user.email}
          {log.actor_type === "api_key" && (
            <span className="ml-1 text-xs text-muted-foreground">(API key)</span>
          )}
        </span>
      );
    }
    const config = ACTOR_TYPE_CONFIG[log.actor_type] || ACTOR_TYPE_CONFIG.anonymous;
    return (
      <Badge variant="outline" className={config.className}>
        <span className="flex items-center gap-1">
          {config.icon}
          {config.label}
        </span>
      </Badge>
    );
  }

  function renderMetadata(metadata: Record<string, unknown> | null) {
    if (!metadata || Object.keys(metadata).length === 0) return "—";
    return (
      <span className="font-mono text-xs text-muted-foreground">
        {JSON.stringify(metadata)}
      </span>
    );
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
            Action Log
          </li>
        </ol>
      </nav>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <ScrollText className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Action Log</h1>
        </div>
        <p className="mt-2 text-muted-foreground">
          Audit trail of key administrative and registration actions — who did what and when
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[180px] max-w-xs">
              <Label className="text-sm font-medium mb-2 block">Action</Label>
              <Select value={actionFilter} onValueChange={(v) => { setActionFilter(v); setOffset(0); }}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="model_submission.upload">Model Submission</SelectItem>
                  <SelectItem value="community_submission.approve">Community Approve</SelectItem>
                  <SelectItem value="community_submission.reject">Community Reject</SelectItem>
                  <SelectItem value="community_submission.revert">Community Revert</SelectItem>
                  <SelectItem value="model.archive">Model Archive</SelectItem>
                  <SelectItem value="model.unarchive">Model Unarchive</SelectItem>
                  <SelectItem value="sponsorship.create">Sponsorship Create</SelectItem>
                  <SelectItem value="sponsorship.review">Sponsorship Review</SelectItem>
                  <SelectItem value="sponsorship.assign">Sponsorship Assign</SelectItem>
                  <SelectItem value="blog_post.create">Blog Post Create</SelectItem>
                  <SelectItem value="blog_post.update">Blog Post Update</SelectItem>
                  <SelectItem value="blog_post.delete">Blog Post Delete</SelectItem>
                  <SelectItem value="blog_post.publish">Blog Post Publish</SelectItem>
                  <SelectItem value="blog_post.unpublish">Blog Post Unpublish</SelectItem>
                  <SelectItem value="newsletter.subscribe">Newsletter Subscribe</SelectItem>
                  <SelectItem value="newsletter.unsubscribe">Newsletter Unsubscribe</SelectItem>
                  <SelectItem value="contact.submit">Contact Submit</SelectItem>
                  <SelectItem value="contact.status_update">Contact Status Update</SelectItem>
                  <SelectItem value="volunteer.apply">Volunteer Apply</SelectItem>
                  <SelectItem value="question_set.archive">Question Set Archive</SelectItem>
                  <SelectItem value="question_set.status_update">Question Set Status Update</SelectItem>
                  <SelectItem value="automated_run.accept">Automated Run Accept</SelectItem>
                  <SelectItem value="automated_run.reject">Automated Run Reject</SelectItem>
                  <SelectItem value="automated_run.restore">Automated Run Restore</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1 min-w-[180px] max-w-xs">
              <Label className="text-sm font-medium mb-2 block">Entity Type</Label>
              <Select value={entityTypeFilter} onValueChange={(v) => { setEntityTypeFilter(v); setOffset(0); }}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="community_submission">Community Submission</SelectItem>
                  <SelectItem value="model">Model</SelectItem>
                  <SelectItem value="test_run">Test Run</SelectItem>
                  <SelectItem value="sponsorship_request">Sponsorship Request</SelectItem>
                  <SelectItem value="blog_post">Blog Post</SelectItem>
                  <SelectItem value="blog_category">Blog Category</SelectItem>
                  <SelectItem value="newsletter_subscriber">Newsletter Subscriber</SelectItem>
                  <SelectItem value="contact_submission">Contact Submission</SelectItem>
                  <SelectItem value="volunteer_application">Volunteer Application</SelectItem>
                  <SelectItem value="question_set">Question Set</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button variant="outline" onClick={() => loadLogs()} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Events ({total})</CardTitle>
          <CardDescription>
            Most recent first. Use filters to narrow results.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {logs.length > 0 ? (
            <div className="rounded-lg border border-white/[0.08] overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-white/[0.02]">
                    <TableHead>Time</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Actor</TableHead>
                    <TableHead>Entity</TableHead>
                    <TableHead className="max-w-[200px]">Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="whitespace-nowrap">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          {new Date(log.created_at).toLocaleString()}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-xs">
                          {formatAction(log.action)}
                        </Badge>
                      </TableCell>
                      <TableCell>{renderActor(log)}</TableCell>
                      <TableCell>
                        {log.entity_type && log.entity_id ? (
                          <span className="font-mono text-xs" title={log.entity_id}>
                            {log.entity_type}: {log.entity_id.length > 12 ? `${log.entity_id.slice(0, 8)}…` : log.entity_id}
                          </span>
                        ) : (
                          "—"
                        )}
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate" title={JSON.stringify(log.metadata)}>
                        {renderMetadata(log.metadata)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-12">
              <ScrollText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-foreground mb-2">No action logs found</p>
              <p className="text-sm text-muted-foreground">
                {actionFilter !== "all" || entityTypeFilter !== "all"
                  ? "Try adjusting your filters"
                  : "Actions will appear here as they occur"}
              </p>
            </div>
          )}

          {total > limit && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-white/[0.06]">
              <p className="text-sm text-muted-foreground">
                Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={offset === 0}
                  onClick={() => setOffset((o) => Math.max(0, o - limit))}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={offset + limit >= total}
                  onClick={() => setOffset((o) => o + limit)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
