"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";

interface VersionStats {
  question_set_id: string;
  semantic_version: string;
  marketing_version: string;
  total_questions: number;
  target_total: number;
  tier_stats: {
    [key: number]: {
      count: number;
      target: number;
      categories: {
        [key: string]: {
          count: number;
          target: number;
        };
      };
    };
  };
}

interface VersionInfo {
  id: string;
  semantic_version: string;
  marketing_version: string;
  status: "draft" | "locked" | "active" | "archived";
  created_at: string;
  published_at?: string;
  is_current?: boolean;
}

export default function VersionDetailPage({
  params,
}: {
  params: Promise<{ version: string }>;
}) {
  const resolvedParams = use(params);
  const version = resolvedParams.version;
  
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null);
  const [versionStats, setVersionStats] = useState<VersionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPublishDialog, setShowPublishDialog] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [locking, setLocking] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && version) {
      loadVersionData();
    }
  }, [user, userLoading, router, version]);

  async function loadVersionData() {
    setLoading(true);
    try {
      // Load version info from question-sets
      const versionsResponse = await fetch("/api/admin/question-sets");
      if (versionsResponse.ok) {
        const data = await versionsResponse.json();
        const versionData = data.items?.find(
          (qs: { semantic_version: string }) => qs.semantic_version === version
        );
        if (versionData) {
          setVersionInfo({
            id: versionData.id,
            semantic_version: versionData.semantic_version,
            marketing_version: versionData.marketing_version,
            status: versionData.status,
            created_at: versionData.created_at,
            published_at: versionData.published_at,
            is_current: versionData.status === "active",
          });
        }
      }

      // Load version stats
      const statsResponse = await fetch(`/api/admin/versions/${version}/stats`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setVersionStats(statsData);
      }
    } catch (error) {
      console.error("Failed to load version data:", error);
      toast.error("Failed to load version data");
    } finally {
      setLoading(false);
    }
  }

  async function handleLockVersion() {
    setLocking(true);
    try {
      const response = await fetch(`/api/admin/versions/${version}/lock`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success(`Version ${version} locked`);
        loadVersionData();
      } else {
        throw new Error("Failed to lock");
      }
    } catch (error) {
      console.error("Failed to lock version:", error);
      toast.error("Failed to lock version");
    } finally {
      setLocking(false);
    }
  }

  async function handlePublishVersion() {
    setPublishing(true);
    try {
      const response = await fetch(`/api/admin/versions/${version}/publish`, {
        method: "PUT",
      });

      if (response.ok) {
        toast.success(`Version ${version} published`);
        setShowPublishDialog(false);
        loadVersionData();
      } else {
        throw new Error("Failed to publish");
      }
    } catch (error) {
      console.error("Failed to publish version:", error);
      toast.error("Failed to publish version");
    } finally {
      setPublishing(false);
    }
  }

  const getCategoryName = (category: string) => {
    const categoryMap: Record<string, string> = {
      "3.1": "Missiological Research",
      "3.2": "Evangelistic Material",
      "3.3": "Apologetics",
      "3.4": "Conversational AI",
      "3.5": "Intercessory Prayer",
      "3.6": "Problematic Vocabulary",
      "3.7": "Difficult Passages",
      "4.1": "Exclusivity of Jesus",
      "4.2": "Universality of Sin",
      "4.3": "Reality of Judgment",
      "4.4": "Lordship of Jesus",
      "4.5": "Call to Repentance",
      "4.6": "Burden to Make Disciples",
      "5.1": "Existence of God",
      "5.2": "Historical Jesus",
      "5.3": "The Crucifixion",
      "5.4": "The Resurrection",
      "5.5": "Universal Sinfulness",
      "5.6": "Salvation Through Faith",
    };
    return categoryMap[category] || category;
  };

  const getTierProgress = (tier: number) => {
    if (!versionStats) return { current: 0, target: 0, percent: 0 };
    const stats = versionStats.tier_stats[tier];
    if (!stats) return { current: 0, target: 0, percent: 0 };
    return {
      current: stats.count,
      target: stats.target,
      percent: stats.target > 0 ? Math.round((stats.count / stats.target) * 100) : 0,
    };
  };

  const validateDistribution = () => {
    if (!versionStats) return false;
    const total = versionStats.total_questions || 1;
    const tier1Percent = Math.round((getTierProgress(1).current / total) * 100);
    const tier2Percent = Math.round((getTierProgress(2).current / total) * 100);
    const tier3Percent = Math.round((getTierProgress(3).current / total) * 100);
    
    return tier1Percent >= 65 && tier1Percent <= 75 &&
           tier2Percent >= 15 && tier2Percent <= 25 &&
           tier3Percent >= 5 && tier3Percent <= 15;
  };

  if (userLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-8 w-32 mb-4" />
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (!versionInfo) {
    return (
      <div className="container py-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin/versions">← Back to Versions</Link>
        </Button>
        <Card>
          <CardContent className="py-12 text-center">
            <h2 className="text-2xl font-bold mb-2">Version Not Found</h2>
            <p className="text-muted-foreground">
              Version {version} could not be found.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isValid = validateDistribution();

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin/versions">← Back to Versions</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-4xl font-bold">{versionInfo.semantic_version}</h1>
              <Badge
                variant={
                  versionInfo.status === "active"
                    ? "default"
                    : versionInfo.status === "locked"
                    ? "secondary"
                    : versionInfo.status === "archived"
                    ? "outline"
                    : "outline"
                }
                className={versionInfo.status === "active" ? "bg-[--ga-red]" : ""}
              >
                {versionInfo.status}
              </Badge>
              {isValid ? (
                <Badge variant="outline" className="text-green-600 border-green-600">
                  Valid Distribution
                </Badge>
              ) : (
                <Badge variant="destructive">Invalid Distribution</Badge>
              )}
            </div>
            <p className="mt-2 text-muted-foreground">
              {versionInfo.marketing_version}
            </p>
          </div>
          <div className="flex gap-2">
            {versionInfo.status === "draft" && (
              <Button
                variant="outline"
                onClick={handleLockVersion}
                disabled={!isValid || locking}
              >
                {locking ? "Locking..." : "Lock Version"}
              </Button>
            )}
            {versionInfo.status === "locked" && (
              <Button
                onClick={() => setShowPublishDialog(true)}
                className="bg-[--ga-red] hover:bg-[--ga-dark-red]"
              >
                Publish Version
              </Button>
            )}
            <Button asChild variant="outline">
              <Link href={`/admin/questions?version=${version}`}>
                Manage Questions
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Version Info Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Version Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-4">
            <div>
              <div className="text-sm text-muted-foreground">Created</div>
              <div className="text-lg font-medium">
                {new Date(versionInfo.created_at).toLocaleDateString()}
              </div>
            </div>
            {versionInfo.published_at && (
              <div>
                <div className="text-sm text-muted-foreground">Published</div>
                <div className="text-lg font-medium">
                  {new Date(versionInfo.published_at).toLocaleDateString()}
                </div>
              </div>
            )}
            <div>
              <div className="text-sm text-muted-foreground">Total Questions</div>
              <div className="text-lg font-medium">
                {versionStats?.total_questions || 0} / {versionStats?.target_total || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Completion</div>
              <div className="text-lg font-medium">
                {versionStats && versionStats.target_total > 0
                  ? Math.round((versionStats.total_questions / versionStats.target_total) * 100)
                  : 0}%
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tier Stats */}
      {versionStats && (
        <>
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            {[1, 2, 3].map((tier) => {
              const progress = getTierProgress(tier);
              const weight = tier === 1 ? "70%" : tier === 2 ? "20%" : "10%";
              return (
                <Card key={tier}>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Tier {tier} ({weight} weight)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">
                      {progress.current} / {progress.target}
                    </div>
                    <div className="mt-2">
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            progress.percent >= 100
                              ? "bg-green-500"
                              : progress.percent >= 80
                              ? "bg-primary"
                              : "bg-orange-500"
                          }`}
                          style={{ width: `${Math.min(100, progress.percent)}%` }}
                        />
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {progress.percent}% complete
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Category Completeness Grid */}
          <Card>
            <CardHeader>
              <CardTitle>Category Completeness</CardTitle>
              <CardDescription>
                Progress by category within {versionStats.semantic_version}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[1, 2, 3].map((tier) => {
                  const tierStat = versionStats.tier_stats[tier];
                  if (!tierStat) return null;
                  
                  const categories = Object.entries(tierStat.categories).sort();
                  
                  return (
                    <div key={tier}>
                      <h3 className="text-lg font-semibold mb-3">
                        Tier {tier} ({tier === 1 ? "70%" : tier === 2 ? "20%" : "10%"} weight)
                      </h3>
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {categories.map(([category, stats]) => {
                          const percent = stats.target > 0 
                            ? Math.round((stats.count / stats.target) * 100) 
                            : 0;
                          return (
                            <div
                              key={category}
                              className="p-3 border rounded-lg space-y-2"
                            >
                              <div className="flex justify-between items-start">
                                <div className="flex-1">
                                  <div className="font-medium text-sm">
                                    {category}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {getCategoryName(category)}
                                  </div>
                                </div>
                                <Badge
                                  variant={
                                    percent >= 100
                                      ? "default"
                                      : percent >= 80
                                      ? "secondary"
                                      : "outline"
                                  }
                                >
                                  {percent}%
                                </Badge>
                              </div>
                              <div className="space-y-1">
                                <div className="flex justify-between text-xs">
                                  <span className="text-muted-foreground">
                                    {stats.count} / {stats.target}
                                  </span>
                                  <span className="text-muted-foreground">
                                    {stats.target - stats.count} remaining
                                  </span>
                                </div>
                                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                  <div
                                    className={`h-full transition-all ${
                                      percent >= 100
                                        ? "bg-green-500"
                                        : percent >= 80
                                        ? "bg-primary"
                                        : "bg-orange-500"
                                    }`}
                                    style={{ width: `${Math.min(100, percent)}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Publish Dialog */}
      <Dialog open={showPublishDialog} onOpenChange={setShowPublishDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Publish Version</DialogTitle>
            <DialogDescription>
              Are you sure you want to publish version {version}? This
              will make it the current active version.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span>Questions:</span>
                <span className="font-medium">{versionStats?.total_questions}</span>
              </div>
              <div className="flex justify-between">
                <span>Tier 1:</span>
                <span className="font-medium">
                  {getTierProgress(1).current} ({getTierProgress(1).percent}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tier 2:</span>
                <span className="font-medium">
                  {getTierProgress(2).current} ({getTierProgress(2).percent}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tier 3:</span>
                <span className="font-medium">
                  {getTierProgress(3).current} ({getTierProgress(3).percent}%)
                </span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPublishDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handlePublishVersion}
              disabled={publishing}
              className="bg-[--ga-red] hover:bg-[--ga-dark-red]"
            >
              {publishing ? "Publishing..." : "Publish Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
