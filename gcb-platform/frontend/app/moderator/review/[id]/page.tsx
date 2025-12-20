"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface VerdictReview {
  id: string;
  question_id: string;
  question_content: string;
  question_tier: string;
  question_category: string;
  model_response: string;
  judge_verdict: string;
  judge_reasoning: string;
  reviewer_verdict?: "agree" | "disagree" | "unsure";
  reviewer_notes?: string;
}

interface TestRunForReview {
  id: string;
  model_id: string;
  model_name: string;
  version: string;
  overall_score: number;
  tier1_score: number;
  tier2_score: number;
  tier3_score: number;
  verdicts_to_review: VerdictReview[];
}

export default function ModeratorReviewPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const testId = params.id as string;
  
  const [testRun, setTestRun] = useState<TestRunForReview | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [overallAssessment, setOverallAssessment] = useState<string>("");
  const [hasConcerns, setHasConcerns] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && testId) {
      loadReviewData();
    }
  }, [user, userLoading, testId, router]);

  async function loadReviewData() {
    setLoading(true);
    try {
      // In a real implementation, this would call the moderator queue detail API
      const response = await fetch(`/api/moderator/queue/${testId}`);
      if (response.ok) {
        const data = await response.json();
        setTestRun(data);
      } else {
        // Use placeholder data for demo
        setTestRun({
          id: testId,
          model_id: "example-model",
          model_name: "Example Model",
          version: "1.0.0",
          overall_score: 75.5,
          tier1_score: 80.0,
          tier2_score: 70.0,
          tier3_score: 65.0,
          verdicts_to_review: Array.from({ length: 20 }, (_, i) => ({
            id: `verdict-${i}`,
            question_id: `q-${i}`,
            question_content: `Sample question ${i + 1} about Christian doctrine and practice...`,
            question_tier: i < 14 ? "tier1" : i < 18 ? "tier2" : "tier3",
            question_category: ["scripture", "theology", "ethics", "apologetics"][i % 4],
            model_response: `This is the model's response to question ${i + 1}. It provides an answer that may or may not align with Christian doctrine...`,
            judge_verdict: ["ACCEPTED", "COMPROMISED", "REFUSED", "ACCEPTED"][i % 4],
            judge_reasoning: `The judge determined this response to be ${["ACCEPTED", "COMPROMISED", "REFUSED", "ACCEPTED"][i % 4]} because...`,
          })),
        });
      }
    } catch (error) {
      console.error("Failed to load review data:", error);
      toast.error("Failed to load review data");
    } finally {
      setLoading(false);
    }
  }

  function handleVerdictReview(verdict: "agree" | "disagree" | "unsure") {
    if (!testRun) return;
    const updated = { ...testRun };
    updated.verdicts_to_review[currentIndex].reviewer_verdict = verdict;
    setTestRun(updated);
  }

  function handleNotesChange(notes: string) {
    if (!testRun) return;
    const updated = { ...testRun };
    updated.verdicts_to_review[currentIndex].reviewer_notes = notes;
    setTestRun(updated);
  }

  function goToNext() {
    if (!testRun) return;
    if (currentIndex < testRun.verdicts_to_review.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }

  function goToPrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }

  async function handleSubmitReview() {
    if (!testRun) return;

    const reviewedCount = testRun.verdicts_to_review.filter(
      (v) => v.reviewer_verdict
    ).length;

    if (reviewedCount < testRun.verdicts_to_review.length) {
      toast.error("Please review all verdicts before submitting");
      return;
    }

    setSubmitting(true);
    try {
      // Map frontend verdict structure to backend API format
      const verdict_reviews = testRun.verdicts_to_review
        .filter((v) => v.reviewer_verdict) // Only include reviewed verdicts
        .map((v) => ({
          result_id: v.id, // The verdict ID should be the result_id
          verdict: v.reviewer_verdict === "agree" ? "agree" : 
                   v.reviewer_verdict === "disagree" ? "disagree" : "unsure",
          notes: v.reviewer_notes || undefined,
        }));

      // Map overall assessment - frontend uses different values
      let overall_assessment: "verified" | "concerns" | "escalated" = "verified";
      if (overallAssessment === "concerns" || hasConcerns) {
        overall_assessment = "concerns";
      } else if (overallAssessment === "escalated") {
        overall_assessment = "escalated";
      }

      await apiClient.submitModerationReview({
        test_id: testId,
        verdict_reviews,
        overall_assessment,
        notes: overallAssessment === "concerns" || hasConcerns ? "Reviewer has concerns" : undefined,
      });

      toast.success("Review submitted successfully");
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

  if (!user || !testRun) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Review Not Available</CardTitle>
            <CardDescription>
              This test run is not available for review.
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

  const currentVerdict = testRun.verdicts_to_review[currentIndex];
  const reviewedCount = testRun.verdicts_to_review.filter(
    (v) => v.reviewer_verdict
  ).length;
  const progressPercent = Math.round(
    (reviewedCount / testRun.verdicts_to_review.length) * 100
  );

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/moderator">← Back to Queue</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Review: {testRun.model_name}</h1>
            <p className="text-muted-foreground mt-2">
              Version {testRun.version} • Score: {testRun.overall_score.toFixed(1)}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{reviewedCount}/{testRun.verdicts_to_review.length}</div>
            <div className="text-sm text-muted-foreground">Verdicts Reviewed</div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <Progress value={progressPercent} className="h-2 mb-2" />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Progress: {progressPercent}%</span>
            <span>Verdict {currentIndex + 1} of {testRun.verdicts_to_review.length}</span>
          </div>
        </CardContent>
      </Card>

      {/* Main Review Interface */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: Question and Response */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{currentVerdict.question_tier}</Badge>
                  <Badge variant="secondary">{currentVerdict.question_category}</Badge>
                </div>
                <Badge
                  variant={
                    currentVerdict.judge_verdict === "ACCEPTED"
                      ? "default"
                      : currentVerdict.judge_verdict === "REFUSED"
                      ? "destructive"
                      : "outline"
                  }
                >
                  Judge: {currentVerdict.judge_verdict}
                </Badge>
              </div>
              <CardTitle className="text-lg mt-4">Question</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{currentVerdict.question_content}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Model Response</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{currentVerdict.model_response}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Judge Reasoning</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{currentVerdict.judge_reasoning}</p>
            </CardContent>
          </Card>
        </div>

        {/* Right: Review Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Assessment</CardTitle>
              <CardDescription>
                Do you agree with the judge&apos;s verdict?
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <RadioGroup
                value={currentVerdict.reviewer_verdict || ""}
                onValueChange={(value) =>
                  handleVerdictReview(value as "agree" | "disagree" | "unsure")
                }
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="agree" id="agree" />
                  <Label htmlFor="agree" className="font-normal cursor-pointer">
                    Agree with verdict
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="disagree" id="disagree" />
                  <Label htmlFor="disagree" className="font-normal cursor-pointer">
                    Disagree with verdict
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="unsure" id="unsure" />
                  <Label htmlFor="unsure" className="font-normal cursor-pointer">
                    Unsure / Need discussion
                  </Label>
                </div>
              </RadioGroup>

              <div>
                <Label htmlFor="notes">Notes (Optional)</Label>
                <Input
                  id="notes"
                  placeholder="Add notes about this verdict..."
                  value={currentVerdict.reviewer_notes || ""}
                  onChange={(e) => handleNotesChange(e.target.value)}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={goToPrevious}
                  disabled={currentIndex === 0}
                >
                  ← Previous
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={goToNext}
                  disabled={currentIndex >= testRun.verdicts_to_review.length - 1}
                >
                  Next →
                </Button>
              </div>

              {/* Quick Navigation */}
              <div className="mt-4">
                <Label className="text-xs text-muted-foreground">Quick Jump</Label>
                <div className="flex flex-wrap gap-1 mt-2">
                  {testRun.verdicts_to_review.map((v, i) => (
                    <Button
                      key={v.id}
                      variant={i === currentIndex ? "default" : v.reviewer_verdict ? "secondary" : "outline"}
                      size="sm"
                      className="w-8 h-8 p-0"
                      onClick={() => setCurrentIndex(i)}
                    >
                      {i + 1}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit Section */}
          {reviewedCount === testRun.verdicts_to_review.length && (
            <Card className="border-[--ga-red]">
              <CardHeader>
                <CardTitle>Submit Review</CardTitle>
                <CardDescription>
                  All verdicts reviewed. Ready to submit.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="overall">Overall Assessment</Label>
                  <Input
                    id="overall"
                    placeholder="Overall thoughts on this test run..."
                    value={overallAssessment}
                    onChange={(e) => setOverallAssessment(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="concerns"
                    checked={hasConcerns}
                    onChange={(e) => setHasConcerns(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="concerns" className="font-normal cursor-pointer">
                    Flag for committee review (has concerns)
                  </Label>
                </div>
                <Button
                  variant="brand"
                  className="w-full"
                  onClick={handleSubmitReview}
                  disabled={submitting}
                >
                  {submitting ? "Submitting..." : "Submit Review"}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
