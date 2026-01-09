"use client";

import { useEffect, useState, useCallback } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient, FilterOptionsResponse } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpDown, BarChart3, Filter, AlertTriangle, ChevronUp, ChevronDown, Shield, ShieldAlert, ShieldX, Grid3X3, List } from "lucide-react";
import { BenchmarkHelpIcon } from "@/components/benchmark";
import { CategoryRankingCard, type CategoryModel } from "@/components/research";
import {
  TIER_CATEGORIES,
  CATEGORY_NAMES,
  CATEGORY_DESCRIPTIONS,
  getTierForCategory,
} from "@/lib/benchmark-definitions";

interface LeaderboardItem {
  id: string;
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

interface CategoryRankingData {
  categoryCode: string;
  models: CategoryModel[];
  totalModels: number;
}

// Helper to determine verdict based on score
function getVerdict(score: number): { label: string; variant: "default" | "secondary" | "destructive" | "outline"; icon: React.ReactNode; className: string } {
  if (score >= 75) {
    return { 
      label: "Aligned", 
      variant: "default", 
      icon: <Shield className="h-3 w-3" />, 
      className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" 
    };
  } else if (score >= 50) {
    return { 
      label: "Caution", 
      variant: "secondary", 
      icon: <ShieldAlert className="h-3 w-3" />, 
      className: "bg-amber-500/20 text-amber-400 border-amber-500/30" 
    };
  } else {
    return { 
      label: "Compromised", 
      variant: "destructive", 
      icon: <ShieldX className="h-3 w-3" />, 
      className: "bg-red-500/20 text-red-400 border-red-500/30" 
    };
  }
}

// Score progress bar component
function ScoreBar({ score, max = 100 }: { score: number; max?: number }) {
  const percentage = (score / max) * 100;
  const color = score >= 75 ? "bg-emerald-500" : score >= 50 ? "bg-amber-500" : "bg-red-500";
  
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-2 bg-white/[0.06] rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-300 rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-medium tabular-nums w-10 text-right text-foreground">{score.toFixed(1)}</span>
    </div>
  );
}

// Tier score display
function TierScore({ score }: { score?: number }) {
  if (score == null) return <span className="text-muted-foreground/50">—</span>;
  
  const color = score >= 75 ? "text-emerald-400" : score >= 50 ? "text-amber-400" : "text-red-400";
  return <span className={`text-sm font-medium ${color}`}>{score.toFixed(0)}</span>;
}

// Get all category codes in order
function getAllCategoryCodes(): string[] {
  return [
    ...TIER_CATEGORIES[1],
    ...TIER_CATEGORIES[2],
    ...TIER_CATEGORIES[3],
  ];
}

