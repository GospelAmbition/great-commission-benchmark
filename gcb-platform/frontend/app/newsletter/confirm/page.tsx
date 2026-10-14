"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import { readNewsletterActionToken } from "@/lib/newsletter-privacy";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ConfirmNewsletterPage() {
  const [token, setToken] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => { const value = readNewsletterActionToken(); if (value) setToken(value); }, []);

  async function confirm() {
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/newsletter/confirm-resubscribe`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Unable to confirm. Request a new link from the signup page.");
      setMessage(data.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to confirm. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="container mx-auto max-w-xl px-4 py-16">
    <Card>
      <CardHeader>
        <CardTitle>{message ? "Confirmation received" : "Confirm newsletter resubscription"}</CardTitle>
        <CardDescription>Choose whether to receive Great Commission Benchmark newsletter emails again.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {message ? <p role="status">{message}</p> : <>
          <p className="text-sm">Your address stays unsubscribed unless you confirm. Opening this page does not change your subscription.</p>
          <Button disabled={!token || busy} onClick={confirm}>{busy ? "Confirming…" : "Confirm resubscription"}</Button>
          {!token && <p className="text-sm">Open the link in your confirmation email, or request a new one from the signup page.</p>}
        </>}
        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
        <p className="text-sm"><Link href="/newsletter" className="underline">Newsletter signup</Link> · <Link href="/newsletter/unsubscribe" className="underline">Stay unsubscribed</Link></p>
      </CardContent>
    </Card>
  </main>;
}
