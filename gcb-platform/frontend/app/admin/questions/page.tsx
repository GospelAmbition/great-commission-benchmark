"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@auth0/nextjs-auth0/client";
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
  tier: "tier1" | "tier2" | "tier3";
  category: string;
  status: "draft" | "pending" | "approved" | "rejected";
  created_at: string;
  updated_at: string;
}

export default function AdminQuestionsPage() {
  const { user, isLoading: userLoading } = useUser();
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
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
      router.push("/api/auth/login");
      return;
    }
    if (user) {
      loadQuestions();
    }
  }, [user, userLoading, router]);

  async function loadQuestions() {
    setLoading(true);
    try {
      const response = await fetch("/api/admin/questions");
      if (response.ok) {
        const data = await response.json();
        setQuestions(data.items || []);
      } else {
        // Use placeholder data for demo
        setQuestions(
          Array.from({ length: 10 }, (_, i) => ({
            id: `q-${i}`,
            content: `Sample question ${i + 1} about Christian doctrine and practice...`,
            tier: (["tier1", "tier2", "tier3"] as const)[i % 3],
            category: categories[i % categories.length],
            status: (["draft", "pending", "approved", "rejected"] as const)[i % 4],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }))
        );
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
    if (tierFilter !== "all" && q.tier !== tierFilter) return false;
    if (categoryFilter !== "all" && q.category !== categoryFilter) return false;
    if (statusFilter !== "all" && q.status !== statusFilter) return false;
    return true;
  });

  const tierCounts = questions.reduce((acc, q) => {
    acc[q.tier] = (acc[q.tier] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);


  if (userLoading || loading) {
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

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Questions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{questions.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 1 (70%)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{tierCounts.tier1 || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 2 (20%)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{tierCounts.tier2 || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tier 3 (10%)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{tierCounts.tier3 || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
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
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat} className="capitalize">
                    {cat}
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
                    <Badge variant="outline">{q.tier}</Badge>
                  </TableCell>
                  <TableCell className="capitalize">{q.category}</TableCell>
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
                    {new Date(q.updated_at).toLocaleDateString()}
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
              <Badge variant="outline">{selectedQuestion?.tier}</Badge>
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
