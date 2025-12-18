"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProcessingPage() {
  const params = useParams();
  const router = useRouter();
  const testId = params.id as string;
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (testId) {
      const interval = setInterval(() => {
        loadProgress();
      }, 2000); // Poll every 2 seconds

      loadProgress();

      return () => clearInterval(interval);
    }
  }, [testId]);

  async function loadProgress() {
    try {
      const progressData = await apiClient.getTestProgress(testId);
      setProgress(progressData);
      setLoading(false);

      // If test is complete, redirect to results
      if (progressData.status === "completed") {
        setPolling(false);
        router.push(`/tests/${testId}/results`);
      }
    } catch (error) {
      console.error("Failed to load progress:", error);
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8 max-w-3xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  const completed = progress?.completed_questions || 0;
  const total = progress?.total_questions || 100;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const estimatedTimeRemaining = progress?.estimated_time_remaining_minutes || 0;

  return (
    <div className="container py-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Test Processing</h1>
        <p className="mt-2 text-muted-foreground">
          Your benchmark test is running. This may take a few minutes.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Progress</CardTitle>
          <CardDescription>
            Question {completed} of {total}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Progress value={percentage} className="h-4" />
            <div className="mt-2 flex justify-between text-sm text-muted-foreground">
              <span>{percentage}% complete</span>
              {estimatedTimeRemaining > 0 && (
                <span>~{estimatedTimeRemaining} minutes remaining</span>
              )}
            </div>
          </div>

          {progress?.current_tier && (
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Current Tier</div>
              <div className="font-semibold capitalize">{progress.current_tier}</div>
              {progress.current_category && (
                <>
                  <div className="text-sm text-muted-foreground mt-2 mb-1">Current Category</div>
                  <div className="font-semibold capitalize">{progress.current_category}</div>
                </>
              )}
            </div>
          )}

          <div className="bg-[--ga-accent-red] p-4 rounded-lg border border-[--ga-light-red]">
            <p className="text-sm">
              <strong>Note:</strong> You can safely navigate away from this page. We'll notify you
              when your test is complete, or you can check back later from your dashboard.
            </p>
          </div>

          <div className="flex gap-4">
            <Button asChild variant="outline">
              <a href="/dashboard">Go to Dashboard</a>
            </Button>
            <Button asChild variant="outline">
              <a href="/research">Browse Leaderboard</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
