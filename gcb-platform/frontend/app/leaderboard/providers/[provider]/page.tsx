"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { apiClient, LeaderboardItem } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import { Shield, ShieldAlert, ShieldX, CheckCircle2 } from "lucide-react";

function getVerdictInfo(score: number) {
  if (score >= 80) {
    return {
      label: "Excellent",
      icon: <Shield className="h-4 w-4" />,
      textColor: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
    };
  } else if (score >= 61) {
    return {
      label: "Good",
      icon: <CheckCircle2 className="h-4 w-4" />,
      textColor: "text-blue-400",
      bgColor: "bg-blue-500/10",
    };
  } else if (score >= 40) {
    return {
      label: "Fair",
      icon: <ShieldAlert className="h-4 w-4" />,
      textColor: "text-amber-400",
      bgColor: "bg-amber-500/10",
    };
  } else {
    return {
      label: "Poor",
      icon: <ShieldX className="h-4 w-4" />,
      textColor: "text-red-400",
      bgColor: "bg-red-500/10",
    };
  }
}

export default function ProviderDetailPage() {
  const params = useParams();
  const rawProvider = params.provider as string;
  const provider = (() => {
    try {
      return decodeURIComponent(rawProvider);
    } catch {
      return rawProvider;
    }
  })();

  const [models, setModels] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (provider) {
      loadProviderModels();
    }
  }, [provider]);

  async function loadProviderModels() {
    setLoading(true);
    try {
      const data = await apiClient.getLeaderboard({ provider, limit: 100 });
      setModels(data.items || []);
    } catch (error) {
      console.error("Failed to load provider models:", error);
    } finally {
      setLoading(false);
    }
  }

  const providerDisplayName = formatProvider(provider);

  // Calculate provider stats
  const modelCount = models.length;
  const avgScore = modelCount > 0
    ? models.reduce((sum, m) => sum + m.overall_score, 0) / modelCount
    : 0;
  const topScore = modelCount > 0
    ? Math.max(...models.map((m) => m.overall_score))
    : 0;

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-12 w-64 mb-2" />
        <Skeleton className="h-6 w-96 mb-8" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Back Navigation */}
      <Button asChild variant="ghost" className="mb-4">
        <Link href="/leaderboard">← Back to Leaderboard</Link>
      </Button>

      {/* Provider Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <ProviderIcon provider={provider} size={48} />
          <div>
            <h1 className="text-4xl font-bold">{providerDisplayName}</h1>
            <p className="text-muted-foreground">
              {modelCount} model{modelCount !== 1 ? "s" : ""} tested on the Great Commission Benchmark
            </p>
          </div>
        </div>
      </div>

      {/* Provider Stats */}
      {modelCount > 0 && (
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Models Tested
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{modelCount}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-muted-foreground">
                {avgScore.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Top Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-[--ga-red]">
                {topScore.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Models List */}
      <div className="mb-4">
        <h2 className="text-2xl font-semibold">Models</h2>
      </div>

      {modelCount === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              No models from {providerDisplayName} have been tested yet.
            </p>
            <Button asChild variant="outline" className="mt-4">
              <Link href="/leaderboard">View All Models</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {models.map((model) => {
            const displayName = getDisplayModelName(model.model_name, model.model_id);
            const verdict = getVerdictInfo(model.overall_score);

            return (
              <Link
                key={model.id}
                href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}
                className="block group"
              >
                <Card className="h-full transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-lg font-semibold group-hover:text-primary transition-colors line-clamp-2">
                        {displayName}
                      </CardTitle>
                      <Badge
                        variant="outline"
                        className={`shrink-0 ${verdict.textColor} ${verdict.bgColor} border-current`}
                      >
                        <span className="mr-1">{verdict.icon}</span>
                        {verdict.label}
                      </Badge>
                    </div>
                    {model.model_id && (
                      <p className="text-xs text-muted-foreground/60 truncate">
                        {model.model_id}
                      </p>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-muted-foreground">Overall Score</span>
                          <span className="text-lg font-bold">{model.overall_score.toFixed(1)}%</span>
                        </div>
                        <Progress value={model.overall_score} className="h-2" />
                      </div>

                      {/* Tier Scores */}
                      <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-white/5">
                        <div>
                          <div className="text-xs text-muted-foreground">Task</div>
                          <div className={`text-sm font-semibold ${
                            model.tier1_score != null
                              ? model.tier1_score >= 80
                                ? "text-emerald-400"
                                : model.tier1_score >= 61
                                  ? "text-blue-400"
                                  : model.tier1_score >= 40
                                    ? "text-amber-400"
                                    : "text-red-400"
                              : "text-muted-foreground"
                          }`}>
                            {model.tier1_score?.toFixed(0) || "—"}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground">Doctrine</div>
                          <div className={`text-sm font-semibold ${
                            model.tier2_score != null
                              ? model.tier2_score >= 80
                                ? "text-emerald-400"
                                : model.tier2_score >= 61
                                  ? "text-blue-400"
                                  : model.tier2_score >= 40
                                    ? "text-amber-400"
                                    : "text-red-400"
                              : "text-muted-foreground"
                          }`}>
                            {model.tier2_score?.toFixed(0) || "—"}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground">Worldview</div>
                          <div className={`text-sm font-semibold ${
                            model.tier3_score != null
                              ? model.tier3_score >= 80
                                ? "text-emerald-400"
                                : model.tier3_score >= 61
                                  ? "text-blue-400"
                                  : model.tier3_score >= 40
                                    ? "text-amber-400"
                                    : "text-red-400"
                              : "text-muted-foreground"
                          }`}>
                            {model.tier3_score?.toFixed(0) || "—"}
                          </div>
                        </div>
                      </div>

                      {model.test_count > 1 && (
                        <div className="text-xs text-muted-foreground/60 text-center">
                          Average of {model.test_count} tests
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
