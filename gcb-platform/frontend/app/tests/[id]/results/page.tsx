"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChart } from "@/components/charts/CategoryChart";
import { TestProgressIndicator, ShareModal } from "@/components/test-flow";
import { 
  CheckCircle2, 
  Share2, 
  Trophy, 
  ArrowRight,
  Medal,
  Sparkles,
  ExternalLink
} from "lucide-react";
import { BenchmarkHelpIcon } from "@/components/benchmark";
import { cn } from "@/lib/utils";

// Tier bar component
function TierBar({ 
  name, 
  weight, 
  score,
  className 
}: { 
  name: string; 
  weight: string;
  score: number | null;
  className?: string;
}) {
  const displayScore = score ?? 0;
  const barColor = displayScore >= 80 
    ? "bg-[var(--ga-red)]" 
    : displayScore >= 50 
      ? "bg-amber-500" 
      : "bg-muted-foreground";

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex justify-between text-sm">
        <span className="font-medium">{name} ({weight})</span>
        <span className={cn(
          "font-bold",
          displayScore >= 80 && "text-[var(--ga-red)]",
          displayScore >= 50 && displayScore < 80 && "text-amber-600",
          displayScore < 50 && "text-muted-foreground"
        )}>
          {score !== null ? `${score.toFixed(1)}%` : "—"}
        </span>
      </div>
      <div className="h-3 bg-muted rounded-full overflow-hidden">
        <div 
          className={cn("h-full transition-all duration-1000 ease-out rounded-full", barColor)}
          style={{ width: `${displayScore}%` }}
        />
      </div>
    </div>
  );
}

