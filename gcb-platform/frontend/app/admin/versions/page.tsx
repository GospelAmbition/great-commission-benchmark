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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Link from "next/link";
import { toast } from "sonner";

interface BenchmarkVersion {
  version: string;
  status: "draft" | "locked" | "published" | "archived";
  question_count: number;
  tier1_count: number;
  tier2_count: number;
  tier3_count: number;
  created_at: string;
  published_at?: string;
  is_current: boolean;
}

export default function AdminVersionsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [versions, setVersions] = useState<BenchmarkVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newVersion, setNewVersion] = useState("");
  const [newMarketingVersion, setNewMarketingVersion] = useState("");
  const [copyFromVersion, setCopyFromVersion] = useState(false);
  const [sourceVersion, setSourceVersion] = useState("");
  const [creating, setCreating] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<BenchmarkVersion | null>(null);
  const [showPublishDialog, setShowPublishDialog] = useState(false);
  const [showEmptyDialog, setShowEmptyDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadVersions();
    }
  }, [user, userLoading, router]);

  async function loadVersions() {
    setLoading(true);
    try {
      const response = await fetch("/api/admin/versions");
      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions || []);
      } else {
        // Use placeholder data for demo
        setVersions([
          {
            version: "1.0.0",
            status: "published",
            question_count: 100,
            tier1_count: 70,
            tier2_count: 20,
            tier3_count: 10,
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            published_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
            is_current: true,
          },
          {
            version: "0.9.0",
            status: "archived",
            question_count: 80,
            tier1_count: 56,
            tier2_count: 16,
            tier3_count: 8,
            created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
            published_at: new Date(Date.now() - 55 * 24 * 60 * 60 * 1000).toISOString(),
            is_current: false,
          },
          {
            version: "1.1.0",
            status: "draft",
            question_count: 50,
            tier1_count: 35,
            tier2_count: 10,
            tier3_count: 5,
            created_at: new Date().toISOString(),
            is_current: false,
          },
        ]);
      }
    } catch (error) {
      console.error("Failed to load versions:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateVersion() {
    if (!newVersion) return;
    setCreating(true);
    try {
      if (copyFromVersion && sourceVersion) {
        // Copy from existing version
        const response = await fetch(`/api/admin/versions/${sourceVersion}/copy`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            new_semantic_version: newVersion,
            new_marketing_version: newMarketingVersion || `Version ${newVersion}`,
          }),
        });

        if (response.ok) {
          toast.success(`Version ${newVersion} created by copying from ${sourceVersion}`);
          setShowCreateDialog(false);
          setNewVersion("");
          setNewMarketingVersion("");
          setCopyFromVersion(false);
          setSourceVersion("");
          loadVersions();
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || "Failed to copy version");
        }
      } else {
        // Create empty version
        const response = await fetch("/api/admin/versions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            version: newVersion,
            marketing_version: newMarketingVersion || `Version ${newVersion}`,
          }),
        });

        if (response.ok) {
          toast.success(`Version ${newVersion} created`);
          setShowCreateDialog(false);
          setNewVersion("");
          setNewMarketingVersion("");
          setCopyFromVersion(false);
          setSourceVersion("");
          loadVersions();
        } else {
          throw new Error("Failed to create version");
        }
      }
    } catch (error: any) {
      console.error("Failed to create version:", error);
      toast.error(error.message || "Failed to create version");
    } finally {
      setCreating(false);
    }
  }

  async function handleLockVersion(version: string) {
    try {
      const response = await fetch(`/api/admin/versions/${version}/lock`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success(`Version ${version} locked`);
        loadVersions();
      } else {
        throw new Error("Failed to lock");
      }
    } catch (error) {
      console.error("Failed to lock version:", error);
      toast.error("Failed to lock version");
    }
  }

  async function handlePublishVersion() {
    if (!selectedVersion) return;
    try {
      const response = await fetch(
        `/api/admin/versions/${selectedVersion.version}/publish`,
        {
          method: "PUT",
        }
      );

      if (response.ok) {
        toast.success(`Version ${selectedVersion.version} published`);
        setShowPublishDialog(false);
        setSelectedVersion(null);
        loadVersions();
      } else {
        throw new Error("Failed to publish");
      }
    } catch (error) {
      console.error("Failed to publish version:", error);
      toast.error("Failed to publish version");
    }
  }

  async function handleEmptyVersion() {
    if (!selectedVersion) return;
    setActionLoading(true);
    try {
      const response = await fetch(
        `/api/admin/versions/${selectedVersion.version}/empty`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        const data = await response.json();
        toast.success(`Removed ${data.deleted_questions} questions from version ${selectedVersion.version}`);
        setShowEmptyDialog(false);
        setSelectedVersion(null);
        loadVersions();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to empty version");
      }
    } catch (error: any) {
      console.error("Failed to empty version:", error);
      toast.error(error.message || "Failed to empty version");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteVersion() {
    if (!selectedVersion) return;
    setActionLoading(true);
    try {
      const response = await fetch(
        `/api/admin/versions/${selectedVersion.version}/delete`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        toast.success(`Version ${selectedVersion.version} deleted`);
        setShowDeleteDialog(false);
        setSelectedVersion(null);
        loadVersions();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to delete version");
      }
    } catch (error: any) {
      console.error("Failed to delete version:", error);
      toast.error(error.message || "Failed to delete version");
    } finally {
      setActionLoading(false);
    }
  }

  function getTierDistribution(v: BenchmarkVersion) {
    const total = v.question_count || 1;
    return {
      tier1: Math.round((v.tier1_count / total) * 100),
      tier2: Math.round((v.tier2_count / total) * 100),
      tier3: Math.round((v.tier3_count / total) * 100),
    };
  }

  function validateDistribution(v: BenchmarkVersion) {
    const dist = getTierDistribution(v);
    const isValid = dist.tier1 >= 65 && dist.tier1 <= 75 &&
                   dist.tier2 >= 15 && dist.tier2 <= 25 &&
                   dist.tier3 >= 5 && dist.tier3 <= 15;
    return isValid;
  }

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

  const currentVersion = versions.find((v) => v.is_current);

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Version Management</h1>
            <p className="mt-2 text-muted-foreground">
              Manage benchmark versions and question sets
            </p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            Create New Version
          </Button>
        </div>
      </div>

      {/* Current Version */}
      {currentVersion && (
        <Card className="mb-8 border-[--ga-red]">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Current Version</CardTitle>
              <Badge variant="brand">Active</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-4">
              <div>
                <div className="text-3xl font-bold">{currentVersion.version}</div>
                <div className="text-sm text-muted-foreground">Version</div>
              </div>
              <div>
                <div className="text-3xl font-bold">{currentVersion.question_count}</div>
                <div className="text-sm text-muted-foreground">Total Questions</div>
              </div>
              <div>
                <div className="text-3xl font-bold">
                  {currentVersion.published_at
                    ? new Date(currentVersion.published_at).toLocaleDateString()
                    : "—"}
                </div>
                <div className="text-sm text-muted-foreground">Published</div>
              </div>
              <div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Tier 1</span>
                    <span>{currentVersion.tier1_count} ({getTierDistribution(currentVersion).tier1}%)</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tier 2</span>
                    <span>{currentVersion.tier2_count} ({getTierDistribution(currentVersion).tier2}%)</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tier 3</span>
                    <span>{currentVersion.tier3_count} ({getTierDistribution(currentVersion).tier3}%)</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Versions */}
      <Card>
        <CardHeader>
          <CardTitle>All Versions</CardTitle>
          <CardDescription>
            Benchmark version history and drafts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Version</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Questions</TableHead>
                <TableHead>Tier Distribution</TableHead>
                <TableHead>Validation</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {versions.map((v) => {
                const dist = getTierDistribution(v);
                const isValid = validateDistribution(v);
                return (
                  <TableRow key={v.version}>
                    <TableCell className="font-medium">
                      {v.version}
                      {v.is_current && (
                        <Badge className="ml-2" variant="brand">
                          Current
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          v.status === "published"
                            ? "default"
                            : v.status === "locked"
                            ? "secondary"
                            : v.status === "archived"
                            ? "outline"
                            : "outline"
                        }
                      >
                        {v.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{v.question_count}</TableCell>
                    <TableCell>
                      <div className="text-xs space-y-1">
                        <div>T1: {dist.tier1}%</div>
                        <div>T2: {dist.tier2}%</div>
                        <div>T3: {dist.tier3}%</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {isValid ? (
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Valid
                        </Badge>
                      ) : (
                        <Badge variant="destructive">Invalid</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(v.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {v.status === "draft" && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleLockVersion(v.version)}
                              disabled={!isValid}
                            >
                              Lock
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedVersion(v);
                                setShowEmptyDialog(true);
                              }}
                            >
                              Empty
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() => {
                                setSelectedVersion(v);
                                setShowDeleteDialog(true);
                              }}
                            >
                              Delete
                            </Button>
                          </>
                        )}
                        {v.status === "locked" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedVersion(v);
                              setShowPublishDialog(true);
                            }}
                          >
                            Publish
                          </Button>
                        )}
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/admin/versions/${v.version}`}>View</Link>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Version</DialogTitle>
            <DialogDescription>
              Create a new benchmark version draft
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <Label htmlFor="version">Version Number</Label>
              <Input
                id="version"
                placeholder="e.g., 1.2.0"
                value={newVersion}
                onChange={(e) => setNewVersion(e.target.value)}
                className="mt-1"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Use semantic versioning (MAJOR.MINOR.PATCH)
              </p>
            </div>
            <div>
              <Label htmlFor="marketing-version">Marketing Version (Optional)</Label>
              <Input
                id="marketing-version"
                placeholder="e.g., Version 1.2"
                value={newMarketingVersion}
                onChange={(e) => setNewMarketingVersion(e.target.value)}
                className="mt-1"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="copy-from"
                checked={copyFromVersion}
                onChange={(e) => {
                  setCopyFromVersion(e.target.checked);
                  if (!e.target.checked) {
                    setSourceVersion("");
                  }
                }}
                className="rounded"
              />
              <Label htmlFor="copy-from" className="cursor-pointer">
                Copy questions from existing version
              </Label>
            </div>
            {copyFromVersion && (
              <div>
                <Label htmlFor="source-version">Source Version</Label>
                <Select value={sourceVersion} onValueChange={setSourceVersion}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select version to copy from" />
                  </SelectTrigger>
                  <SelectContent>
                    {versions.map((v) => (
                      <SelectItem key={v.version} value={v.version}>
                        {v.version} - {v.question_count} questions
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-2">
                  All questions from the selected version will be copied to the new version
                </p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowCreateDialog(false);
              setNewVersion("");
              setNewMarketingVersion("");
              setCopyFromVersion(false);
              setSourceVersion("");
            }}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateVersion}
              disabled={!newVersion || creating || (copyFromVersion && !sourceVersion)}
            >
              {creating ? "Creating..." : copyFromVersion ? "Copy Version" : "Create Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Publish Dialog */}
      <Dialog open={showPublishDialog} onOpenChange={setShowPublishDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Publish Version</DialogTitle>
            <DialogDescription>
              Are you sure you want to publish version {selectedVersion?.version}? This
              will make it the current active version.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span>Questions:</span>
                <span className="font-medium">{selectedVersion?.question_count}</span>
              </div>
              <div className="flex justify-between">
                <span>Tier 1:</span>
                <span className="font-medium">
                  {selectedVersion && getTierDistribution(selectedVersion).tier1}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tier 2:</span>
                <span className="font-medium">
                  {selectedVersion && getTierDistribution(selectedVersion).tier2}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tier 3:</span>
                <span className="font-medium">
                  {selectedVersion && getTierDistribution(selectedVersion).tier3}%
                </span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPublishDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="brand"
              onClick={handlePublishVersion}
            >
              Publish Version
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Empty Version Dialog */}
      <Dialog open={showEmptyDialog} onOpenChange={setShowEmptyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Empty Version</DialogTitle>
            <DialogDescription>
              Are you sure you want to remove all questions from version {selectedVersion?.version}?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-destructive/10 border border-destructive/20 p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span>Questions to remove:</span>
                <span className="font-medium text-destructive">{selectedVersion?.question_count}</span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                The version will remain as a draft but will have no questions.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEmptyDialog(false)} disabled={actionLoading}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleEmptyVersion}
              disabled={actionLoading}
            >
              {actionLoading ? "Emptying..." : "Empty Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Version Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Version</DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete version {selectedVersion?.version}?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-destructive/10 border border-destructive/20 p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span>Version:</span>
                <span className="font-medium">{selectedVersion?.version}</span>
              </div>
              <div className="flex justify-between">
                <span>Questions:</span>
                <span className="font-medium text-destructive">{selectedVersion?.question_count}</span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                This will permanently delete the version and all its questions.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)} disabled={actionLoading}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteVersion}
              disabled={actionLoading}
            >
              {actionLoading ? "Deleting..." : "Delete Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
