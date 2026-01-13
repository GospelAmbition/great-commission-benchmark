"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
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
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { apiClient, FilterOptionsResponse } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpDown, BarChart3, Filter, ChevronUp, ChevronDown, ChevronRight, Shield, ShieldAlert, ShieldX, CheckCircle2, HelpCircle, GitCompare } from "lucide-react";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { GuardrailsAnimation } from "@/components/home/GuardrailsAnimation";

interface ScoreRange {
  min_score?: number;
  max_score?: number;
}

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
  test_count: number; // Number of tests averaged
  score_range?: ScoreRange; // Min/max scores when test_count > 1
}

// Helper to determine verdict based on score
function getVerdict(score: number): { label: string; variant: "default" | "secondary" | "destructive" | "outline"; icon: React.ReactNode; className: string } {
  if (score >= 80) {
    return { 
      label: "Excellent", 
      variant: "default", 
      icon: <Shield className="h-3 w-3" />, 
      className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" 
    };
  } else if (score >= 61) {
    return { 
      label: "Good", 
      variant: "secondary", 
      icon: <CheckCircle2 className="h-3 w-3" />, 
      className: "bg-blue-500/20 text-blue-400 border-blue-500/30" 
    };
  } else if (score >= 40) {
    return { 
      label: "Fair", 
      variant: "secondary", 
      icon: <ShieldAlert className="h-3 w-3" />, 
      className: "bg-amber-500/20 text-amber-400 border-amber-500/30" 
    };
  } else {
    return { 
      label: "Poor", 
      variant: "destructive", 
      icon: <ShieldX className="h-3 w-3" />, 
      className: "bg-red-500/20 text-red-400 border-red-500/30" 
    };
  }
}

