"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { Sparkles, MessageSquare, DollarSign, User, Clock, CheckCircle2, XCircle } from "lucide-react";

interface SponsorshipDetail {
  id: string;
  request_type: string;
  openrouter_model_id?: string;
  custom_model_name?: string;
  model_name: string;
  user_id: string;
  user_name: string;
  user_email: string;
  message?: string;
  status: string;
  payment_id?: string;
  payment_status?: string;
  created_at: string;
  reviewed_at?: string;
  reviewer_notes?: string;
}

export default function SponsorshipReviewPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const sponsorshipId = params.id as string;
  
  const [sponsorship, setSponsorship] = useState<SponsorshipDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [action, setAction] = useState<"approve" | "reject" | "">("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && sponsorshipId) {
      loadSponsorshipData();
    }
  }, [user, userLoading, sponsorshipId, router]);

  async function loadSponsorshipData() {
    setLoading(true);
    try {
      const data = await apiClient.getSponsorshipDetail(sponsorshipId);
      setSponsorship(data);
    } catch (error: any) {
      console.error("Failed to load sponsorship:", error);
      toast.error(error.message || "Failed to load sponsorship data");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitReview() {
    if (!sponsorship || !action) {
      toast.error("Please select an action (approve or reject)");
      return;
    }

    // For sponsorships, verify payment before approving
    if (action === "approve" && sponsorship.request_type === "sponsorship" && sponsorship.payment_status !== "succeeded") {
      toast.error("Cannot approve - payment not completed");
      return;
    }

    setSubmitting(true);
    try {
      const data = await apiClient.reviewSponsorship(
        sponsorshipId,
        action,
        notes.trim() || undefined
      );
      toast.success(data.message || "Review submitted successfully");
      router.push("/moderator");
    } catch (error: any) {
      console.error("Failed to submit review:", error);
      toast.error(error.message || "Failed to submit review");
    } finally {
      setSubmitting(false);
    }
  }

  if (userLoading || loading) {
    return (
      <div className="container py-8 max-w-4xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user || !sponsorship) {
    return (
      <div className="container py-8 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle>Review Not Available</CardTitle>
            <CardDescription>
              This sponsorship request is not available for review.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/moderator">Back to Queue</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isSponsorship = sponsorship.request_type === "sponsorship";
  const isPaid = sponsorship.payment_status === "succeeded";

  return (
    <div className="container py-8 max-w-4xl">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/moderator">← Back to Queue</Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              {isSponsorship ? (
                <Sparkles className="h-8 w-8 text-[--ga-red]" />
              ) : (
                <MessageSquare className="h-8 w-8 text-muted-foreground" />
              )}
              <h1 className="text-3xl font-bold">
                {isSponsorship ? "Sponsorship Request" : "Model Request"}
              </h1>
            </div>
            <p className="text-muted-foreground mt-2">
              {sponsorship.model_name}
            </p>
          </div>
          <div className="text-right">
            <Badge variant={sponsorship.status === "pending" ? "destructive" : "outline"}>
              {sponsorship.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Request Details */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Request Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <Label className="text-sm text-muted-foreground">Type</Label>
              <div className="flex items-center gap-2">
                {isSponsorship ? (
                  <>
                    <DollarSign className="h-4 w-4 text-green-600" />
                    <span className="font-medium">Paid Sponsorship ($20)</span>
                  </>
                ) : (
                  <>
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Free Request</span>
                  </>
                )}
              </div>
            </div>

            <div className="space-y-1">
              <Label className="text-sm text-muted-foreground">Model</Label>
              <p className="font-medium break-all">
                {sponsorship.openrouter_model_id || sponsorship.custom_model_name || sponsorship.model_name}
              </p>
            </div>

            <div className="space-y-1">
              <Label className="text-sm text-muted-foreground">User</Label>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{sponsorship.user_name}</span>
                <span className="text-sm text-muted-foreground">({sponsorship.user_email})</span>
              </div>
            </div>

            <div className="space-y-1">
              <Label className="text-sm text-muted-foreground">Submitted</Label>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {new Date(sponsorship.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Payment Status (for sponsorships) */}
          {isSponsorship && (
            <div className="pt-4 border-t">
              <Label className="text-sm text-muted-foreground">Payment Status</Label>
              <div className="mt-1 flex items-center gap-2">
                {isPaid ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <Badge variant="default" className="bg-green-100 text-green-700 border-green-200">
                      Payment Received
                    </Badge>
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5 text-destructive" />
                    <Badge variant="destructive">
                      {sponsorship.payment_status || "Payment Pending"}
                    </Badge>
                  </>
                )}
              </div>
              {!isPaid && (
                <p className="text-sm text-destructive mt-2">
                  Cannot approve sponsorship until payment is completed.
                </p>
              )}
            </div>
          )}

          {/* Message */}
          {sponsorship.message && (
            <div className="pt-4 border-t">
              <Label className="text-sm text-muted-foreground">Message from User</Label>
              <div className="mt-2 p-4 bg-muted rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{sponsorship.message}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Review Decision */}
      <Card>
        <CardHeader>
          <CardTitle>Review Decision</CardTitle>
          <CardDescription>
            {isSponsorship 
              ? "Approve to queue this model for benchmark testing, or reject if there are issues."
              : "Approve to acknowledge the request, or reject if it's not appropriate."
            }
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-base font-semibold mb-3 block">Action</Label>
            <RadioGroup value={action} onValueChange={(value) => setAction(value as "approve" | "reject")}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem 
                  value="approve" 
                  id="approve" 
                  disabled={isSponsorship && !isPaid}
                />
                <Label htmlFor="approve" className={`font-normal cursor-pointer ${isSponsorship && !isPaid ? "text-muted-foreground" : ""}`}>
                  Approve - {isSponsorship ? "Queue model for benchmark testing" : "Acknowledge model request"}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="reject" id="reject" />
                <Label htmlFor="reject" className="font-normal cursor-pointer">
                  Reject - {isSponsorship ? "Decline sponsorship request" : "Decline model request"}
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label htmlFor="notes" className="text-base font-semibold mb-2 block">
              Notes {action === "reject" && <span className="text-destructive">*</span>}
            </Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder={action === "reject" 
                ? "Please provide feedback on why this request is being rejected..." 
                : "Optional notes..."
              }
              rows={4}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => router.push("/moderator")} disabled={submitting}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmitReview}
              disabled={submitting || !action || (action === "reject" && !notes.trim()) || (action === "approve" && isSponsorship && !isPaid)}
            >
              {submitting ? "Submitting..." : "Submit Review"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
