"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";

interface PublicProfile {
  id: string;
  username: string;
  display_name?: string;
  member_since: string;
  test_count: number;
  contribution_count: number;
  models_tested: string[];
  recent_tests: Array<{
    id: string;
    model_name: string;
    score: number;
    created_at: string;
  }>;
}

export default function PublicProfilePage() {
  const params = useParams();
  const userId = params.id as string;
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      loadProfile();
    }
  }, [userId]);

  async function loadProfile() {
    setLoading(true);
    try {
      const response = await fetch(`/api/public/profiles/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        // API call failed - profile not found or not public
        setProfile(null);
      }
    } catch (error) {
      console.error("Failed to load profile:", error);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8">
        <div className="flex items-center gap-4 mb-8">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container py-8">
        <Card>
          <CardHeader>
            <CardTitle>Profile Not Found</CardTitle>
            <CardDescription>
              This user profile could not be found or is private.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/leaderboard">Back to Leaderboard</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Profile Header */}
      <div className="flex items-center gap-6 mb-8">
        <Avatar className="h-20 w-20">
          <AvatarFallback className="text-2xl">
            {profile.display_name?.[0] || profile.username[0].toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div>
          <h1 className="text-3xl font-bold">
            {profile.display_name || profile.username}
          </h1>
          <p className="text-muted-foreground">@{profile.username}</p>
          <p className="text-sm text-muted-foreground mt-1">
            Member since {new Date(profile.member_since).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tests Run
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{profile.test_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Contributions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{profile.contribution_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Models Tested
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{profile.models_tested.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Models Tested */}
      {profile.models_tested.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Models Tested</CardTitle>
            <CardDescription>
              AI models this user has contributed tests for
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {profile.models_tested.map((model) => (
                <Badge key={model} variant="secondary">
                  {model}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Test Contributions */}
      <Card>
        <CardHeader>
          <CardTitle>Test Contributions</CardTitle>
          <CardDescription>
            Recent benchmark tests contributed by this user
          </CardDescription>
        </CardHeader>
        <CardContent>
          {profile.recent_tests.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {profile.recent_tests.map((test) => (
                  <TableRow key={test.id}>
                    <TableCell>
                      {new Date(test.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="font-medium">{test.model_name}</TableCell>
                    <TableCell>{test.score.toFixed(1)}</TableCell>
                    <TableCell>
                      <Button asChild variant="ghost" size="sm">
                        <Link href={`/leaderboard/models/${encodeURIComponent(test.model_name)}`}>
                          View Model
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No public test contributions yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
