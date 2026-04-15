"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { PostEditor } from "@/components/blog/PostEditor";
import { ImageUploader } from "@/components/blog/ImageUploader";
import { ChevronLeft, Save, Send, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

interface BlogCategory {
  id: string;
  name: string;
  slug: string;
}

export default function NewBlogPostPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const { canManageBlog, canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  
  const [form, setForm] = useState({
    title: "",
    slug: "",
    excerpt: "",
    content: "",
    featured_image_url: "",
    category_ids: [] as string[],
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
      loadCategories();
    }
  }, [user, userLoading, profileLoading, canManageBlog, canAdmin, isAdmin, router]);

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

  if (userLoading || profileLoading) {
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

  function generateSlug(title: string) {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/[\s_]+/g, "-")
      .replace(/-+/g, "-")
      .trim();
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

  async function handleSave(publish: boolean = false) {
    if (!form.title || !form.slug) {
      toast.error("Title and slug are required");
      return;
    }

    if (publish) {
      setPublishing(true);
    } else {
      setSaving(true);
    }

    try {
      // Create the post
      const response = await fetch("/api/blog-manager/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: form.title,
          slug: form.slug,
          excerpt: form.excerpt || null,
          content: form.content || null,
          featured_image_url: form.featured_image_url || null,
          category_ids: form.category_ids,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create post");
      }

      const post = await response.json();

      // If publishing, publish the post
      if (publish) {
        const publishResponse = await fetch(`/api/blog-manager/posts/${post.id}/publish`, {
          method: "POST",
        });

        if (!publishResponse.ok) {
          toast.warning("Post created but failed to publish");
        } else {
          toast.success("Post published successfully!");
        }
      } else {
        toast.success("Post saved as draft");
      }

      router.push("/blog-manager");
    } catch (error: any) {
      toast.error(error.message || "Failed to save post");
    } finally {
      setSaving(false);
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

  return (
    <div className="container py-8 max-w-5xl">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/blog-manager">
          <Button variant="ghost" size="icon">
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">New Post</h1>
          <p className="text-muted-foreground">Create a new blog post for the Insights section</p>
        </div>
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
                  onChange={(e) => {
                    const title = e.target.value;
                    setForm({
                      ...form,
                      title,
                      slug: form.slug || generateSlug(title),
                    });
                  }}
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
                onClick={() => handleSave(false)}
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
                    Save Draft
                  </>
                )}
              </Button>
              <Button
                onClick={() => handleSave(true)}
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
        </div>
      </div>
    </div>
  );
}

