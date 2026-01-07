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
import { VersionHistoryChart } from "@/components/charts/VersionHistoryChart";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/research">← Back to Leaderboard</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">{model.model_name || model.name}</h1>
            <div className="mt-2 flex items-center gap-4">
              <Badge variant="secondary">{model.provider}</Badge>
              {model.trust_tier && (
                <Badge variant="outline">{model.trust_tier}</Badge>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button asChild variant="outline">
              <Link href={`/research/compare?models=${encodeURIComponent(modelId)}`}>Compare</Link>
            </Button>
            <Button asChild variant="brand">
              <Link href="/tests/new">Run Test</Link>
            </Button>
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
              {model.overall_score?.toFixed(1) || model.score?.toFixed(1) || "—"}
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
              {model.tier1_score?.toFixed(1) || "—"}
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
              {model.tier2_score?.toFixed(1) || "—"}
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
              {model.tier3_score?.toFixed(1) || "—"}
            </div>
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
          <Card>
            <CardHeader>
              <CardTitle>Model Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="font-medium">Provider:</span> {model.provider}
              </div>
              {model.model_id && (
                <div>
                  <span className="font-medium">Model ID:</span> {model.model_id}
                </div>
              )}
              {model.test_count && (
                <div>
                  <span className="font-medium">Tests Run:</span> {model.test_count}
                </div>
              )}
            </CardContent>
          </Card>
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
