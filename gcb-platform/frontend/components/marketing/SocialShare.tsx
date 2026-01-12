"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { Share2, Twitter, Linkedin, Mail, Link2, Check } from "lucide-react";
import { trackSocialShare } from "@/lib/analytics";

interface SocialShareProps {
  /** The URL to share */
  url: string;
  /** The title/headline for sharing */
  title: string;
  /** Optional description for platforms that support it */
  description?: string;
  /** Optional hashtags for Twitter (without #) */
  hashtags?: string[];
  /** Visual variant */
  variant?: "default" | "outline" | "ghost";
  /** Size variant */
  size?: "default" | "sm" | "lg" | "icon";
  /** Additional class names */
  className?: string;
  /** Callback when share is attempted */
  onShare?: (platform: string) => void;
}

// Facebook icon component (lucide-react doesn't have one)
function FacebookIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
    </svg>
  );
}

/**
 * SocialShare Component
 * Provides share buttons for social media platforms with native Web Share API fallback
 */
export function SocialShare({
  url,
  title,
  description,
  hashtags = ["GreatCommissionBenchmark", "AI"],
  variant = "outline",
  size = "default",
  className,
  onShare,
}: SocialShareProps) {
  const [copied, setCopied] = useState(false);

  // Encode parameters for URLs
  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);
  const encodedDescription = encodeURIComponent(description || title);
  const hashtagString = hashtags.join(",");

  // Share URLs for each platform
  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}&hashtags=${hashtagString}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedTitle}`,
    email: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${encodedUrl}`,
  };

  // Handle share action
  const handleShare = async (platform: string) => {
    onShare?.(platform);
    // Track share event
    trackSocialShare(platform, "page");

    // Try native Web Share API for mobile
    if (platform === "native" && navigator.share) {
      try {
        await navigator.share({
          title,
          text: description || title,
          url,
        });
        toast.success("Shared successfully!");
        return;
      } catch (err) {
        // User cancelled or error - fall through to show menu
        if ((err as Error).name !== "AbortError") {
          console.error("Share failed:", err);
        }
        return;
      }
    }

    // Copy to clipboard
    if (platform === "copy") {
      try {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        toast.success("Link copied to clipboard!");
        setTimeout(() => setCopied(false), 2000);
      } catch {
        toast.error("Failed to copy link");
      }
      return;
    }

    // Open share URL in new window
    const shareUrl = shareUrls[platform as keyof typeof shareUrls];
    if (shareUrl) {
      if (platform === "email") {
        window.location.href = shareUrl;
      } else {
        window.open(shareUrl, "_blank", "noopener,noreferrer,width=600,height=400");
      }
    }
  };

  // Check if native share is available (primarily mobile)
  const hasNativeShare = typeof navigator !== "undefined" && navigator.share;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} className={className}>
          <Share2 className="h-4 w-4 mr-2" />
          Share
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {hasNativeShare && (
          <DropdownMenuItem onClick={() => handleShare("native")}>
            <Share2 className="h-4 w-4 mr-2" />
            Share...
          </DropdownMenuItem>
        )}
        <DropdownMenuItem onClick={() => handleShare("twitter")}>
          <Twitter className="h-4 w-4 mr-2" />
          Share on X
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("linkedin")}>
          <Linkedin className="h-4 w-4 mr-2" />
          Share on LinkedIn
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("facebook")}>
          <FacebookIcon className="h-4 w-4 mr-2" />
          Share on Facebook
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("email")}>
          <Mail className="h-4 w-4 mr-2" />
          Share via Email
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("copy")}>
          {copied ? (
            <Check className="h-4 w-4 mr-2 text-green-500" />
          ) : (
            <Link2 className="h-4 w-4 mr-2" />
          )}
          {copied ? "Copied!" : "Copy Link"}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Compact share buttons for inline use
 */
export function SocialShareButtons({
  url,
  title,
  description,
  hashtags = ["GreatCommissionBenchmark", "AI"],
  className,
  onShare,
}: Omit<SocialShareProps, "variant" | "size">) {
  const [copied, setCopied] = useState(false);

  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);
  const encodedDescription = encodeURIComponent(description || title);
  const hashtagString = hashtags.join(",");

  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}&hashtags=${hashtagString}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedTitle}`,
  };

  const handleShare = (platform: string) => {
    onShare?.(platform);
    trackSocialShare(platform, "page");
    const shareUrl = shareUrls[platform as keyof typeof shareUrls];
    if (shareUrl) {
      window.open(shareUrl, "_blank", "noopener,noreferrer,width=600,height=400");
    }
  };

  const handleCopy = async () => {
    onShare?.("copy");
    trackSocialShare("copy", "page");
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      toast.success("Link copied!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy link");
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className || ""}`}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => handleShare("twitter")}
        title="Share on X (Twitter)"
      >
        <Twitter className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => handleShare("linkedin")}
        title="Share on LinkedIn"
      >
        <Linkedin className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => handleShare("facebook")}
        title="Share on Facebook"
      >
        <FacebookIcon className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={handleCopy}
        title="Copy link"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Link2 className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
