"use client";

import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpDown } from "lucide-react";

interface LeaderboardItem {
  model_id: string;
  model_name: string;
  provider: string;
  overall_score: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  trust_tier?: string;
  test_count?: number;
}

export default function ResearchPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set());
  const [filters, setFilters] = useState({
    version: "",
    category: "",
    tier: "",
    provider: "",
    trust_tier: "",
    sort: "score",
    order: "desc" as "asc" | "desc",
  });
  const [pagination, setPagination] = useState({
    limit: 50,
    offset: 0,
    total: 0,
  });

  useEffect(() => {
    loadLeaderboard();
  }, [filters, pagination.offset]);

  async function loadLeaderboard() {
    setLoading(true);
    try {
      const result = await apiClient.getLeaderboard({
        ...filters,
        limit: pagination.limit,
        offset: pagination.offset,
      });
      if (result.items) {
        setLeaderboard(result.items);
        setPagination((prev) => ({ ...prev, total: result.total || 0 }));
      }
    } catch (error) {
      console.error("Failed to load leaderboard:", error);
    } finally {
      setLoading(false);
    }
  }

  function toggleModelSelection(modelId: string) {
    const newSelected = new Set(selectedModels);
    if (newSelected.has(modelId)) {
      newSelected.delete(modelId);
    } else if (newSelected.size < 5) {
      newSelected.add(modelId);
    }
    setSelectedModels(newSelected);
  }

  function handleSort(field: string) {
    setFilters((prev) => ({
      ...prev,
      sort: field,
      order: prev.sort === field && prev.order === "desc" ? "asc" : "desc",
    }));
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Research</h1>
        <p className="mt-2 text-muted-foreground">
          Explore benchmark results, compare models, and dive deep into performance data
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Refine your search</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Provider</label>
              <Select
                value={filters.provider}
                onValueChange={(value) =>
                  setFilters((prev) => ({ ...prev, provider: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All providers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All providers</SelectItem>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                  <SelectItem value="google">Google</SelectItem>
                  <SelectItem value="meta">Meta</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Trust Tier</label>
              <Select
                value={filters.trust_tier}
                onValueChange={(value) =>
                  setFilters((prev) => ({ ...prev, trust_tier: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All tiers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All tiers</SelectItem>
                  <SelectItem value="automated">Automated</SelectItem>
                  <SelectItem value="reviewed">Reviewed</SelectItem>
                  <SelectItem value="validated">Validated</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Category</label>
              <Select
                value={filters.category}
                onValueChange={(value) =>
                  setFilters((prev) => ({ ...prev, category: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All categories</SelectItem>
                  <SelectItem value="scripture">Scripture</SelectItem>
                  <SelectItem value="theology">Theology</SelectItem>
                  <SelectItem value="ethics">Ethics</SelectItem>
                  <SelectItem value="apologetics">Apologetics</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Tier</label>
              <Select
                value={filters.tier}
                onValueChange={(value) =>
                  setFilters((prev) => ({ ...prev, tier: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All tiers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All tiers</SelectItem>
                  <SelectItem value="tier1">Tier 1 (Task)</SelectItem>
                  <SelectItem value="tier2">Tier 2 (Doctrine)</SelectItem>
                  <SelectItem value="tier3">Tier 3 (Worldview)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Compare Button */}
      {selectedModels.size > 0 && (
        <div className="mb-4">
          <Button asChild>
            <Link href={`/research/compare?models=${Array.from(selectedModels).join(",")}`}>
              Compare {selectedModels.size} Model{selectedModels.size > 1 ? "s" : ""}
            </Link>
          </Button>
        </div>
      )}

      {/* Disclaimer */}
      <div className="mb-4 p-4 bg-muted rounded-lg border-l-4 border-[--ga-red]">
        <p className="text-sm text-muted-foreground">
          <strong>Disclaimer:</strong> This benchmark is for informational purposes only and does not 
          constitute an endorsement or recommendation of any AI model or service. Results reflect 
          performance on specific test questions at a point in time and may not predict performance 
          on other tasks or future model versions.
        </p>
      </div>

      {/* Leaderboard Table */}
      <Card>
        <CardHeader>
          <CardTitle>Leaderboard</CardTitle>
          <CardDescription>
            Showing {pagination.offset + 1}-
            {Math.min(pagination.offset + pagination.limit, pagination.total)} of{" "}
            {pagination.total} models
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <Checkbox disabled />
                    </TableHead>
                    <TableHead>Rank</TableHead>
                    <TableHead>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSort("model_name")}
                        className="h-8"
                      >
                        Model
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                      </Button>
                    </TableHead>
                    <TableHead>Provider</TableHead>
                    <TableHead>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSort("score")}
                        className="h-8"
                      >
                        Overall Score
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                      </Button>
                    </TableHead>
                    <TableHead>Tier 1</TableHead>
                    <TableHead>Tier 2</TableHead>
                    <TableHead>Tier 3</TableHead>
                    <TableHead>Trust</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leaderboard.map((item, index) => (
                    <TableRow key={item.model_id}>
                      <TableCell>
                        <Checkbox
                          checked={selectedModels.has(item.model_id)}
                          onCheckedChange={() => toggleModelSelection(item.model_id)}
                          disabled={!selectedModels.has(item.model_id) && selectedModels.size >= 5}
                        />
                      </TableCell>
                      <TableCell className="font-medium">
                        {pagination.offset + index + 1}
                      </TableCell>
                      <TableCell>
                        <Link
                          href={`/research/models/${item.model_id}`}
                          className="hover:underline font-medium"
                        >
                          {item.model_name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">{item.provider}</Badge>
                      </TableCell>
                      <TableCell className="font-semibold">
                        {item.overall_score.toFixed(1)}
                      </TableCell>
                      <TableCell>{item.tier1_score?.toFixed(1) || "—"}</TableCell>
                      <TableCell>{item.tier2_score?.toFixed(1) || "—"}</TableCell>
                      <TableCell>{item.tier3_score?.toFixed(1) || "—"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{item.trust_tier || "automated"}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/research/models/${item.model_id}`}>View</Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between">
                <Button
                  variant="outline"
                  disabled={pagination.offset === 0}
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      offset: Math.max(0, prev.offset - prev.limit),
                    }))
                  }
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {Math.floor(pagination.offset / pagination.limit) + 1} of{" "}
                  {Math.ceil(pagination.total / pagination.limit)}
                </span>
                <Button
                  variant="outline"
                  disabled={pagination.offset + pagination.limit >= pagination.total}
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      offset: prev.offset + prev.limit,
                    }))
                  }
                >
                  Next
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
