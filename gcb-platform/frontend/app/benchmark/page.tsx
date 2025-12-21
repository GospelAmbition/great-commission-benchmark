"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/input";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

interface QuestionSet {
  id: string;
  semantic_version: string;
  marketing_version: string;
  status: "draft" | "locked" | "active" | "archived";
  question_count: number;
  created_at: string;
  locked_at?: string;
  archived_at?: string;
}

interface Question {
  id: string;
  question_set_id: string;
  tier: number;
  category: string;
  content: string;
  metadata?: Record<string, any>;
  is_locked: boolean;
}

interface BenchmarkOverview {
  active_version: {
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
  } | null;
  draft_versions: Array<{
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
    created_at: string;
  }>;
  locked_versions: Array<{
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
    locked_at: string;
  }>;
  stats: {
    total_versions: number;
    total_questions: number;
    draft_count: number;
    locked_count: number;
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function BenchmarkDashboardPage() {
  const { data: session, status } = useSession();
  const { isBenchmarkDeveloper, loading: profileLoading } = useUserProfile();
  const router = useRouter();
  
  const [overview, setOverview] = useState<BenchmarkOverview | null>(null);
  const [questionSets, setQuestionSets] = useState<QuestionSet[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  
  // Filters
  const [selectedVersionId, setSelectedVersionId] = useState<string>("");
  const [selectedTier, setSelectedTier] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  
  // Dialogs
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditQuestionDialog, setShowEditQuestionDialog] = useState(false);
  const [showCreateQuestionDialog, setShowCreateQuestionDialog] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState<{
    action: string;
    version: QuestionSet;
  } | null>(null);
  
  // Form state
  const [newVersion, setNewVersion] = useState({ semantic_version: "", marketing_version: "", copy_from: "" });
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [newQuestion, setNewQuestion] = useState({ tier: "1", category: "", content: "" });
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (status === "loading" || profileLoading) return;
    
    if (!session?.user) {
      router.push("/api/auth/signin");
      return;
    }
    
    if (!isBenchmarkDeveloper) {
      router.push("/dashboard");
      toast.error("You don't have permission to access the Benchmark Development dashboard");
      return;
    }
    
    loadData();
  }, [session, status, profileLoading, isBenchmarkDeveloper, router]);

  async function getAuthToken(): Promise<string | null> {
    try {
      const response = await fetch('/api/auth/token');
      if (response.ok) {
        const data = await response.json();
        return data.token || null;
      }
    } catch {
      return null;
    }
    return null;
  }

