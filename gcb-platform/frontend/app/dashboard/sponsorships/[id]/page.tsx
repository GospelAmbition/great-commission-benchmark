"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { Sparkles, MessageSquare, DollarSign, User, Clock, CheckCircle2, XCircle, ArrowLeft } from "lucide-react";

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

export default function SponsorshipDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const sponsorshipId = params.id as string;
  
  const [sponsorship, setSponsorship] = useState<SponsorshipDetail | null>(null);
  const [loading, setLoading] = useState(true);

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
      const data = await apiClient.getUserSponsorshipDetail(sponsorshipId);
      setSponsorship(data);
    } catch (error: any) {
      console.error("Failed to load sponsorship:", error);
      toast.error(error.message || "Failed to load sponsorship data");
    } finally {
      setLoading(false);
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
            <CardTitle>Sponsorship Not Found</CardTitle>
            <CardDescription>
              This sponsorship request could not be found.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/dashboard">Back to Dashboard</Link>
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
      <div className="mb-6">
        <Button asChild variant="ghost" size="sm">
          <Link href="/dashboard">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </Button>
      </div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Sponsorship Request</h1>
        <p className="text-muted-foreground">
          View details of your sponsorship request
        </p>
      </div>

      <div className="space-y-6">
        {/* Status Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Request Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <Badge 
                  className={
                    sponsorship.status === "approved" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                    sponsorship.status === "rejected" ? "bg-red-500/20 text-red-400 border-red-500/30" :
                    sponsorship.status === "pending" ? "bg-blue-500/20 text-blue-400 border-blue-500/30" :
                    "bg-white/[0.06] text-muted-foreground border-white/10"
                  }
                >
                  {sponsorship.status}
                </Badge>
              </div>
              {isSponsorship && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Payment Status</p>
                  <Badge 
                    className={
                      sponsorship.payment_status === "succeeded" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                      sponsorship.payment_status === "failed" ? "bg-red-500/20 text-red-400 border-red-500/30" :
                      "bg-white/[0.06] text-muted-foreground border-white/10"
                    }
                  >
                    {sponsorship.payment_status || "pending"}
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Model Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Model Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Model</p>
              <p className="text-lg font-medium">{sponsorship.model_name}</p>
              {sponsorship.openrouter_model_id && (
                <p className="text-sm text-muted-foreground mt-1">
                  OpenRouter ID: {sponsorship.openrouter_model_id}
                </p>
              )}
            </div>
            {sponsorship.message && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Message</p>
                <p className="text-sm">{sponsorship.message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Timeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Submitted</p>
              <p className="text-sm">
                {new Date(sponsorship.created_at).toLocaleString()}
              </p>
            </div>
            {sponsorship.reviewed_at && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Reviewed</p>
                <p className="text-sm">
                  {new Date(sponsorship.reviewed_at).toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Reviewer Notes */}
        {sponsorship.reviewer_notes && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Reviewer Notes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap">{sponsorship.reviewer_notes}</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