// Score progress bar component
function ScoreBar({ score, max = 100 }: { score: number; max?: number }) {
  const percentage = (score / max) * 100;
  const color = score >= 80 ? "bg-emerald-500" : score >= 61 ? "bg-blue-500" : score >= 40 ? "bg-amber-500" : "bg-red-500";
  
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-2 bg-white/[0.06] rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-300 rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Tier score display
function TierScore({ score }: { score?: number }) {
  if (score == null) return <span className="text-muted-foreground/50">—</span>;
  
  const color = score >= 80 ? "text-emerald-400" : score >= 61 ? "text-blue-400" : score >= 40 ? "text-amber-400" : "text-red-400";
  return <span className={`text-sm font-medium ${color}`}>{score.toFixed(0)}</span>;
}

// Total Score display with white circle
function TotalScore({ score }: { score: number }) {
  return (
    <div className="flex items-center justify-center">
      <div className="flex items-center justify-center min-w-[3rem] h-12 rounded-full border border-white/60 bg-white/5 hover:bg-white/10 hover:border-white/80 transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md px-4">
        <span className="text-sm font-medium tabular-nums text-foreground px-2">
          {score.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

function LeaderboardContent() {
  const searchParams = useSearchParams();
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set());
  const [filterOptions, setFilterOptions] = useState<FilterOptionsResponse | null>(null);
  const processedUrlParams = useRef<string | null>(null);
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

  // Load filter options on mount
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Pre-select models from URL query params (only on initial load or URL change)
  useEffect(() => {
    const modelsParam = searchParams.get("models");
    // Only process if URL params changed or leaderboard just loaded
    if (modelsParam && leaderboard.length > 0 && modelsParam !== processedUrlParams.current) {
      processedUrlParams.current = modelsParam;
      const modelIds = modelsParam.split(",").map(id => decodeURIComponent(id));
      // Match by either id (UUID) or model_id (OpenRouter-style ID)
      const matchingIds = new Set<string>();
      leaderboard.forEach(item => {
        if (modelIds.includes(item.id) || modelIds.includes(item.model_id)) {
          matchingIds.add(item.id);
        }
      });
      // Update selection if we found matches
      if (matchingIds.size > 0) {
        setSelectedModels(matchingIds);
      }
    }
  }, [searchParams, leaderboard]);

  useEffect(() => {
    loadLeaderboard();
  }, [filters, pagination.offset]);

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
      <div className="relative border-b border-white/[0.06] overflow-x-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-40" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-3xl md:text-4xl font-light text-foreground">Leaderboard</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl font-light">
            Compare AI models and explore benchmark results across all categories
          </p>
        </div>
        
        {/* Guardrails Animation - positioned on right, allowed to overflow */}
        <div className="hidden lg:block absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none">
          <GuardrailsAnimation />
        </div>
      </div>

      <div className="container py-6 space-y-4">
        {/* Model Comparison Instructions */}
        {selectedModels.size === 0 ? (
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/10 shrink-0">
                  <GitCompare className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold text-foreground">Compare Models Side-by-Side</h3>
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Select 2-5 models using the checkboxes in the table below to compare their performance across all benchmark categories. 
                    You'll see detailed side-by-side comparisons of scores, verdicts, and category breakdowns.
                  </p>
                  <div className="flex items-center gap-4 pt-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      <span>Select models using checkboxes</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      <span>Compare up to 5 models at once</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      <span>View detailed comparisons</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-primary/10 border-primary/30">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-lg bg-primary/20">
                    <GitCompare className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-foreground mb-1">
                      {selectedModels.size} model{selectedModels.size > 1 ? "s" : ""} selected for comparison
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedModels.size < 2 
                        ? "Select at least one more model to compare (minimum 2 models required)"
                        : "Click the button below to view detailed side-by-side comparison"}
                    </p>
                  </div>
                </div>
                {selectedModels.size >= 2 && (
                  <Button asChild variant="brand" size="default" className="gap-2">
                    <Link href={`/leaderboard/compare?models=${Array.from(selectedModels).map(id => encodeURIComponent(id)).join(",")}`}>
                      <GitCompare className="h-4 w-4" />
                      Compare {selectedModels.size} Models
                    </Link>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Leaderboard Table */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Model Rankings</CardTitle>
              <Sheet open={filtersOpen} onOpenChange={setFiltersOpen}>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    <Filter className="h-4 w-4" />
                    Filters
                    {(filters.version || filters.category || filters.tier || filters.provider || filters.trust_tier) && (
                      <Badge variant="secondary" className="ml-1 h-5 min-w-5 px-1.5 text-xs">
                        {[
                          filters.version && 1,
                          filters.category && 1,
                          filters.tier && 1,
                          filters.provider && 1,
                          filters.trust_tier && 1,
                        ].filter(Boolean).length}
                      </Badge>
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-full sm:max-w-md">
                  <SheetHeader>
                    <SheetTitle>Filters</SheetTitle>
                    <SheetDescription>
                      Adjust filters to refine the leaderboard results
                    </SheetDescription>
                  </SheetHeader>
                  <div className="mt-6 space-y-6 px-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Version</label>
                      <Select
                        value={filters.version || "all"}
                        onValueChange={(value) =>
                          setFilters((prev) => ({ ...prev, version: value === "all" ? "" : value }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Latest version" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Latest version</SelectItem>
                          {filterOptions?.versions?.map((version) => (
                            <SelectItem key={version} value={version}>
                              v{version}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Provider</label>
                      <Select
                        value={filters.provider || "all"}
                        onValueChange={(value) =>
                          setFilters((prev) => ({ ...prev, provider: value === "all" ? "" : value }))
                        }
                      >
                        <SelectTrigger>
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
                      <label className="text-sm font-medium mb-2 block">Trust Tier</label>
                      <Select
                        value={filters.trust_tier || "all"}
                        onValueChange={(value) =>
                          setFilters((prev) => ({ ...prev, trust_tier: value === "all" ? "" : value }))
                        }
                      >
                        <SelectTrigger>
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
                      <label className="text-sm font-medium mb-2 block">Category</label>
                      <Select
                        value={filters.category || "all"}
                        onValueChange={(value) =>
                          setFilters((prev) => ({ ...prev, category: value === "all" ? "" : value }))
                        }
                      >
                        <SelectTrigger>
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
                      <label className="text-sm font-medium mb-2 block">Tier Focus</label>
                      <Select
                        value={filters.tier || "all"}
                        onValueChange={(value) =>
                          setFilters((prev) => ({ ...prev, tier: value === "all" ? "" : value }))
                        }
                      >
                        <SelectTrigger>
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
                </SheetContent>
              </Sheet>
            </div>
            <CardDescription>
              {pagination.total > 0
                ? `Showing ${pagination.offset + 1}-${Math.min(pagination.offset + pagination.limit, pagination.total)} of ${pagination.total} models • Select 2-5 models to compare`
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
                        <TableHead className="w-10" title="Select models to compare (2-5 models)">
                          <div className="flex items-center gap-1.5">
                            <Checkbox disabled className="border-white/20" />
                            <HelpCircle className="h-3 w-3 text-muted-foreground/60" />
                          </div>
                        </TableHead>
                        <TableHead className="w-14 text-center">#</TableHead>
                        <TableHead>Provider</TableHead>
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
                        <TableHead className="text-center text-xs">
                          <span title="Tier 1: Task Capability (70% weight)">Task</span>
                        </TableHead>
                        <TableHead className="text-center text-xs">
                          <span title="Tier 2: Gospel Core (20% weight)">Gospel</span>
                        </TableHead>
                        <TableHead className="text-center text-xs">
                          <span title="Tier 3: Worldview Confession (10% weight)">Worldview</span>
                        </TableHead>
                        <TableHead>Verdict</TableHead>
                        <TableHead className="min-w-[160px]"></TableHead>
                        <TableHead className="text-center">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSort("score")}
                            className="h-7 px-2 -ml-2 hover:bg-white/5 hover:text-foreground"
                          >
                            Total Score
                            {filters.sort === "score" && (
                              filters.order === "asc" ? <ChevronUp className="ml-1 h-3 w-3" /> : <ChevronDown className="ml-1 h-3 w-3" />
                            )}
                            {filters.sort !== "score" && <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />}
                          </Button>
                        </TableHead>
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
                            <TableCell className="py-3 text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <ProviderIcon provider={item.provider} size={16} />
                                {formatProvider(item.provider)}
                              </div>
                            </TableCell>
                            <TableCell className="py-3">
                              <Link
                                href={`/leaderboard/models/${encodeURIComponent(item.model_id)}`}
                                className="font-medium text-foreground hover:text-primary transition-colors"
                              >
                                {getDisplayModelName(item.model_name, item.model_id)}
                              </Link>
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
                              <ScoreBar score={item.overall_score} />
                            </TableCell>
                            <TableCell className="py-3">
                              <div className="flex items-center gap-2">
                                <TotalScore score={item.overall_score} />
                                {item.test_count > 1 && (
                                  <Badge 
                                    variant="outline" 
                                    className="text-xs bg-white/5 border-white/20 text-muted-foreground"
                                    title={`Average of ${item.test_count} tests${item.score_range ? ` (${item.score_range.min_score?.toFixed(1)}-${item.score_range.max_score?.toFixed(1)}%)` : ''}`}
                                  >
                                    {item.test_count}×
                                  </Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className="py-3">
                              <Button asChild variant="ghost" size="sm" className="h-7 px-2">
                                <Link href={`/leaderboard/models/${encodeURIComponent(item.model_id)}`}>
                                  <ChevronRight className="h-4 w-4" />
                                </Link>
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

        {/* Disclaimer */}
        <div className="flex items-start gap-3 p-3 bg-white/[0.02] rounded-lg border border-white/[0.06]">
          <p className="text-xs text-muted-foreground/70 leading-relaxed">
            <span className="font-medium text-muted-foreground">Disclaimer:</span> This benchmark is for informational purposes only and does not 
            constitute an endorsement or recommendation of any AI model or service. Results reflect 
            performance on specific test questions at a point in time and may not predict performance 
            on other tasks or future model versions.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LeaderboardPage() {
  return (
    <Suspense fallback={
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    }>
      <LeaderboardContent />
    </Suspense>
  );
}
