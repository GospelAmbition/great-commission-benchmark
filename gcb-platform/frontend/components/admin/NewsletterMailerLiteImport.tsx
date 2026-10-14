"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Preview = {
  snapshot_sha256: string; group_id: string; total_rows: number; requires_consent: boolean;
  counts: Record<string, number>; remote_status_counts: Record<string, number>;
  rows: { row: number; email: string; action: string; message: string }[]; rows_truncated: boolean;
};

export function NewsletterMailerLiteImport({ onImported }: { onImported: () => void }) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [consent, setConsent] = useState(false);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function run(apply = false) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch("/api/admin/newsletter/mailerlite/import", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dry_run: !apply, snapshot_sha256: apply ? preview?.snapshot_sha256 : undefined, confirm_subscribed: consent, consent_note: note }),
      });
      const data = await response.json();
      if (!response.ok) {
        setPreview(null);
        throw new Error(typeof data.detail === "string" ? data.detail : "Unable to import MailerLite contacts");
      }
      if (apply) {
        setPreview(null);
        setConsent(false);
        setNote("");
        setMessage(data.message);
        onImported();
      } else {
        setPreview(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import MailerLite contacts");
    } finally {
      setBusy(false);
    }
  }

  return <Card className="mb-8">
    <CardHeader><CardTitle>Import existing MailerLite contacts</CardTitle></CardHeader>
    <CardContent className="space-y-4">
      <p className="text-sm text-muted-foreground">Bring contacts from the configured production group into the platform. Includes active, unsubscribed, unconfirmed, bounced and junk statuses. Existing opt-outs stay inactive. Up to 10,000 records; use CSV batches for larger groups or contacts outside this group.</p>
      <Button variant="outline" disabled={busy} onClick={() => run()}>Preview MailerLite import</Button>
      {preview && <div className="space-y-3">
        <p className="text-sm">Group {preview.group_id} · {preview.total_rows} records</p>
        <p className="text-sm">MailerLite statuses: {Object.entries(preview.remote_status_counts).map(([key, value]) => `${key}: ${value}`).join(" · ")}</p>
        <ul className="text-sm list-disc pl-5">{Object.entries(preview.counts).map(([key, value]) => <li key={key}>{key.replaceAll("_", " ")}: {value}</li>)}</ul>
        <details><summary className="cursor-pointer text-sm">Review contacts{preview.rows_truncated ? " (first 200)" : ""}</summary>
          <ul className="max-h-64 overflow-auto text-sm space-y-1 mt-2">{preview.rows.map(row => <li key={row.row}>{row.email} — {row.message}</li>)}</ul>
        </details>
        {preview.requires_consent && <div className="space-y-2">
          <label className="flex gap-2 items-start text-sm"><input type="checkbox" checked={consent} disabled={busy} onChange={e => setConsent(e.target.checked)} />I confirm that these new active contacts opted in to the GCB newsletter.</label>
          <Label htmlFor="mailerlite-consent-note">How did these contacts subscribe?</Label>
          <Input id="mailerlite-consent-note" value={note} disabled={busy} maxLength={1000} onChange={e => setNote(e.target.value)} />
        </div>}
        <p className="text-sm text-muted-foreground">Import rechecks the group and queues changes for verification. It does not send a campaign.</p>
        <Button disabled={busy || (preview.requires_consent && (!consent || !note.trim()))} onClick={() => run(true)}>Import reviewed contacts</Button>
      </div>}
      {message && <p role="status" className="text-sm">{message}</p>}
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </CardContent>
  </Card>;
}
