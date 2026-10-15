"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import { readNewsletterActionToken } from "@/lib/newsletter-privacy";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function UnsubscribePage() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const value = readNewsletterActionToken();
    if (value) setToken(value);
    setReady(true);
  }, []);

  async function unsubscribe(event: React.FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/newsletter/unsubscribe`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(token ? { token } : { email: email.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Unable to unsubscribe. Check your email address and try again.");
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to unsubscribe. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="container mx-auto max-w-xl px-4 py-16">
    <Card>
      <CardHeader>
        <CardTitle>{done ? "Unsubscribe request saved" : "Unsubscribe from the newsletter"}</CardTitle>
        <CardDescription>{done ? "If this address was subscribed, it has been removed from the newsletter audience." : "You can stop receiving Great Commission Benchmark newsletter emails. No account is required."}</CardDescription>
      </CardHeader>
      <CardContent>
        {!done && <form onSubmit={unsubscribe} className="space-y-4">
          {!token && <div className="space-y-2">
            <Label htmlFor="unsubscribe-email">Email address</Label>
            <Input id="unsubscribe-email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} disabled={busy} />
          </div>}
          <Button type="submit" disabled={!ready || busy || (!token && !email.trim())}>{busy ? "Unsubscribing…" : "Unsubscribe"}</Button>
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          {token && <Button type="button" variant="link" disabled={busy} onClick={() => { setToken(null); setError(""); }}>Use my email address instead</Button>}
        </form>}
        <p className="mt-6 text-sm"><Link href="/newsletter" className="underline">Newsletter signup</Link> · <Link href="/" className="underline">Back to GCB</Link></p>
      </CardContent>
    </Card>
  </main>;
}
