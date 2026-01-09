"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { apiClient, CompareResponse } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { RadarChart } from "@/components/charts/RadarChart";
import { CategoryHeatmap } from "@/components/charts/CategoryHeatmap";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Shield, ShieldAlert, ShieldX, Trophy, Crown, Medal, ArrowRight, ChevronRight } from "lucide-react";
import { BenchmarkHelpIcon } from "@/components/benchmark";

// Verdict helper
function getVerdict(score: number): { label: string; icon: React.ReactNode; color: string; bgColor: string } {
  if (score >= 75) {
    return { label: "Aligned", icon: <Shield className="h-4 w-4" />, color: "text-emerald-400", bgColor: "bg-emerald-500/20 border-emerald-500/30" };
  } else if (score >= 50) {
    return { label: "Caution", icon: <ShieldAlert className="h-4 w-4" />, color: "text-amber-400", bgColor: "bg-amber-500/20 border-amber-500/30" };
  } else {
    return { label: "Compromised", icon: <ShieldX className="h-4 w-4" />, color: "text-red-400", bgColor: "bg-red-500/20 border-red-500/30" };
  }
}

// Rank medal icons
function RankIcon({ rank }: { rank: number }) {
  if (rank === 1) return <Crown className="h-5 w-5 text-yellow-500" />;
  if (rank === 2) return <Medal className="h-5 w-5 text-slate-400" />;
  if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />;
  return null;
}

