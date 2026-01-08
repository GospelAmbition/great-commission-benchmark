"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { TestProgressIndicator } from "@/components/test-flow";
import { 
  Loader2, 
  ChevronDown, 
  ChevronUp,
  Info,
  AlertTriangle,
  RefreshCw,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface LogEntry {
  timestamp: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
}

export default function ProcessingPage() {
  const params = useParams();
  const router = useRouter();
  const testId = params.id as string;
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [logExpanded, setLogExpanded] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (testId) {
      // Initial load
      loadProgress();
      
      // Start polling
      const interval = setInterval(() => {
        loadProgress();
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [testId]);

  // Auto-scroll log to bottom when new entries are added
  useEffect(() => {
    if (logExpanded && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, logExpanded]);

  async function loadProgress() {
    try {
      const progressData = await apiClient.getTestProgress(testId);
      setProgress(progressData);
      setLoading(false);

      // Update logs based on progress
      updateLogs(progressData);

      // Redirect to results if complete
      if (progressData.status === "completed") {
        router.push(`/tests/${testId}/results`);
      }
    } catch (error) {
      console.error("Failed to load progress:", error);
      setLoading(false);
    }
  }

  function updateLogs(progressData: any) {
    const newLogs: LogEntry[] = [];
    const now = new Date();
    
    // Add initial log if we're just starting
    if (progressData.started_at) {
      const startTime = new Date(progressData.started_at);
      newLogs.push({
        timestamp: startTime.toLocaleTimeString(),
        message: "Test initiated",
        type: "info"
      });
      
      newLogs.push({
        timestamp: startTime.toLocaleTimeString(),
        message: `Connected to model: ${progressData.model_name || "Unknown"}`,
        type: "info"
      });
    }

    // Add tier progress
    if (progressData.current_tier) {
      const tierMessages: Record<string, string> = {
        "tier1": "Starting Tier 1: Task Capability (210 questions)",
        "tier2": "Starting Tier 2: Gospel Core (60 questions)",
        "tier3": "Starting Tier 3: Worldview Confession (30 questions)",
      };
      
      if (tierMessages[progressData.current_tier]) {
        newLogs.push({
          timestamp: now.toLocaleTimeString(),
          message: tierMessages[progressData.current_tier],
          type: "info"
        });
      }
    }

    // Add current question progress
    if (progressData.completed_questions > 0) {
      newLogs.push({
        timestamp: now.toLocaleTimeString(),
        message: `Processing question ${progressData.completed_questions} of ${progressData.total_questions}...`,
        type: "info"
      });
    }

    // Handle retry/recovery state
    if (progressData.status === "retrying") {
      newLogs.push({
        timestamp: now.toLocaleTimeString(),
        message: "Briefly paused — reconnecting to API...",
        type: "warning"
      });
    }

    // Only update logs if we have new entries to prevent constant re-renders
    if (newLogs.length > 0) {
      setLogs(prevLogs => {
        // Deduplicate by keeping only unique messages (simple approach)
        const existingMessages = new Set(prevLogs.map(l => l.message));
        const uniqueNewLogs = newLogs.filter(l => !existingMessages.has(l.message));
        
        if (uniqueNewLogs.length === 0) return prevLogs;
        return [...prevLogs, ...uniqueNewLogs].slice(-50); // Keep last 50 entries
      });
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8 mx-auto" />
        <Skeleton className="h-[400px] max-w-2xl mx-auto" />
      </div>
    );
  }

  const completed = progress?.completed_questions || 0;
  const total = progress?.total_questions || 300;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const estimatedTimeRemaining = progress?.estimated_time_remaining_minutes || 0;
  const isRetrying = progress?.status === "retrying";
  const isAwaitingAdmin = progress?.status === "awaiting_admin";

  // Calculate elapsed time
  const startedAt = progress?.started_at ? new Date(progress.started_at) : null;
  const elapsedMinutes = startedAt 
    ? Math.round((Date.now() - startedAt.getTime()) / 60000) 
    : 0;

  return (
    <div className="container py-8">
      {/* Progress Indicator */}
      <div className="max-w-4xl mx-auto">
        <TestProgressIndicator currentStep="processing" />
      </div>

      {/* Main content - centered */}
      <div className="max-w-2xl mx-auto">
        {/* Spinner and heading */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-[var(--ga-accent-red)] mb-6">
            {isRetrying ? (
              <RefreshCw className="h-10 w-10 text-[var(--ga-red)] animate-spin" />
            ) : (
              <Loader2 className="h-10 w-10 text-[var(--ga-red)] animate-spin" />
            )}
          </div>
          
          <h1 className="text-4xl font-bold mb-2">
            {isRetrying ? "Reconnecting..." : isAwaitingAdmin ? "Awaiting Admin" : "Your Test is Running"}
          </h1>
          
          <p className="text-lg text-muted-foreground">
            {progress?.model_name || "Model"} · {progress?.version || "Current Version"}
          </p>
        </div>

        {/* Progress bar */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <Progress value={percentage} className="h-4" />
              
              <div className="flex justify-between text-sm">
                <span className="font-medium">{percentage}% complete</span>
                <span className="text-muted-foreground">
                  {completed} of {total} questions
                </span>
              </div>

              {/* Time info */}
              <div className="flex justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>Started: {elapsedMinutes} minute{elapsedMinutes !== 1 ? "s" : ""} ago</span>
                </div>
                {estimatedTimeRemaining > 0 && (
                  <span>Est. completion: ~{estimatedTimeRemaining} more minute{estimatedTimeRemaining !== 1 ? "s" : ""}</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recovery/retry notice */}
        {isRetrying && (
          <Card className="mb-6 border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <RefreshCw className="h-5 w-5 text-amber-600 mt-0.5 animate-spin" />
                <div>
                  <p className="font-medium text-amber-900 dark:text-amber-100">
                    Briefly paused — reconnecting to API...
                  </p>
                  <p className="text-sm text-amber-800 dark:text-amber-200 mt-1">
                    The test will automatically resume. No action needed.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Awaiting admin notice */}
        {isAwaitingAdmin && (
          <Card className="mb-6 border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
                <div>
                  <p className="font-medium">Test Requires Attention</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    The test encountered persistent errors. An administrator has been notified.
                    You can wait for admin completion or request a refund.
                  </p>
                  <div className="flex gap-3 mt-4">
                    <Button variant="outline" size="sm">
                      Request Refund
                    </Button>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href="/dashboard">Go to Dashboard</Link>
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Current tier/category info */}
        {progress?.current_tier && !isAwaitingAdmin && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Current Tier</div>
                  <div className="font-semibold flex items-center gap-2">
                    <Badge variant="outline">{progress.current_tier}</Badge>
                    <span className="capitalize">
                      {progress.current_tier === "tier1" && "Task Capability"}
                      {progress.current_tier === "tier2" && "Gospel Core"}
                      {progress.current_tier === "tier3" && "Worldview Confession"}
                    </span>
                  </div>
                </div>
                {progress.current_category && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Current Category</div>
                    <div className="font-semibold capitalize">{progress.current_category}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Safe to leave notice */}
        {!isAwaitingAdmin && (
          <Card className="mb-6 bg-[var(--ga-accent-red)] border-[var(--ga-light-red)]">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-[var(--ga-red)] mt-0.5" />
                <div>
                  <p className="font-medium">You can safely leave this page</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    We'll send you an email when your results are ready.
                    You can also check your Dashboard for updates.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action buttons */}
        <div className="flex gap-4 justify-center mb-8">
          <Button asChild variant="outline">
            <Link href="/dashboard">Go to Dashboard</Link>
          </Button>
          <Button variant="secondary" disabled>
            Stay on This Page
          </Button>
        </div>

        {/* Processing Log (collapsible) */}
        <Card>
          <CardHeader 
            className="cursor-pointer select-none"
            onClick={() => setLogExpanded(!logExpanded)}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Processing Log</CardTitle>
              <Button variant="ghost" size="sm">
                {logExpanded ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardHeader>
          
          {logExpanded && (
            <CardContent>
              <div className="bg-muted rounded-lg p-4 font-mono text-sm max-h-[300px] overflow-y-auto">
                {logs.length === 0 ? (
                  <p className="text-muted-foreground">Waiting for log entries...</p>
                ) : (
                  <div className="space-y-1">
                    {logs.map((log, index) => (
                      <div 
                        key={index} 
                        className={cn(
                          "flex gap-3",
                          log.type === "warning" && "text-amber-600 dark:text-amber-400",
                          log.type === "error" && "text-destructive",
                          log.type === "success" && "text-green-600 dark:text-green-400"
                        )}
                      >
                        <span className="text-muted-foreground shrink-0">{log.timestamp}</span>
                        <span>{log.message}</span>
                      </div>
                    ))}
                    <div ref={logEndRef} />
                  </div>
                )}
                {/* Blinking cursor */}
                <span className="inline-block w-2 h-4 bg-foreground animate-pulse ml-1" />
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
}