  async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  }

  async function loadData() {
    setLoading(true);
    try {
      const [overviewData, questionSetsData] = await Promise.all([
        apiRequest<BenchmarkOverview>('/api/benchmark/overview'),
        apiRequest<{ items: QuestionSet[]; total: number }>('/api/benchmark/question-sets'),
      ]);
      
      setOverview(overviewData);
      setQuestionSets(questionSetsData.items || []);
      
      // Auto-select a version for questions tab
      if (!selectedVersionId) {
        if (overviewData.draft_versions.length > 0) {
          setSelectedVersionId(overviewData.draft_versions[0].id);
        } else if (overviewData.active_version) {
          setSelectedVersionId(overviewData.active_version.id);
        }
      }
    } catch (error) {
      console.error("Failed to load benchmark data:", error);
      toast.error("Failed to load benchmark data");
    } finally {
      setLoading(false);
    }
  }

  async function loadQuestions() {
    if (!selectedVersionId) return;
    
    setQuestionsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("question_set_id", selectedVersionId);
      if (selectedTier !== "all") params.append("tier", selectedTier);
      if (selectedCategory !== "all") params.append("category", selectedCategory);
      params.append("limit", "100");
      
      const data = await apiRequest<{ items: Question[]; total: number }>(
        `/api/benchmark/questions?${params.toString()}`
      );
      setQuestions(data.items || []);
    } catch (error) {
      console.error("Failed to load questions:", error);
      toast.error("Failed to load questions");
    } finally {
      setQuestionsLoading(false);
    }
  }

  useEffect(() => {
    if (selectedVersionId) {
      loadQuestions();
    }
  }, [selectedVersionId, selectedTier, selectedCategory]);

  // Version actions
  async function handleCreateVersion() {
    if (!newVersion.semantic_version || !newVersion.marketing_version) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setActionLoading(true);
    try {
      if (newVersion.copy_from) {
        await apiRequest(`/api/benchmark/question-sets/${newVersion.copy_from}/copy`, {
          method: "POST",
          body: JSON.stringify({
            new_semantic_version: newVersion.semantic_version,
            new_marketing_version: newVersion.marketing_version,
          }),
        });
        toast.success(`Version ${newVersion.semantic_version} created by copying`);
      } else {
        await apiRequest('/api/benchmark/question-sets', {
          method: "POST",
          body: JSON.stringify({
            semantic_version: newVersion.semantic_version,
            marketing_version: newVersion.marketing_version,
          }),
        });
        toast.success(`Version ${newVersion.semantic_version} created`);
      }
      
      setShowCreateDialog(false);
      setNewVersion({ semantic_version: "", marketing_version: "", copy_from: "" });
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to create version");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleVersionAction(action: string, version: QuestionSet) {
    setActionLoading(true);
    try {
      switch (action) {
        case "lock":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/lock`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} locked`);
          break;
        case "unlock":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/unlock`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} unlocked`);
          break;
        case "publish":
          await apiRequest(`/api/benchmark/versions/${version.semantic_version}/publish`, { method: "PUT" });
          toast.success(`Version ${version.semantic_version} published`);
          break;
        case "archive":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/archive`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} archived`);
          break;
        case "delete":
          await apiRequest(`/api/benchmark/question-sets/${version.id}`, { method: "DELETE" });
          toast.success(`Version ${version.semantic_version} deleted`);
          break;
      }
      setShowConfirmDialog(null);
      loadData();
    } catch (error: any) {
      toast.error(error.message || `Failed to ${action} version`);
    } finally {
      setActionLoading(false);
    }
  }

  // Question actions
  async function handleCreateQuestion() {
    if (!newQuestion.category || !newQuestion.content) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setActionLoading(true);
    try {
      const params = new URLSearchParams({
        question_set_id: selectedVersionId,
        tier: newQuestion.tier,
        category: newQuestion.category,
        content: newQuestion.content,
      });
      
      await apiRequest(`/api/benchmark/questions?${params.toString()}`, {
        method: "POST",
      });
      
      toast.success("Question created");
      setShowCreateQuestionDialog(false);
      setNewQuestion({ tier: "1", category: "", content: "" });
      loadQuestions();
      loadData(); // Refresh counts
    } catch (error: any) {
      toast.error(error.message || "Failed to create question");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleUpdateQuestion() {
    if (!editingQuestion) return;
    
    setActionLoading(true);
    try {
      await apiRequest(`/api/benchmark/questions/${editingQuestion.id}`, {
        method: "PUT",
        body: JSON.stringify({
          tier: editingQuestion.tier,
          category: editingQuestion.category,
          content: editingQuestion.content,
        }),
      });
      
      toast.success("Question updated");
      setShowEditQuestionDialog(false);
      setEditingQuestion(null);
      loadQuestions();
    } catch (error: any) {
      toast.error(error.message || "Failed to update question");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteQuestion(questionId: string) {
    if (!confirm("Are you sure you want to delete this question?")) return;
    
    try {
      await apiRequest(`/api/benchmark/questions/${questionId}`, {
        method: "DELETE",
      });
      toast.success("Question deleted");
      loadQuestions();
      loadData(); // Refresh counts
    } catch (error: any) {
      toast.error(error.message || "Failed to delete question");
    }
  }

  function getStatusBadgeVariant(status: string): "default" | "secondary" | "outline" | "destructive" {
    switch (status) {
      case "active": return "default";
      case "locked": return "secondary";
      case "draft": return "outline";
      case "archived": return "outline";
      default: return "outline";
    }
  }

  const categories = {
    1: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"],
    2: ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"],
    3: ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"],
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

  if (status === "loading" || profileLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!session?.user || !isBenchmarkDeveloper) {
    return null;
  }

  const selectedVersion = questionSets.find(qs => qs.id === selectedVersionId);
  const canEditQuestions = selectedVersion?.status === "draft";

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Benchmark Development</h1>
        <p className="mt-2 text-muted-foreground">
          Manage benchmark versions and questions
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card className={overview?.active_version ? "border-green-500" : ""}>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Version
            </CardTitle>
          </CardHeader>
          <CardContent>
            {overview?.active_version ? (
              <>
                <div className="text-2xl font-bold">{overview.active_version.semantic_version}</div>
                <p className="text-sm text-muted-foreground">
                  {overview.active_version.question_count} questions
                </p>
              </>
            ) : (
              <div className="text-muted-foreground">No active version</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Drafts in Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.draft_count || 0}</div>
            <p className="text-sm text-muted-foreground">
              {overview?.draft_versions[0]?.semantic_version || "No drafts"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pending Publish
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.locked_count || 0}</div>
            <p className="text-sm text-muted-foreground">locked versions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Questions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.total_questions || 0}</div>
            <p className="text-sm text-muted-foreground">across all versions</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs defaultValue="versions" className="space-y-6">
        <TabsList>
          <TabsTrigger value="versions">Versions</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
        </TabsList>

        {/* Versions Tab */}
        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Version Management</CardTitle>
                  <CardDescription>Create and manage benchmark versions</CardDescription>
                </div>
                <Button onClick={() => setShowCreateDialog(true)}>
                  Create New Version
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Questions</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {questionSets.map((qs) => (
                    <TableRow key={qs.id}>
                      <TableCell>
                        <div className="font-medium">{qs.semantic_version}</div>
                        <div className="text-sm text-muted-foreground">{qs.marketing_version}</div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(qs.status)}>
                          {qs.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{qs.question_count}</TableCell>
                      <TableCell>
                        {new Date(qs.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2 flex-wrap">
                          {qs.status === "draft" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "lock", version: qs })}
                              >
                                Lock
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => setShowConfirmDialog({ action: "delete", version: qs })}
                              >
                                Delete
                              </Button>
                            </>
                          )}
                          {qs.status === "locked" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "unlock", version: qs })}
                              >
                                Unlock
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "publish", version: qs })}
                              >
                                Publish
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "archive", version: qs })}
                              >
                                Archive
                              </Button>
                            </>
                          )}
                          {qs.status === "active" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowConfirmDialog({ action: "archive", version: qs })}
                            >
                              Archive
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedVersionId(qs.id);
                              const tabsEl = document.querySelector('[data-state="inactive"][value="questions"]');
                              if (tabsEl) (tabsEl as HTMLElement).click();
                            }}
                          >
                            View Questions
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <CardTitle>Question Management</CardTitle>
                  <CardDescription>
                    Browse and edit questions by version
                    {!canEditQuestions && selectedVersion && (
                      <span className="text-orange-500 ml-2">
                        (Read-only - version is {selectedVersion.status})
                      </span>
                    )}
                  </CardDescription>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Select value={selectedVersionId} onValueChange={setSelectedVersionId}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Select version" />
                    </SelectTrigger>
                    <SelectContent>
                      {questionSets.map((qs) => (
                        <SelectItem key={qs.id} value={qs.id}>
                          {qs.semantic_version} ({qs.status})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={selectedTier} onValueChange={setSelectedTier}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue placeholder="Tier" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Tiers</SelectItem>
                      <SelectItem value="1">Tier 1</SelectItem>
                      <SelectItem value="2">Tier 2</SelectItem>
                      <SelectItem value="3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {selectedTier !== "all" ? (
                        categories[parseInt(selectedTier) as 1 | 2 | 3]?.map((cat) => (
                          <SelectItem key={cat} value={cat}>
                            {cat} - {getCategoryName(cat)}
                          </SelectItem>
                        ))
                      ) : (
                        Object.entries(categories).flatMap(([tier, cats]) =>
                          cats.map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              T{tier}: {cat} - {getCategoryName(cat)}
                            </SelectItem>
                          ))
                        )
                      )}
                    </SelectContent>
                  </Select>
                  {canEditQuestions && (
                    <Button onClick={() => setShowCreateQuestionDialog(true)}>
                      Add Question
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {questionsLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-16" />
                  ))}
                </div>
              ) : questions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  {selectedVersionId ? "No questions found" : "Select a version to view questions"}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[80px]">Tier</TableHead>
                      <TableHead className="w-[120px]">Category</TableHead>
                      <TableHead>Content</TableHead>
                      {canEditQuestions && <TableHead className="w-[150px]">Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {questions.map((q) => (
                      <TableRow key={q.id}>
                        <TableCell>
                          <Badge variant="outline">T{q.tier}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">{q.category}</div>
                          <div className="text-xs text-muted-foreground">
                            {getCategoryName(q.category)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="max-w-lg truncate">{q.content}</div>
                        </TableCell>
                        {canEditQuestions && (
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setEditingQuestion(q);
                                  setShowEditQuestionDialog(true);
                                }}
                              >
                                Edit
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => handleDeleteQuestion(q.id)}
                              >
                                Delete
                              </Button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Version Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Version</DialogTitle>
            <DialogDescription>
              Create a new benchmark version draft
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="semantic_version">Semantic Version</Label>
              <Input
                id="semantic_version"
                placeholder="e.g., 1.2.0"
                value={newVersion.semantic_version}
                onChange={(e) => setNewVersion({ ...newVersion, semantic_version: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="marketing_version">Marketing Version</Label>
              <Input
                id="marketing_version"
                placeholder="e.g., Version 1.2"
                value={newVersion.marketing_version}
                onChange={(e) => setNewVersion({ ...newVersion, marketing_version: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="copy_from">Copy from (optional)</Label>
              <Select
                value={newVersion.copy_from}
                onValueChange={(value) => setNewVersion({ ...newVersion, copy_from: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Start empty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Start empty</SelectItem>
                  {questionSets.map((qs) => (
                    <SelectItem key={qs.id} value={qs.id}>
                      {qs.semantic_version} ({qs.question_count} questions)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateVersion} disabled={actionLoading}>
              {actionLoading ? "Creating..." : "Create Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Question Dialog */}
      <Dialog open={showCreateQuestionDialog} onOpenChange={setShowCreateQuestionDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Question</DialogTitle>
            <DialogDescription>
              Add a new question to {selectedVersion?.semantic_version}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="new_tier">Tier</Label>
                <Select
                  value={newQuestion.tier}
                  onValueChange={(value) => setNewQuestion({ ...newQuestion, tier: value, category: "" })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Tier 1 (70%)</SelectItem>
                    <SelectItem value="2">Tier 2 (20%)</SelectItem>
                    <SelectItem value="3">Tier 3 (10%)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="new_category">Category</Label>
                <Select
                  value={newQuestion.category}
                  onValueChange={(value) => setNewQuestion({ ...newQuestion, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories[parseInt(newQuestion.tier) as 1 | 2 | 3]?.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat} - {getCategoryName(cat)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="new_content">Question Content</Label>
              <textarea
                id="new_content"
                className="w-full min-h-[200px] p-3 border rounded-md"
                placeholder="Enter the question content..."
                value={newQuestion.content}
                onChange={(e) => setNewQuestion({ ...newQuestion, content: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateQuestionDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateQuestion} disabled={actionLoading}>
              {actionLoading ? "Adding..." : "Add Question"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Question Dialog */}
      <Dialog open={showEditQuestionDialog} onOpenChange={setShowEditQuestionDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Question</DialogTitle>
          </DialogHeader>
          {editingQuestion && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_tier">Tier</Label>
                  <Select
                    value={String(editingQuestion.tier)}
                    onValueChange={(value) => setEditingQuestion({ ...editingQuestion, tier: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Tier 1</SelectItem>
                      <SelectItem value="2">Tier 2</SelectItem>
                      <SelectItem value="3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit_category">Category</Label>
                  <Select
                    value={editingQuestion.category}
                    onValueChange={(value) => setEditingQuestion({ ...editingQuestion, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories[editingQuestion.tier as 1 | 2 | 3]?.map((cat) => (
                        <SelectItem key={cat} value={cat}>
                          {cat} - {getCategoryName(cat)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="edit_content">Question Content</Label>
                <textarea
                  id="edit_content"
                  className="w-full min-h-[200px] p-3 border rounded-md"
                  value={editingQuestion.content}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, content: e.target.value })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditQuestionDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateQuestion} disabled={actionLoading}>
              {actionLoading ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirm Action Dialog */}
      <Dialog open={!!showConfirmDialog} onOpenChange={() => setShowConfirmDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {showConfirmDialog?.action === "delete" ? "Delete Version" :
               showConfirmDialog?.action === "publish" ? "Publish Version" :
               showConfirmDialog?.action === "lock" ? "Lock Version" :
               showConfirmDialog?.action === "unlock" ? "Unlock Version" :
               showConfirmDialog?.action === "archive" ? "Archive Version" : "Confirm Action"}
            </DialogTitle>
            <DialogDescription>
              {showConfirmDialog?.action === "delete" && (
                <>Are you sure you want to delete version {showConfirmDialog.version.semantic_version}? This cannot be undone.</>
              )}
              {showConfirmDialog?.action === "publish" && (
                <>Are you sure you want to publish version {showConfirmDialog.version.semantic_version}? This will make it the active version.</>
              )}
              {showConfirmDialog?.action === "lock" && (
                <>Are you sure you want to lock version {showConfirmDialog.version.semantic_version}? This will prevent further edits until unlocked.</>
              )}
              {showConfirmDialog?.action === "unlock" && (
                <>Are you sure you want to unlock version {showConfirmDialog.version.semantic_version}? This will revert it to draft status.</>
              )}
              {showConfirmDialog?.action === "archive" && (
                <>Are you sure you want to archive version {showConfirmDialog.version.semantic_version}?</>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(null)}>
              Cancel
            </Button>
            <Button
              variant={showConfirmDialog?.action === "delete" ? "destructive" : "default"}
              onClick={() => showConfirmDialog && handleVersionAction(showConfirmDialog.action, showConfirmDialog.version)}
              disabled={actionLoading}
            >
              {actionLoading ? "Processing..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
