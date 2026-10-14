"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type ImportResult = {
  dry_run: boolean;
  batch_id: string | null;
  total_rows: number;
  counts: Record<string, number>;
  rows: { row: number; email: string; action: string; message: string }[];
  rows_truncated: boolean;
  requires_consent: boolean;
  message: string;
};

const labels: Record<string, string> = {
  create_active: "New active subscribers",
  create_unsubscribed: "New suppression records",
  unsubscribe: "Existing subscribers to unsubscribe",
  unchanged: "Already present",
  protected: "Unsubscribes preserved",
  duplicate: "Duplicate rows skipped",
  invalid: "Invalid rows skipped",
};

export function NewsletterImport({ onImported }: { onImported: () => void }) {
  const [open, setOpen] = useState(false);
  const [csv, setCsv] = useState("");
  const [source, setSource] = useState("");
  const [emailColumn, setEmailColumn] = useState("");
  const [nameColumn, setNameColumn] = useState("");
  const [statusColumn, setStatusColumn] = useState("");
  const [consentNote, setConsentNote] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState("");

  function invalidate() {
    setResult(null);
    setError("");
  }

  async function readFile(file?: File) {
    invalidate();
    setCsv("");
    setConfirmed(false);
    if (!file) return;
    if (file.size > 2_000_000) {
      setError("Choose a CSV file no larger than 2 MB (10,000 rows maximum).");
      return;
    }
    setBusy(true);
    try {
      const text = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
      setCsv(text);
    } catch {
      setError("Unable to read this file. Export it as UTF-8 CSV and try again.");
    } finally {
      setBusy(false);
    }
  }

  async function submit(dryRun: boolean) {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/admin/newsletter/subscribers/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          csv_content: csv, source: source.trim(),
          email_column: emailColumn.trim() || null,
          name_column: nameColumn.trim() || null,
          status_column: statusColumn.trim() || null,
          consent_note: consentNote.trim(), confirm_subscribed: confirmed, dry_run: dryRun,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Import failed. Check the file and try again.");
      setResult(data);
      if (!dryRun) {
        toast.success("Subscriber import saved");
        onImported();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import subscribers");
    } finally {
      setBusy(false);
    }
  }

  const changes = result ? (result.counts.create_active || 0) + (result.counts.create_unsubscribed || 0) + (result.counts.unsubscribe || 0) : 0;

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!busy) setOpen(value); }}>
      <Button onClick={() => setOpen(true)}>Import CSV</Button>
      <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import newsletter subscribers</DialogTitle>
          <DialogDescription>
            Upload a CSV from Google Forms or your previous newsletter tool. Preview changes before saving.
            Existing unsubscribes are preserved. This imports into the platform and does not send email.
          </DialogDescription>
        </DialogHeader>
        <fieldset disabled={busy} className="space-y-4 min-w-0">
          <div className="space-y-2">
            <Label htmlFor="subscriber-csv">CSV file (UTF-8, up to 2 MB and 10,000 rows)</Label>
            <Input id="subscriber-csv" type="file" accept=".csv,.tsv,text/csv,text/tab-separated-values" onChange={(e) => readFile(e.target.files?.[0])} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="import-source">Subscriber source</Label>
            <Input id="import-source" value={source} maxLength={120} placeholder="e.g. Google Form — September interest list" onChange={(e) => { setSource(e.target.value); invalidate(); }} />
          </div>
          <details className="text-sm">
            <summary className="cursor-pointer">Custom column names (optional)</summary>
            <p className="text-muted-foreground my-2">Common email, name, and status headers are detected automatically. For other headers, enter their exact names. Without a status column, addresses are treated as active.</p>
            <div className="grid sm:grid-cols-3 gap-3">
              <div><Label htmlFor="email-column">Email column</Label><Input id="email-column" value={emailColumn} placeholder="Auto-detect" onChange={(e) => { setEmailColumn(e.target.value); invalidate(); }} /></div>
              <div><Label htmlFor="name-column">Name column</Label><Input id="name-column" value={nameColumn} placeholder="Auto-detect" onChange={(e) => { setNameColumn(e.target.value); invalidate(); }} /></div>
              <div><Label htmlFor="status-column">Status column</Label><Input id="status-column" value={statusColumn} placeholder="Auto-detect" onChange={(e) => { setStatusColumn(e.target.value); invalidate(); }} /></div>
            </div>
          </details>
          <Button variant="outline" disabled={busy || !csv || !source.trim()} onClick={() => submit(true)}>
            {busy ? "Processing…" : "Preview import"}
          </Button>
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          {result && (
            <div className="space-y-4" aria-live="polite">
              <p className="font-medium">{result.message}</p>
              <p className="text-sm">{result.total_rows} rows checked{result.batch_id ? ` · Import ${result.batch_id}` : ""}</p>
              <dl className="grid sm:grid-cols-2 gap-2 text-sm">
                {Object.entries(result.counts).map(([key, count]) => <div key={key} className="flex justify-between gap-2 rounded border p-2"><dt>{labels[key] || key}</dt><dd className="font-semibold">{count}</dd></div>)}
              </dl>
              <div className="max-h-64 overflow-auto border rounded">
                <Table>
                  <TableHeader><TableRow><TableHead>Row</TableHead><TableHead>Email</TableHead><TableHead>Result</TableHead></TableRow></TableHeader>
                  <TableBody>{result.rows.map((row) => <TableRow key={row.row}><TableCell>{row.row}</TableCell><TableCell className="break-all">{row.email || "—"}</TableCell><TableCell>{row.message}</TableCell></TableRow>)}</TableBody>
                </Table>
              </div>
              {result.rows_truncated && <p className="text-xs text-muted-foreground">Showing the first 200 rows. Counts include the entire file.</p>}
              {result.dry_run && result.requires_consent && (
                <div className="space-y-3">
                  <Label htmlFor="consent-note">How did these people subscribe?</Label>
                  <Input id="consent-note" maxLength={1000} value={consentNote} placeholder="e.g. Selected newsletter opt-in on our Google Form" onChange={(e) => setConsentNote(e.target.value)} />
                  <div className="flex items-start gap-2">
                    <Checkbox id="consent-confirm" checked={confirmed} onCheckedChange={(value) => setConfirmed(value === true)} />
                    <Label htmlFor="consent-confirm" className="text-sm leading-normal">I confirm that the new active subscribers gave permission to receive this newsletter.</Label>
                  </div>
                </div>
              )}
              {result.dry_run && <Button disabled={busy || changes === 0 || (result.requires_consent && (!confirmed || !consentNote.trim()))} onClick={() => submit(false)}>Import valid rows</Button>}
              {!result.dry_run && <Button variant="outline" onClick={() => setOpen(false)}>Done</Button>}
            </div>
          )}
        </fieldset>
      </DialogContent>
    </Dialog>
  );
}
