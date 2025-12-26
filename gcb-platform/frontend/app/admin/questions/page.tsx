"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";
import { toast } from "sonner";

interface Question {
  id: string;
  content: string;
  tier: number; // 1, 2, or 3
  category: string;
  question_set_id?: string;
  status?: "draft" | "pending" | "approved" | "rejected";
  created_at?: string;
  updated_at?: string;
  metadata?: {
    difficulty?: string;
    [key: string]: unknown;
  };
}

interface Version {
  id: string;
  semantic_version: string;
  marketing_version: string;
  status: string;
  created_at: string;
}

interface VersionStats {
  question_set_id: string;
  semantic_version: string;
  marketing_version: string;
  total_questions: number;
  target_total: number;
  tier_stats: {
    [key: number]: {
      count: number;
      target: number;
      categories: {
        [key: string]: {
          count: number;
          target: number;
        };
      };
    };
  };
  difficulty_stats?: {
    easy: { count: number; percentage: number };
    medium: { count: number; percentage: number };
    hard: { count: number; percentage: number };
  };
}

export default function AdminQuestionsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [versions, setVersions] = useState<Version[]>([]);
  const [versionFilter, setVersionFilter] = useState<string>("");
  const [versionStats, setVersionStats] = useState<VersionStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [search, setSearch] = useState("");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [difficultyFilter, setDifficultyFilter] = useState<string>("all");
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [editedContent, setEditedContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [importVersionId, setImportVersionId] = useState<string>("");
  const [importPreview, setImportPreview] = useState<{
    dry_run: boolean;
    file_type: string;
    total_questions: number;
    tier_counts: Record<number, number>;
    category_counts: Record<string, number>;
    difficulty_counts: Record<string, number>;
    parse_errors: Array<{ row: number; field: string; message: string }>;
    sample_questions: Array<{
      content: string;
      tier: number;
      category: string;
      difficulty?: string;
    }>;
  } | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [showAll, setShowAll] = useState(false);
  const pageSize = 100;

  const categories = [
    "scripture",
    "theology",
    "ethics",
    "apologetics",
    "evangelism",
    "discipleship",
    "missions",
    "prayer",
    "worldview",
  ];

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadVersions();
    }
  }, [user, userLoading, router]);

  useEffect(() => {
    if (versionFilter) {
      setCurrentPage(1); // Reset to first page when version changes
      setShowAll(false); // Reset show all when version changes
      loadQuestions(1, false);
      loadVersionStats();
    }
  }, [versionFilter]);

  useEffect(() => {
    if (versionFilter && currentPage > 1 && !showAll) {
      loadQuestions(currentPage, false);
    }
  }, [currentPage]);

  useEffect(() => {
    if (versionFilter && showAll) {
      loadQuestions(1, true);
    }
  }, [showAll]);

  async function loadVersions() {
    try {
      const response = await fetch("/api/admin/question-sets");
      if (response.ok) {
        const data = await response.json();
        const versionList = (data.items || []).map((qs: any) => ({
          id: qs.id,
          semantic_version: qs.semantic_version,
          marketing_version: qs.marketing_version,
          status: qs.status,
          created_at: qs.created_at,
        }));
        setVersions(versionList);
        
        // Set default to active version or most recent draft
        if (!versionFilter && versionList.length > 0) {
          const activeVersion = versionList.find((v: Version) => v.status === "active");
          const draftVersion = versionList.find((v: Version) => v.status === "draft");
          const defaultVersion = activeVersion || draftVersion || versionList[0];
          if (defaultVersion) {
            setVersionFilter(defaultVersion.semantic_version);
          } else {
            // No default version found, stop loading
            setLoading(false);
          }
        } else if (versionList.length === 0) {
          // No versions available, stop loading
          setLoading(false);
        }
      } else {
        // API error, stop loading
        setLoading(false);
      }
    } catch (error) {
      console.error("Failed to load versions:", error);
      setLoading(false);
    }
  }

  async function loadVersionStats() {
    if (!versionFilter) return;
    
    setLoadingStats(true);
    try {
      const response = await fetch(`/api/admin/versions/${versionFilter}/stats`);
      if (response.ok) {
        const data = await response.json();
        setVersionStats(data);
      }
    } catch (error) {
      console.error("Failed to load version stats:", error);
    } finally {
      setLoadingStats(false);
    }
  }

  async function loadQuestions(page: number = 1, loadAll: boolean = false) {
    if (!versionFilter) return;
    
    setLoading(true);
    const offset = loadAll ? 0 : (page - 1) * pageSize;
    const limit = loadAll ? 500 : pageSize; // Backend max is 500
    
    try {
      // Get question_set_id from versions list
      const selectedVersion = versions.find(v => v.semantic_version === versionFilter);
      if (!selectedVersion) {
        // If not in versions list, fetch from API
        const questionSetsResponse = await fetch("/api/admin/question-sets");
        if (questionSetsResponse.ok) {
          const questionSetsData = await questionSetsResponse.json();
          const selectedQuestionSet = questionSetsData.items?.find(
            (qs: { semantic_version: string }) => qs.semantic_version === versionFilter
          );
          
          if (selectedQuestionSet) {
            const response = await fetch(
              `/api/admin/questions?question_set_id=${selectedQuestionSet.id}&limit=${limit}&offset=${offset}`
            );
            if (response.ok) {
              const data = await response.json();
              setQuestions(data.items || []);
              setTotalQuestions(data.total || 0);
            }
          }
        }
      } else {
        const response = await fetch(
          `/api/admin/questions?question_set_id=${selectedVersion.id}&limit=${limit}&offset=${offset}`
        );
        if (response.ok) {
          const data = await response.json();
          setQuestions(data.items || []);
          setTotalQuestions(data.total || 0);
        }
      }
    } catch (error) {
      console.error("Failed to load questions:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveQuestion() {
    if (!selectedQuestion) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/admin/questions/${selectedQuestion.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: editedContent }),
      });

      if (response.ok) {
        toast.success("Question updated");
        setSelectedQuestion(null);
        loadQuestions(currentPage, showAll);
      } else {
        throw new Error("Failed to update");
      }
    } catch (error) {
      console.error("Failed to update question:", error);
      toast.error("Failed to update question");
    } finally {
      setSaving(false);
    }
  }

  async function handleApproveQuestion(id: string) {
    try {
      const response = await fetch(`/api/admin/questions/${id}/approve`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success("Question approved");
        loadQuestions(currentPage, showAll);
      } else {
        throw new Error("Failed to approve");
      }
    } catch (error) {
      console.error("Failed to approve question:", error);
      toast.error("Failed to approve question");
    }
  }

  async function handleRejectQuestion(id: string) {
    try {
      const response = await fetch(`/api/admin/questions/${id}/reject`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success("Question rejected");
        loadQuestions(currentPage, showAll);
      } else {
        throw new Error("Failed to reject");
      }
    } catch (error) {
      console.error("Failed to reject question:", error);
      toast.error("Failed to reject question");
    }
  }

  async function handleImportPreview() {
    if (!importFile) return;
    setLoadingPreview(true);
    setImportPreview(null);
    try {
      const formData = new FormData();
      formData.append("file", importFile);
      formData.append("dry_run", "true");
      if (importVersionId) {
        formData.append("question_set_id", importVersionId);
      }

      const response = await fetch("/api/admin/questions/import", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setImportPreview(result);
      } else {
        const error = await response.json().catch(() => ({ error: "Preview failed" }));
        toast.error(error.error || "Failed to preview file");
      }
    } catch (error) {
      console.error("Failed to preview import:", error);
      toast.error("Failed to preview import");
    } finally {
      setLoadingPreview(false);
    }
  }

  async function handleImport() {
    if (!importFile) return;
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", importFile);
      if (importVersionId) {
        formData.append("question_set_id", importVersionId);
      }

      const response = await fetch("/api/admin/questions/import", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`Imported ${result.imported} questions from ${result.file_type?.toUpperCase() || 'file'}`);
        setShowImportDialog(false);
        setImportFile(null);
        setImportPreview(null);
        setImportVersionId("");
        setCurrentPage(1);
        setShowAll(false);
        loadQuestions(1, false);
        loadVersionStats();
      } else {
        const error = await response.json().catch(() => ({ error: "Import failed" }));
        toast.error(error.error || "Failed to import questions");
      }
    } catch (error) {
      console.error("Failed to import questions:", error);
      toast.error("Failed to import questions");
    } finally {
      setImporting(false);
    }
  }

  function resetImportDialog() {
    setShowImportDialog(false);
    setImportFile(null);
    setImportPreview(null);
    setImportVersionId("");
  }

  const filteredQuestions = questions.filter((q) => {
    if (search && !q.content.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (tierFilter !== "all") {
      const tierNum = parseInt(tierFilter.replace("tier", ""));
      if (q.tier !== tierNum) return false;
    }
    if (categoryFilter !== "all" && q.category !== categoryFilter) return false;
    if (statusFilter !== "all" && q.status !== statusFilter) return false;
    if (difficultyFilter !== "all" && q.metadata?.difficulty !== difficultyFilter) return false;
    return true;
  });

  const tierCounts = questions.reduce((acc, q) => {
    const tierKey = `tier${q.tier}`;
    acc[tierKey] = (acc[tierKey] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const getTierProgress = (tier: number) => {
    if (!versionStats) return { current: 0, target: 0, percent: 0 };
    const stats = versionStats.tier_stats[tier];
    if (!stats) return { current: 0, target: 0, percent: 0 };
    return {
      current: stats.count,
      target: stats.target,
      percent: stats.target > 0 ? Math.round((stats.count / stats.target) * 100) : 0,
    };
  };

  const getCategoryName = (category: string) => {
    const categoryMap: Record<string, string> = {
      "3.1": "Missiological Research",
      "3.2": "Evangelistic Material",
      "3.3": "Apologetics",
      "3.4": "Conversational AI",
      "3.5": "Intercessory Prayer",
      "3.6": "Problematic Vocabulary",
      "3.7": "Difficult Passages",
      "4.1": "Exclusivity of Jesus",
      "4.2": "Universality of Sin",
      "4.3": "Reality of Judgment",
      "4.4": "Lordship of Jesus",
      "4.5": "Call to Repentance",
      "4.6": "Burden to Make Disciples",
      "5.1": "Existence of God",
      "5.2": "Historical Jesus",
      "5.3": "The Crucifixion",
      "5.4": "The Resurrection",
      "5.5": "Universal Sinfulness",
      "5.6": "Salvation Through Faith",
    };
    return categoryMap[category] || category;
  };


  if (userLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Show loading skeleton only while fetching data with a version selected
  if (loading && versionFilter) {
    return (
      <div className="container py-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Question Management</h1>
            <p className="mt-2 text-muted-foreground">
              Manage benchmark questions
            </p>
          </div>
          <Button onClick={() => setShowImportDialog(true)}>
            Import Questions
          </Button>
        </div>
      </div>

      {/* Version Selector - Always visible */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Version</CardTitle>
        </CardHeader>
        <CardContent>
          {versions.length === 0 ? (
            <div className="text-muted-foreground">
              <p>No question sets available.</p>
              <p className="text-sm mt-2">
                Create a question set in the <Link href="/admin/versions" className="text-primary underline">Versions</Link> page first.
              </p>
            </div>
          ) : (
            <Select value={versionFilter} onValueChange={setVersionFilter}>
              <SelectTrigger className="w-full md:w-64">
                <SelectValue placeholder="Select version" />
              </SelectTrigger>
              <SelectContent>
                {versions.map((v) => (
                  <SelectItem key={v.id} value={v.semantic_version}>
                    {v.semantic_version} - {v.marketing_version}
                    {v.status === "active" && " (Active)"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </CardContent>
      </Card>

      {/* Tabbed Content */}
      {versionFilter && (
        <Tabs defaultValue="questions" className="space-y-6">
          <TabsList>
            <TabsTrigger value="questions">Questions</TabsTrigger>
            <TabsTrigger value="question-stats">Question Statistics</TabsTrigger>
            <TabsTrigger value="category-stats">Category Statistics</TabsTrigger>
          </TabsList>

          {/* Question Statistics Tab */}
          <TabsContent value="question-stats">
            {versionStats ? (
              <div className="space-y-6">
                {/* Tier Progress Stats */}
                <div className="grid gap-6 md:grid-cols-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Total Questions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">
                        {versionStats.total_questions} / {versionStats.target_total}
                      </div>
                      <div className="mt-2">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{
                              width: `${Math.min(100, (versionStats.total_questions / versionStats.target_total) * 100)}%`,
                            }}
                          />
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {Math.round((versionStats.total_questions / versionStats.target_total) * 100)}% complete
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  {[1, 2, 3].map((tier) => {
                    const progress = getTierProgress(tier);
                    const weight = tier === 1 ? "70%" : tier === 2 ? "20%" : "10%";
                    return (
                      <Card key={tier}>
                        <CardHeader>
                          <CardTitle className="text-sm font-medium text-muted-foreground">
                            Tier {tier} ({weight})
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">
                            {progress.current} / {progress.target}
                          </div>
                          <div className="mt-2">
                            <div className="h-2 bg-muted rounded-full overflow-hidden">
                              <div
                                className={`h-full transition-all ${
                                  progress.percent >= 100
                                    ? "bg-green-500"
                                    : progress.percent >= 80
                                    ? "bg-primary"
                                    : "bg-orange-500"
                                }`}
                                style={{ width: `${Math.min(100, progress.percent)}%` }}
                              />
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {progress.percent}% complete
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>

                {/* Difficulty Distribution */}
                {versionStats.difficulty_stats && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Difficulty Distribution</CardTitle>
                      <CardDescription>
                        Balance of easy, medium, and hard questions (target: 25-40% each)
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-3">
                        {(["easy", "medium", "hard"] as const).map((difficulty) => {
                          const stats = versionStats.difficulty_stats![difficulty];
                          const count = stats.count;
                          const percentage = Math.round(stats.percentage);
                          const inRange = percentage >= 25 && percentage <= 40;
                          
                          return (
                            <div
                              key={difficulty}
                              className="p-4 border rounded-lg space-y-2"
                            >
                              <div className="flex justify-between items-center">
                                <span className="font-medium capitalize">{difficulty}</span>
                                <Badge variant={inRange ? "default" : "destructive"}>
                                  {percentage}%
                                </Badge>
                              </div>
                              <div className="text-2xl font-bold">{count}</div>
                              <div className="h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className={`h-full transition-all ${
                                    inRange ? "bg-green-500" : "bg-orange-500"
                                  }`}
                                  style={{ width: `${Math.min(100, percentage * 2.5)}%` }}
                                />
                              </div>
                              <div className="text-xs text-muted-foreground">
                                Target: 25-40% ({Math.round(versionStats.total_questions * 0.25)}-{Math.round(versionStats.total_questions * 0.4)})
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : loadingStats ? (
              <Card>
                <CardContent className="py-8">
                  <Skeleton className="h-32 w-full" />
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  No statistics available for this version.
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Category Statistics Tab */}
          <TabsContent value="category-stats">
            {versionStats ? (
              <Card>
                <CardHeader>
                  <CardTitle>Category Completeness</CardTitle>
                  <CardDescription>
                    Progress by category within {versionStats.semantic_version}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {[1, 2, 3].map((tier) => {
                      const tierStat = versionStats.tier_stats[tier];
                      if (!tierStat) return null;
                      
                      const categories = Object.entries(tierStat.categories).sort();
                      
                      return (
                        <div key={tier}>
                          <h3 className="text-lg font-semibold mb-3">
                            Tier {tier} ({tier === 1 ? "70%" : tier === 2 ? "20%" : "10%"} weight)
                          </h3>
                          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {categories.map(([category, stats]) => {
                              const percent = stats.target > 0 
                                ? Math.round((stats.count / stats.target) * 100) 
                                : 0;
                              return (
                                <div
                                  key={category}
                                  className="p-3 border rounded-lg space-y-2"
                                >
                                  <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                      <div className="font-medium text-sm">
                                        {category}
                                      </div>
                                      <div className="text-xs text-muted-foreground">
                                        {getCategoryName(category)}
                                      </div>
                                    </div>
                                    <Badge
                                      variant={
                                        percent >= 100
                                          ? "default"
                                          : percent >= 80
                                          ? "secondary"
                                          : "outline"
                                      }
                                    >
                                      {percent}%
                                    </Badge>
                                  </div>
                                  <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                      <span className="text-muted-foreground">
                                        {stats.count} / {stats.target}
                                      </span>
                                      <span className="text-muted-foreground">
                                        {stats.target - stats.count} remaining
                                      </span>
                                    </div>
                                    <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                      <div
                                        className={`h-full transition-all ${
                                          percent >= 100
                                            ? "bg-green-500"
                                            : percent >= 80
                                            ? "bg-primary"
                                            : "bg-orange-500"
                                        }`}
                                        style={{ width: `${Math.min(100, percent)}%` }}
                                      />
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            ) : loadingStats ? (
              <Card>
                <CardContent className="py-8">
                  <Skeleton className="h-64 w-full" />
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  No category statistics available for this version.
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Questions Tab */}
          <TabsContent value="questions">
            {/* Filters */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Filters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-5">
                  <Input
                    placeholder="Search questions..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  <Select value={tierFilter} onValueChange={setTierFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by tier" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Tiers</SelectItem>
                      <SelectItem value="tier1">Tier 1</SelectItem>
                      <SelectItem value="tier2">Tier 2</SelectItem>
                      <SelectItem value="tier3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {versionStats &&
                        Object.keys(versionStats.tier_stats[1]?.categories || {})
                          .concat(
                            Object.keys(versionStats.tier_stats[2]?.categories || {})
                          )
                          .concat(
                            Object.keys(versionStats.tier_stats[3]?.categories || {})
                          )
                          .map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              {cat} - {getCategoryName(cat)}
                            </SelectItem>
                          ))}
                    </SelectContent>
                  </Select>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Difficulties</SelectItem>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Questions Table */}
            <Card>
        <CardHeader>
          <CardTitle>Questions</CardTitle>
          <CardDescription>
            {filteredQuestions.length} questions matching filters
            {showAll ? (
              <span className="ml-2">
                (showing all {totalQuestions} questions)
              </span>
            ) : totalQuestions > pageSize ? (
              <span className="ml-2">
                (showing page {currentPage} of {Math.ceil(totalQuestions / pageSize)}, {totalQuestions} total)
              </span>
            ) : null}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12 text-center">#</TableHead>
                <TableHead>Question</TableHead>
                <TableHead>Tier</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Difficulty</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Updated</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredQuestions.map((q, index) => (
                <TableRow key={q.id}>
                  <TableCell className="text-center text-muted-foreground text-sm">
                    {showAll ? index + 1 : (currentPage - 1) * pageSize + index + 1}
                  </TableCell>
                  <TableCell className="max-w-md">
                    <div className="whitespace-normal break-words">
                      {q.content}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">Tier {q.tier}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <div className="font-medium">{q.category}</div>
                      <div className="text-xs text-muted-foreground">
                        {getCategoryName(q.category)}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    {q.metadata?.difficulty ? (
                      <Badge variant="secondary" className="capitalize">
                        {q.metadata.difficulty}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground text-sm">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        q.status === "approved"
                          ? "default"
                          : q.status === "rejected"
                          ? "destructive"
                          : q.status === "pending"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {q.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {q.updated_at
                      ? new Date(q.updated_at).toLocaleDateString()
                      : q.created_at
                      ? new Date(q.created_at).toLocaleDateString()
                      : "—"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedQuestion(q);
                          setEditedContent(q.content);
                        }}
                      >
                        Edit
                      </Button>
                      {q.status === "pending" && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleApproveQuestion(q.id)}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRejectQuestion(q.id)}
                          >
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {/* Pagination Controls */}
          {totalQuestions > pageSize && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                {showAll ? (
                  `Showing all ${totalQuestions} questions`
                ) : (
                  <>
                    Showing {(currentPage - 1) * pageSize + 1} to{" "}
                    {Math.min(currentPage * pageSize, totalQuestions)} of {totalQuestions} questions
                  </>
                )}
              </div>
              <div className="flex items-center gap-2">
                {showAll ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowAll(false);
                      setCurrentPage(1);
                      loadQuestions(1, false);
                    }}
                    disabled={loading}
                  >
                    Show Paginated
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1 || loading}
                    >
                      First
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1 || loading}
                    >
                      Previous
                    </Button>
                    <div className="flex items-center gap-1">
                      {/* Page number buttons */}
                      {Array.from({ length: Math.ceil(totalQuestions / pageSize) }, (_, i) => i + 1)
                        .filter(page => {
                          // Show first, last, current, and pages around current
                          const totalPages = Math.ceil(totalQuestions / pageSize);
                          return (
                            page === 1 ||
                            page === totalPages ||
                            Math.abs(page - currentPage) <= 1
                          );
                        })
                        .reduce((acc: (number | string)[], page, i, arr) => {
                          // Add ellipsis between non-consecutive pages
                          if (i > 0 && page - (arr[i - 1] as number) > 1) {
                            acc.push("...");
                          }
                          acc.push(page);
                          return acc;
                        }, [])
                        .map((item, i) =>
                          typeof item === "string" ? (
                            <span key={`ellipsis-${i}`} className="px-2 text-muted-foreground">
                              {item}
                            </span>
                          ) : (
                            <Button
                              key={item}
                              variant={currentPage === item ? "default" : "outline"}
                              size="sm"
                              onClick={() => setCurrentPage(item)}
                              disabled={loading}
                              className="min-w-[32px]"
                            >
                              {item}
                            </Button>
                          )
                        )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage >= Math.ceil(totalQuestions / pageSize) || loading}
                    >
                      Next
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(Math.ceil(totalQuestions / pageSize))}
                      disabled={currentPage >= Math.ceil(totalQuestions / pageSize) || loading}
                    >
                      Last
                    </Button>
                    <div className="border-l pl-2 ml-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setShowAll(true)}
                        disabled={loading}
                      >
                        Show All ({totalQuestions})
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!selectedQuestion} onOpenChange={() => setSelectedQuestion(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Question</DialogTitle>
            <DialogDescription>
              Modify the question content
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="flex gap-2">
              <Badge variant="outline">Tier {selectedQuestion?.tier}</Badge>
              <Badge variant="secondary">{selectedQuestion?.category}</Badge>
            </div>
            <div>
              <Label htmlFor="content">Question Content</Label>
              <textarea
                id="content"
                className="w-full min-h-32 p-2 border rounded-md mt-1"
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedQuestion(null)}>
              Cancel
            </Button>
            <Button onClick={handleSaveQuestion} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={showImportDialog} onOpenChange={resetImportDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Import Questions</DialogTitle>
            <DialogDescription>
              Upload a CSV or JSON file with questions. CSV is the recommended format.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* Version Selection */}
            <div className="space-y-2">
              <Label htmlFor="import-version">Target Version</Label>
              <Select
                value={importVersionId || "auto"}
                onValueChange={(value) => {
                  setImportVersionId(value === "auto" ? "" : value);
                  setImportPreview(null);
                }}
              >
                <SelectTrigger id="import-version">
                  <SelectValue placeholder="Select target version" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto-select (first draft or create new)</SelectItem>
                  {versions
                    .filter((v) => v.status === "draft")
                    .map((v) => (
                      <SelectItem key={v.id} value={v.id}>
                        {v.semantic_version} - {v.marketing_version} (Draft)
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Questions can only be imported to draft versions
              </p>
            </div>

            {/* File Upload */}
            <div className="space-y-2">
              <Label htmlFor="file">Select File</Label>
              <div className="relative">
                <input
                  id="file"
                  type="file"
                  accept=".json,.csv"
                  onChange={(e) => {
                    setImportFile(e.target.files?.[0] || null);
                    setImportPreview(null);
                  }}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="flex items-center gap-2 border-2 border-dashed border-muted-foreground/25 bg-muted/30 hover:border-primary/50 hover:bg-muted/50 rounded-md px-4 py-2 min-h-[2.5rem] transition-colors">
                  <Button
                    type="button"
                    variant="default"
                    size="sm"
                    className="pointer-events-none"
                    onClick={(e) => e.preventDefault()}
                  >
                    Choose File
                  </Button>
                  <span className="text-sm text-muted-foreground flex-1">
                    {importFile ? importFile.name : "No file chosen"}
                  </span>
                </div>
                {importFile && (
                  <div className="mt-2 flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">File size:</span>
                    <span className="font-medium">
                      {(importFile.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                Supported formats: CSV (recommended), JSON
              </p>
            </div>

            {/* Preview Button */}
            {importFile && !importPreview && (
              <Button
                variant="secondary"
                onClick={handleImportPreview}
                disabled={loadingPreview}
                className="w-full"
              >
                {loadingPreview ? "Analyzing file..." : "Preview Import"}
              </Button>
            )}

            {/* Import Preview */}
            {importPreview && (
              <div className="space-y-4 border rounded-lg p-4 bg-muted/30">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Import Preview</h4>
                  <Badge variant="outline">{importPreview.file_type.toUpperCase()}</Badge>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center p-2 bg-background rounded border">
                    <div className="text-2xl font-bold">{importPreview.total_questions}</div>
                    <div className="text-muted-foreground">Total Questions</div>
                  </div>
                  <div className="text-center p-2 bg-background rounded border">
                    <div className="text-2xl font-bold">{Object.keys(importPreview.category_counts).length}</div>
                    <div className="text-muted-foreground">Categories</div>
                  </div>
                  <div className="text-center p-2 bg-background rounded border">
                    <div className="text-2xl font-bold text-destructive">{importPreview.parse_errors.length}</div>
                    <div className="text-muted-foreground">Errors</div>
                  </div>
                </div>

                {/* Tier Distribution */}
                <div>
                  <h5 className="text-sm font-medium mb-2">Tier Distribution</h5>
                  <div className="flex gap-2">
                    {[1, 2, 3].map((tier) => (
                      <Badge key={tier} variant="secondary">
                        Tier {tier}: {importPreview.tier_counts[tier] || 0}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Difficulty Distribution */}
                {Object.keys(importPreview.difficulty_counts).length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium mb-2">Difficulty Distribution</h5>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(importPreview.difficulty_counts).map(([diff, count]) => (
                        <Badge key={diff} variant="outline" className="capitalize">
                          {diff}: {count}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Category Breakdown */}
                <div>
                  <h5 className="text-sm font-medium mb-2">Categories</h5>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(importPreview.category_counts)
                      .sort(([a], [b]) => a.localeCompare(b))
                      .map(([cat, count]) => (
                        <Badge key={cat} variant="outline" className="text-xs">
                          {cat}: {count}
                        </Badge>
                      ))}
                  </div>
                </div>

                {/* Sample Questions */}
                {importPreview.sample_questions.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium mb-2">Sample Questions</h5>
                    <div className="space-y-2 text-sm">
                      {importPreview.sample_questions.map((q, idx) => (
                        <div key={idx} className="p-2 bg-background rounded border">
                          <div className="flex gap-2 mb-1">
                            <Badge variant="secondary" className="text-xs">Tier {q.tier}</Badge>
                            <Badge variant="outline" className="text-xs">{q.category}</Badge>
                            {q.difficulty && (
                              <Badge variant="outline" className="text-xs capitalize">{q.difficulty}</Badge>
                            )}
                          </div>
                          <p className="text-muted-foreground text-xs">{q.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Parse Errors */}
                {importPreview.parse_errors.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium mb-2 text-destructive">Parse Errors</h5>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {importPreview.parse_errors.map((err, idx) => (
                        <div key={idx} className="text-xs text-destructive bg-destructive/10 p-2 rounded">
                          Row {err.row}: {err.field} - {err.message}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* CSV Format Help */}
            <details className="text-sm">
              <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                CSV Format Reference
              </summary>
              <div className="mt-2 p-3 bg-muted rounded text-xs font-mono overflow-x-auto">
                <p className="mb-2 font-sans text-muted-foreground">Required columns: content, category</p>
                <p className="mb-2 font-sans text-muted-foreground">Optional columns: tier, difficulty, expected_verdict, expected_refusal_type, tests_capability, tests_willingness, use_case_tags, audience_context, ministry_type, reasoning</p>
                <p className="font-sans text-muted-foreground">Tier is auto-inferred from category (3.x→1, 4.x→2, 5.x→3)</p>
              </div>
            </details>
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={resetImportDialog}>
              Cancel
            </Button>
            {importPreview && (
              <Button
                variant="secondary"
                onClick={() => setImportPreview(null)}
              >
                Re-select File
              </Button>
            )}
            <Button
              onClick={handleImport}
              disabled={!importFile || importing || !importPreview || importPreview.total_questions === 0}
            >
              {importing ? "Importing..." : `Import ${importPreview?.total_questions || 0} Questions`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
