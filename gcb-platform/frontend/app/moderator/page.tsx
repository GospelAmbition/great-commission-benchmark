"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";
import { apiClient } from "@/lib/api";
import { useUserProfile } from "@/lib/useUserProfile";
import { toast } from "sonner";

export default function ModeratorDashboardPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const { canModerate, canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [communityQueue, setCommunityQueue] = useState<any[]>([]);
  const [sponsorshipQueue, setSponsorshipQueue] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    // Check if user has moderator permission
    if (user && !profileLoading) {
      if (!canModerate && !canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadDashboardData();
    }
  }, [user, userLoading, profileLoading, canModerate, canAdmin, isAdmin, router]);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [communityData, sponsorshipData, statsData, historyData] = await Promise.all([
        apiClient.getCommunitySubmissionQueue().catch(() => ({ items: [], total: 0 })),
        apiClient.getSponsorshipQueue().catch(() => ({ items: [], total: 0 })),
        apiClient.getModeratorStats().catch(() => null),
        apiClient.getModeratorActivity({ limit: 20 }).catch(() => ({ items: [], total: 0 })),
      ]);

      setCommunityQueue(communityData.items || []);
      setSponsorshipQueue(sponsorshipData.items || []);
      
      const totalPending = (communityData.items?.length || 0) + (sponsorshipData.items?.length || 0);
      
      if (statsData) {
        setStats({
          pending_reviews: totalPending,
          completed_this_month: statsData.system_wide?.completed_this_month || 0,
          agreement_rate: statsData.system_wide?.agreement_rate ? statsData.system_wide.agreement_rate / 100 : 0,
        });
      } else {
        setStats({
          pending_reviews: totalPending,
          completed_this_month: 0,
          agreement_rate: 0,
        });
      }
      
      setHistory(historyData.items || []);
    } catch (error) {
      console.error("Failed to load moderator dashboard:", error);
    } finally {
      setLoading(false);
    }
  }

  if (userLoading || profileLoading || (loading && !user)) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Double-check moderator permission before rendering
  if (!canModerate && !canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Moderator Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Review and validate test results
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pending Reviews
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.pending_reviews || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Completed This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.completed_this_month || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Sponsorship Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{sponsorshipQueue.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Moderation Queue */}
      <Card>
        <CardHeader>
          <CardTitle>Moderation Queue</CardTitle>
          <CardDescription>
            Tests and submissions awaiting review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="community" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="community">
                GCB Runner Submissions ({communityQueue.length})
              </TabsTrigger>
              <TabsTrigger value="sponsorship">
                Sponsorships ({sponsorshipQueue.length})
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="community" className="mt-4">
              {communityQueue.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Submission ID</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Submitted</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {communityQueue.map((item) => (
                      <TableRow key={item.submission_id}>
                        <TableCell className="font-mono text-sm">{item.submission_id.slice(0, 8)}...</TableCell>
                        <TableCell>{item.model_name}</TableCell>
                        <TableCell>{item.user_name}</TableCell>
                        <TableCell>{item.overall_score?.toFixed(1) || "—"}</TableCell>
                        <TableCell>
                          <Badge variant={item.status === "pending" ? "destructive" : "outline"}>
                            {item.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {new Date(item.submitted_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Button asChild variant="ghost" size="sm">
                            <Link href={`/moderator/community/${item.submission_id}`}>Review</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No GCB Runner submissions in queue</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="sponsorship" className="mt-4">
              {sponsorshipQueue.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Payment</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sponsorshipQueue.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="text-sm text-muted-foreground">
                          {new Date(item.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Badge variant={item.request_type === "sponsorship" ? "default" : "outline"}>
                            {item.request_type === "sponsorship" ? "Paid ($20)" : "Request"}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate">{item.model_name}</TableCell>
                        <TableCell>{item.user_name}</TableCell>
                        <TableCell>
                          {item.request_type === "sponsorship" ? (
                            <Badge variant={item.payment_status === "succeeded" ? "default" : "destructive"}>
                              {item.payment_status || "pending"}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Button asChild variant="ghost" size="sm">
                            <Link href={`/moderator/sponsorship/${item.id}`}>Review</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No sponsorship requests in queue</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Moderation History */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Moderation History</CardTitle>
          <CardDescription>
            Recent completed reviews
          </CardDescription>
        </CardHeader>
        <CardContent>
          {history.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.map((item) => (
                  <TableRow key={item.review_id}>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        Runner
                      </Badge>
                    </TableCell>
                    <TableCell>{item.model_name}</TableCell>
                    <TableCell className="text-sm text-muted-foreground font-mono">
                      {item.benchmark_version || "—"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={
                        item.action === "verified" || item.action === "approved" ? "default" :
                        item.action === "concerns" || item.action === "rejected" ? "destructive" :
                        item.action === "escalated" ? "destructive" :
                        "outline"
                      }>
                        {item.action}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {item.submission_id ? (
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/moderator/community/${item.submission_id}`} className="font-mono text-sm">
                            {item.submission_id.slice(0, 8)}...
                          </Link>
                        </Button>
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No moderation history yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
