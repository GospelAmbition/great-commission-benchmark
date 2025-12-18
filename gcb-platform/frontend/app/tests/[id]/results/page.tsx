"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChart } from "@/components/charts/CategoryChart";

export default function ResultsPage() {
  const params = useParams();
  const testId = params.id as string;
  const [test, setTest] = useState<any>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (testId) {
      loadResults();
    }
  }, [testId]);

  async function loadResults() {
    setLoading(true);
    try {
      const [testData, resultsData] = await Promise.all([
        apiClient.getTest(testId),
        apiClient.getTestResults(testId).catch(() => []),
      ]);
      setTest(testData);
      setResults(resultsData || []);
    } catch (error) {
      console.error("Failed to load results:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!test) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Results Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/dashboard">Back to Dashboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/dashboard">← Back to Dashboard</Link>
        </Button>
        <div className="text-center">
          <h1 className="text-4xl font-bold">Test Results</h1>
          <p className="mt-2 text-muted-foreground">
            {test.model_name} • {test.version}
          </p>
        </div>
      </div>

      {/* Score Announcement */}
      <Card className="mb-8 bg-[--ga-accent-red] border-[--ga-light-red]">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="text-sm text-muted-foreground mb-2">Overall Score</div>
            <div className="text-6xl font-bold text-[--ga-red] mb-4">
              {test.overall_score?.toFixed(1) || "—"}
            </div>
            <div className="flex items-center justify-center gap-6 text-sm">
              <div>
                <div className="text-muted-foreground">Tier 1</div>
                <div className="font-semibold">{test.tier1_score?.toFixed(1) || "—"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Tier 2</div>
                <div className="font-semibold">{test.tier2_score?.toFixed(1) || "—"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Tier 3</div>
                <div className="font-semibold">{test.tier3_score?.toFixed(1) || "—"}</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="responses">Responses</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Test Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="font-medium">Model:</span> {test.model_name}
              </div>
              <div>
                <span className="font-medium">Version:</span> {test.version}
              </div>
              <div>
                <span className="font-medium">Status:</span>{" "}
                <Badge variant="outline">{test.status}</Badge>
              </div>
              <div>
                <span className="font-medium">Completed:</span>{" "}
                {new Date(test.completed_at || test.created_at).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories">
          <Card>
            <CardHeader>
              <CardTitle>Category Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              {test.category_scores ? (
                <CategoryChart data={test.category_scores} />
              ) : (
                <p className="text-muted-foreground">No category data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="responses">
          <Card>
            <CardHeader>
              <CardTitle>Question Responses</CardTitle>
              <CardDescription>
                Review individual question responses and verdicts
              </CardDescription>
            </CardHeader>
            <CardContent>
              {results.length > 0 ? (
                <div className="space-y-4">
                  {results.map((result, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-sm">
                          Question {index + 1}: {result.question_category || "Unknown"}
                        </CardTitle>
                        <Badge variant="outline">{result.verdict}</Badge>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div>
                          <div className="text-xs text-muted-foreground mb-1">Question</div>
                          <p className="text-sm">{result.question_content || "N/A"}</p>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground mb-1">Response</div>
                          <p className="text-sm">{result.response || "N/A"}</p>
                        </div>
                        {result.reasoning && (
                          <div>
                            <div className="text-xs text-muted-foreground mb-1">Reasoning</div>
                            <p className="text-sm">{result.reasoning}</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No response data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="mt-8 flex gap-4 justify-center">
        <Button asChild variant="outline">
          <Link href="/tests/new">Run Another Test</Link>
        </Button>
        <Button asChild className="bg-[--ga-red] hover:bg-[--ga-dark-red]">
          <Link href="/research">View Leaderboard</Link>
        </Button>
      </div>
    </div>
  );
}
