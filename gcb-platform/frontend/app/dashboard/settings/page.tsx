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
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import Link from "next/link";
import { Copy, Key, Trash2, Plus, Eye, EyeOff } from "lucide-react";

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

interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
  expires_at: string | null;
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
  
  // API Key state
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [apiKeysLoading, setApiKeysLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState("");
  const [creatingKey, setCreatingKey] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
  const [showNewKey, setShowNewKey] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadSettings();
      loadAPIKeys();
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
  
  async function loadAPIKeys() {
    setApiKeysLoading(true);
    try {
      const response = await apiClient.getAPIKeys();
      setApiKeys(response.api_keys);
    } catch (error) {
      console.error("Failed to load API keys:", error);
    } finally {
      setApiKeysLoading(false);
    }
  }
  
  async function handleCreateAPIKey() {
    if (!newKeyName.trim()) {
      toast.error("Please enter a name for the API key");
      return;
    }
    
    setCreatingKey(true);
    try {
      const response = await apiClient.createAPIKey(newKeyName.trim());
      setNewlyCreatedKey(response.key);
      setShowNewKey(true);
      setNewKeyName("");
      await loadAPIKeys();
      toast.success("API key created successfully");
    } catch (error: any) {
      console.error("Failed to create API key:", error);
      toast.error(error.message || "Failed to create API key");
    } finally {
      setCreatingKey(false);
    }
  }
  
  async function handleRevokeAPIKey(keyId: string, keyName: string) {
    if (!confirm(`Are you sure you want to revoke the API key "${keyName}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      await apiClient.revokeAPIKey(keyId);
      await loadAPIKeys();
      toast.success("API key revoked successfully");
    } catch (error: any) {
      console.error("Failed to revoke API key:", error);
      toast.error(error.message || "Failed to revoke API key");
    }
  }
  
  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  }
  
  function formatDate(dateString: string | null): string {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
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

      {/* API Keys */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Keys
          </CardTitle>
          <CardDescription>
            Manage API keys for the GCB Runner CLI. Use these keys to run benchmarks locally.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* New Key Created Alert */}
          {newlyCreatedKey && (
            <div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
              <p className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
                🎉 API Key Created Successfully
              </p>
              <p className="text-xs text-green-700 dark:text-green-300 mb-3">
                Copy this key now. It will not be shown again.
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 p-2 bg-white dark:bg-gray-900 rounded border text-sm font-mono overflow-x-auto">
                  {showNewKey ? newlyCreatedKey : "••••••••••••••••••••••••••••••••"}
                </code>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowNewKey(!showNewKey)}
                >
                  {showNewKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => copyToClipboard(newlyCreatedKey)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-3"
                onClick={() => {
                  setNewlyCreatedKey(null);
                  setShowNewKey(false);
                }}
              >
                Dismiss
              </Button>
            </div>
          )}

          {/* Create New Key */}
          <div className="flex gap-2">
            <Input
              placeholder="Key name (e.g., My Laptop, CI Server)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateAPIKey()}
              disabled={creatingKey}
            />
            <Button
              onClick={handleCreateAPIKey}
              disabled={creatingKey || !newKeyName.trim()}
            >
              <Plus className="h-4 w-4 mr-2" />
              {creatingKey ? "Creating..." : "Create Key"}
            </Button>
          </div>

          <Separator />

          {/* Existing Keys */}
          {apiKeysLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </div>
          ) : apiKeys.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No API keys yet. Create one to use the GCB Runner CLI.
            </p>
          ) : (
            <div className="space-y-3">
              {apiKeys.map((key) => (
                <div
                  key={key.id}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    key.is_active
                      ? "bg-background"
                      : "bg-muted opacity-60"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium truncate">{key.name}</p>
                      {!key.is_active && (
                        <Badge variant="secondary" className="text-xs">
                          Revoked
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                      <code className="bg-muted px-1.5 py-0.5 rounded">
                        {key.key_prefix}...
                      </code>
                      <span>Created {formatDate(key.created_at)}</span>
                      {key.last_used_at && (
                        <span>Last used {formatDate(key.last_used_at)}</span>
                      )}
                    </div>
                  </div>
                  {key.is_active && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                      onClick={() => handleRevokeAPIKey(key.id, key.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}

          <p className="text-xs text-muted-foreground">
            Use your API key with the GCB Runner CLI:{" "}
            <code className="bg-muted px-1.5 py-0.5 rounded">gcb-runner config</code>
          </p>
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
