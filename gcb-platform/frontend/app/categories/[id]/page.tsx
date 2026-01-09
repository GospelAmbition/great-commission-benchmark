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
import { TopPerformersTierComparisonChart } from "@/components/charts/TopPerformersTierComparisonChart";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { ArrowLeft } from "lucide-react";
import { TIER_INFO } from "@/lib/benchmark-definitions";

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
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
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
            tier1_score: item.tier1_score,
            tier2_score: item.tier2_score,
            tier3_score: item.tier3_score,
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

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4 gap-2">
          <Link href="/categories">
            <ArrowLeft className="h-4 w-4" />
            Back to Categories
          </Link>
        </Button>
        <Card>
          <CardHeader>
            <div className="flex items-center gap-4 mb-2">
              <CardTitle className="text-4xl font-bold capitalize mb-0">{categoryInfo.name}</CardTitle>
              <Badge variant="secondary">{categoryInfo.tier}</Badge>
            </div>
            <CardDescription className="text-base">{categoryInfo.description}</CardDescription>
          </CardHeader>
        </Card>
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
              <CardDescription className="flex items-center gap-2">
                <ProviderIcon provider={model.provider} size={14} />
                {model.provider}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-[--ga-red]">
                {model.category_score.toFixed(1)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Overall: {model.overall_score.toFixed(1)}
              </p>
              <Button asChild variant="outline" className="w-full mt-4">
                <Link href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}>View Details</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Top Performers Chart */}
      {topPerformers.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Top Performers Comparison</CardTitle>
            <CardDescription>
              {TIER_INFO[1].name} • {TIER_INFO[2].name} • {TIER_INFO[3].name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TopPerformersTierComparisonChart
              data={topPerformers.map((model) => ({
                model_name: model.model_name,
                tier1_score: model.tier1_score,
                tier2_score: model.tier2_score,
                tier3_score: model.tier3_score,
                provider: model.provider,
              }))}
            />
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
                      href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}
                      className="hover:underline font-medium"
                    >
                      {model.model_name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <ProviderIcon provider={model.provider} size={16} />
                      <Badge variant="secondary">{model.provider}</Badge>
                    </div>
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
                      <Link href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}>View</Link>
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
