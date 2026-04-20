"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { PostCard } from "@/components/blog/PostCard";
import { Plus, FolderPlus, Tag, FileText, Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
}

interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: BlogCategory[];
  created_at: string;
  published_at?: string;
}

export default function BlogManagerPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const { canManageBlog, canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Pagination state
  const PAGE_SIZE = 20;
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPosts, setTotalPosts] = useState(0);

  // Global stats (independent of status filter / page)
  const [totalAllPosts, setTotalAllPosts] = useState(0);
  const [totalPublished, setTotalPublished] = useState(0);
  const [totalDrafts, setTotalDrafts] = useState(0);
  
  // Category dialog state
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [categoryForm, setCategoryForm] = useState({ name: "", slug: "", description: "" });
  const [editingCategory, setEditingCategory] = useState<BlogCategory | null>(null);
  const [savingCategory, setSavingCategory] = useState(false);
  
  // Delete dialog state
  const [deletePost, setDeletePost] = useState<BlogPost | null>(null);
  const [deleteCategory, setDeleteCategory] = useState<BlogCategory | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && !profileLoading) {
      if (!canManageBlog && !canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadData();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, userLoading, profileLoading, canManageBlog, canAdmin, isAdmin, statusFilter, currentPage, router]);

  async function loadData() {
    setLoading(true);
    try {
      await Promise.all([loadPosts(), loadCategories(), loadStats()]);
    } finally {
      setLoading(false);
    }
  }

  async function loadPosts() {
    try {
      const params = new URLSearchParams();
      if (statusFilter && statusFilter !== "all") {
        params.append("status", statusFilter);
      }
      params.append("limit", String(PAGE_SIZE));
      params.append("offset", String((currentPage - 1) * PAGE_SIZE));

      const response = await fetch(`/api/blog-manager/posts?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setPosts(data.items || []);
        setTotalPosts(data.total ?? 0);
      }
    } catch (error) {
      console.error("Failed to load posts:", error);
      toast.error("Failed to load posts");
    }
  }

  async function loadStats() {
    try {
      const [allRes, pubRes, draftRes] = await Promise.all([
        fetch("/api/blog-manager/posts?limit=1&offset=0"),
        fetch("/api/blog-manager/posts?status=published&limit=1&offset=0"),
        fetch("/api/blog-manager/posts?status=draft&limit=1&offset=0"),
      ]);
      if (allRes.ok) {
        const d = await allRes.json();
        setTotalAllPosts(d.total ?? 0);
      }
      if (pubRes.ok) {
        const d = await pubRes.json();
        setTotalPublished(d.total ?? 0);
      }
      if (draftRes.ok) {
        const d = await draftRes.json();
        setTotalDrafts(d.total ?? 0);
      }
    } catch {
      // Stats are non-critical; keep existing values
    }
  }

  async function loadCategories() {
    try {
      const response = await fetch("/api/blog-manager/categories");
      if (response.ok) {
        const data = await response.json();
        setCategories(data.items || []);
      }
    } catch (error) {
      console.error("Failed to load categories:", error);
    }
  }

  if (userLoading || profileLoading || (loading && !user)) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Double-check blog management permission before rendering
  if (!canManageBlog && !canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  function generateSlug(name: string) {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/[\s_]+/g, "-")
      .replace(/-+/g, "-")
      .trim();
  }

  async function handleSaveCategory() {
    if (!categoryForm.name || !categoryForm.slug) {
      toast.error("Name and slug are required");
      return;
    }

    setSavingCategory(true);
    try {
      const url = editingCategory
        ? `/api/blog-manager/categories/${editingCategory.id}`
        : "/api/blog-manager/categories";
      const method = editingCategory ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(categoryForm),
      });

      if (response.ok) {
        toast.success(editingCategory ? "Category updated" : "Category created");
        setCategoryDialogOpen(false);
        setCategoryForm({ name: "", slug: "", description: "" });
        setEditingCategory(null);
        loadCategories();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to save category");
      }
    } catch (error) {
      toast.error("Failed to save category");
    } finally {
      setSavingCategory(false);
    }
  }

  async function handleDeletePost() {
    if (!deletePost) return;

    setDeleting(true);
    try {
      const response = await fetch(`/api/blog-manager/posts/${deletePost.id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Post deleted");
        setDeletePost(null);
        await Promise.all([loadPosts(), loadStats()]);
      } else {
        toast.error("Failed to delete post");
      }
    } catch (error) {
      toast.error("Failed to delete post");
    } finally {
      setDeleting(false);
    }
  }

  async function handleDeleteCategory() {
    if (!deleteCategory) return;

    setDeleting(true);
    try {
      const response = await fetch(`/api/blog-manager/categories/${deleteCategory.id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Category deleted");
        setDeleteCategory(null);
        loadCategories();
      } else {
        toast.error("Failed to delete category");
      }
    } catch (error) {
      toast.error("Failed to delete category");
    } finally {
      setDeleting(false);
    }
  }

  function openEditCategory(category: BlogCategory) {
    setEditingCategory(category);
    setCategoryForm({
      name: category.name,
      slug: category.slug,
      description: category.description || "",
    });
    setCategoryDialogOpen(true);
  }

  function openNewCategory() {
    setEditingCategory(null);
    setCategoryForm({ name: "", slug: "", description: "" });
    setCategoryDialogOpen(true);
  }

  const totalPages = Math.max(1, Math.ceil(totalPosts / PAGE_SIZE));

  return (
    <div className="container py-8">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-4xl font-bold">Blog Management</h1>
          <p className="mt-2 text-muted-foreground">
            Manage articles for the Insights section
          </p>
        </div>
        <Link href="/blog-manager/new">
          <Button variant="brand">
            <Plus className="h-4 w-4 mr-2" />
            New Post
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Posts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAllPosts}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Published
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{totalPublished}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Drafts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{totalDrafts}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{categories.length}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="posts" className="space-y-6">
        <TabsList>
          <TabsTrigger value="posts" className="gap-2">
            <FileText className="h-4 w-4" />
            Posts
          </TabsTrigger>
          <TabsTrigger value="categories" className="gap-2">
            <Tag className="h-4 w-4" />
            Categories
          </TabsTrigger>
        </TabsList>

        {/* Posts Tab */}
        <TabsContent value="posts" className="space-y-4">
          {/* Filter */}
          <div className="flex gap-2">
            <Button
              variant={statusFilter === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => { setStatusFilter("all"); setCurrentPage(1); }}
            >
              All ({totalAllPosts})
            </Button>
            <Button
              variant={statusFilter === "published" ? "default" : "outline"}
              size="sm"
              onClick={() => { setStatusFilter("published"); setCurrentPage(1); }}
            >
              Published ({totalPublished})
            </Button>
            <Button
              variant={statusFilter === "draft" ? "default" : "outline"}
              size="sm"
              onClick={() => { setStatusFilter("draft"); setCurrentPage(1); }}
            >
              Drafts ({totalDrafts})
            </Button>
          </div>

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          ) : posts.length === 0 ? (
            <Card className="p-12 text-center">
              <CardContent>
                <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground mb-4">
                  {statusFilter === "all"
                    ? "No posts yet. Create your first post!"
                    : `No ${statusFilter} posts found.`}
                </p>
                <Link href="/blog-manager/new">
                  <Button>Create Post</Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  showActions
                  onEdit={() => router.push(`/blog-manager/${post.id}`)}
                  onDelete={() => setDeletePost(post)}
                />
              ))}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <p className="text-sm text-muted-foreground">
                    Showing {(currentPage - 1) * PAGE_SIZE + 1}–
                    {Math.min(currentPage * PAGE_SIZE, totalPosts)} of {totalPosts} posts
                  </p>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage((p) => p - 1)}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    {Array.from({ length: totalPages }, (_, i) => i + 1)
                      .filter((page) => {
                        if (totalPages <= 7) return true;
                        if (page === 1 || page === totalPages) return true;
                        return Math.abs(page - currentPage) <= 1;
                      })
                      .reduce<(number | "ellipsis")[]>((acc, page, idx, arr) => {
                        if (idx > 0 && page - (arr[idx - 1] as number) > 1) {
                          acc.push("ellipsis");
                        }
                        acc.push(page);
                        return acc;
                      }, [])
                      .map((item, idx) =>
                        item === "ellipsis" ? (
                          <span key={`e-${idx}`} className="px-2 text-muted-foreground text-sm">
                            …
                          </span>
                        ) : (
                          <Button
                            key={item}
                            variant={item === currentPage ? "default" : "outline"}
                            size="sm"
                            className="min-w-[2rem]"
                            onClick={() => setCurrentPage(item)}
                          >
                            {item}
                          </Button>
                        )
                      )}
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage((p) => p + 1)}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </TabsContent>

        {/* Categories Tab */}
        <TabsContent value="categories" className="space-y-4">
          <div className="flex justify-end">
            <Button onClick={openNewCategory}>
              <FolderPlus className="h-4 w-4 mr-2" />
              New Category
            </Button>
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          ) : categories.length === 0 ? (
            <Card className="p-12 text-center">
              <CardContent>
                <Tag className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground mb-4">
                  No categories yet. Create your first category!
                </p>
                <Button onClick={openNewCategory}>Create Category</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {categories.map((category) => (
                <Card key={category.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <CardDescription>/{category.slug}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {category.description && (
                      <p className="text-sm text-muted-foreground mb-4">
                        {category.description}
                      </p>
                    )}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditCategory(category)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => setDeleteCategory(category)}
                      >
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Category Dialog */}
      <Dialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingCategory ? "Edit Category" : "New Category"}
            </DialogTitle>
            <DialogDescription>
              {editingCategory
                ? "Update the category details"
                : "Create a new category for organizing posts"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={categoryForm.name}
                onChange={(e) => {
                  const name = e.target.value;
                  setCategoryForm({
                    ...categoryForm,
                    name,
                    slug: editingCategory ? categoryForm.slug : generateSlug(name),
                  });
                }}
                placeholder="e.g., Prompting Tips"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slug">Slug</Label>
              <Input
                id="slug"
                value={categoryForm.slug}
                onChange={(e) =>
                  setCategoryForm({ ...categoryForm, slug: e.target.value })
                }
                placeholder="e.g., prompting-tips"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Input
                id="description"
                value={categoryForm.description}
                onChange={(e) =>
                  setCategoryForm({ ...categoryForm, description: e.target.value })
                }
                placeholder="Brief description of this category"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCategoryDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveCategory} disabled={savingCategory}>
              {savingCategory ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : editingCategory ? (
                "Update"
              ) : (
                "Create"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Post Confirmation */}
      <AlertDialog open={!!deletePost} onOpenChange={() => setDeletePost(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Post</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{deletePost?.title}&quot;? This action
              cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeletePost}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleting}
            >
              {deleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Category Confirmation */}
      <AlertDialog open={!!deleteCategory} onOpenChange={() => setDeleteCategory(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Category</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the &quot;{deleteCategory?.name}&quot; category?
              Posts in this category will not be deleted but will be uncategorized.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteCategory}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleting}
            >
              {deleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

