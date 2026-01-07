"use client";

import Link from "next/link";
import Image from "next/image";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, User, Edit, Eye, Trash2 } from "lucide-react";

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

interface PostCardProps {
  post: BlogPost;
  onEdit?: (post: BlogPost) => void;
  onDelete?: (post: BlogPost) => void;
  showActions?: boolean;
}

export function PostCard({ post, onEdit, onDelete, showActions = false }: PostCardProps) {
  function formatDate(dateString?: string) {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <div className="flex flex-col md:flex-row">
        {/* Image */}
        <div className="relative h-32 md:h-auto md:w-48 flex-shrink-0 bg-muted">
          {post.featured_image_url ? (
            <Image
              src={post.featured_image_url}
              alt={post.title}
              fill
              className="object-cover"
            />
          ) : (
            <div className="h-full w-full flex items-center justify-center bg-gradient-to-br from-[--ga-red]/10 to-muted">
              <span className="text-2xl font-bold text-[--ga-red]/20">GCB</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              {/* Status & Categories */}
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <Badge 
                  variant={post.status === "published" ? "default" : "secondary"}
                  className={post.status === "published" ? "bg-green-600" : ""}
                >
                  {post.status === "published" ? "Published" : "Draft"}
                </Badge>
                {post.categories.slice(0, 2).map((cat) => (
                  <Badge key={cat.id} variant="outline" className="text-xs">
                    {cat.name}
                  </Badge>
                ))}
                {post.categories.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{post.categories.length - 2}
                  </Badge>
                )}
              </div>

              {/* Title */}
              <h3 className="font-semibold text-lg line-clamp-1 mb-1">
                {post.title}
              </h3>

              {/* Excerpt */}
              {post.excerpt && (
                <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                  {post.excerpt}
                </p>
              )}

              {/* Meta */}
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {post.author.name || "Anonymous"}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {post.status === "published" && post.published_at
                    ? formatDate(post.published_at)
                    : formatDate(post.created_at)}
                </span>
              </div>
            </div>

            {/* Actions */}
            {showActions && (
              <div className="flex items-center gap-2 flex-shrink-0">
                <Link href={`/action/${post.slug}`} target="_blank">
                  <Button variant="ghost" size="icon" title="View post">
                    <Eye className="h-4 w-4" />
                  </Button>
                </Link>
                {onEdit && (
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={() => onEdit(post)}
                    title="Edit post"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                )}
                {onDelete && (
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={() => onDelete(post)}
                    title="Delete post"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

