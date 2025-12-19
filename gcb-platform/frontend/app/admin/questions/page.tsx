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
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [editedContent, setEditedContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);

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
      loadQuestions();
      loadVersionStats();
    }
  }, [versionFilter]);

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

  async function loadQuestions() {
    if (!versionFilter) return;
    
    setLoading(true);
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
              `/api/admin/questions?question_set_id=${selectedQuestionSet.id}`
            );
            if (response.ok) {
              const data = await response.json();
              setQuestions(data.items || []);
            }
          }
        }
      } else {
        const response = await fetch(
          `/api/admin/questions?question_set_id=${selectedVersion.id}`
        );
        if (response.ok) {
          const data = await response.json();
          setQuestions(data.items || []);
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
        loadQuestions();
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
        loadQuestions();
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
        loadQuestions();
      } else {
        throw new Error("Failed to reject");
      }
    } catch (error) {
      console.error("Failed to reject question:", error);
      toast.error("Failed to reject question");
    }
  }

  async function handleImport() {
    if (!importFile) return;
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", importFile);

      const response = await fetch("/api/admin/questions/import", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`Imported ${result.imported} questions`);
        setShowImportDialog(false);
        setImportFile(null);
        loadQuestions();
      } else {
        throw new Error("Failed to import");
      }
    } catch (error) {
      console.error("Failed to import questions:", error);
      toast.error("Failed to import questions");
    } finally {
      setImporting(false);
    }
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

      {/* Version Selector */}
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

      {/* Stats */}
      {versionStats && (
        <>
          <div className="grid gap-6 md:grid-cols-4 mb-8">
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

          {/* Category Completeness Grid */}
          <Card className="mb-6">
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
        </>
      )}

      {/* Filters */}
      {versionFilter && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
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
            </div>
          </CardContent>
        </Card>
      )}

      {/* Questions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Questions</CardTitle>
          <CardDescription>
            {filteredQuestions.length} questions matching filters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Question</TableHead>
                <TableHead>Tier</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Updated</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredQuestions.map((q) => (
                <TableRow key={q.id}>
                  <TableCell className="max-w-md truncate">
                    {q.content.substring(0, 100)}...
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
        </CardContent>
      </Card>

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
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Import Questions</DialogTitle>
            <DialogDescription>
              Upload a JSON or CSV file with questions
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="file">Select File</Label>
            <Input
              id="file"
              type="file"
              accept=".json,.csv"
              onChange={(e) => setImportFile(e.target.files?.[0] || null)}
              className="mt-1"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Supported formats: JSON, CSV
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowImportDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleImport} disabled={!importFile || importing}>
              {importing ? "Importing..." : "Import"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
