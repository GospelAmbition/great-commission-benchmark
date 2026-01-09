"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { CliSubmissionUpload } from "@/components/cli-submission-upload";
import { SponsorModelCard } from "@/components/sponsor-model-card";
import { APIKeysCard } from "@/components/api-keys-card";
import { 
  Terminal, 
  Key, 
  Upload, 
  Heart, 
  Users, 
  Mail, 
  CheckCircle2,
  Copy,
  ExternalLink,
  Download
} from "lucide-react";
import { DashboardIcon } from "@/lib/icons";
import { toast } from "sonner";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadDashboardData();
    }
  }, [user, userLoading, router]);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [profileData, submissionsData] = await Promise.all([
        apiClient.getUserProfile().catch(() => null),
        apiClient.getUserSubmissions().catch(() => []),
      ]);

      setProfile(profileData);
      setSubmissions(submissionsData || []);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  }

  if (userLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const hasApiKey = profile?.has_api_key;
  const hasSubmissions = submissions.length > 0;

  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-20" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <DashboardIcon className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">
              Welcome, {profile?.name || user.name || "Tester"}!
            </h1>
          </div>
          <p className="text-muted-foreground">
            Help us measure which AI models best serve the Great Commission
          </p>
        </div>
      </div>

      {/* Engagement Cards */}
      <div className="container pt-8 max-w-7xl">
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg">Support the Project</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Help keep the benchmark running and accessible to everyone.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/contribute">Donate →</Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg">Volunteer</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Help review submissions, develop features, or spread the word.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/contribute">Get Involved →</Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg">Newsletter</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Get updates on new features, benchmark results, and more.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/dashboard/settings">Subscribe →</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="container py-8 max-w-7xl">
        {/* Two-column layout: Main content + Side column */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Get Started as a Tester */}
            <Card className="border-primary/20 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 gradient-red-glow opacity-10" />
              <CardHeader className="relative">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Terminal className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <CardTitle>Get Started as a Tester</CardTitle>
                    <CardDescription>
                      Run the benchmark locally and submit your results to the leaderboard
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="space-y-6">
                  {/* Step 1: API Key */}
                  <div className="flex items-start gap-4">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${hasApiKey ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/[0.06] text-muted-foreground'}`}>
                      {hasApiKey ? <CheckCircle2 className="h-5 w-5" /> : <span className="font-bold">1</span>}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground flex items-center gap-2">
                        <Key className="h-4 w-4" />
                        Generate an API Key
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Create an API key to authenticate the GCB Runner with your account.
                      </p>
                      <Button asChild variant="outline" size="sm" className="mt-2">
                        <Link href="/dashboard/settings">
                          {hasApiKey ? "Manage API Keys" : "Create API Key"} →
                        </Link>
                      </Button>
                    </div>
                  </div>

                  {/* Step 2: Download */}
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/[0.06] text-muted-foreground flex items-center justify-center">
                      <span className="font-bold">2</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground flex items-center gap-2">
                        <Download className="h-4 w-4" />
                        Download the GCB Runner
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Download the standalone executable for your platform — no Python required.
                      </p>
                      <Button asChild variant="glow" size="sm" className="mt-2">
                        <Link href="/runner">
                          <Download className="h-4 w-4 mr-2" />
                          Download GCB Runner
                        </Link>
                      </Button>
                    </div>
                  </div>

                  {/* Step 3: Configure */}
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/[0.06] text-muted-foreground flex items-center justify-center">
                      <span className="font-bold">3</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground">Configure Your API Key</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Run the config command and enter your API key when prompted.
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <code className="bg-white/[0.06] text-foreground px-3 py-2 rounded-md text-sm font-mono flex-1 border border-white/[0.08]">
                          gcb-runner config
                        </code>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => copyToClipboard("gcb-runner config")}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Step 4: Run */}
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/[0.06] text-muted-foreground flex items-center justify-center">
                      <span className="font-bold">4</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground">Run the Benchmark</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Launch the interactive menu to select a model and run the benchmark.
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <code className="bg-white/[0.06] text-foreground px-3 py-2 rounded-md text-sm font-mono flex-1 border border-white/[0.08]">
                          gcb-runner
                        </code>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => copyToClipboard("gcb-runner")}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Step 5: Upload */}
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/[0.06] text-muted-foreground flex items-center justify-center">
                      <span className="font-bold">5</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground flex items-center gap-2">
                        <Upload className="h-4 w-4" />
                        Export and Upload Your Results
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Export your results and upload them here for moderator review and leaderboard inclusion.
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <code className="bg-white/[0.06] text-foreground px-3 py-2 rounded-md text-sm font-mono border border-white/[0.08]">
                          gcb-runner export --run N
                        </code>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => copyToClipboard("gcb-runner export --run N")}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                      <Button 
                        variant="brand" 
                        size="sm" 
                        className="mt-3"
                        onClick={() => setUploadDialogOpen(true)}
                      >
                        <Upload className="h-4 w-4 mr-2" />
                        Upload GCB Runner Results
                      </Button>
                    </div>
                  </div>

                  {/* Learn More */}
                  <div className="pt-4 border-t border-white/[0.06]">
                    <Button asChild variant="outline" size="sm">
                      <Link href="/runner">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Full GCB Runner Documentation
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Your Submissions */}
            <Card>
              <CardHeader>
                <CardTitle>Your Submissions</CardTitle>
                <CardDescription>GCB Runner test results you&apos;ve submitted for review</CardDescription>
              </CardHeader>
              <CardContent>
                {submissions.length > 0 ? (
                  <div className="rounded-lg border border-white/[0.08] overflow-hidden">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-white/[0.02]">
                          <TableHead>Date</TableHead>
                          <TableHead>Model</TableHead>
                          <TableHead>Score</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {submissions.map((submission: any) => (
                          <TableRow key={submission.id}>
                            <TableCell className="text-muted-foreground">
                              {new Date(submission.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="text-foreground font-medium">{submission.model_name}</TableCell>
                            <TableCell className="text-foreground">
                              {submission.overall_score ? submission.overall_score.toFixed(1) : "—"}
                            </TableCell>
                            <TableCell>
                              <Badge 
                                className={
                                  submission.status === "approved" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                                  submission.status === "rejected" ? "bg-red-500/20 text-red-400 border-red-500/30" :
                                  "bg-white/[0.06] text-muted-foreground border-white/10"
                                }
                              >
                                {submission.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Button asChild variant="ghost" size="sm">
                                <Link href={`/dashboard/submissions/${submission.id}`}>View</Link>
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 rounded-full bg-white/[0.06] mx-auto mb-4 flex items-center justify-center">
                      <Terminal className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <p className="text-foreground mb-2">No submissions yet</p>
                    <p className="text-sm text-muted-foreground mb-4">
                      Run the GCB Runner and upload your first test results
                    </p>
                    <Button onClick={() => setUploadDialogOpen(true)}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Your First Results
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

          </div>

          {/* Side Column - Upload Results + Sponsor Model Card */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Upload Results Card */}
              <Card className="border-primary/20">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Upload className="h-5 w-5 text-primary" />
                    <CardTitle className="text-lg">Upload Test Results</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Ran the gcb-runner? Upload your exported results for moderator review and leaderboard inclusion.
                  </p>
                  <Button 
                    variant="glow" 
                    className="w-full"
                    onClick={() => setUploadDialogOpen(true)}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload GCB Runner Results
                  </Button>
                </CardContent>
              </Card>

              <APIKeysCard />

              <SponsorModelCard />
            </div>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid gap-4 md:grid-cols-3 mt-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                GCB Runner Submissions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">{submissions?.length ?? 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Approved
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {submissions?.filter((s: any) => s.status === "approved").length ?? 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Contributions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">{profile?.contribution_count || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* CLI Submission Upload Dialog */}
        <CliSubmissionUpload
          open={uploadDialogOpen}
          onOpenChange={setUploadDialogOpen}
          onSuccess={() => {
            loadDashboardData();
          }}
        />
      </div>
    </div>
  );
}
