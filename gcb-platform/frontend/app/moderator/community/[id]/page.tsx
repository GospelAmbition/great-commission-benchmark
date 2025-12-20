"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface SubmissionDetail {
  submission_id: string;
  model_name: string;
  user_name: string;
  user_email: string;
  cli_version: string;
  question_set_version: string;
  overall_score: number;
  tier1_score: number;
  tier2_score: number;
  tier3_score: number;
  total_questions: number;
  status: string;
  submitted_at: string;
  results_package: any;
  sample_responses: Array<{
    question_id: string | number;
    tier: number;
    category: string;
    response: string;
    verdict: string;
    judge_reasoning?: string;
  }>;
  sample_size: number;
}

export default function CommunitySubmissionReviewPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const submissionId = params.id as string;
  
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [action, setAction] = useState<"approve" | "reject" | "">("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && submissionId) {
      loadSubmissionData();
    }
  }, [user, userLoading, submissionId, router]);

  async function loadSubmissionData() {
    setLoading(true);
    try {
      const data = await apiClient.getCommunitySubmissionDetail(submissionId);
      setSubmission(data);
    } catch (error: any) {
      console.error("Failed to load submission:", error);
      toast.error(error.message || "Failed to load submission data");
    } finally {
      setLoading(false);
    }
  }

  function goToNext() {
    if (!submission) return;
    if (currentIndex < submission.sample_responses.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }

  function goToPrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }

  async function handleSubmitReview() {
    if (!submission || !action) {
      toast.error("Please select an action (approve or reject)");
      return;
    }

    setSubmitting(true);
    try {
      const data = await apiClient.reviewCommunitySubmission(
        submissionId,
        action,
        notes.trim() || undefined
      );
      toast.success(data.message || "Review submitted successfully");
      router.push("/moderator");
    } catch (error: any) {
      console.error("Failed to submit review:", error);
      toast.error(error.message || "Failed to submit review");
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

  if (!user || !submission) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Review Not Available</CardTitle>
            <CardDescription>
              This submission is not available for review.
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

  const currentResponse = submission.sample_responses[currentIndex];
  const tierLabels = { 1: "Tier 1: Task Capability", 2: "Tier 2: Doctrinal Fidelity", 3: "Tier 3: Worldview Confession" };
  const verdictLabels: Record<string, string> = {
    ACCEPTED: "Accepted",
    COMPROMISED: "Compromised",
    REFUSED: "Refused",
    ERROR: "Error",
    // Legacy mappings for backward compatibility with existing data
    LOYAL: "Accepted",
    DISLOYAL: "Refused",
    AFFIRMED: "Accepted",
    HEDGED: "Compromised",
    DENIED: "Refused",
  };

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/moderator">← Back to Queue</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Review: {submission.model_name}</h1>
            <p className="text-muted-foreground mt-2">
              CLI Submission • Version {submission.question_set_version} • Score: {submission.overall_score.toFixed(1)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Submitted by {submission.user_name} • {new Date(submission.submitted_at).toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <Badge variant={submission.status === "pending" ? "destructive" : "outline"}>
              {submission.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overall Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submission.overall_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 1</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submission.tier1_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 2</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submission.tier2_score.toFixed(1)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tier 3</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submission.tier3_score.toFixed(1)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Sample Responses Review */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Sample Responses Review</CardTitle>
          <CardDescription>
            Reviewing {submission.sample_size} of {submission.total_questions} responses
            ({Math.round((submission.sample_size / submission.total_questions) * 100)}% sample)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-muted-foreground">
                Response {currentIndex + 1} of {submission.sample_responses.length}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={goToPrevious} disabled={currentIndex === 0}>
                  Previous
                </Button>
                <Button variant="outline" size="sm" onClick={goToNext} disabled={currentIndex === submission.sample_responses.length - 1}>
                  Next
                </Button>
              </div>
            </div>

            {currentResponse && (
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-semibold">Tier & Category</Label>
                  <div className="flex gap-2 mt-1">
                    <Badge variant="outline">{tierLabels[currentResponse.tier as keyof typeof tierLabels]}</Badge>
                    <Badge variant="outline">{currentResponse.category}</Badge>
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-semibold">Model Response</Label>
                  <div className="mt-1 p-4 bg-muted rounded-md text-sm whitespace-pre-wrap">
                    {currentResponse.response}
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-semibold">Judge Verdict</Label>
                  <div className="mt-1">
                    <Badge variant={currentResponse.verdict === "ACCEPTED" ? "default" : currentResponse.verdict === "COMPROMISED" ? "secondary" : "destructive"}>
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
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Review Decision */}
      <Card>
        <CardHeader>
          <CardTitle>Review Decision</CardTitle>
          <CardDescription>
            Approve or reject this submission based on your review
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-base font-semibold mb-3 block">Action</Label>
            <RadioGroup value={action} onValueChange={(value) => setAction(value as "approve" | "reject")}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="approve" id="approve" />
                <Label htmlFor="approve" className="font-normal cursor-pointer">
                  Approve - Submission looks good and will be added to leaderboard
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="reject" id="reject" />
                <Label htmlFor="reject" className="font-normal cursor-pointer">
                  Reject - Submission has issues that need to be addressed
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label htmlFor="notes" className="text-base font-semibold mb-2 block">
              Notes {action === "reject" && <span className="text-destructive">*</span>}
            </Label>
            <textarea
              id="notes"
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder={action === "reject" ? "Please provide feedback on why this submission is being rejected..." : "Optional notes for the submitter..."}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => router.push("/moderator")} disabled={submitting}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmitReview}
              disabled={submitting || !action || (action === "reject" && !notes.trim())}
            >
              {submitting ? "Submitting..." : "Submit Review"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
