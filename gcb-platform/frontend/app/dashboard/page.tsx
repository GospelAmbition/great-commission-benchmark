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
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { CliSubmissionUpload } from "@/components/cli-submission-upload";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [tests, setTests] = useState<any[]>([]);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadDashboardData();
    }
  }, [user, userLoading, router]);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [profileData, testsData, submissionsData, activityData] = await Promise.all([
        apiClient.getUserProfile().catch(() => null),
        apiClient.getUserTests({ limit: 10 }).catch(() => ({ items: [] })),
        apiClient.getUserSubmissions().catch(() => []),
        apiClient.getUserActivity().catch(() => []),
      ]);

      setProfile(profileData);
      if (testsData?.items) {
        setTests(testsData.items);
      }
      setSubmissions(submissionsData || []);
      setActivity(activityData || []);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  }

  if (userLoading || loading) {
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

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Welcome back, {profile?.name || user.name || "User"}!
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tests Run
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{profile?.test_count || tests.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Submissions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{submissions?.length ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Contributions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{profile?.contribution_count || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Test History */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Tests</CardTitle>
              <CardDescription>Your recent benchmark test runs</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setUploadDialogOpen(true)}>
                Upload CLI Results
              </Button>
              <Button asChild>
                <Link href="/tests/new">Run New Test</Link>
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {tests.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tests.map((test) => (
                  <TableRow key={test.id}>
                    <TableCell>
                      {new Date(test.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{test.model_name || test.model_id}</TableCell>
                    <TableCell>{test.version}</TableCell>
                    <TableCell>
                      {test.overall_score ? test.overall_score.toFixed(1) : "—"}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{test.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <Button asChild variant="ghost" size="sm">
                        <Link href={`/dashboard/tests/${test.id}`}>View</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No tests yet</p>
              <Button asChild>
                <Link href="/tests/new">Run Your First Test</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Community Submissions */}
      {submissions.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Community Submissions</CardTitle>
            <CardDescription>Your submitted test results</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {submissions.map((submission) => (
                  <TableRow key={submission.id}>
                    <TableCell>
                      {new Date(submission.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{submission.model_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{submission.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <Button asChild variant="ghost" size="sm">
                        <Link href={`/dashboard/submissions/${submission.id}`}>View</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Activity Feed */}
      {activity.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activity.map((item, index) => (
                <div key={index} className="flex items-start gap-4 border-b pb-4 last:border-0">
                  <div className="flex-1">
                    <p className="text-sm">{item.description || item.type}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                  {item.link && (
                    <Button asChild variant="ghost" size="sm">
                      <Link href={item.link}>View</Link>
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* CLI Submission Upload Dialog */}
      <CliSubmissionUpload
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        onSuccess={() => {
          // Refresh submissions list after successful upload
          loadDashboardData();
        }}
      />
    </div>
  );
}
