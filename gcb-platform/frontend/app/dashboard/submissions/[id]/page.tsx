"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

interface SubmissionDetail {
  id: string;
  model_name: string;
  status: string;
  cli_version: string;
  question_set_version: string;
  overall_score: number;
  tier1_score: number;
  tier2_score: number;
  tier3_score: number;
  total_questions: number;
  verdict_counts: Record<string, number>;
  submitted_at: string | null;
  reviewed_at: string | null;
  reviewer_notes: string | null;
  judge_model: string | null;
  backend: string | null;
  completed_at: string | null;
  responses: Array<{
    question_id: string;
    tier: number;
    category: string;
    response: string;
    verdict: string;
    verdict_normalized?: string;
    judge_reasoning?: string;
    response_time_ms?: number;
  }>;
  fee_waived: boolean;
}

export default function SubmissionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const submissionId = params.id as string;
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [verdictFilter, setVerdictFilter] = useState<string>("all");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [expandedResponse, setExpandedResponse] = useState<string | null>(null);

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
      const data = await apiClient.getUserSubmissionDetail(submissionId);
      setSubmission(data);
    } catch (error) {
      console.error("Failed to load submission data:", error);
      toast.error("Failed to load submission details");
    } finally {
      setLoading(false);
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

  if (!submission) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Submission Not Found</CardTitle>
            <CardDescription>
              This submission could not be found or you don&apos;t have access to it.
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

  const filteredResponses = submission.responses.filter((response) => {
    if (verdictFilter !== "all" && response.verdict !== verdictFilter) return false;
    if (tierFilter !== "all" && response.tier !== parseInt(tierFilter)) return false;
    return true;
  });

  const verdictCounts = submission.verdict_counts || {};

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/dashboard">← Back to Dashboard</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">{submission.model_name}</h1>
            <div className="mt-2 flex items-center gap-4">
              <Badge variant="secondary">v{submission.question_set_version}</Badge>
              <Badge
                variant={
                  submission.status === "approved"
                    ? "default"
                    : submission.status === "rejected"
                    ? "destructive"
                    : "outline"
                }
              >
                {submission.status}
              </Badge>
              {submission.fee_waived && (
                <Badge variant="outline" className="text-green-600 border-green-600">
                  Fee Waived
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

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
              {submission.overall_score?.toFixed(1) || "—"}
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
              {submission.tier1_score?.toFixed(1) || "—"}
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
              {submission.tier2_score?.toFixed(1) || "—"}
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
              {submission.tier3_score?.toFixed(1) || "—"}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="verdicts">Verdicts</TabsTrigger>
          <TabsTrigger value="responses">All Responses</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Submission Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">Model:</span>
                  <p className="text-muted-foreground">{submission.model_name}</p>
                </div>
                <div>
                  <span className="font-medium">Benchmark Version:</span>
                  <p className="text-muted-foreground">{submission.question_set_version}</p>
                </div>
                <div>
                  <span className="font-medium">CLI Version:</span>
                  <p className="text-muted-foreground">{submission.cli_version}</p>
                </div>
                <div>
                  <span className="font-medium">Backend:</span>
                  <p className="text-muted-foreground">{submission.backend || "—"}</p>
                </div>
                <div>
                  <span className="font-medium">Judge Model:</span>
                  <p className="text-muted-foreground">{submission.judge_model || "—"}</p>
                </div>
                <div>
                  <span className="font-medium">Total Questions:</span>
                  <p className="text-muted-foreground">{submission.total_questions}</p>
                </div>
                <div>
                  <span className="font-medium">Submitted:</span>
                  <p className="text-muted-foreground">
                    {submission.submitted_at
                      ? new Date(submission.submitted_at).toLocaleString()
                      : "—"}
                  </p>
                </div>
                <div>
                  <span className="font-medium">Test Completed:</span>
                  <p className="text-muted-foreground">
                    {submission.completed_at
                      ? new Date(submission.completed_at).toLocaleString()
                      : "—"}
                  </p>
                </div>
              </div>
              {submission.reviewer_notes && (
                <div className="mt-4 p-4 bg-muted rounded">
                  <span className="font-medium">Reviewer Notes:</span>
                  <p className="text-muted-foreground mt-1">{submission.reviewer_notes}</p>
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
                <div className="grid grid-cols-3 gap-4">
                  {["ACCEPTED", "COMPROMISED", "REFUSED"].map((verdict) => (
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
                    { verdict: "REFUSED", points: 0.0 },
                  ].map(({ verdict, points }) => {
                    const count = verdictCounts[verdict] || 0;
                    const total = submission.total_questions || 1;
                    const percent = ((count / total) * 100).toFixed(1);
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
                      <SelectItem value="REFUSED">Refused</SelectItem>
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
                      <SelectItem value="1">Tier 1</SelectItem>
                      <SelectItem value="2">Tier 2</SelectItem>
                      <SelectItem value="3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredResponses.length > 0 ? (
                <div className="space-y-4">
                  {filteredResponses.map((response, index) => (
                    <Card
                      key={response.question_id || index}
                      className="cursor-pointer"
                      onClick={() =>
                        setExpandedResponse(
                          expandedResponse === response.question_id ? null : response.question_id
                        )
                      }
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">Tier {response.tier}</Badge>
                            <Badge variant="secondary">{response.category}</Badge>
                            {response.response_time_ms && (
                              <span className="text-xs text-muted-foreground">
                                {(response.response_time_ms / 1000).toFixed(1)}s
                              </span>
                            )}
                          </div>
                          <Badge
                            variant="outline"
                            className={
                              response.verdict === "ACCEPTED"
                                ? "bg-green-500/20 text-green-400 border-green-500/30"
                                : response.verdict === "REFUSED"
                                ? "bg-red-500/20 text-red-400 border-red-500/30"
                                : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                            }
                          >
                            {response.verdict}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-2">
                          {response.response?.substring(0, 200)}
                          {(response.response?.length || 0) > 200 ? "..." : ""}
                        </p>
                        {expandedResponse === response.question_id && (
                          <div className="mt-4 space-y-4 border-t pt-4">
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">
                                Full Response
                              </div>
                              <p className="text-sm bg-muted p-2 rounded whitespace-pre-wrap">
                                {response.response || "No response"}
                              </p>
                            </div>
                            {response.judge_reasoning && (
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">
                                  Judge Reasoning
                                </div>
                                <p className="text-sm text-muted-foreground">
                                  {response.judge_reasoning}
                                </p>
                              </div>
                            )}
                            {response.thought_process && (
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">
                                  Thought Process
                                </div>
                                <p className="text-sm bg-muted p-2 rounded whitespace-pre-wrap">
                                  {response.thought_process}
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

