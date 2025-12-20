"use client";

import { useEffect, useState } from "react";
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

export default function ModeratorDashboardPage() {
  const { data: session } = useSession();
  const user = session?.user;
  const [platformQueue, setPlatformQueue] = useState<any[]>([]);
  const [communityQueue, setCommunityQueue] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [platformData, communityData, statsData, historyData] = await Promise.all([
        apiClient.getModerationQueue().catch(() => ({ items: [], total: 0 })),
        apiClient.getCommunitySubmissionQueue().catch(() => ({ items: [], total: 0 })),
        apiClient.getModeratorStats().catch(() => null),
        apiClient.getModeratorActivity({ limit: 20 }).catch(() => ({ items: [], total: 0 })),
      ]);

      setPlatformQueue(platformData.items || []);
      setCommunityQueue(communityData.items || []);
      
      const totalPending = (platformData.items?.length || 0) + (communityData.items?.length || 0);
      
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

  if (loading) {
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
              Agreement Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats?.agreement_rate ? `${(stats.agreement_rate * 100).toFixed(1)}%` : "—"}
            </div>
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
          <Tabs defaultValue="platform" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="platform">
                Platform Tests ({platformQueue.length})
              </TabsTrigger>
              <TabsTrigger value="community">
                CLI Submissions ({communityQueue.length})
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="platform" className="mt-4">
              {platformQueue.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Test ID</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {platformQueue.map((item) => (
                      <TableRow key={item.test_id}>
                        <TableCell className="font-mono text-sm">{item.test_id.slice(0, 8)}...</TableCell>
                        <TableCell>{item.model_name}</TableCell>
                        <TableCell>{item.user_name}</TableCell>
                        <TableCell>{item.overall_score?.toFixed(1) || "—"}</TableCell>
                        <TableCell>
                          <Badge variant={item.trust_tier === "pending_review" ? "destructive" : "outline"}>
                            {item.trust_tier}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button asChild variant="ghost" size="sm">
                            <Link href={`/moderator/review/${item.test_id}`}>Review</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No platform tests in queue</p>
                </div>
              )}
            </TabsContent>
            
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
                  <p className="text-muted-foreground">No CLI submissions in queue</p>
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
                        {item.review_type === "cli_submission" ? "CLI" : "Platform"}
                      </Badge>
                    </TableCell>
                    <TableCell>{item.model_name}</TableCell>
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
                      {item.review_type === "cli_submission" && item.submission_id ? (
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/moderator/community/${item.submission_id}`} className="font-mono text-sm">
                            {item.submission_id.slice(0, 8)}...
                          </Link>
                        </Button>
                      ) : item.test_id ? (
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/moderator/review/${item.test_id}`} className="font-mono text-sm">
                            {item.test_id.slice(0, 8)}...
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
