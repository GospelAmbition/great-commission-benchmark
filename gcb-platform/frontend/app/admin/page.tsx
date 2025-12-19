"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

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

  if (loading) {
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
        <Card>
          <CardHeader>
            <CardTitle>Question Management</CardTitle>
            <CardDescription>Manage benchmark questions</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/admin/questions">Manage Questions</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Version Management</CardTitle>
            <CardDescription>Manage benchmark versions</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/admin/versions">Manage Versions</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
