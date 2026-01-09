"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChart } from "@/components/charts/CategoryChart";
import { RadarChart } from "@/components/charts/RadarChart";
import { VersionHistoryChart } from "@/components/charts/VersionHistoryChart";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Shield, ShieldAlert, ShieldX, CheckCircle2, XCircle, AlertTriangle, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { BenchmarkHelpIcon } from "@/components/benchmark";

// Verdict helper functions
function getVerdict(score: number): { label: string; description: string; icon: React.ReactNode; bgColor: string; borderColor: string; textColor: string; iconBg: string } {
  if (score >= 75) {
    return { 
      label: "Aligned", 
      description: "This model demonstrates strong alignment with Great Commission objectives.",
      icon: <Shield className="h-6 w-6" />, 
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/30",
      textColor: "text-emerald-400",
      iconBg: "bg-emerald-500/20"
    };
  } else if (score >= 50) {
    return { 
      label: "Caution", 
      description: "This model shows partial alignment but may resist certain Great Commission tasks.",
      icon: <ShieldAlert className="h-6 w-6" />, 
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/30",
      textColor: "text-amber-400",
      iconBg: "bg-amber-500/20"
    };
  } else {
    return { 
      label: "Compromised", 
      description: "This model shows significant resistance to Great Commission work.",
      icon: <ShieldX className="h-6 w-6" />, 
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/30",
      textColor: "text-red-400",
      iconBg: "bg-red-500/20"
    };
  }
}

// Category heatmap for single model
function SingleModelHeatmap({ categoryScores }: { categoryScores: Record<string, number> }) {
  const categories = Object.entries(categoryScores);
  
  if (categories.length === 0) {
    return <p className="text-muted-foreground">No category data available</p>;
  }

  const getColor = (value: number) => {
    if (value >= 80) return "bg-green-500 text-white";
    if (value >= 60) return "bg-green-300 text-green-900";
    if (value >= 40) return "bg-yellow-300 text-yellow-900";
    if (value >= 20) return "bg-orange-300 text-orange-900";
    return "bg-red-300 text-red-900";
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {categories.map(([category, score]) => (
          <div key={category} className={`${getColor(score)} rounded-lg p-3 text-center`}>
            <div className="text-2xl font-bold">{score.toFixed(0)}</div>
            <div className="text-xs capitalize opacity-80">{category.replace(/_/g, ' ')}</div>
          </div>
        ))}
      </div>
      {/* Legend */}
      <div className="flex items-center justify-center gap-2 text-xs pt-2">
        <span className="text-muted-foreground">Low</span>
        <div className="flex gap-1">
          <div className="w-6 h-4 bg-red-300 rounded" />
          <div className="w-6 h-4 bg-orange-300 rounded" />
          <div className="w-6 h-4 bg-yellow-300 rounded" />
          <div className="w-6 h-4 bg-green-300 rounded" />
          <div className="w-6 h-4 bg-green-500 rounded" />
        </div>
        <span className="text-muted-foreground">High</span>
      </div>
    </div>
  );
}

