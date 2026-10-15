"use client";

import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type Send = { id: string; post_title: string | null; audience: string; status: string; provider: string; campaign_id: string | null; recipient_count: number | null; error_message: string | null; created_at: string };

export function NewsletterCampaignSends() {
  const [sends, setSends] = useState<Send[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    const response = await fetch("/api/admin/newsletter/sends?limit=10");
    if (!response.ok) throw new Error("Unable to load campaign send history");
    const data = await response.json();
    setSends(data.items || []);
  }, []);
  useEffect(() => { load().catch((err) => setError(err.message)); }, [load]);

  async function refresh(id?: string) {
    setBusy(true);
    setError("");
    try {
      if (id) {
        const response = await fetch(`/api/admin/newsletter/sends/${id}/refresh`, { method: "POST" });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(typeof data.detail === "string" ? data.detail : "Unable to verify campaign status");
        }
      }
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to refresh campaigns");
    } finally {
      setBusy(false);
    }
  }

  return <Card className="mb-8">
    <CardHeader className="flex flex-row items-center justify-between">
      <CardTitle>Recent campaign sends</CardTitle>
      <Button variant="outline" disabled={busy} onClick={() => refresh()}>Refresh history</Button>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground mb-3">Scheduled means MailerLite accepted delivery. Sent means completion was confirmed. Refreshing checks status and never sends another email.</p>
      {error && <p role="alert" className="text-sm text-destructive mb-3">{error}</p>}
      {sends.length === 0 ? <p className="text-sm">No recent sends.</p> : <Table>
        <TableHeader><TableRow><TableHead>Campaign</TableHead><TableHead>Audience</TableHead><TableHead>Status</TableHead><TableHead>Action</TableHead></TableRow></TableHeader>
        <TableBody>{sends.map((send) => <TableRow key={send.id}>
          <TableCell><p>{send.post_title || "Newsletter"}</p><p className="text-xs text-muted-foreground">{new Date(send.created_at).toLocaleString()} · {send.provider}</p><p className="text-xs text-muted-foreground break-all">Send log: {send.id}</p></TableCell>
          <TableCell>{send.audience} · {send.recipient_count ?? "—"}</TableCell>
          <TableCell><p className="capitalize">{send.status.replaceAll("_", " ")}</p>{send.error_message && <p className="text-xs text-destructive max-w-sm">{send.error_message}</p>}</TableCell>
          <TableCell>{send.provider === "mailerlite" && send.status !== "sent" && <Button size="sm" variant="outline" disabled={busy} onClick={() => refresh(send.id)}>Check status</Button>}</TableCell>
        </TableRow>)}</TableBody>
      </Table>}
    </CardContent>
  </Card>;
}
