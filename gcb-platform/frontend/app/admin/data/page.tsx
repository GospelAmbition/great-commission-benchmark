"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";
import { ChevronRight } from "lucide-react";

interface TestRun {
  id: string;
  user_id: string;
  user_email: string | null;
  model_id: string;
  model_name: string | null;
  question_set_id: string | null;
  question_set_version: string | null;
  status: string;
  result_count: number;
  created_at: string | null;
  completed_at: string | null;
}

interface CommunitySubmission {
  id: string;
  user_id: string;
  user_email: string | null;
  model_name: string;
  organization: string | null;
  status: string;
  overall_score: number | null;
  question_set_version: string;
  submitted_at: string | null;
  reviewed_at: string | null;
}

interface ModelItem {
  id: string;
  model_id: string;
  name: string;
  provider: string;
  is_active: boolean;
  test_run_count: number;
  created_at: string | null;
}

export default function AdminDataPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  
  // Test runs state
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [testRunsLoading, setTestRunsLoading] = useState(true);
  const [testRunsTotal, setTestRunsTotal] = useState(0);
  const [testRunStatusFilter, setTestRunStatusFilter] = useState<string>("all");
  const [selectedTestRuns, setSelectedTestRuns] = useState<Set<string>>(new Set());
  
  // Community submissions state
  const [submissions, setSubmissions] = useState<CommunitySubmission[]>([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(true);
  const [submissionsTotal, setSubmissionsTotal] = useState(0);
  const [submissionStatusFilter, setSubmissionStatusFilter] = useState<string>("all");
  const [selectedSubmissions, setSelectedSubmissions] = useState<Set<string>>(new Set());
  
  // Models state
  const [models, setModels] = useState<ModelItem[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsTotal, setModelsTotal] = useState(0);
  const [modelSearch, setModelSearch] = useState("");
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set());
  const [recalculatingModelId, setRecalculatingModelId] = useState<string | null>(null);
  
  // Delete dialog state
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    type: "test-run" | "submission" | "model" | null;
    id: string | null;
    name: string;
    isBulk: boolean;
    count: number;
  }>({
    open: false,
    type: null,
    id: null,
    name: "",
    isBulk: false,
    count: 0,
  });
  const [bulkConfirmText, setBulkConfirmText] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    // Check if user is admin
    if (user && !profileLoading) {
      if (!canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadTestRuns();
      loadSubmissions();
      loadModels();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router]);

  useEffect(() => {
    if (user) loadTestRuns();
  }, [testRunStatusFilter]);

  useEffect(() => {
    if (user) loadSubmissions();
  }, [submissionStatusFilter]);

  useEffect(() => {
    if (user) {
      const debounce = setTimeout(() => loadModels(), 300);
      return () => clearTimeout(debounce);
    }
  }, [modelSearch]);

  async function loadTestRuns() {
    setTestRunsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (testRunStatusFilter !== "all") {
        params.set("status", testRunStatusFilter);
      }
      const response = await fetch(`/api/admin/test-runs?${params}`);
      if (response.ok) {
        const data = await response.json();
        setTestRuns(data.items || []);
        setTestRunsTotal(data.total || 0);
      } else {
        toast.error("Failed to load test runs");
      }
    } catch (error) {
      console.error("Failed to load test runs:", error);
      toast.error("Failed to load test runs");
    } finally {
      setTestRunsLoading(false);
    }
  }

  async function loadSubmissions() {
    setSubmissionsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (submissionStatusFilter !== "all") {
        params.set("status", submissionStatusFilter);
      }
      const response = await fetch(`/api/admin/community-submissions?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data.items || []);
        setSubmissionsTotal(data.total || 0);
      } else {
        toast.error("Failed to load submissions");
      }
    } catch (error) {
      console.error("Failed to load submissions:", error);
      toast.error("Failed to load submissions");
    } finally {
      setSubmissionsLoading(false);
    }
  }

  async function loadModels() {
    setModelsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (modelSearch) {
        params.set("search", modelSearch);
      }
      const response = await fetch(`/api/admin/models?${params}`);
      if (response.ok) {
        const data = await response.json();
        setModels(data.items || []);
        setModelsTotal(data.total || 0);
      } else {
        toast.error("Failed to load models");
      }
    } catch (error) {
      console.error("Failed to load models:", error);
      toast.error("Failed to load models");
    } finally {
      setModelsLoading(false);
    }
  }

  function openDeleteDialog(
    type: "test-run" | "submission" | "model",
    id: string,
    name: string
  ) {
    setDeleteDialog({
      open: true,
      type,
      id,
      name,
      isBulk: false,
      count: 1,
    });
    setBulkConfirmText("");
  }

  function openBulkDeleteDialog(type: "test-run" | "submission" | "model") {
    const selectedSet =
      type === "test-run"
        ? selectedTestRuns
        : type === "submission"
        ? selectedSubmissions
        : selectedModels;
    
    if (selectedSet.size === 0) {
      toast.error("No items selected");
      return;
    }

    setDeleteDialog({
      open: true,
      type,
      id: null,
      name: "",
      isBulk: true,
      count: selectedSet.size,
    });
    setBulkConfirmText("");
  }

  async function handleDelete() {
    if (!deleteDialog.type) return;
    
    // For bulk delete, verify confirmation text
    if (deleteDialog.isBulk) {
      const expectedText = `DELETE ${deleteDialog.count} ITEMS`;
      if (bulkConfirmText !== expectedText) {
        toast.error(`Please type "${expectedText}" to confirm`);
        return;
      }
    }

    setDeleting(true);
    try {
      if (deleteDialog.isBulk) {
        // Bulk delete
        const selectedSet =
          deleteDialog.type === "test-run"
            ? selectedTestRuns
            : deleteDialog.type === "submission"
            ? selectedSubmissions
            : selectedModels;
        
        const endpoint =
          deleteDialog.type === "test-run"
            ? "/api/admin/test-runs"
            : deleteDialog.type === "submission"
            ? "/api/admin/community-submissions"
            : "/api/admin/models";

        let successCount = 0;
        let errorCount = 0;

        for (const id of selectedSet) {
          try {
            const response = await fetch(`${endpoint}/${id}`, {
              method: "DELETE",
            });
            if (response.ok) {
              successCount++;
            } else {
              errorCount++;
            }
          } catch {
            errorCount++;
          }
        }

        if (successCount > 0) {
          toast.success(`Deleted ${successCount} item(s)`);
        }
        if (errorCount > 0) {
          toast.error(`Failed to delete ${errorCount} item(s)`);
        }

        // Clear selection
        if (deleteDialog.type === "test-run") {
          setSelectedTestRuns(new Set());
          loadTestRuns();
          loadModels(); // refresh model counts so placeholders update
        } else if (deleteDialog.type === "submission") {
          setSelectedSubmissions(new Set());
          loadSubmissions();
        } else {
          setSelectedModels(new Set());
          loadModels();
        }
      } else {
        // Single delete
        const endpoint =
          deleteDialog.type === "test-run"
            ? `/api/admin/test-runs/${deleteDialog.id}`
            : deleteDialog.type === "submission"
            ? `/api/admin/community-submissions/${deleteDialog.id}`
            : `/api/admin/models/${deleteDialog.id}`;

        const response = await fetch(endpoint, { method: "DELETE" });
        
        if (response.ok) {
          toast.success("Item deleted successfully");
          if (deleteDialog.type === "test-run") {
            loadTestRuns();
            loadModels(); // refresh model counts so placeholders update
          } else if (deleteDialog.type === "submission") loadSubmissions();
          else loadModels();
        } else {
          const error = await response.json();
          toast.error(error.detail || "Failed to delete item");
        }
      }
    } catch (error) {
      console.error("Delete error:", error);
      toast.error("Failed to delete item(s)");
    } finally {
      setDeleting(false);
      setDeleteDialog({ open: false, type: null, id: null, name: "", isBulk: false, count: 0 });
      setBulkConfirmText("");
    }
  }

  function toggleTestRunSelection(id: string) {
    const newSet = new Set(selectedTestRuns);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedTestRuns(newSet);
  }

  function toggleSubmissionSelection(id: string) {
    const newSet = new Set(selectedSubmissions);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedSubmissions(newSet);
  }

  function toggleModelSelection(id: string) {
    const newSet = new Set(selectedModels);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedModels(newSet);
  }

  async function handleRecalculateScores(modelId: string, modelName: string) {
    setRecalculatingModelId(modelId);
    try {
      const response = await fetch(`/api/admin/models/${modelId}/recalculate-scores`, {
        method: "POST",
      });
      const data = await response.json();
      if (response.ok) {
        toast.success(data.message || `Recalculated scores for ${data.updated_count ?? 0} test run(s)`);
      } else {
        toast.error(data.detail || "Failed to recalculate scores");
      }
    } catch (error) {
      console.error("Recalculate scores error:", error);
      toast.error("Failed to recalculate scores");
    } finally {
      setRecalculatingModelId(null);
    }
  }

  function selectAllTestRuns() {
    if (selectedTestRuns.size === testRuns.length) {
      setSelectedTestRuns(new Set());
    } else {
      setSelectedTestRuns(new Set(testRuns.map((tr) => tr.id)));
    }
  }

  function selectAllSubmissions() {
    if (selectedSubmissions.size === submissions.length) {
      setSelectedSubmissions(new Set());
    } else {
      setSelectedSubmissions(new Set(submissions.map((s) => s.id)));
    }
  }

  function selectAllModels() {
    if (selectedModels.size === models.length) {
      setSelectedModels(new Set());
    } else {
      setSelectedModels(new Set(models.map((m) => m.id)));
    }
  }

  if (userLoading || profileLoading) {
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

  // Double-check admin permission before rendering
  if (!canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed":
      case "approved":
        return "default";
      case "running":
      case "reviewing":
      case "pending":
        return "secondary";
      case "failed":
      case "rejected":
        return "destructive";
      default:
        return "outline";
    }
  };

  return (
    <div className="container py-8">
      {/* Breadcrumb */}
      <nav className="mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/admin" className="hover:text-primary transition-colors">
              Admin
            </Link>
          </li>
          <li>
            <ChevronRight className="h-4 w-4" />
          </li>
          <li className="text-foreground font-medium">
            Data Management
          </li>
        </ol>
      </nav>

      <div className="mb-8">
        <h1 className="text-4xl font-bold">Data Management</h1>
        <p className="mt-2 text-muted-foreground">
          Delete test runs, submissions, and clean up database records
        </p>
      </div>

      <Tabs defaultValue="test-runs" className="space-y-6">
        <TabsList>
          <TabsTrigger value="test-runs">
            Test Runs ({testRunsTotal})
          </TabsTrigger>
          <TabsTrigger value="submissions">
            Community Submissions ({submissionsTotal})
          </TabsTrigger>
          <TabsTrigger value="models">
            Models ({modelsTotal})
          </TabsTrigger>
        </TabsList>

        {/* Test Runs Tab */}
        <TabsContent value="test-runs">
          <Card>
            <CardHeader>
              <CardTitle>Test Runs</CardTitle>
              <CardDescription>
                Manage and delete test runs. Deleting a test run also deletes all its results.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-4">
                <Select value={testRunStatusFilter} onValueChange={setTestRunStatusFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="running">Running</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
                {selectedTestRuns.size > 0 && (
                  <Button
                    variant="destructive"
                    onClick={() => openBulkDeleteDialog("test-run")}
                  >
                    Delete Selected ({selectedTestRuns.size})
                  </Button>
                )}
              </div>

              {/* Table */}
              {testRunsLoading ? (
                <Skeleton className="h-64" />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <Checkbox
                          checked={selectedTestRuns.size === testRuns.length && testRuns.length > 0}
                          onCheckedChange={selectAllTestRuns}
                        />
                      </TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>Version</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Results</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {testRuns.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-muted-foreground">
                          No test runs found
                        </TableCell>
                      </TableRow>
                    ) : (
                      testRuns.map((tr) => (
                        <TableRow key={tr.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedTestRuns.has(tr.id)}
                              onCheckedChange={() => toggleTestRunSelection(tr.id)}
                            />
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {tr.user_email || tr.user_id.slice(0, 8)}
                          </TableCell>
                          <TableCell>{tr.model_name || "—"}</TableCell>
                          <TableCell>{tr.question_set_version || "—"}</TableCell>
                          <TableCell>
                            <Badge variant={getStatusBadgeVariant(tr.status)}>
                              {tr.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{tr.result_count}</TableCell>
                          <TableCell>
                            {tr.created_at
                              ? new Date(tr.created_at).toLocaleDateString()
                              : "—"}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() =>
                                openDeleteDialog(
                                  "test-run",
                                  tr.id,
                                  `Test run for ${tr.model_name || "unknown model"}`
                                )
                              }
                            >
                              Delete
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Community Submissions Tab */}
        <TabsContent value="submissions">
          <Card>
            <CardHeader>
              <CardTitle>Community Submissions</CardTitle>
              <CardDescription>
                Manage and delete community-submitted benchmark results.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-4">
                <Select value={submissionStatusFilter} onValueChange={setSubmissionStatusFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="reviewing">Reviewing</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
                {selectedSubmissions.size > 0 && (
                  <Button
                    variant="destructive"
                    onClick={() => openBulkDeleteDialog("submission")}
                  >
                    Delete Selected ({selectedSubmissions.size})
                  </Button>
                )}
              </div>

              {/* Table */}
              {submissionsLoading ? (
                <Skeleton className="h-64" />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <Checkbox
                          checked={selectedSubmissions.size === submissions.length && submissions.length > 0}
                          onCheckedChange={selectAllSubmissions}
                        />
                      </TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>Organization</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Version</TableHead>
                      <TableHead>Submitted</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {submissions.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} className="text-center text-muted-foreground">
                          No submissions found
                        </TableCell>
                      </TableRow>
                    ) : (
                      submissions.map((sub) => (
                        <TableRow key={sub.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedSubmissions.has(sub.id)}
                              onCheckedChange={() => toggleSubmissionSelection(sub.id)}
                            />
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {sub.user_email || sub.user_id.slice(0, 8)}
                          </TableCell>
                          <TableCell>{sub.model_name}</TableCell>
                          <TableCell>{sub.organization || "—"}</TableCell>
                          <TableCell>
                            <Badge variant={getStatusBadgeVariant(sub.status)}>
                              {sub.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{sub.overall_score ?? "—"}</TableCell>
                          <TableCell>{sub.question_set_version}</TableCell>
                          <TableCell>
                            {sub.submitted_at
                              ? new Date(sub.submitted_at).toLocaleDateString()
                              : "—"}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() =>
                                openDeleteDialog(
                                  "submission",
                                  sub.id,
                                  `Submission for ${sub.model_name}`
                                )
                              }
                            >
                              Delete
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models">
          <Card>
            <CardHeader>
              <CardTitle>Models</CardTitle>
              <CardDescription>
                Manage and delete model records. Models with existing test runs cannot be deleted.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-4">
                <Input
                  placeholder="Search by name or provider..."
                  value={modelSearch}
                  onChange={(e) => setModelSearch(e.target.value)}
                  className="max-w-sm"
                />
                {selectedModels.size > 0 && (
                  <Button
                    variant="destructive"
                    onClick={() => openBulkDeleteDialog("model")}
                  >
                    Delete Selected ({selectedModels.size})
                  </Button>
                )}
              </div>

              {/* Table */}
              {modelsLoading ? (
                <Skeleton className="h-64" />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <Checkbox
                          checked={selectedModels.size === models.length && models.length > 0}
                          onCheckedChange={selectAllModels}
                        />
                      </TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Provider</TableHead>
                      <TableHead>Model ID</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Test Runs</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {models.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-muted-foreground">
                          No models found
                        </TableCell>
                      </TableRow>
                    ) : (
                      models.map((model) => (
                        <TableRow key={model.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedModels.has(model.id)}
                              onCheckedChange={() => toggleModelSelection(model.id)}
                              disabled={model.test_run_count > 0}
                            />
                          </TableCell>
                          <TableCell className="font-medium">{model.name}</TableCell>
                          <TableCell>{model.provider}</TableCell>
                          <TableCell className="font-mono text-xs">{model.model_id}</TableCell>
                          <TableCell>
                            <Badge variant={model.is_active ? "default" : "secondary"}>
                              {model.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {model.test_run_count > 0 ? (
                              <span className="text-muted-foreground">
                                {model.test_run_count} (protected)
                              </span>
                            ) : (
                              "0"
                            )}
                          </TableCell>
                          <TableCell>
                            {model.created_at
                              ? new Date(model.created_at).toLocaleDateString()
                              : "—"}
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2 flex-wrap">
                            {model.test_run_count > 0 && (
                              <Button
                                variant="outline"
                                size="sm"
                                disabled={recalculatingModelId === model.id}
                                onClick={() => handleRecalculateScores(model.id, model.name)}
                              >
                                {recalculatingModelId === model.id ? "Recalculating…" : "Recalculate scores"}
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              disabled={model.test_run_count > 0}
                              onClick={() =>
                                openDeleteDialog("model", model.id, model.name)
                              }
                            >
                              {model.test_run_count > 0 ? "Protected" : "Delete"}
                            </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onOpenChange={(open) => {
        if (!open) {
          setDeleteDialog({ open: false, type: null, id: null, name: "", isBulk: false, count: 0 });
          setBulkConfirmText("");
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {deleteDialog.isBulk
                ? `Delete ${deleteDialog.count} item(s)?`
                : "Delete item?"}
            </DialogTitle>
            <DialogDescription>
              {deleteDialog.isBulk ? (
                <>
                  <p className="mb-4">
                    You are about to permanently delete {deleteDialog.count}{" "}
                    {deleteDialog.type === "test-run"
                      ? "test run(s)"
                      : deleteDialog.type === "submission"
                      ? "submission(s)"
                      : "model(s)"}
                    . This action cannot be undone.
                  </p>
                  <p className="mb-2">
                    Type <strong>DELETE {deleteDialog.count} ITEMS</strong> to confirm:
                  </p>
                  <Input
                    value={bulkConfirmText}
                    onChange={(e) => setBulkConfirmText(e.target.value)}
                    placeholder={`DELETE ${deleteDialog.count} ITEMS`}
                    className="font-mono"
                  />
                </>
              ) : (
                <p>
                  Are you sure you want to delete{" "}
                  <strong>{deleteDialog.name}</strong>?{" "}
                  {deleteDialog.type === "test-run" &&
                    "This will also delete all associated results."}
                  This action cannot be undone.
                </p>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteDialog({ open: false, type: null, id: null, name: "", isBulk: false, count: 0 });
                setBulkConfirmText("");
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={
                deleting ||
                (deleteDialog.isBulk &&
                  bulkConfirmText !== `DELETE ${deleteDialog.count} ITEMS`)
              }
            >
              {deleting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
