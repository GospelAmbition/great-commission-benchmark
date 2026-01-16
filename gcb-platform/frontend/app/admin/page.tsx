"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useUserProfile } from "@/lib/useUserProfile";
import { toast } from "sonner";
import { ExternalLink, RefreshCw, Mail, MessageSquare, Bell } from "lucide-react";
import { apiClient } from "@/lib/api";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [refreshingCache, setRefreshingCache] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    // Check if user is admin
    if (user && !profileLoading) {
      if (!canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadDashboardData();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router]);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const response = await fetch("/api/admin/stats");
      if (!response.ok) {
        throw new Error("Failed to fetch stats");
      }
      const data = await response.json();
      setStats({
        total_users: data.users?.total || 0,
        total_tests: data.tests?.total || 0,
        total_revenue: data.revenue?.total || 0,
        moderation_queue_size: data.moderation?.pending_reviews || 0,
        total_api_keys: data.api_keys?.total || 0,
        active_api_keys: data.api_keys?.active || 0,
      });
    } catch (error) {
      console.error("Failed to load admin dashboard:", error);
      // Set fallback values on error
      setStats({
        total_users: 0,
        total_tests: 0,
        total_revenue: 0,
        moderation_queue_size: 0,
        total_api_keys: 0,
        active_api_keys: 0,
      });
    } finally {
      setLoading(false);
    }
  }

  async function syncModelDescriptions() {
    setSyncing(true);
    try {
      const response = await fetch("/api/admin/models/sync-descriptions", {
        method: "POST",
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to sync model descriptions");
      }
      const data = await response.json();
      toast.success(data.message || `Synced ${data.updated_count || 0} model(s)`);
    } catch (error: any) {
      console.error("Failed to sync model descriptions:", error);
      toast.error(error.message || "Failed to sync model descriptions");
    } finally {
      setSyncing(false);
    }
  }

  async function refreshCache() {
    setRefreshingCache(true);
    try {
      const response = await fetch("/api/admin/cache/refresh", {
        method: "POST",
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to refresh cache");
      }
      const data = await response.json();
      toast.success(data.message || "Cache refreshed successfully");
    } catch (error: any) {
      console.error("Failed to refresh cache:", error);
      toast.error(error.message || "Failed to refresh cache");
    } finally {
      setRefreshingCache(false);
    }
  }

  async function testEmail() {
    setTestingEmail(true);
    try {
      const result = await apiClient.sendTestEmail();
      if (result.success) {
        toast.success(result.message || "Test email sent successfully");
      } else {
        toast.error(result.message || "Failed to send test email");
      }
    } catch (error: any) {
      console.error("Failed to send test email:", error);
      toast.error(error.message || "Failed to send test email");
    } finally {
      setTestingEmail(false);
    }
  }

  if (userLoading || profileLoading || (loading && !user)) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-5">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Double-check admin permission before rendering
  if (!canAdmin && !isAdmin) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Admin Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          System overview and management
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-6 md:grid-cols-5 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_users || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Tests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_tests || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${stats?.total_revenue?.toFixed(2) || "0.00"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Moderation Queue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.moderation_queue_size || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              API Keys Issued
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.active_api_keys || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.total_api_keys || 0} total ({stats?.total_api_keys - stats?.active_api_keys || 0} revoked)
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Admin Actions */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>User Management</CardTitle>
            <CardDescription>Manage users and roles</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/admin/users">Manage Users</Link>
            </Button>
          </CardContent>
        </Card>
        <Card className="border-[--ga-red]">
          <CardHeader>
            <CardTitle>Benchmark Development</CardTitle>
            <CardDescription>Unified version and question management</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="brand">
              <Link href="/benchmark">Open Dashboard</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Blog Management</CardTitle>
            <CardDescription>Manage Insights section articles and content</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/blog-manager">Manage Blog</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Data Management</CardTitle>
            <CardDescription>Delete test runs, submissions, and clean up data</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/data">Manage Data</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Payments & Stripe</CardTitle>
            <CardDescription>Manage Stripe configuration and view transaction history</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/payments">Manage Payments</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Volunteer Applications</CardTitle>
            <CardDescription>Review and manage volunteer applications for moderation and advisory roles</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/volunteers">View Applications</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Sponsorship Management</CardTitle>
            <CardDescription>Assign moderators to sponsorship requests and manage assignments</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/sponsorships">Manage Sponsorships</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Contact Submissions
            </CardTitle>
            <CardDescription>View and manage contact form submissions from the website</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/contacts">View Submissions</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notification Settings
            </CardTitle>
            <CardDescription>Configure who receives email notifications for new submissions</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link href="/admin/notifications">Configure Recipients</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Model Utilities</CardTitle>
            <CardDescription>Sync model descriptions from OpenRouter API</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={syncModelDescriptions} 
              disabled={syncing}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? "animate-spin" : ""}`} />
              {syncing ? "Syncing..." : "Sync Model Descriptions"}
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Cache Management</CardTitle>
            <CardDescription>Manually refresh the leaderboard and public data caches</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={refreshCache} 
              disabled={refreshingCache}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshingCache ? "animate-spin" : ""}`} />
              {refreshingCache ? "Refreshing..." : "Refresh Cache"}
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Email Service</CardTitle>
            <CardDescription>Test email delivery to verify Resend configuration</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={testEmail} 
              disabled={testingEmail}
              variant="outline"
            >
              <Mail className={`h-4 w-4 mr-2 ${testingEmail ? "animate-pulse" : ""}`} />
              {testingEmail ? "Sending..." : "Test Email Service"}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Platform Stack */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Platform Stack</CardTitle>
          <CardDescription>Services and infrastructure powering the Great Commission Benchmark</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">Railway</h4>
                <p className="text-sm text-muted-foreground">Cloud hosting and deployment platform</p>
              </div>
              <a href="https://railway.app" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">PorkBun</h4>
                <p className="text-sm text-muted-foreground">Domain name hosting</p>
              </div>
              <a href="https://porkbun.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">GitHub</h4>
                <p className="text-sm text-muted-foreground">Source control</p>
              </div>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">MailerLite</h4>
                <p className="text-sm text-muted-foreground">Email marketing and mailing lists</p>
              </div>
              <a href="https://mailerlite.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">Google Cloud</h4>
                <p className="text-sm text-muted-foreground">OAuth authentication provider</p>
              </div>
              <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">Stripe</h4>
                <p className="text-sm text-muted-foreground">Payment processing and subscriptions</p>
              </div>
              <a href="https://dashboard.stripe.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">PostgreSQL</h4>
                <p className="text-sm text-muted-foreground">Database (hosted on Railway)</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">Resend</h4>
                <p className="text-sm text-muted-foreground">Transactional email system</p>
              </div>
              <a href="https://resend.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">Railway Storage</h4>
                <p className="text-sm text-muted-foreground">Storage bucket for file uploads</p>
              </div>
              <a href="https://railway.app" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">React Tailwind Next</h4>
                <p className="text-sm text-muted-foreground">Frontend framework</p>
              </div>
              <a href="https://nextjs.org" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">FastAPI</h4>
                <p className="text-sm text-muted-foreground">Backend API framework (Python)</p>
              </div>
              <a href="https://fastapi.tiangolo.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg border bg-muted/30">
              <div className="flex-1">
                <h4 className="font-medium">NextAuth.js</h4>
                <p className="text-sm text-muted-foreground">Authentication library</p>
              </div>
              <a href="https://next-auth.js.org" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
