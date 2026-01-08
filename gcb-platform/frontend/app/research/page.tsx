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
import { Progress } from "@/components/ui/progress";
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
import { ArrowUpDown, BarChart3, Filter, AlertTriangle, ChevronUp, ChevronDown, Shield, ShieldAlert, ShieldX } from "lucide-react";
import { BenchmarkHelpIcon } from "@/components/benchmark";

interface LeaderboardItem {
  id: string; // UUID for API operations (compare)
  model_id: string; // OpenRouter-style ID for display/routing
  model_name: string;
  provider: string;
  overall_score: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  trust_tier?: string;
  test_count?: number;
}

// Helper to determine verdict based on score
function getVerdict(score: number): { label: string; variant: "default" | "secondary" | "destructive" | "outline"; icon: React.ReactNode; color: string } {
  if (score >= 75) {
    return { label: "Aligned", variant: "default", icon: <Shield className="h-3 w-3" />, color: "bg-green-600" };
  } else if (score >= 50) {
    return { label: "Caution", variant: "secondary", icon: <ShieldAlert className="h-3 w-3" />, color: "bg-yellow-500" };
  } else {
    return { label: "Compromised", variant: "destructive", icon: <ShieldX className="h-3 w-3" />, color: "bg-red-600" };
  }
}

// Score progress bar component
function ScoreBar({ score, max = 100 }: { score: number; max?: number }) {
  const percentage = (score / max) * 100;
  const color = score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  
  return (
    <div className="flex items-center gap-2 min-w-[100px]">
      <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-medium tabular-nums w-10 text-right">{score.toFixed(1)}</span>
    </div>
  );
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
    model_type: "", // "open_source" | "proprietary" | ""
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

  function toggleModelSelection(id: string) {
    const newSelected = new Set(selectedModels);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else if (newSelected.size < 5) {
      newSelected.add(id);
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
    <div className="flex flex-col">
      {/* Page Header */}
      <div 
        className="border-b border-red-900/20"
        style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
      >
        <div className="container py-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-white/10">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">Research</h1>
          </div>
          <p className="text-white/80">
            Explore benchmark results, compare models, and dive deep into performance data
          </p>
        </div>
      </div>

      <div className="container py-6 space-y-4">
        {/* Filters */}
        <Card className="bg-white">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-slate-500" />
              <CardTitle className="text-base text-slate-900">Filters</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
              <div>
                <label className="text-xs font-medium mb-1.5 block text-slate-500">Provider</label>
                <Select
                  value={filters.provider || "all"}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, provider: value === "all" ? "" : value }))
                  }
                >
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="All providers" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All providers</SelectItem>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="anthropic">Anthropic</SelectItem>
                    <SelectItem value="google">Google</SelectItem>
                    <SelectItem value="meta">Meta</SelectItem>
                    <SelectItem value="mistral">Mistral</SelectItem>
                    <SelectItem value="cohere">Cohere</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium mb-1.5 block text-slate-500">Model Type</label>
                <Select
                  value={filters.model_type || "all"}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, model_type: value === "all" ? "" : value }))
                  }
                >
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All types</SelectItem>
                    <SelectItem value="open_source">Open Source</SelectItem>
                    <SelectItem value="proprietary">Proprietary</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium mb-1.5 block text-slate-500">Trust Tier</label>
                <Select
                  value={filters.trust_tier || "all"}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, trust_tier: value === "all" ? "" : value }))
                  }
                >
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="All tiers" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All tiers</SelectItem>
                    <SelectItem value="automated">Automated</SelectItem>
                    <SelectItem value="reviewed">Reviewed</SelectItem>
                    <SelectItem value="validated">Validated</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium mb-1.5 block text-slate-500">Category</label>
                <Select
                  value={filters.category || "all"}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, category: value === "all" ? "" : value }))
                  }
                >
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    <SelectItem value="scripture">Scripture</SelectItem>
                    <SelectItem value="theology">Theology</SelectItem>
                    <SelectItem value="ethics">Ethics</SelectItem>
                    <SelectItem value="apologetics">Apologetics</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium mb-1.5 block text-slate-500">Tier Focus</label>
                <Select
                  value={filters.tier || "all"}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, tier: value === "all" ? "" : value }))
                  }
                >
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="All tiers" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All tiers</SelectItem>
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
          <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
            <span className="text-sm font-medium text-red-800">
              {selectedModels.size} model{selectedModels.size > 1 ? "s" : ""} selected
            </span>
            <Button asChild variant="brand" size="sm">
              <Link href={`/research/compare?models=${Array.from(selectedModels).map(id => encodeURIComponent(id)).join(",")}`}>
                Compare Models
              </Link>
            </Button>
          </div>
        )}

        {/* Disclaimer */}
        <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border-l-4 border-red-700">
          <AlertTriangle className="h-4 w-4 text-red-700 mt-0.5 shrink-0" />
          <p className="text-xs text-slate-600 leading-relaxed">
            <span className="font-semibold text-slate-900">Disclaimer:</span> This benchmark is for informational purposes only and does not 
            constitute an endorsement or recommendation of any AI model or service. Results reflect 
            performance on specific test questions at a point in time and may not predict performance 
            on other tasks or future model versions.
          </p>
        </div>

        {/* Leaderboard Table */}
        <Card className="bg-white">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg text-slate-900">Leaderboard</CardTitle>
              <BenchmarkHelpIcon size="default" />
            </div>
            <CardDescription className="text-slate-600">
              {pagination.total > 0
                ? `Showing ${pagination.offset + 1}-${Math.min(pagination.offset + pagination.limit, pagination.total)} of ${pagination.total} models`
                : "No models to display"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : leaderboard.length === 0 ? (
              <div className="text-center py-10">
                <div className="w-12 h-12 rounded-full bg-slate-100 mx-auto mb-3 flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-slate-400" />
                </div>
                <p className="text-base font-medium text-slate-900 mb-1">No benchmark results available yet</p>
                <p className="text-sm text-slate-600">
                  Check back soon as we continue to evaluate AI models on the Great Commission Benchmark.
                </p>
              </div>
            ) : (
              <>
                <div className="rounded-lg border overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-slate-50 hover:bg-slate-50">
                        <TableHead className="w-10">
                          <Checkbox disabled />
                        </TableHead>
                        <TableHead className="w-14 text-center text-slate-600">#</TableHead>
                        <TableHead>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSort("model_name")}
                            className="h-7 px-2 -ml-2 text-slate-700 hover:bg-transparent hover:text-red-700"
                          >
                            Model
                            {filters.sort === "model_name" && (
                              filters.order === "asc" ? <ChevronUp className="ml-1 h-3 w-3" /> : <ChevronDown className="ml-1 h-3 w-3" />
                            )}
                            {filters.sort !== "model_name" && <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />}
                          </Button>
                        </TableHead>
                        <TableHead className="text-slate-600">Provider</TableHead>
                        <TableHead className="min-w-[140px]">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSort("score")}
                            className="h-7 px-2 -ml-2 text-slate-700 hover:bg-transparent hover:text-red-700"
                          >
                            GCB Score
                            {filters.sort === "score" && (
                              filters.order === "asc" ? <ChevronUp className="ml-1 h-3 w-3" /> : <ChevronDown className="ml-1 h-3 w-3" />
                            )}
                            {filters.sort !== "score" && <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />}
                          </Button>
                        </TableHead>
                        <TableHead className="text-center text-slate-600 text-xs">
                          <span title="Tier 1: Task Capability (70% weight) - Categories 3.1-3.7">Task</span>
                        </TableHead>
                        <TableHead className="text-center text-slate-600 text-xs">
                          <span title="Tier 2: Doctrinal Fidelity (20% weight) - Categories 4.1-4.6">Doctrine</span>
                        </TableHead>
                        <TableHead className="text-center text-slate-600 text-xs">
                          <span title="Tier 3: Worldview Confession (10% weight) - Categories 5.1-5.6">Worldview</span>
                        </TableHead>
                        <TableHead className="text-slate-600">Verdict</TableHead>
                        <TableHead className="text-slate-600">Trust</TableHead>
                        <TableHead className="w-16"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {leaderboard.map((item, index) => {
                        const verdict = getVerdict(item.overall_score);
                        return (
                          <TableRow key={`${item.model_id}-${index}`} className="group">
                            <TableCell className="py-2">
                              <Checkbox
                                checked={selectedModels.has(item.id)}
                                onCheckedChange={() => toggleModelSelection(item.id)}
                                disabled={!selectedModels.has(item.id) && selectedModels.size >= 5}
                              />
                            </TableCell>
                            <TableCell className="py-2 text-center font-bold text-slate-400">
                              {pagination.offset + index + 1}
                            </TableCell>
                            <TableCell className="py-2">
                              <Link
                                href={`/research/models/${encodeURIComponent(item.model_id)}`}
                                className="font-medium text-slate-900 hover:text-red-700 transition-colors"
                              >
                                {item.model_name}
                              </Link>
                            </TableCell>
                            <TableCell className="py-2">
                              <Badge variant="secondary" className="font-normal bg-slate-100 text-slate-700">{item.provider}</Badge>
                            </TableCell>
                            <TableCell className="py-2">
                              <ScoreBar score={item.overall_score} />
                            </TableCell>
                            <TableCell className="py-2 text-center">
                              {item.tier1_score != null ? (
                                <span className={`text-sm font-medium ${item.tier1_score >= 75 ? "text-green-600" : item.tier1_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                                  {item.tier1_score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-slate-300">—</span>
                              )}
                            </TableCell>
                            <TableCell className="py-2 text-center">
                              {item.tier2_score != null ? (
                                <span className={`text-sm font-medium ${item.tier2_score >= 75 ? "text-green-600" : item.tier2_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                                  {item.tier2_score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-slate-300">—</span>
                              )}
                            </TableCell>
                            <TableCell className="py-2 text-center">
                              {item.tier3_score != null ? (
                                <span className={`text-sm font-medium ${item.tier3_score >= 75 ? "text-green-600" : item.tier3_score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                                  {item.tier3_score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-slate-300">—</span>
                              )}
                            </TableCell>
                            <TableCell className="py-2">
                              <Badge 
                                variant={verdict.variant}
                                className={`text-xs gap-1 ${verdict.variant === "default" ? "bg-green-600 hover:bg-green-700" : verdict.variant === "destructive" ? "" : "bg-yellow-500 hover:bg-yellow-600 text-white"}`}
                              >
                                {verdict.icon}
                                {verdict.label}
                              </Badge>
                            </TableCell>
                            <TableCell className="py-2">
                              <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">{item.trust_tier || "automated"}</Badge>
                            </TableCell>
                            <TableCell className="py-2">
                              <Button asChild variant="ghost" size="sm" className="h-7 px-2 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Link href={`/research/models/${encodeURIComponent(item.model_id)}`}>View</Link>
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination */}
                <div className="mt-4 flex items-center justify-between">
                  <Button
                    variant="outline"
                    size="sm"
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
                  <span className="text-sm text-slate-600">
                    Page {Math.floor(pagination.offset / pagination.limit) + 1} of{" "}
                    {Math.ceil(pagination.total / pagination.limit) || 1}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
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
    </div>
  );
}
