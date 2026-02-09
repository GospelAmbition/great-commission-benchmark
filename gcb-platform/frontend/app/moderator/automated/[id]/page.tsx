"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface AutomatedRunDetail {
  test_run_id: string;
  model_name: string;
  model_id: string;
  provider: string;
  user_name: string;
  user_email: string;
  benchmark_version: string;
  status: string;
  trust_tier: string;
  overall_score: number;
  tier1_score: number;
  tier2_score: number;
  tier3_score: number;
  total_questions: number;
  tier_stats: Record<number, Record<string, number>>;
  completed_at: string | null;
  admin_notes: string | null;
  moderator_reviewed_at: string | null;
  moderator_decision: string | null;
  moderator_name: string | null;
  sample_responses: Array<{
    question_id: string;
    tier: number;
    category: string;
    response: string;
    verdict: string;
    judge_reasoning?: string;
    thought_process?: string | null;
  }>;
  sample_size: number;
}

export default function AutomatedRunReviewPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const testRunId = params.id as string;

  const [run, setRun] = useState<AutomatedRunDetail | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && testRunId) {
      loadRunData();
    }
  }, [user, userLoading, testRunId, router]);

  async function loadRunData() {
    setLoading(true);
    try {
      const data = await apiClient.getAutomatedTestRunDetail(testRunId);
      setRun(data);
    } catch (error: any) {
      console.error("Failed to load automated run:", error);
      toast.error(error.message || "Failed to load test run data");
    } finally {
      setLoading(false);
    }
  }

  function goToNext() {
    if (!run) return;
    if (currentIndex < run.sample_responses.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }

  function goToPrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }

  async function handleAccept() {
    if (!run) return;
    setSubmitting(true);
    try {
      const data = await apiClient.acceptAutomatedTestRun(testRunId);
      toast.success(data.message || "Test run accepted");
      router.push("/moderator");
    } catch (error: any) {
      console.error("Failed to accept:", error);
      toast.error(error.message || "Failed to accept test run");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject() {
    if (!run) return;
    setSubmitting(true);
    try {
      const data = await apiClient.rejectAutomatedTestRun(testRunId);
      toast.success(data.message || "Test run rejected");
      router.push("/moderator");
    } catch (error: any) {
      console.error("Failed to reject:", error);
      toast.error(error.message || "Failed to reject test run");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRestore() {
    if (!run) return;
    setSubmitting(true);
    try {
      const data = await apiClient.restoreAutomatedTestRun(testRunId);
      toast.success(data.message || "Test run restored");
      router.push("/moderator");
    } catch (error: any) {
      console.error("Failed to restore:", error);
      toast.error(error.message || "Failed to restore test run");
    } finally {
      setSubmitting(false);
    }
  }

  if (userLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user || !run) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Review Not Available</CardTitle>
            <CardDescription>
              This automated test run is not available for review.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/moderator">Back to Queue</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentResponse = run.sample_responses[currentIndex];
  const tierLabels: Record<number, string> = { 1: "Tier 1: Task Capability", 2: "Tier 2: Gospel Core", 3: "Tier 3: Worldview Confession" };
  const verdictLabels: Record<string, string> = {
    ACCEPTED: "Accepted",
    COMPROMISED: "Compromised",
    REFUSED: "Refused",
    ERROR: "Error",
  };

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/moderator">← Back to Queue</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Review: {run.model_name}</h1>
            <p className="text-muted-foreground mt-2">
              Bulk Test Run • {run.model_id} • Version {run.benchmark_version} • Score: {run.overall_score.toFixed(1)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Submitted by {run.user_name} • {run.completed_at ? new Date(run.completed_at).toLocaleString() : "Unknown date"}
            </p>
          </div>
          <div className="text-right flex flex-col gap-2 items-end">
            <Badge variant={run.status === "completed" ? "default" : run.status === "rejected" ? "destructive" : "outline"}>
              {run.status}
            </Badge>
            <Badge variant="outline" className="text-xs">
              trust: {run.trust_tier}
            </Badge>
          </div>
        </div>
      </div>

      {/* Admin Notes (if any) */}
      {run.admin_notes && (
        <Card className="mb-6 border-yellow-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-yellow-500">Moderator Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{run.admin_notes}</p>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overall Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.overall_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 1</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.tier1_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 2</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.tier2_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 3</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.tier3_score.toFixed(1)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Sample Responses Review */}
      {run.sample_responses.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Sample Responses Review</CardTitle>
            <CardDescription>
              Reviewing {run.sample_size} of {run.total_questions} responses
              ({run.total_questions > 0 ? Math.round((run.sample_size / run.total_questions) * 100) : 0}% sample)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm text-muted-foreground">
                  Response {currentIndex + 1} of {run.sample_responses.length}
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={goToPrevious} disabled={currentIndex === 0}>
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" onClick={goToNext} disabled={currentIndex === run.sample_responses.length - 1}>
                    Next
                  </Button>
                </div>
              </div>

              {currentResponse && (
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-semibold">Tier & Category</Label>
                    <div className="flex gap-2 mt-1">
                      <Badge variant="outline">{tierLabels[currentResponse.tier] || `Tier ${currentResponse.tier}`}</Badge>
                      <Badge variant="outline">{currentResponse.category}</Badge>
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm font-semibold">Model Response</Label>
                    <div className="mt-1 p-4 bg-muted rounded-md text-sm whitespace-pre-wrap max-h-[400px] overflow-y-auto">
                      {currentResponse.response}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm font-semibold">Judge Verdict</Label>
                    <div className="mt-1">
                      <Badge
                        variant="outline"
                        className={
                          currentResponse.verdict === "ACCEPTED"
                            ? "bg-green-500/20 text-green-400 border-green-500/30"
                            : currentResponse.verdict === "REFUSED"
                            ? "bg-red-500/20 text-red-400 border-red-500/30"
                            : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                        }
                      >
                        {verdictLabels[currentResponse.verdict] || currentResponse.verdict}
                      </Badge>
                    </div>
                  </div>

                  {currentResponse.judge_reasoning && (
                    <div>
                      <Label className="text-sm font-semibold">Judge Reasoning</Label>
                      <div className="mt-1 p-4 bg-muted rounded-md text-sm">
                        {currentResponse.judge_reasoning}
                      </div>
                    </div>
                  )}

                  {currentResponse.thought_process && (
                    <div>
                      <Label className="text-sm font-semibold">Thought Process</Label>
                      <div className="mt-1 p-4 bg-muted rounded-md text-sm whitespace-pre-wrap">
                        {currentResponse.thought_process}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Card */}
      <Card>
        <CardHeader>
          <CardTitle>Moderation Action</CardTitle>
          <CardDescription>
            {run.moderator_reviewed_at == null
              ? "Accept to keep on the leaderboard and move to history, or reject to remove from the leaderboard and move to history."
              : run.moderator_decision === "accepted"
              ? "You accepted this run. It remains on the leaderboard."
              : run.status === "rejected"
              ? "This run was rejected and is not on the leaderboard. You can restore it."
              : `Current status: ${run.status}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={() => router.push("/moderator")} disabled={submitting}>
            Back
          </Button>
          {run.moderator_reviewed_at == null && (
            <>
              <Button variant="default" onClick={handleAccept} disabled={submitting}>
                {submitting ? "Accepting..." : "Accept (keep on leaderboard)"}
              </Button>
              <Button variant="destructive" onClick={handleReject} disabled={submitting}>
                {submitting ? "Rejecting..." : "Reject (remove from leaderboard)"}
              </Button>
            </>
          )}
          {run.moderator_reviewed_at != null && run.status === "rejected" && (
            <Button onClick={handleRestore} disabled={submitting}>
              {submitting ? "Restoring..." : "Restore to Leaderboard"}
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