function ComparePageContent() {
  const searchParams = useSearchParams();
  const modelIdsParam = searchParams.get("models");
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (modelIdsParam) {
      // Decode URL-encoded model IDs (e.g., qwen%2Fqwen3-coder becomes qwen/qwen3-coder)
      const ids = modelIdsParam.split(",").map(id => decodeURIComponent(id)).slice(0, 5);
      loadComparison(ids);
    } else {
      setLoading(false);
    }
  }, [modelIdsParam]);

  async function loadComparison(modelIds: string[]) {
    setLoading(true);
    try {
      const result = await apiClient.compareModels(modelIds);
      setComparison(result);
    } catch (error) {
      console.error("Failed to load comparison:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (!comparison || !comparison.models) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Comparison Not Available</CardTitle>
            <CardDescription>
              Please select models to compare from the leaderboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/leaderboard">Back to Leaderboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const categories = comparison.categories || [];
  const radarData = comparison.models.map((model) => ({
    label: getDisplayModelName(model.model_name, model.model_id),
    scores: model.category_scores || {},
  }));

  // Sort models by overall score and assign ranks
  const rankedModels = [...comparison.models]
    .sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0))
    .map((model, index) => ({ ...model, rank: index + 1, displayName: getDisplayModelName(model.model_name, model.model_id) }));

  // Find the winner
  const winner = rankedModels[0];

  // Prepare heatmap data
  const heatmapData = comparison.models.map((model) => ({
    model_name: getDisplayModelName(model.model_name, model.model_id),
    categories: model.category_scores || {},
  }));

  return (
    <div className="container py-8">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground mb-6">
        <Link href="/leaderboard" className="hover:text-foreground transition-colors">
          Leaderboard
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Compare Models</span>
      </nav>

      <div className="mb-8">
        <h1 className="text-4xl font-bold">Model Comparison</h1>
        <p className="mt-2 text-muted-foreground">
          Side-by-side comparison of {comparison.models.length} model
          {comparison.models.length > 1 ? "s" : ""}
        </p>
        <Button asChild variant="outline" size="sm" className="mt-4">
          <Link href="/leaderboard">← Change Selection</Link>
        </Button>
      </div>

      {/* Head-to-Head Summary */}
      {rankedModels.length >= 2 && (
        <Card className="mb-8 border-yellow-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Head-to-Head Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center gap-8 flex-wrap">
              <div className="text-center">
                <div className="text-lg font-bold text-foreground">{winner.displayName}</div>
                <div className="text-3xl font-bold text-emerald-400">{winner.overall_score?.toFixed(1)}</div>
                <Badge className="mt-2 bg-emerald-600">Winner</Badge>
              </div>
              <div className="text-2xl font-bold text-muted-foreground">vs</div>
              {rankedModels.slice(1).map((model, index) => (
                <div key={model.model_id || `runner-up-${index}`} className="text-center">
                  <div className="text-lg font-bold text-muted-foreground">{model.displayName}</div>
                  <div className="text-3xl font-bold text-muted-foreground">{model.overall_score?.toFixed(1)}</div>
                  <Badge variant="outline" className="mt-2">#{model.rank}</Badge>
                </div>
              ))}
            </div>
            <div className="mt-6 text-center text-sm text-muted-foreground">
              <strong className="text-foreground">{winner.displayName}</strong> outperforms by{" "}
              <span className="text-emerald-400 font-semibold">
                +{((winner.overall_score || 0) - (rankedModels[1]?.overall_score || 0)).toFixed(1)} points
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Side-by-side Scores */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {rankedModels.map((model, index) => {
          const verdict = getVerdict(model.overall_score || 0);
          return (
            <Card key={model.model_id || `model-${index}`} className={`relative ${model.rank === 1 ? "border-2 border-yellow-400 shadow-lg" : ""}`}>
              {model.rank === 1 && (
                <div className="absolute -top-3 -right-3 bg-yellow-400 text-yellow-900 rounded-full p-2">
                  <Crown className="h-4 w-4" />
                </div>
              )}
              <CardHeader>
                <div className="flex items-center gap-2">
                  <RankIcon rank={model.rank} />
                  <CardTitle className="text-lg">{model.displayName}</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{formatProvider(model.provider)}</Badge>
                  <Badge className={`${verdict.color} ${verdict.bgColor} border`} variant="outline">
                    {verdict.icon}
                    <span className="ml-1">{verdict.label}</span>
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">Overall Score</div>
                  <div className="text-3xl font-bold text-[--ga-red]">
                    {model.overall_score?.toFixed(1) || "—"}
                  </div>
                  <Progress value={model.overall_score || 0} className="h-2 mt-2" />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <div className="text-xs text-muted-foreground">Task (70%)</div>
                    <div className={`font-semibold ${model.tier1_score != null && model.tier1_score >= 75 ? "text-green-600" : model.tier1_score != null && model.tier1_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                      {model.tier1_score?.toFixed(1) || "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Doctrine (20%)</div>
                    <div className={`font-semibold ${model.tier2_score != null && model.tier2_score >= 75 ? "text-green-600" : model.tier2_score != null && model.tier2_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                      {model.tier2_score?.toFixed(1) || "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Worldview (10%)</div>
                    <div className={`font-semibold ${model.tier3_score != null && model.tier3_score >= 75 ? "text-green-600" : model.tier3_score != null && model.tier3_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                      {model.tier3_score?.toFixed(1) || "—"}
                    </div>
                  </div>
                </div>
                <Button asChild variant="outline" className="w-full">
                  <Link href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}>
                    View Details
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Category Heatmap */}
      {heatmapData.length > 0 && categories.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Category Heatmap</CardTitle>
              <BenchmarkHelpIcon size="default" />
            </div>
            <CardDescription>
              Side-by-side category scores - darker green indicates stronger alignment
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CategoryHeatmap data={heatmapData} categories={categories} />
          </CardContent>
        </Card>
      )}

      {/* Radar Chart */}
      {radarData.length > 0 && categories.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Performance Profile Comparison</CardTitle>
              <BenchmarkHelpIcon size="default" />
            </div>
            <CardDescription>
              Visual comparison of model &quot;shapes&quot; across all categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RadarChart data={radarData} categories={categories} />
          </CardContent>
        </Card>
      )}

      {/* Category Breakdown Table */}
      {comparison.category_breakdown && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Category Breakdown</CardTitle>
              <BenchmarkHelpIcon size="default" />
            </div>
            <CardDescription>
              Detailed scores by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Category</TableHead>
                  {comparison.models.map((model, index) => (
                    <TableHead key={model.model_id || `header-${index}`}>{getDisplayModelName(model.model_name, model.model_id)}</TableHead>
                  ))}
                  <TableHead>Best</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categories.map((category: string) => {
                  const scores = comparison.models.map((model) => {
                    const score = model.category_scores?.[category] || 0;
                    return { model: getDisplayModelName(model.model_name, model.model_id), score };
                  });
                  const best = scores.reduce((max, curr) =>
                    curr.score > max.score ? curr : max
                  );

                  return (
                    <TableRow key={category}>
                      <TableCell className="font-medium capitalize">
                        {category}
                      </TableCell>
                      {scores.map((item, idx) => (
                        <TableCell
                          key={idx}
                          className={
                            item.score === best.score ? "font-bold text-[--ga-red]" : ""
                          }
                        >
                          {item.score.toFixed(1)}
                        </TableCell>
                      ))}
                      <TableCell>
                        <Badge variant="outline">{best.model}</Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    }>
      <ComparePageContent />
    </Suspense>
  );
}
