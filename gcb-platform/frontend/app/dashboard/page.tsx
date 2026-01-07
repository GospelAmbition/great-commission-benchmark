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
    <div className="container py-8 max-w-7xl">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900">Welcome, {profile?.name || user.name || "Tester"}!</h1>
        <p className="mt-2 text-slate-600">
          Help us measure which AI models best serve the Great Commission
        </p>
      </div>

      {/* Two-column layout: Main content + Side column */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Content Column */}
        <div className="lg:col-span-2 space-y-8">
          {/* Stats Summary */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500">
                  GCB Runner Submissions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900">{submissions?.length ?? 0}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500">
                  Approved
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900">
                  {submissions?.filter((s: any) => s.status === "approved").length ?? 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500">
                  Contributions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900">{profile?.contribution_count || 0}</div>
              </CardContent>
            </Card>
          </div>

          {/* Get Started as a Tester */}
          <Card className="border-red-200 bg-red-50/50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Terminal className="h-6 w-6 text-red-700" />
                <div>
                  <CardTitle className="text-slate-900">Get Started as a Tester</CardTitle>
                  <CardDescription className="text-slate-600">
                    Run the benchmark locally and submit your results to the leaderboard
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Step 1: API Key */}
                <div className="flex items-start gap-4">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${hasApiKey ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                    {hasApiKey ? <CheckCircle2 className="h-5 w-5" /> : <span className="font-bold">1</span>}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                      <Key className="h-4 w-4" />
                      Generate an API Key
                    </h3>
                    <p className="text-sm text-slate-600 mt-1">
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
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
                    <span className="font-bold">2</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                      <Download className="h-4 w-4" />
                      Download the GCB Runner
                    </h3>
                    <p className="text-sm text-slate-600 mt-1">
                      Download the standalone executable for your platform — no Python required.
                    </p>
                    <Button asChild variant="brand" size="sm" className="mt-2">
                      <Link href="/runner">
                        <Download className="h-4 w-4 mr-2" />
                        Download GCB Runner
                      </Link>
                    </Button>
                  </div>
                </div>

                {/* Step 3: Configure */}
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
                    <span className="font-bold">3</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900">Configure Your API Key</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      Run the config command and enter your API key when prompted.
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <code className="bg-slate-100 text-slate-800 px-3 py-2 rounded-md text-sm font-mono flex-1">
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
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
                    <span className="font-bold">4</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900">Run the Benchmark</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      Launch the interactive menu to select a model and run the benchmark.
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <code className="bg-slate-100 text-slate-800 px-3 py-2 rounded-md text-sm font-mono flex-1">
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
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${hasSubmissions ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                    {hasSubmissions ? <CheckCircle2 className="h-5 w-5" /> : <span className="font-bold">5</span>}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                      <Upload className="h-4 w-4" />
                      Upload Your Results
                    </h3>
                    <p className="text-sm text-slate-600 mt-1">
                      Export your results and upload them here for moderator review and leaderboard inclusion.
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <code className="bg-slate-100 text-slate-800 px-3 py-2 rounded-md text-sm font-mono">
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
                <div className="pt-4 border-t border-red-200">
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
              <CardTitle className="text-slate-900">Your Submissions</CardTitle>
              <CardDescription className="text-slate-600">GCB Runner test results you&apos;ve submitted for review</CardDescription>
            </CardHeader>
            <CardContent>
              {submissions.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead className="text-slate-700">Date</TableHead>
                      <TableHead className="text-slate-700">Model</TableHead>
                      <TableHead className="text-slate-700">Score</TableHead>
                      <TableHead className="text-slate-700">Status</TableHead>
                      <TableHead className="text-slate-700">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {submissions.map((submission: any) => (
                      <TableRow key={submission.id}>
                        <TableCell className="text-slate-700">
                          {new Date(submission.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="text-slate-900 font-medium">{submission.model_name}</TableCell>
                        <TableCell className="text-slate-700">
                          {submission.overall_score ? submission.overall_score.toFixed(1) : "—"}
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={
                              submission.status === "approved" ? "default" :
                              submission.status === "rejected" ? "destructive" :
                              "outline"
                            }
                            className={
                              submission.status === "approved" ? "bg-green-100 text-green-700 border-green-200" :
                              submission.status === "rejected" ? "bg-red-100 text-red-700 border-red-200" :
                              "bg-slate-100 text-slate-700 border-slate-200"
                            }
                          >
                            {submission.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button asChild variant="ghost" size="sm" className="text-slate-700 hover:text-red-700">
                            <Link href={`/dashboard/submissions/${submission.id}`}>View</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <Terminal className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                  <p className="text-slate-700 mb-2">No submissions yet</p>
                  <p className="text-sm text-slate-500 mb-4">
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

          {/* Engagement Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-lg text-slate-900">Support the Project</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-4">
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
                  <Users className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-lg text-slate-900">Volunteer</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-4">
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
                  <Mail className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-lg text-slate-900">Newsletter</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-4">
                  Get updates on new features, benchmark results, and more.
                </p>
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link href="/dashboard/settings">Subscribe →</Link>
                </Button>
              </CardContent>
            </Card>
          </div>

        </div>

        {/* Side Column - Sponsor Model Card + Upload Results */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 space-y-6">
            <SponsorModelCard />
            
            {/* Upload Results Card */}
            <Card className="border-red-200">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Upload className="h-5 w-5 text-red-700" />
                  <CardTitle className="text-lg text-slate-900">Upload Test Results</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-4">
                  Ran the gcb-runner? Upload your exported results for moderator review and leaderboard inclusion.
                </p>
                <Button 
                  variant="brand" 
                  className="w-full"
                  onClick={() => setUploadDialogOpen(true)}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload GCB Runner Results
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
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
  );
}
