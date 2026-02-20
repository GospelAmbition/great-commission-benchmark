"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";
import { Bell, ChevronRight, Sparkles, Shield, MessageSquare, ClipboardCheck, Save } from "lucide-react";

interface NotificationSetting {
  id: string;
  notification_type: string;
  recipient_email: string | null;
  is_enabled: boolean;
  description: string | null;
  updated_at: string;
  updated_by_id: string | null;
  updated_by_name: string | null;
}

const NOTIFICATION_TYPE_CONFIG: Record<string, { 
  title: string; 
  icon: React.ReactNode;
  description: string;
}> = {
  sponsorship: {
    title: "Sponsorship Requests",
    icon: <Sparkles className="h-5 w-5 text-primary" />,
    description: "Notified when a new sponsorship or model request is submitted.",
  },
  volunteer: {
    title: "Volunteer Applications",
    icon: <Shield className="h-5 w-5 text-primary" />,
    description: "Notified when someone applies to volunteer as a moderator or advisor.",
  },
  contact: {
    title: "Contact Form Submissions",
    icon: <MessageSquare className="h-5 w-5 text-primary" />,
    description: "Notified when someone submits the contact form on the website.",
  },
  moderation: {
    title: "Moderation Alerts",
    icon: <ClipboardCheck className="h-5 w-5 text-primary" />,
    description: "Notified when a community submission enters the moderation queue.",
  },
};

export default function AdminNotificationsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { canAdmin, isAdmin, loading: profileLoading } = useUserProfile();
  const [settings, setSettings] = useState<NotificationSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [editedSettings, setEditedSettings] = useState<Record<string, { recipient_email: string; is_enabled: boolean }>>({});

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user && !profileLoading) {
      if (!canAdmin && !isAdmin) {
        toast.error("You don't have permission to access this page");
        router.push("/dashboard");
        return;
      }
      loadSettings();
    }
  }, [user, userLoading, profileLoading, canAdmin, isAdmin, router]);

  async function loadSettings() {
    setLoading(true);
    try {
      const response = await fetch("/api/admin/notification-settings");
      if (response.ok) {
        const data = await response.json();
        setSettings(data.settings || []);
        // Initialize edited settings
        const edited: Record<string, { recipient_email: string; is_enabled: boolean }> = {};
        for (const setting of data.settings || []) {
          edited[setting.notification_type] = {
            recipient_email: setting.recipient_email || "",
            is_enabled: setting.is_enabled,
          };
        }
        setEditedSettings(edited);
      } else {
        toast.error("Failed to load notification settings");
      }
    } catch (error) {
      console.error("Failed to load notification settings:", error);
      toast.error("Failed to load notification settings");
    } finally {
      setLoading(false);
    }
  }

  function handleChange(type: string, field: "recipient_email" | "is_enabled", value: string | boolean) {
    setEditedSettings((prev) => ({
      ...prev,
      [type]: {
        ...prev[type],
        [field]: value,
      },
    }));
  }

  async function handleSave(type: string) {
    const edited = editedSettings[type];
    if (!edited) return;

    setSaving(type);
    try {
      const response = await fetch(`/api/admin/notification-settings/${type}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recipient_email: edited.recipient_email || null,
          is_enabled: edited.is_enabled,
        }),
      });

      if (response.ok) {
        toast.success(`${NOTIFICATION_TYPE_CONFIG[type]?.title || type} settings updated`);
        loadSettings(); // Reload to get updated_at and updated_by
      } else {
        const error = await response.json().catch(() => ({}));
        toast.error(error.detail || "Failed to update settings");
      }
    } catch (error) {
      console.error("Failed to save notification setting:", error);
      toast.error("Failed to save notification setting");
    } finally {
      setSaving(null);
    }
  }

  function hasChanges(type: string): boolean {
    const setting = settings.find((s) => s.notification_type === type);
    const edited = editedSettings[type];
    if (!setting || !edited) return false;
    return (
      (setting.recipient_email || "") !== edited.recipient_email ||
      setting.is_enabled !== edited.is_enabled
    );
  }

  if (userLoading || profileLoading || loading) {
    return (
      <div className="container py-8 max-w-4xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="space-y-4">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  if (!user || (!canAdmin && !isAdmin)) {
    return null;
  }

  return (
    <div className="container py-8 max-w-4xl">
      {/* Breadcrumb */}
      <nav className="mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/admin" className="hover:text-primary transition-colors">
              Admin
            </Link>
          </li>
          <li>
            <ChevronRight className="h-4 w-4" />
          </li>
          <li className="text-foreground font-medium">
            Notification Recipients
          </li>
        </ol>
      </nav>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Bell className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Notification Recipients</h1>
        </div>
        <p className="mt-2 text-muted-foreground">
          Configure who receives email notifications for new submissions
        </p>
      </div>

      <div className="space-y-4">
        {["sponsorship", "volunteer", "contact", "moderation"].map((type) => {
          const config = NOTIFICATION_TYPE_CONFIG[type];
          const setting = settings.find((s) => s.notification_type === type);
          const edited = editedSettings[type] || { recipient_email: "", is_enabled: true };
          const changed = hasChanges(type);

          return (
            <Card key={type} className={changed ? "border-primary/50" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      {config?.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{config?.title || type}</CardTitle>
                      <CardDescription>{config?.description}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor={`${type}-enabled`} className="text-sm text-muted-foreground">
                      {edited.is_enabled ? "Enabled" : "Disabled"}
                    </Label>
                    <Switch
                      id={`${type}-enabled`}
                      checked={edited.is_enabled}
                      onCheckedChange={(checked) => handleChange(type, "is_enabled", checked)}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor={`${type}-email`}>Recipient Email</Label>
                  <Input
                    id={`${type}-email`}
                    type="email"
                    value={edited.recipient_email}
                    onChange={(e) => handleChange(type, "recipient_email", e.target.value)}
                    placeholder="admin@example.com"
                    className="mt-1"
                    disabled={!edited.is_enabled}
                  />
                  {!edited.recipient_email && edited.is_enabled && (
                    <p className="text-xs text-yellow-500 mt-1">
                      No email configured. Notifications will not be sent.
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <div className="text-xs text-muted-foreground">
                    {setting?.updated_by_name && (
                      <span>
                        Last updated by {setting.updated_by_name}
                        {setting.updated_at && (
                          <> on {new Date(setting.updated_at).toLocaleDateString()}</>
                        )}
                      </span>
                    )}
                  </div>
                  <Button
                    onClick={() => handleSave(type)}
                    disabled={!changed || saving === type}
                    size="sm"
                  >
                    {saving === type ? (
                      "Saving..."
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            When notifications are enabled and a recipient email is configured, the system will automatically
            send an email alert whenever a new submission is received.
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <span className="font-medium text-foreground">Sponsorship Requests:</span> Sent when someone submits
              a model sponsorship request or free model test request.
            </li>
            <li>
              <span className="font-medium text-foreground">Volunteer Applications:</span> Sent when someone applies
              to join as a moderator or advisor.
            </li>
            <li>
              <span className="font-medium text-foreground">Contact Form:</span> Sent when someone submits
              the website contact form.
            </li>
            <li>
              <span className="font-medium text-foreground">Moderation Alerts:</span> Sent when a community
              submission enters the moderation queue and needs reviewer attention.
            </li>
          </ul>
          <p>
            Disable notifications temporarily by toggling the switch, or remove the email address to stop
            notifications without losing your configuration.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
