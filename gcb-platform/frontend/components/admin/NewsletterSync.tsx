"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = {
  pending: number;
  errors: number;
  enabled: boolean;
  lastSyncedAt: string | null;
  webhookConfigured?: boolean;
  lastWebhookAt?: string | null;
  onQueued: () => void;
};

export function NewsletterSync({ pending, errors, enabled, lastSyncedAt, webhookConfigured, lastWebhookAt, onQueued }: Props) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function run(action: "check" | "retry" | "reconcile") {
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const url = action === "check" ? "/api/admin/newsletter/connection" : `/api/admin/newsletter/sync/retry${action === "reconcile" ? "?reconcile=true" : ""}`;
      const response = await fetch(url, { method: action === "check" ? "GET" : "POST" });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Unable to complete sync action");
      if (action === "check") {
        const production = data.groups.production;
        setMessage(`Connection verified. Production group: ${production.name || production.id}.${data.groups.test ? ` Test group: ${data.groups.test.name || data.groups.test.id}.` : " Test group is not configured."}`);
      } else {
        setMessage(`${data.queued} subscribers queued.${data.worker_enabled ? " Automatic sync will process them." : " Automatic sync is disabled; enable it in deployment settings to process the queue."}`);
        onQueued();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to complete sync action");
    } finally {
      setBusy(false);
    }
  }

  return <Card className="h-full min-w-0">
    <CardHeader><CardTitle>MailerLite connection and sync</CardTitle></CardHeader>
    <CardContent className="space-y-3">
      <p className="text-sm">{pending} pending · {errors} need retry · Automatic sync {enabled ? "enabled" : "disabled"}</p>
      <p className="text-sm text-muted-foreground">Last verified sync: {lastSyncedAt ? new Date(lastSyncedAt).toLocaleString() : "None yet"}. Subscriber status is confirmed after checking MailerLite; queued work survives restarts.</p>
      <p className="text-sm text-muted-foreground">Unsubscribe webhook: {webhookConfigured ? "secret configured" : "not configured"}. Last authenticated event: {lastWebhookAt ? new Date(lastWebhookAt).toLocaleString() : "None yet"}.</p>
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" disabled={busy} onClick={() => run("check")}>Check connection</Button>
        <Button variant="outline" disabled={busy || pending + errors === 0} onClick={() => run("retry")}>Retry pending syncs</Button>
        <Button variant="outline" disabled={busy} onClick={() => run("reconcile")}>Recheck all subscribers</Button>
      </div>
      {message && <p role="status" className="text-sm">{message}</p>}
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </CardContent>
  </Card>;
}
