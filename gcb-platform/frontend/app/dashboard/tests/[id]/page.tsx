"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
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
import { apiClient, TestRun as ApiTestRun, TestResult as ApiTestResult } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChart } from "@/components/charts/CategoryChart";
import { toast } from "sonner";

// Extend API types with required fields for local use
type TestRun = ApiTestRun;
type TestResult = ApiTestResult;

export default function TestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const testId = params.id as string;
  const [test, setTest] = useState<TestRun | null>(null);
  const [results, setResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [verdictFilter, setVerdictFilter] = useState<string>("all");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [expandedResult, setExpandedResult] = useState<string | null>(null);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && testId) {
      loadTestData();
    }
  }, [user, userLoading, testId, router]);

  async function loadTestData() {
    setLoading(true);
    try {
      const [testData, resultsData] = await Promise.all([
        apiClient.getTest(testId),
        apiClient.getTestResults(testId).catch(() => []),
      ]);
      setTest(testData);
      setResults(resultsData || []);
    } catch (error) {
      console.error("Failed to load test data:", error);
      toast.error("Failed to load test details");
    } finally {
      setLoading(false);
    }
  }

  async function handleRetest() {
    try {
      // In a real implementation, this would call the retest API
      toast.success("Retest initiated");
      router.push("/tests/new");
    } catch (error) {
      toast.error("Failed to initiate retest");
    }
  }

  async function handleCancel() {
    try {
      await apiClient.cancelTest(testId);
      toast.success("Test cancelled");
      loadTestData();
    } catch (error) {
      toast.error("Failed to cancel test");
    }
  }

  if (userLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (!test) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Test Not Found</CardTitle>
            <CardDescription>
              This test could not be found or you don&apos;t have access to it.
            </CardDescription>
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

  const isRunning = test.status === "running";
  const isCompleted = test.status === "completed";
  const totalQuestions = test.total_questions || 0;
  const completedQuestions = test.completed_questions || 0;
  const progressPercent = totalQuestions > 0
    ? Math.round((completedQuestions / totalQuestions) * 100)
    : 0;

  const filteredResults = results.filter((result) => {
    if (verdictFilter !== "all" && result.verdict !== verdictFilter) return false;
    if (tierFilter !== "all" && result.question_tier !== tierFilter) return false;
    return true;
  });

  const verdictCounts = results.reduce((acc, r) => {
    acc[r.verdict] = (acc[r.verdict] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/dashboard">← Back to Dashboard</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">{test.model_name}</h1>
            <div className="mt-2 flex items-center gap-4">
              <Badge variant="secondary">{test.version}</Badge>
              <Badge
                variant={
                  test.status === "completed"
                    ? "default"
                    : test.status === "running"
                    ? "outline"
                    : "destructive"
                }
              >
                {test.status}
              </Badge>
            </div>
          </div>
          <div className="flex gap-2">
            {isRunning && (
              <Button variant="destructive" onClick={handleCancel}>
                Cancel Test
              </Button>
            )}
            {isCompleted && (
              <>
                <Button variant="outline" onClick={handleRetest}>
                  Run Again
                </Button>
                <Button asChild variant="brand">
                  <Link href={`/research/models/${test.model_id}`}>
                    View on Leaderboard
                  </Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Progress for running tests */}
      {isRunning && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Test Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={progressPercent} className="h-4 mb-2" />
            <p className="text-sm text-muted-foreground">
              {completedQuestions} of {totalQuestions} questions completed ({progressPercent}%)
            </p>
          </CardContent>
        </Card>
      )}

      {/* Score Overview */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Overall Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[--ga-red]">
              {test.overall_score?.toFixed(1) || "—"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 1 (Task)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {test.tier1_score?.toFixed(1) || "—"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 2 (Doctrine)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {test.tier2_score?.toFixed(1) || "—"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 3 (Worldview)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {test.tier3_score?.toFixed(1) || "—"}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="verdicts">Verdicts</TabsTrigger>
          <TabsTrigger value="responses">All Responses</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Test Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">Model ID:</span>
                  <p className="text-muted-foreground">{test.model_id}</p>
                </div>
                <div>
                  <span className="font-medium">Benchmark Version:</span>
                  <p className="text-muted-foreground">{test.version}</p>
                </div>
                <div>
                  <span className="font-medium">Created:</span>
                  <p className="text-muted-foreground">
                    {new Date(test.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <span className="font-medium">Completed:</span>
                  <p className="text-muted-foreground">
                    {test.completed_at
                      ? new Date(test.completed_at).toLocaleString()
                      : "—"}
                  </p>
                </div>
              </div>
              {test.system_prompt && (
                <div>
                  <span className="font-medium">System Prompt:</span>
                  <p className="text-muted-foreground mt-1 p-2 bg-muted rounded text-sm">
                    {test.system_prompt}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Verdict Distribution */}
          {Object.keys(verdictCounts).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Verdict Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-4">
                  {["ACCEPTED", "COMPROMISED", "HEDGED", "REFUSED", "ERROR"].map((verdict) => (
                    <div key={verdict} className="text-center">
                      <div className="text-2xl font-bold">
                        {verdictCounts[verdict] || 0}
                      </div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {verdict.toLowerCase()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="categories">
          <Card>
            <CardHeader>
              <CardTitle>Category Breakdown</CardTitle>
              <CardDescription>
                Performance across different categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              {test.category_scores && Object.keys(test.category_scores).length > 0 ? (
                <CategoryChart data={test.category_scores} />
              ) : (
                <p className="text-muted-foreground">No category data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="verdicts">
          <Card>
            <CardHeader>
              <CardTitle>Verdict Summary</CardTitle>
              <CardDescription>
                Breakdown of how the model responded
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Verdict</TableHead>
                    <TableHead>Count</TableHead>
                    <TableHead>Percentage</TableHead>
                    <TableHead>Points</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    { verdict: "ACCEPTED", points: 1.0 },
                    { verdict: "COMPROMISED", points: 0.5 },
                    { verdict: "HEDGED", points: 0.3 },
                    { verdict: "REFUSED", points: 0.0 },
                    { verdict: "ERROR", points: 0.0 },
                  ].map(({ verdict, points }) => {
                    const count = verdictCounts[verdict] || 0;
                    const percent = results.length > 0
                      ? ((count / results.length) * 100).toFixed(1)
                      : "0.0";
                    return (
                      <TableRow key={verdict}>
                        <TableCell className="font-medium">{verdict}</TableCell>
                        <TableCell>{count}</TableCell>
                        <TableCell>{percent}%</TableCell>
                        <TableCell>{points.toFixed(1)}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="responses">
          <Card>
            <CardHeader>
              <CardTitle>Individual Responses</CardTitle>
              <CardDescription>
                Browse all question responses and verdicts
              </CardDescription>
              <div className="flex gap-4 mt-4">
                <div className="w-40">
                  <Select value={verdictFilter} onValueChange={setVerdictFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by verdict" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Verdicts</SelectItem>
                      <SelectItem value="ACCEPTED">Accepted</SelectItem>
                      <SelectItem value="COMPROMISED">Compromised</SelectItem>
                      <SelectItem value="HEDGED">Hedged</SelectItem>
                      <SelectItem value="REFUSED">Refused</SelectItem>
                      <SelectItem value="ERROR">Error</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="w-40">
                  <Select value={tierFilter} onValueChange={setTierFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by tier" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Tiers</SelectItem>
                      <SelectItem value="tier1">Tier 1</SelectItem>
                      <SelectItem value="tier2">Tier 2</SelectItem>
                      <SelectItem value="tier3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredResults.length > 0 ? (
                <div className="space-y-4">
                  {filteredResults.map((result, index) => (
                    <Card
                      key={result.id || index}
                      className="cursor-pointer"
                      onClick={() =>
                        setExpandedResult(
                          expandedResult === result.id ? null : result.id
                        )
                      }
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{result.question_tier}</Badge>
                            <Badge variant="secondary">{result.question_category}</Badge>
                          </div>
                          <Badge
                            variant={
                              result.verdict === "ACCEPTED"
                                ? "default"
                                : result.verdict === "REFUSED"
                                ? "destructive"
                                : "outline"
                            }
                          >
                            {result.verdict}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm font-medium mb-2">
                          {result.question_content?.substring(0, 200)}
                          {(result.question_content?.length || 0) > 200 ? "..." : ""}
                        </p>
                        {expandedResult === result.id && (
                          <div className="mt-4 space-y-4 border-t pt-4">
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">
                                Full Question
                              </div>
                              <p className="text-sm">{result.question_content}</p>
                            </div>
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">
                                Model Response
                              </div>
                              <p className="text-sm bg-muted p-2 rounded">
                                {result.response || "No response"}
                              </p>
                            </div>
                            {result.reasoning && (
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">
                                  Judge Reasoning
                                </div>
                                <p className="text-sm text-muted-foreground">
                                  {result.reasoning}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  No responses match the current filters
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
