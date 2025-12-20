"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { apiClient, CompareResponse } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { RadarChart } from "@/components/charts/RadarChart";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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
              <Link href="/research">Back to Leaderboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const categories = comparison.categories || [];
  const radarData = comparison.models.map((model) => ({
    label: model.model_name,
    scores: model.category_scores || {},
  }));

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/research">← Back to Leaderboard</Link>
        </Button>
        <h1 className="text-4xl font-bold">Model Comparison</h1>
        <p className="mt-2 text-muted-foreground">
          Side-by-side comparison of {comparison.models.length} model
          {comparison.models.length > 1 ? "s" : ""}
        </p>
      </div>

      {/* Side-by-side Scores */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {comparison.models.map((model) => (
          <Card key={model.model_id}>
            <CardHeader>
              <CardTitle className="text-lg">{model.model_name}</CardTitle>
              <Badge variant="secondary">{model.provider}</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-muted-foreground">Overall Score</div>
                <div className="text-3xl font-bold text-[--ga-red]">
                  {model.overall_score?.toFixed(1) || "—"}
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <div className="text-xs text-muted-foreground">Tier 1</div>
                  <div className="font-semibold">{model.tier1_score?.toFixed(1) || "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Tier 2</div>
                  <div className="font-semibold">{model.tier2_score?.toFixed(1) || "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Tier 3</div>
                  <div className="font-semibold">{model.tier3_score?.toFixed(1) || "—"}</div>
                </div>
              </div>
              <Button asChild variant="outline" className="w-full">
                <Link href={`/research/models/${encodeURIComponent(model.model_id)}`}>View Details</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Radar Chart */}
      {radarData.length > 0 && categories.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Category Comparison</CardTitle>
            <CardDescription>
              Visual comparison across all categories
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
            <CardTitle>Category Breakdown</CardTitle>
            <CardDescription>
              Detailed scores by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Category</TableHead>
                  {comparison.models.map((model) => (
                    <TableHead key={model.model_id}>{model.model_name}</TableHead>
                  ))}
                  <TableHead>Best</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categories.map((category: string) => {
                  const scores = comparison.models.map((model) => {
                    const score = model.category_scores?.[category] || 0;
                    return { model: model.model_name, score };
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
