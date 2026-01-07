"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Check, Copy, Twitter, Linkedin, Facebook, Mail } from "lucide-react";

interface ShareModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  modelName: string;
  score: number;
  testId: string;
  sponsorName?: string;
}

export function ShareModal({
  open,
  onOpenChange,
  modelName,
  score,
  testId,
  sponsorName,
}: ShareModalProps) {
  const [copied, setCopied] = useState(false);
  
  // Construct the share URL
  const baseUrl = typeof window !== "undefined" 
    ? window.location.origin 
    : "https://greatcommissionbenchmark.ai";
  const shareUrl = `${baseUrl}/tests/${testId}/results`;
  
  // Construct share text
  const shareText = sponsorName
    ? `${modelName} scored ${score.toFixed(1)} on the Great Commission Benchmark! Sponsored by ${sponsorName}`
    : `${modelName} scored ${score.toFixed(1)} on the Great Commission Benchmark!`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast.success("Link copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy link");
    }
  };

  const openShareWindow = (url: string) => {
    window.open(url, "_blank", "width=600,height=400,noopener,noreferrer");
  };

  const handleTwitterShare = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
    openShareWindow(url);
  };

  const handleLinkedInShare = () => {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
    openShareWindow(url);
  };

  const handleFacebookShare = () => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
    openShareWindow(url);
  };

  const handleEmailShare = () => {
    const subject = encodeURIComponent(`${modelName} - Great Commission Benchmark Results`);
    const body = encodeURIComponent(`${shareText}\n\nView the full results: ${shareUrl}`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share Your Results</DialogTitle>
          <DialogDescription>
            {shareText}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Copy link input */}
          <div className="flex items-center gap-2">
            <Input
              value={shareUrl}
              readOnly
              className="font-mono text-sm"
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={handleCopy}
              className="shrink-0"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Social share buttons */}
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">Share on:</div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleTwitterShare}
                className="flex-1"
              >
                <Twitter className="h-4 w-4 mr-2" />
                Twitter
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLinkedInShare}
                className="flex-1"
              >
                <Linkedin className="h-4 w-4 mr-2" />
                LinkedIn
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleFacebookShare}
                className="flex-1"
              >
                <Facebook className="h-4 w-4 mr-2" />
                Facebook
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleEmailShare}
                className="flex-1"
              >
                <Mail className="h-4 w-4 mr-2" />
                Email
              </Button>
            </div>
          </div>

          {/* Status indicator */}
          <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <Check className="h-4 w-4" />
            Results are live and ready to share
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