// Score badge with animation
function ScoreBadge({ score, className }: { score: number | null; className?: string }) {
  const displayScore = score ?? 0;
  
  return (
    <div className={cn(
      "relative inline-flex items-center justify-center",
      className
    )}>
      {/* Animated ring for high scores */}
      {displayScore >= 90 && (
        <div className="absolute inset-0 rounded-full animate-ping bg-[var(--ga-accent-red)] opacity-75" />
      )}
      
      <div className={cn(
        "relative w-32 h-32 rounded-full flex flex-col items-center justify-center",
        "border-4",
        displayScore >= 80 
          ? "bg-[var(--ga-accent-red)] border-[var(--ga-red)]" 
          : displayScore >= 50 
            ? "bg-amber-50 border-amber-400 dark:bg-amber-950/50" 
            : "bg-muted border-muted-foreground/30"
      )}>
        <div className={cn(
          "text-4xl font-bold",
          displayScore >= 80 && "text-[var(--ga-red)]",
          displayScore >= 50 && displayScore < 80 && "text-amber-600",
          displayScore < 50 && "text-muted-foreground"
        )}>
          {score !== null ? score.toFixed(1) : "—"}
        </div>
        <div className="text-sm text-muted-foreground">Overall Score</div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  const params = useParams();
  const testId = params.id as string;
  const [test, setTest] = useState<any>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showShareModal, setShowShareModal] = useState(false);
  const [animateIn, setAnimateIn] = useState(false);

  useEffect(() => {
    if (testId) {
      loadResults();
    }
  }, [testId]);

  // Trigger animation after load
  useEffect(() => {
    if (!loading && test) {
      setTimeout(() => setAnimateIn(true), 100);
    }
  }, [loading, test]);

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
        <Skeleton className="h-12 w-64 mb-8 mx-auto" />
        <Skeleton className="h-[600px] max-w-4xl mx-auto" />
      </div>
    );
  }

  if (!test) {
    return (
      <div className="container py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Results Not Found</CardTitle>
            <CardDescription>
              The test results could not be found or are not yet available.
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

  const overallScore = test.overall_score ?? null;
  const tier1Score = test.tier1_score ?? null;
  const tier2Score = test.tier2_score ?? null;
  const tier3Score = test.tier3_score ?? null;

  return (
    <div className="container py-8">
      <ShareModal
        open={showShareModal}
        onOpenChange={setShowShareModal}
        modelName={test.model_name || "Model"}
        score={overallScore ?? 0}
        testId={testId}
        sponsorName={test.sponsor_name}
      />

      {/* Progress Indicator */}
      <div className="max-w-4xl mx-auto">
        <TestProgressIndicator currentStep="results" />
      </div>

      {/* Main content */}
      <div className="max-w-4xl mx-auto">
        {/* Celebration header */}
        <div className={cn(
          "text-center mb-8 transition-all duration-700 transform",
          animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}>
          {/* Success icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 mb-4">
            <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          
          <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-2">
            <Sparkles className="h-8 w-8 text-[var(--ga-red)]" />
            Test Complete!
            <Sparkles className="h-8 w-8 text-[var(--ga-red)]" />
          </h1>
          
          <p className="text-lg text-muted-foreground">
            {test.model_name} · {test.version || "Current Version"}
          </p>
          
          {test.sponsor_name && (
            <p className="text-sm text-muted-foreground mt-1">
              Sponsored by <span className="font-medium">{test.sponsor_name}</span>
            </p>
          )}
        </div>

        {/* Score announcement card */}
        <Card className={cn(
          "mb-8 bg-gradient-to-br from-[var(--ga-accent-red)] to-white dark:to-background border-[var(--ga-light-red)]",
          "transition-all duration-700 delay-200 transform",
          animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}>
          <CardContent className="pt-8 pb-8">
            <div className="flex flex-col md:flex-row items-center justify-center gap-8">
              {/* Score badge */}
              <ScoreBadge score={overallScore} />

              {/* Tier breakdown */}
              <div className="flex-1 max-w-md w-full space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-lg">Tier Breakdown</h3>
                  <BenchmarkHelpIcon size="default" />
                </div>
                
                <TierBar 
                  name="Tier 1: Task Capability" 
                  weight="70%" 
                  score={tier1Score}
                />
                <TierBar 
                  name="Tier 2: Gospel Core" 
                  weight="20%" 
                  score={tier2Score}
                />
                <TierBar 
                  name="Tier 3: Worldview Confession" 
                  weight="10%" 
                  score={tier3Score}
                />
              </div>
            </div>

            {/* Leaderboard rank */}
            {test.leaderboard_rank && (
              <div className="text-center mt-6 pt-6 border-t">
                <div className="inline-flex items-center gap-2 text-lg">
                  <Medal className="h-5 w-5 text-[var(--ga-red)]" />
                  <span className="font-medium">
                    Rank: #{test.leaderboard_rank} on Leaderboard
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Published notice */}
        <Card className={cn(
          "mb-8 border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20",
          "transition-all duration-700 delay-300 transform",
          animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}>
          <CardContent className="pt-6 pb-6">
            <div className="flex items-center gap-4">
              <div className="shrink-0">
                <Trophy className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 dark:text-green-100">
                  Published!
                </h3>
                <p className="text-sm text-green-800 dark:text-green-200">
                  Your results are now live on the leaderboard. Share your results or run another test.
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => setShowShareModal(true)}
                className="shrink-0"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share Results
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Detailed results tabs */}
        <Tabs defaultValue="overview" className={cn(
          "transition-all duration-700 delay-400 transform",
          animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="categories">Categories</TabsTrigger>
            <TabsTrigger value="responses">Responses</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Test Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Model</div>
                    <div className="font-medium">{test.model_name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Version</div>
                    <div className="font-medium">{test.version || "Current"}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Status</div>
                    <Badge variant="outline" className="mt-1">{test.status}</Badge>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Completed</div>
                    <div className="font-medium">
                      {new Date(test.completed_at || test.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Trust Tier</div>
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "mt-1",
                        test.trust_tier === "validated" && "bg-green-100 text-green-800 border-green-300",
                        test.trust_tier === "reviewed" && "bg-yellow-100 text-yellow-800 border-yellow-300",
                        test.trust_tier === "automated" && "bg-gray-100 text-gray-800 border-gray-300"
                      )}
                    >
                      {test.trust_tier || "automated"}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Questions</div>
                    <div className="font-medium">{results.length || "300"}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="categories" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Category Breakdown</CardTitle>
                  <BenchmarkHelpIcon size="default" />
                </div>
                <CardDescription>
                  Performance across all 19 benchmark categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                {test.category_scores ? (
                  <CategoryChart data={test.category_scores} />
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    No category data available
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="responses" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Question Responses</CardTitle>
                <CardDescription>
                  Review individual question responses and verdicts
                </CardDescription>
              </CardHeader>
              <CardContent>
                {results.length > 0 ? (
                  <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                    {results.map((result, index) => (
                      <Card key={index} className="bg-muted/50">
                        <CardHeader className="pb-2">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-sm">
                              Question {index + 1}
                              {result.question_category && (
                                <span className="text-muted-foreground font-normal ml-2">
                                  · {result.question_category}
                                </span>
                              )}
                            </CardTitle>
                            <Badge 
                              variant="outline"
                              className={cn(
                                result.verdict === "ACCEPTED" && "bg-green-100 text-green-800 border-green-300",
                                result.verdict === "COMPROMISED" && "bg-amber-100 text-amber-800 border-amber-300",
                                result.verdict === "REFUSED" && "bg-red-100 text-red-800 border-red-300"
                              )}
                            >
                              {result.verdict}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {result.question_content && (
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">Question</div>
                              <p className="text-sm">{result.question_content}</p>
                            </div>
                          )}
                          <div>
                            <div className="text-xs text-muted-foreground mb-1">Response</div>
                            <p className="text-sm">{result.response || "N/A"}</p>
                          </div>
                          {result.reasoning && (
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">Reasoning</div>
                              <p className="text-sm text-muted-foreground">{result.reasoning}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    No response data available
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Action buttons */}
        <div className={cn(
          "flex flex-wrap gap-4 justify-center mt-8",
          "transition-all duration-700 delay-500 transform",
          animateIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}>
          <Button asChild variant="outline">
            <Link href="/tests/new">
              Run Another Test
              <ArrowRight className="h-4 w-4 ml-2" />
            </Link>
          </Button>
          <Button asChild variant="brand">
            <Link href="/research">
              View Leaderboard
              <ExternalLink className="h-4 w-4 ml-2" />
            </Link>
          </Button>
          <Button
            variant="secondary"
            onClick={() => setShowShareModal(true)}
          >
            <Share2 className="h-4 w-4 mr-2" />
            Share Results
          </Button>
        </div>
      </div>
    </div>
  );
}