// Strengths and Weaknesses component
function StrengthsWeaknesses({ categoryScores, tier1, tier2, tier3 }: { 
  categoryScores?: Record<string, number>;
  tier1?: number;
  tier2?: number;
  tier3?: number;
}) {
  const strengths: string[] = [];
  const weaknesses: string[] = [];
  const neutral: string[] = [];

  // Analyze tier scores
  if (tier1 != null) {
    if (tier1 >= 75) strengths.push("Strong task completion capability");
    else if (tier1 < 50) weaknesses.push("Limited task completion capability");
  }
  if (tier2 != null) {
    if (tier2 >= 75) strengths.push("Maintains doctrinal fidelity");
    else if (tier2 < 50) weaknesses.push("Weak doctrinal alignment");
  }
  if (tier3 != null) {
    if (tier3 >= 75) strengths.push("Affirms Christian worldview");
    else if (tier3 < 50) weaknesses.push("Resists worldview confession");
  }

  // Analyze category scores
  if (categoryScores) {
    Object.entries(categoryScores).forEach(([category, score]) => {
      const prettyName = category.replace(/_/g, ' ');
      if (score >= 80) strengths.push(`Excellent at ${prettyName}`);
      else if (score < 40) weaknesses.push(`Struggles with ${prettyName}`);
    });
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="space-y-2">
        <h4 className="font-semibold text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          Strengths
        </h4>
        {strengths.length > 0 ? (
          <ul className="space-y-1">
            {strengths.slice(0, 5).map((s, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <TrendingUp className="h-3 w-3 mt-1 text-emerald-500 shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">No notable strengths identified</p>
        )}
      </div>
      <div className="space-y-2">
        <h4 className="font-semibold text-red-400 flex items-center gap-2">
          <XCircle className="h-4 w-4" />
          Weaknesses
        </h4>
        {weaknesses.length > 0 ? (
          <ul className="space-y-1">
            {weaknesses.slice(0, 5).map((w, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <TrendingDown className="h-3 w-3 mt-1 text-red-500 shrink-0" />
                {w}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">No notable weaknesses identified</p>
        )}
      </div>
    </div>
  );
}

export default function ModelDetailPage() {
  const params = useParams();
  // Decode the model ID from URL params (Next.js may leave it encoded)
  const rawModelId = params.id as string;
  const modelId = (() => {
    try {
      return decodeURIComponent(rawModelId);
    } catch {
      return rawModelId;
    }
  })();
  const [model, setModel] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (modelId) {
      loadModelData();
    }
  }, [modelId]);

  async function loadModelData() {
    setLoading(true);
    try {
      const modelData = await apiClient.getModel(modelId);
      setModel(modelData);
    } catch (error) {
      console.error("Failed to load model:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-4" />
        <Skeleton className="h-8 w-96 mb-8" />
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (!model) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Model Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/research">Back to Leaderboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const overallScore = model.overall_score ?? model.score ?? 0;
  const verdict = getVerdict(overallScore);

  // Prepare radar chart data
  const displayName = getDisplayModelName(model.model_name || model.name, model.model_id);
  const radarCategories = model.category_scores ? Object.keys(model.category_scores) : [];
  const radarData = model.category_scores ? [{
    label: displayName,
    scores: model.category_scores
  }] : [];

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/research">← Back to Leaderboard</Link>
        </Button>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-4xl font-bold">{displayName}</h1>
            <div className="mt-2 flex items-center gap-4">
              <Badge variant="secondary">{formatProvider(model.provider)}</Badge>
              {model.trust_tier && (
                <Badge variant="outline">{model.trust_tier}</Badge>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button asChild variant="outline">
              <Link href={`/research/compare?models=${encodeURIComponent(model.id)}`}>Compare</Link>
            </Button>
          </div>
        </div>
      </div>

      {/* The Verdict - Prominent Summary */}
      <Card className={`mb-8 border ${verdict.bgColor} ${verdict.borderColor}`}>
        <CardContent className="pt-6">
          <div className="flex items-start gap-6 flex-wrap md:flex-nowrap">
            <div className={`p-4 rounded-full ${verdict.iconBg} ${verdict.textColor}`}>
              {verdict.icon}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className={`text-2xl font-bold ${verdict.textColor}`}>{verdict.label}</h2>
                <div className="text-4xl font-bold text-foreground">{overallScore.toFixed(1)}</div>
              </div>
              <p className="text-muted-foreground mb-4">{verdict.description}</p>
              <StrengthsWeaknesses 
                categoryScores={model.category_scores}
                tier1={model.tier1_score}
                tier2={model.tier2_score}
                tier3={model.tier3_score}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Overview with Progress Bars */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Overall Score
              </CardTitle>
              <BenchmarkHelpIcon size="sm" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-[--ga-red] mb-2">
              {overallScore.toFixed(1)}
            </div>
            <Progress value={overallScore} className="h-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 1 (Task) <span className="text-xs text-slate-400">70%</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold mb-2 ${model.tier1_score != null ? (model.tier1_score >= 75 ? "text-green-600" : model.tier1_score >= 50 ? "text-yellow-600" : "text-red-600") : ""}`}>
              {model.tier1_score?.toFixed(1) || "—"}
            </div>
            {model.tier1_score != null && <Progress value={model.tier1_score} className="h-2" />}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 2 (Doctrine) <span className="text-xs text-slate-400">20%</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold mb-2 ${model.tier2_score != null ? (model.tier2_score >= 75 ? "text-green-600" : model.tier2_score >= 50 ? "text-yellow-600" : "text-red-600") : ""}`}>
              {model.tier2_score?.toFixed(1) || "—"}
            </div>
            {model.tier2_score != null && <Progress value={model.tier2_score} className="h-2" />}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 3 (Worldview) <span className="text-xs text-slate-400">10%</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold mb-2 ${model.tier3_score != null ? (model.tier3_score >= 75 ? "text-green-600" : model.tier3_score >= 50 ? "text-yellow-600" : "text-red-600") : ""}`}>
              {model.tier3_score?.toFixed(1) || "—"}
            </div>
            {model.tier3_score != null && <Progress value={model.tier3_score} className="h-2" />}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="history">Version History</TabsTrigger>
          <TabsTrigger value="tests">Recent Tests</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Radar Chart - The Model Shape */}
          {radarData.length > 0 && radarCategories.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Performance Profile</CardTitle>
                <CardDescription>
                  Visual representation of performance across all evaluated categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RadarChart data={radarData} categories={radarCategories} />
              </CardContent>
            </Card>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Model Information */}
            <Card>
              <CardHeader>
                <CardTitle>Model Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-muted-foreground">Provider</span>
                    <p className="font-medium">{formatProvider(model.provider)}</p>
                  </div>
                  {model.model_id && (
                    <div>
                      <span className="text-sm text-muted-foreground">Model ID</span>
                      <p className="font-medium text-sm break-all">{model.model_id}</p>
                    </div>
                  )}
                  {model.test_count != null && (
                    <div>
                      <span className="text-sm text-muted-foreground">Tests Run</span>
                      <p className="font-medium">{model.test_count}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button asChild variant="outline" className="w-full justify-start">
                  <Link href={`/research/compare?models=${encodeURIComponent(model.id)}`}>
                    Compare with other models
                  </Link>
                </Button>
                <Button asChild variant="outline" className="w-full justify-start">
                  <Link href="/research">
                    View full leaderboard
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="categories" className="space-y-6">
          {/* Category Heatmap */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Category Heatmap</CardTitle>
                <BenchmarkHelpIcon size="default" />
              </div>
              <CardDescription>
                Performance breakdown by category - darker green indicates stronger alignment
              </CardDescription>
            </CardHeader>
            <CardContent>
              {model.category_scores ? (
                <SingleModelHeatmap categoryScores={model.category_scores} />
              ) : (
                <p className="text-muted-foreground">No category data available</p>
              )}
            </CardContent>
          </Card>

          {/* Bar Chart View */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Category Breakdown (Bar Chart)</CardTitle>
                <BenchmarkHelpIcon size="default" />
              </div>
              <CardDescription>
                Performance across different categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              {model.category_scores ? (
                <CategoryChart data={model.category_scores} />
              ) : (
                <p className="text-muted-foreground">No category data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>
                Score trends across benchmark versions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {model.version_history ? (
                <VersionHistoryChart data={model.version_history} />
              ) : (
                <p className="text-muted-foreground">No version history available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tests">
          <Card>
            <CardHeader>
              <CardTitle>Recent Test Runs</CardTitle>
            </CardHeader>
            <CardContent>
              {model.test_history && model.test_history.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Version</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Trust Tier</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {model.test_history.map((run: any) => (
                      <TableRow key={run.test_run_id}>
                        <TableCell>
                          {new Date(run.completed_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{run.benchmark_version}</TableCell>
                        <TableCell>{run.overall_score?.toFixed(1) || "—"}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{run.trust_tier}</Badge>
                        </TableCell>
                        <TableCell>
                          <Button asChild variant="ghost" size="sm">
                            <Link href={`/tests/${run.test_run_id}/results`}>View</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">No test runs available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
