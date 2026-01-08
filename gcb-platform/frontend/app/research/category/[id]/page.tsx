"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChart } from "@/components/charts/CategoryChart";

const CATEGORY_INFO: Record<string, { name: string; description: string; tier: string }> = {
  scripture: {
    name: "Scripture",
    description: "Processing and explaining Scripture accurately and helpfully",
    tier: "Task Capability",
  },
  theology: {
    name: "Theology",
    description: "Understanding and articulating theological concepts",
    tier: "Gospel Core",
  },
  ethics: {
    name: "Ethics",
    description: "Applying Christian ethics to modern situations",
    tier: "Gospel Core",
  },
  apologetics: {
    name: "Apologetics",
    description: "Defending the faith and engaging with objections",
    tier: "Task Capability",
  },
  evangelism: {
    name: "Evangelism",
    description: "Creating evangelistic content and outreach materials",
    tier: "Task Capability",
  },
  discipleship: {
    name: "Discipleship",
    description: "Developing discipleship tools and resources",
    tier: "Task Capability",
  },
  missions: {
    name: "Missions",
    description: "Supporting missiological research and cross-cultural ministry",
    tier: "Task Capability",
  },
  prayer: {
    name: "Prayer",
    description: "Creating prayer resources and guides",
    tier: "Task Capability",
  },
  worldview: {
    name: "Worldview",
    description: "Affirming Christian truth claims when directly asked",
    tier: "Worldview Confession",
  },
};

interface CategoryModel {
  model_id: string;
  model_name: string;
  provider: string;
  category_score: number;
  overall_score: number;
  trust_tier?: string;
}

export default function CategoryPage() {
  const params = useParams();
  const categoryId = params.id as string;
  const [models, setModels] = useState<CategoryModel[]>([]);
  const [loading, setLoading] = useState(true);

  const categoryInfo = CATEGORY_INFO[categoryId] || {
    name: categoryId,
    description: "Category results",
    tier: "Unknown",
  };

  useEffect(() => {
    if (categoryId) {
      loadCategoryData();
    }
  }, [categoryId]);

  async function loadCategoryData() {
    setLoading(true);
    try {
      const result = await apiClient.getLeaderboard({
        category: categoryId,
        limit: 50,
        sort: "score",
        order: "desc",
      });
      if (result.items) {
        setModels(
          result.items.map((item: any) => ({
            model_id: item.model_id,
            model_name: item.model_name,
            provider: item.provider,
            category_score: item.category_scores?.[categoryId] || item.overall_score,
            overall_score: item.overall_score,
            trust_tier: item.trust_tier,
          }))
        );
      }
    } catch (error) {
      console.error("Failed to load category data:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-4" />
        <Skeleton className="h-8 w-96 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  const topPerformers = models.slice(0, 3);
  const chartData: Record<string, number> = {};
  topPerformers.forEach((model) => {
    chartData[model.model_name] = model.category_score;
  });

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/research">← Back to Leaderboard</Link>
        </Button>
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-4xl font-bold capitalize">{categoryInfo.name}</h1>
          <Badge variant="secondary">{categoryInfo.tier}</Badge>
        </div>
        <p className="text-muted-foreground">{categoryInfo.description}</p>
      </div>

      {/* Top Performers */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        {topPerformers.map((model, index) => (
          <Card key={model.model_id} className={index === 0 ? "border-[--ga-red]" : ""}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant={index === 0 ? "default" : "outline"}>#{index + 1}</Badge>
                {model.trust_tier && (
                  <Badge variant="outline">{model.trust_tier}</Badge>
                )}
              </div>
              <CardTitle className="text-lg mt-2">{model.model_name}</CardTitle>
              <CardDescription>{model.provider}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-[--ga-red]">
                {model.category_score.toFixed(1)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Overall: {model.overall_score.toFixed(1)}
              </p>
              <Button asChild variant="outline" className="w-full mt-4">
                <Link href={`/research/models/${encodeURIComponent(model.model_id)}`}>View Details</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Top Performers Chart */}
      {Object.keys(chartData).length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Top Performers Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <CategoryChart data={chartData} />
          </CardContent>
        </Card>
      )}

      {/* Full Rankings */}
      <Card>
        <CardHeader>
          <CardTitle>All Models - {categoryInfo.name} Rankings</CardTitle>
          <CardDescription>
            {models.length} models ranked by {categoryInfo.name.toLowerCase()} performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Provider</TableHead>
                <TableHead>{categoryInfo.name} Score</TableHead>
                <TableHead>Overall Score</TableHead>
                <TableHead>Trust</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {models.map((model, index) => (
                <TableRow key={model.model_id}>
                  <TableCell className="font-medium">{index + 1}</TableCell>
                  <TableCell>
                    <Link
                      href={`/research/models/${encodeURIComponent(model.model_id)}`}
                      className="hover:underline font-medium"
                    >
                      {model.model_name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{model.provider}</Badge>
                  </TableCell>
                  <TableCell className="font-semibold text-[--ga-red]">
                    {model.category_score.toFixed(1)}
                  </TableCell>
                  <TableCell>{model.overall_score.toFixed(1)}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{model.trust_tier || "automated"}</Badge>
                  </TableCell>
                  <TableCell>
                    <Button asChild variant="ghost" size="sm">
                      <Link href={`/research/models/${encodeURIComponent(model.model_id)}`}>View</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
