"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import Link from "next/link";

interface UserProfile {
  name: string;
  email: string;
  organization?: string;
}

interface NotificationPreferences {
  test_completed: boolean;
  test_failed: boolean;
  submission_approved: boolean;
  submission_rejected: boolean;
  newsletter: boolean;
}

export default function SettingsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [notifications, setNotifications] = useState<NotificationPreferences>({
    test_completed: true,
    test_failed: true,
    submission_approved: true,
    submission_rejected: true,
    newsletter: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadSettings();
    }
  }, [user, userLoading, router]);

  async function loadSettings() {
    setLoading(true);
    try {
      const profileData = await apiClient.getUserProfile().catch(() => null);
      if (profileData) {
        setProfile({
          name: profileData.name || user?.name || "",
          email: profileData.email || user?.email || "",
          organization: profileData.organization || "",
        });
      } else {
        setProfile({
          name: user?.name || "",
          email: user?.email || "",
          organization: "",
        });
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveProfile() {
    if (!profile) return;
    setSaving(true);
    try {
      await apiClient.updateUserProfile({
        name: profile.name,
        organization: profile.organization,
      });
      toast.success("Profile updated successfully");
    } catch (error) {
      console.error("Failed to save profile:", error);
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveNotifications() {
    setSaving(true);
    try {
      // In a real implementation, this would call the notifications API
      await fetch("/api/user/notifications", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(notifications),
      });
      toast.success("Notification preferences updated");
    } catch (error) {
      console.error("Failed to save notifications:", error);
      toast.error("Failed to update notification preferences");
    } finally {
      setSaving(false);
    }
  }

  if (userLoading || loading) {
    return (
      <div className="container py-8 max-w-2xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-64 mb-6" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="container py-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Account Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your profile and preferences
        </p>
      </div>

      {/* Profile Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>
            Your public profile information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Display Name</Label>
            <Input
              id="name"
              value={profile?.name || ""}
              onChange={(e) =>
                setProfile((prev) => prev && { ...prev, name: e.target.value })
              }
              placeholder="Your display name"
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              value={profile?.email || ""}
              disabled
              className="bg-muted"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Email is managed through your Google account
            </p>
          </div>
          <div>
            <Label htmlFor="organization">Organization (Optional)</Label>
            <Input
              id="organization"
              value={profile?.organization || ""}
              onChange={(e) =>
                setProfile((prev) => prev && { ...prev, organization: e.target.value })
              }
              placeholder="Your church, ministry, or organization"
            />
          </div>
          <Button onClick={handleSaveProfile} disabled={saving}>
            {saving ? "Saving..." : "Save Profile"}
          </Button>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            Choose what email notifications you receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="test_completed"
              checked={notifications.test_completed}
              onCheckedChange={(checked) =>
                setNotifications((prev) => ({
                  ...prev,
                  test_completed: checked as boolean,
                }))
              }
            />
            <Label htmlFor="test_completed" className="font-normal">
              Test completed - Notify me when my benchmark tests finish
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="test_failed"
              checked={notifications.test_failed}
              onCheckedChange={(checked) =>
                setNotifications((prev) => ({
                  ...prev,
                  test_failed: checked as boolean,
                }))
              }
            />
            <Label htmlFor="test_failed" className="font-normal">
              Test failed - Notify me if a test encounters an error
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="submission_approved"
              checked={notifications.submission_approved}
              onCheckedChange={(checked) =>
                setNotifications((prev) => ({
                  ...prev,
                  submission_approved: checked as boolean,
                }))
              }
            />
            <Label htmlFor="submission_approved" className="font-normal">
              Submission approved - Notify me when my submission is approved
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="submission_rejected"
              checked={notifications.submission_rejected}
              onCheckedChange={(checked) =>
                setNotifications((prev) => ({
                  ...prev,
                  submission_rejected: checked as boolean,
                }))
              }
            />
            <Label htmlFor="submission_rejected" className="font-normal">
              Submission rejected - Notify me if my submission is rejected
            </Label>
          </div>
          <Separator />
          <div className="flex items-center space-x-2">
            <Checkbox
              id="newsletter"
              checked={notifications.newsletter}
              onCheckedChange={(checked) =>
                setNotifications((prev) => ({
                  ...prev,
                  newsletter: checked as boolean,
                }))
              }
            />
            <Label htmlFor="newsletter" className="font-normal">
              Newsletter - Receive updates about new features and benchmark results
            </Label>
          </div>
          <Button onClick={handleSaveNotifications} disabled={saving}>
            {saving ? "Saving..." : "Save Preferences"}
          </Button>
        </CardContent>
      </Card>

      {/* Connected Accounts */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Connected Accounts</CardTitle>
          <CardDescription>
            Manage your authentication providers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium">Google</p>
              <p className="text-sm text-muted-foreground">
                {user.email} • Connected
              </p>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link href="/api/auth/signout">Sign Out</Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible account actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete Account</p>
              <p className="text-sm text-muted-foreground">
                Permanently delete your account and all associated data
              </p>
            </div>
            <Button variant="destructive" size="sm">
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
