"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PostEditor } from "@/components/blog/PostEditor";
import { ImageUploader } from "@/components/blog/ImageUploader";
import { ModelPicker } from "@/components/blog/ModelPicker";
import { ChevronLeft, Save, Send, Eye, EyeOff, Loader2, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

interface BlogCategory {
  id: string;
  name: string;
  slug: string;
}

interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  content?: string;
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: BlogCategory[];
  related_models?: { id: string; model_id: string; name: string; provider: string }[];
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export default function EditBlogPostPage() {
  const router = useRouter();
  const params = useParams();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const { canManageBlog, canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const postId = params.id as string;
  
  const [post, setPost] = useState<BlogPost | null>(null);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  
  const [form, setForm] = useState({
    title: "",
    slug: "",
    excerpt: "",
    content: "",
    featured_image_url: "",
    category_ids: [] as string[],
    model_ids: [] as string[],
  });

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    // Check if user has blog management permission
    if (user && !profileLoading) {
      if (!canManageBlog && !canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      if (postId) {
        loadData();
      }
    }
  }, [user, userLoading, profileLoading, canManageBlog, canAdmin, isAdmin, postId, router]);

  async function loadData() {
    setLoading(true);
    try {
      await Promise.all([loadPost(), loadCategories()]);
    } finally {
      setLoading(false);
    }
  }

  async function loadPost() {
    try {
      const response = await fetch(`/api/blog-manager/posts/${postId}`);
      if (response.ok) {
        const data = await response.json();
        setPost(data);
        setForm({
          title: data.title,
          slug: data.slug,
          excerpt: data.excerpt || "",
          content: data.content || "",
          featured_image_url: data.featured_image_url || "",
          category_ids: data.categories.map((c: BlogCategory) => c.id),
          model_ids: (data.related_models || []).map((m: { model_id: string }) => m.model_id),
        });
      } else {
        toast.error("Post not found");
        router.push("/blog-manager");
      }
    } catch (error) {
      console.error("Failed to load post:", error);
      toast.error("Failed to load post");
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
        <div className="h-[500px] border rounded-md flex items-center justify-center bg-muted">
          <p className="text-muted-foreground">Loading...</p>
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

  async function handleUploadImage(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/blog-manager/upload-image", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload image");
    }

    const data = await response.json();
    return data.url;
  }

  async function handleSave() {
    if (!form.title || !form.slug) {
      toast.error("Title and slug are required");
      return;
    }

    setSaving(true);

    try {
      const response = await fetch(`/api/blog-manager/posts/${postId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: form.title,
          slug: form.slug,
          excerpt: form.excerpt || null,
          content: form.content || null,
          featured_image_url: form.featured_image_url || null,
          category_ids: form.category_ids,
          model_ids: form.model_ids,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update post");
      }

      const updatedPost = await response.json();
      setPost(updatedPost);
      toast.success("Post saved");
    } catch (error: any) {
      toast.error(error.message || "Failed to save post");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublish() {
    setPublishing(true);

    try {
      await fetch(`/api/blog-manager/posts/${postId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: form.title,
          slug: form.slug,
          excerpt: form.excerpt || null,
          content: form.content || null,
          featured_image_url: form.featured_image_url || null,
          category_ids: form.category_ids,
          model_ids: form.model_ids,
        }),
      });

      // Then publish
      const response = await fetch(`/api/blog-manager/posts/${postId}/publish`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to publish post");
      }

      const updatedPost = await response.json();
      setPost(updatedPost);
      toast.success("Post published!");
    } catch (error: any) {
      toast.error(error.message || "Failed to publish post");
    } finally {
      setPublishing(false);
    }
  }

  async function handleUnpublish() {
    setPublishing(true);

    try {
      const response = await fetch(`/api/blog-manager/posts/${postId}/unpublish`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to unpublish post");
      }

      const updatedPost = await response.json();
      setPost(updatedPost);
      toast.success("Post unpublished");
    } catch (error: any) {
      toast.error(error.message || "Failed to unpublish post");
    } finally {
      setPublishing(false);
    }
  }

  function toggleCategory(categoryId: string) {
    setForm((prev) => ({
      ...prev,
      category_ids: prev.category_ids.includes(categoryId)
        ? prev.category_ids.filter((id) => id !== categoryId)
        : [...prev.category_ids, categoryId],
    }));
  }

  if (loading) {
    return (
      <div className="container py-8 max-w-5xl">
        <Skeleton className="h-10 w-64 mb-8" />
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-96" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        </div>
      </div>
    );
  }

  if (!post) {
    return null;
  }

  return (
    <div className="container py-8 max-w-5xl">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Link href="/blog-manager">
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold">Edit Post</h1>
              <Badge variant={post.status === "published" ? "default" : "secondary"}>
                {post.status === "published" ? "Published" : "Draft"}
              </Badge>
            </div>
            <p className="text-muted-foreground">
              Last updated {new Date(post.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        {post.status === "published" && (
          <Link href={`/insights/${post.slug}`} target="_blank">
            <Button variant="outline">
              <ExternalLink className="h-4 w-4 mr-2" />
              View Post
            </Button>
          </Link>
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Post Content</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Enter post title"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="slug">Slug</Label>
                <Input
                  id="slug"
                  value={form.slug}
                  onChange={(e) => setForm({ ...form, slug: e.target.value })}
                  placeholder="url-friendly-slug"
                />
                <p className="text-xs text-muted-foreground">
                  URL: /insights/{form.slug || "your-slug"}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="excerpt">Excerpt</Label>
                <Textarea
                  id="excerpt"
                  value={form.excerpt}
                  onChange={(e) => setForm({ ...form, excerpt: e.target.value })}
                  placeholder="Brief summary of the post (shown in listings)"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Content</Label>
                <PostEditor
                  value={form.content}
                  onChange={(content) => setForm({ ...form, content })}
                  onImageUpload={handleUploadImage}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handleSave}
                disabled={saving || publishing}
                variant="outline"
                className="w-full"
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>

              {post.status === "draft" ? (
                <Button
                  onClick={handlePublish}
                  disabled={saving || publishing}
                  variant="brand"
                  className="w-full"
                >
                  {publishing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Publishing...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Publish
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  onClick={handleUnpublish}
                  disabled={saving || publishing}
                  variant="outline"
                  className="w-full"
                >
                  {publishing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Unpublishing...
                    </>
                  ) : (
                    <>
                      <EyeOff className="h-4 w-4 mr-2" />
                      Unpublish
                    </>
                  )}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Featured Image */}
          <Card>
            <CardHeader>
              <CardTitle>Featured Image</CardTitle>
            </CardHeader>
            <CardContent>
              <ImageUploader
                value={form.featured_image_url}
                onChange={(url) => setForm({ ...form, featured_image_url: url || "" })}
                onUpload={handleUploadImage}
              />
            </CardContent>
          </Card>

          {/* Categories */}
          <Card>
            <CardHeader>
              <CardTitle>Categories</CardTitle>
            </CardHeader>
            <CardContent>
              {categories.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No categories yet.{" "}
                  <Link href="/blog-manager" className="text-[--ga-red] hover:underline">
                    Create one
                  </Link>
                </p>
              ) : (
                <div className="space-y-3">
                  {categories.map((category) => (
                    <div key={category.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={category.id}
                        checked={form.category_ids.includes(category.id)}
                        onCheckedChange={() => toggleCategory(category.id)}
                      />
                      <label
                        htmlFor={category.id}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                      >
                        {category.name}
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Linked Models */}
          <ModelPicker
            value={form.model_ids}
            onChange={(model_ids) => setForm((prev) => ({ ...prev, model_ids }))}
          />

          {/* Post Info */}
          <Card>
            <CardHeader>
              <CardTitle>Post Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Author</span>
                <span>{post.author.name || post.author.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span>{new Date(post.created_at).toLocaleDateString()}</span>
              </div>
              {post.published_at && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Published</span>
                  <span>{new Date(post.published_at).toLocaleDateString()}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