export default function ResearchPage() {
  const [activeTab, setActiveTab] = useState("leaderboard");
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set());
  const [filterOptions, setFilterOptions] = useState<FilterOptionsResponse | null>(null);
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

  // Category rankings state
  const [categoryRankings, setCategoryRankings] = useState<Record<string, CategoryRankingData>>({});
  const [categoryRankingsLoading, setCategoryRankingsLoading] = useState(false);
  const [categoryRankingsLoaded, setCategoryRankingsLoaded] = useState(false);

  // Load filter options on mount
  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    loadLeaderboard();
  }, [filters, pagination.offset]);

  // Load category rankings when switching to that tab
  useEffect(() => {
    if (activeTab === "categories" && !categoryRankingsLoaded && !categoryRankingsLoading) {
      loadCategoryRankings();
    }
  }, [activeTab, categoryRankingsLoaded, categoryRankingsLoading]);

  async function loadFilterOptions() {
    try {
      const options = await apiClient.getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error("Failed to load filter options:", error);
    }
  }

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

  const loadCategoryRankings = useCallback(async () => {
    setCategoryRankingsLoading(true);
    try {
      const allCategories = getAllCategoryCodes();
      
      // Fetch all categories in parallel
      const results = await Promise.all(
        allCategories.map(async (categoryCode) => {
          try {
            const result = await apiClient.getLeaderboard({
              category: categoryCode,
              limit: 5,
              sort: "score",
              order: "desc",
            });
            return {
              categoryCode,
              models: (result.items || []).map((item: any) => ({
                model_id: item.model_id,
                model_name: item.model_name,
                provider: item.provider,
                // Use category-specific score if available, fallback to overall
                score: item.category_scores?.[categoryCode] ?? item.overall_score,
              })),
              totalModels: result.total || 0,
            };
          } catch (error) {
            console.error(`Failed to load category ${categoryCode}:`, error);
            return {
              categoryCode,
              models: [],
              totalModels: 0,
            };
          }
        })
      );

      // Convert to record
      const rankingsMap: Record<string, CategoryRankingData> = {};
      results.forEach((result) => {
        rankingsMap[result.categoryCode] = result;
      });
      
      setCategoryRankings(rankingsMap);
      setCategoryRankingsLoaded(true);
    } catch (error) {
      console.error("Failed to load category rankings:", error);
    } finally {
      setCategoryRankingsLoading(false);
    }
  }, []);

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
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-20" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Research</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl">
            Explore benchmark results, compare models, and dive deep into performance data
          </p>
        </div>
      </div>

      <div className="container py-6 space-y-4">
        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="leaderboard" className="gap-2">
              <List className="h-4 w-4" />
              Leaderboard
            </TabsTrigger>
            <TabsTrigger value="categories" className="gap-2">
              <Grid3X3 className="h-4 w-4" />
              Category Rankings
            </TabsTrigger>
          </TabsList>

          {/* Leaderboard Tab */}
          <TabsContent value="leaderboard" className="space-y-4 mt-4">
            {/* Filters */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <CardTitle className="text-base">Filters</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <label className="text-xs font-medium mb-1.5 block text-muted-foreground">Provider</label>
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
                        {filterOptions?.providers.map((provider) => (
                          <SelectItem key={provider} value={provider}>
                            {provider.charAt(0).toUpperCase() + provider.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-medium mb-1.5 block text-muted-foreground">Trust Tier</label>
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
                        {filterOptions?.trust_tiers.map((tier) => (
                          <SelectItem key={tier} value={tier}>
                            {tier.charAt(0).toUpperCase() + tier.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-medium mb-1.5 block text-muted-foreground">Category</label>
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
                        {filterOptions?.categories.map((category) => (
                          <SelectItem key={category} value={category}>
                            {category.charAt(0).toUpperCase() + category.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-medium mb-1.5 block text-muted-foreground">Tier Focus</label>
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
                        {filterOptions?.tiers.map((tier) => (
                          <SelectItem key={tier.value} value={tier.value}>
                            {tier.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Compare Button */}
            {selectedModels.size > 0 && (
              <div className="flex items-center gap-3 p-3 bg-primary/10 rounded-lg border border-primary/20">
                <span className="text-sm font-medium text-primary">
                  {selectedModels.size} model{selectedModels.size > 1 ? "s" : ""} selected
                </span>
                <Button asChild variant="brand" size="sm">
                  <Link href={`/research/compare?models=${Array.from(selectedModels).map(id => encodeURIComponent(id)).join(",")}`}>
                    Compare Models
                  </Link>
                </Button>
              </div>
            )}

            {/* Leaderboard Table */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Leaderboard</CardTitle>
                  <BenchmarkHelpIcon size="default" />
                </div>
                <CardDescription>
                  {pagination.total > 0
                    ? `Showing ${pagination.offset + 1}-${Math.min(pagination.offset + pagination.limit, pagination.total)} of ${pagination.total} models`
                    : "No models to display"}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                {loading ? (
                  <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-12 w-full" />
                    ))}
                  </div>
                ) : leaderboard.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-12 h-12 rounded-full bg-white/[0.06] mx-auto mb-3 flex items-center justify-center">
                      <BarChart3 className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <p className="text-base font-medium text-foreground mb-1">No benchmark results available yet</p>
                    <p className="text-sm text-muted-foreground">
                      Check back soon as we continue to evaluate AI models on the Great Commission Benchmark.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="rounded-lg border border-white/[0.08] overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-white/[0.02] hover:bg-white/[0.02] border-white/[0.08]">
                            <TableHead className="w-10">
                              <Checkbox disabled className="border-white/20" />
                            </TableHead>
                            <TableHead className="w-14 text-center">#</TableHead>
                            <TableHead>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleSort("model_name")}
                                className="h-7 px-2 -ml-2 hover:bg-white/5 hover:text-foreground"
                              >
                                Model
                                {filters.sort === "model_name" && (
                                  filters.order === "asc" ? <ChevronUp className="ml-1 h-3 w-3" /> : <ChevronDown className="ml-1 h-3 w-3" />
                                )}
                                {filters.sort !== "model_name" && <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />}
                              </Button>
                            </TableHead>
                            <TableHead>Provider</TableHead>
                            <TableHead className="min-w-[160px]">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleSort("score")}
                                className="h-7 px-2 -ml-2 hover:bg-white/5 hover:text-foreground"
                              >
                                GCB Score
                                {filters.sort === "score" && (
                                  filters.order === "asc" ? <ChevronUp className="ml-1 h-3 w-3" /> : <ChevronDown className="ml-1 h-3 w-3" />
                                )}
                                {filters.sort !== "score" && <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />}
                              </Button>
                            </TableHead>
                            <TableHead className="text-center text-xs">
                              <span title="Tier 1: Task Capability (70% weight)">Task</span>
                            </TableHead>
                            <TableHead className="text-center text-xs">
                              <span title="Tier 2: Gospel Core (20% weight)">Gospel Core</span>
                            </TableHead>
                            <TableHead className="text-center text-xs">
                              <span title="Tier 3: Worldview Confession (10% weight)">Worldview</span>
                            </TableHead>
                            <TableHead>Verdict</TableHead>
                            <TableHead>Trust</TableHead>
                            <TableHead className="w-16"></TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {leaderboard.map((item, index) => {
                            const verdict = getVerdict(item.overall_score);
                            return (
                              <TableRow key={`${item.model_id}-${index}`} className="group">
                                <TableCell className="py-3">
                                  <Checkbox
                                    checked={selectedModels.has(item.id)}
                                    onCheckedChange={() => toggleModelSelection(item.id)}
                                    disabled={!selectedModels.has(item.id) && selectedModels.size >= 5}
                                    className="border-white/20"
                                  />
                                </TableCell>
                                <TableCell className="py-3 text-center font-bold text-muted-foreground">
                                  {pagination.offset + index + 1}
                                </TableCell>
                                <TableCell className="py-3">
                                  <Link
                                    href={`/research/models/${encodeURIComponent(item.model_id)}`}
                                    className="font-medium text-foreground hover:text-primary transition-colors"
                                  >
                                    {getDisplayModelName(item.model_name, item.model_id)}
                                  </Link>
                                </TableCell>
                                <TableCell className="py-3 text-muted-foreground">
                                  {formatProvider(item.provider)}
                                </TableCell>
                                <TableCell className="py-3">
                                  <ScoreBar score={item.overall_score} />
                                </TableCell>
                                <TableCell className="py-3 text-center">
                                  <TierScore score={item.tier1_score} />
                                </TableCell>
                                <TableCell className="py-3 text-center">
                                  <TierScore score={item.tier2_score} />
                                </TableCell>
                                <TableCell className="py-3 text-center">
                                  <TierScore score={item.tier3_score} />
                                </TableCell>
                                <TableCell className="py-3">
                                  <Badge className={`${verdict.className} border`}>
                                    {verdict.icon}
                                    <span className="ml-1">{verdict.label}</span>
                                  </Badge>
                                </TableCell>
                                <TableCell className="py-3">
                                  <Badge variant="outline">{item.trust_tier || "automated"}</Badge>
                                </TableCell>
                                <TableCell className="py-3">
                                  <Button asChild variant="ghost" size="sm" className="h-7 px-2 opacity-0 group-hover:opacity-100 transition-opacity">
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
                      <span className="text-sm text-muted-foreground">
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
          </TabsContent>

          {/* Category Rankings Tab */}
          <TabsContent value="categories" className="space-y-6 mt-4">
            {categoryRankingsLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                  <Skeleton key={i} className="h-64" />
                ))}
              </div>
            ) : (
              <>
                {/* Tier 1: Task Capability */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-semibold text-foreground">Task Capability</h2>
                    <Badge variant="outline" className="bg-red-500/10 text-red-400 border-transparent">
                      70% weight
                    </Badge>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {TIER_CATEGORIES[1].map((categoryCode) => {
                      const data = categoryRankings[categoryCode];
                      return (
                        <CategoryRankingCard
                          key={categoryCode}
                          categoryCode={categoryCode}
                          categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                          description={CATEGORY_DESCRIPTIONS[categoryCode]}
                          tier={1}
                          models={data?.models || []}
                          totalModels={data?.totalModels}
                        />
                      );
                    })}
                  </div>
                </div>

                {/* Tier 2: Gospel Core */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-semibold text-foreground">Gospel Core</h2>
                    <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-transparent">
                      20% weight
                    </Badge>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {TIER_CATEGORIES[2].map((categoryCode) => {
                      const data = categoryRankings[categoryCode];
                      return (
                        <CategoryRankingCard
                          key={categoryCode}
                          categoryCode={categoryCode}
                          categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                          description={CATEGORY_DESCRIPTIONS[categoryCode]}
                          tier={2}
                          models={data?.models || []}
                          totalModels={data?.totalModels}
                        />
                      );
                    })}
                  </div>
                </div>

                {/* Tier 3: Worldview Confession */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-semibold text-foreground">Worldview Confession</h2>
                    <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-transparent">
                      10% weight
                    </Badge>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {TIER_CATEGORIES[3].map((categoryCode) => {
                      const data = categoryRankings[categoryCode];
                      return (
                        <CategoryRankingCard
                          key={categoryCode}
                          categoryCode={categoryCode}
                          categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                          description={CATEGORY_DESCRIPTIONS[categoryCode]}
                          tier={3}
                          models={data?.models || []}
                          totalModels={data?.totalModels}
                        />
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>

        {/* Disclaimer */}
        <div className="flex items-start gap-3 p-3 bg-amber-500/5 rounded-lg border-l-2 border-amber-500">
          <AlertTriangle className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />
          <p className="text-xs text-muted-foreground leading-relaxed">
            <span className="font-semibold text-foreground">Disclaimer:</span> This benchmark is for informational purposes only and does not 
            constitute an endorsement or recommendation of any AI model or service. Results reflect 
            performance on specific test questions at a point in time and may not predict performance 
            on other tasks or future model versions.
          </p>
        </div>
      </div>
    </div>
  );
}
