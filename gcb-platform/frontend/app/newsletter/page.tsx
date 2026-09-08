"use client";

import { useEffect, useRef, useState } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { API_URL } from "@/lib/api";
import { useRecaptcha } from "@/hooks/useRecaptcha";
import { RecaptchaScript } from "@/components/recaptcha/RecaptchaScript";
import { trackEvent, trackNewsletterSignup } from "@/lib/analytics";

import { NEWSLETTER_PROMISE, newsletterSource } from "@/lib/newsletter";

export default function NewsletterPage() {
  const { data: session } = useSession();
  const user = session?.user;
  const [email, setEmail] = useState("");
  const [subscribing, setSubscribing] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [successMessage, setSuccessMessage] = useState("Successfully subscribed!");
  const submittingRef = useRef(false);
  const { executeRecaptcha } = useRecaptcha();

  useEffect(() => {
    if (user?.email && !submittingRef.current) {
      setEmail(current => current || user.email || "");
    }
  }, [user]);

  async function handleSubscribe() {
    if (submittingRef.current) return;
    const source = newsletterSource(new URLSearchParams(window.location.search).get("source"));
    trackEvent("newsletter_form_submit", { source });
    const normalizedEmail = email.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      toast.error("Please enter a valid email address");
      trackEvent("newsletter_signup_outcome", { source, outcome: "invalid_email" });
      return;
    }
    submittingRef.current = true;
    setSubscribing(true);
    try {
      // Get reCAPTCHA token if configured
      const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
      let recaptchaToken: string | null = null;
      
      if (siteKey) {
        // Only try to get token if site key is configured
        let retries = 2;
        
        while (!recaptchaToken && retries > 0) {
          recaptchaToken = await executeRecaptcha("newsletter_subscribe");
          if (!recaptchaToken && retries > 1) {
            // Wait a bit before retrying
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
          retries--;
        }
        
        if (!recaptchaToken) {
          toast.error("Security verification failed. Please wait a moment and try again.");
          trackEvent("newsletter_signup_outcome", { source, outcome: "security_error" });
          setSubscribing(false);
          return;
        }
      }
      // If no site key, proceed without token (backend will handle it)

      const response = await fetch(`${API_URL}/api/newsletter/subscribe`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: normalizedEmail, recaptcha_token: recaptchaToken }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = typeof errorData.detail === "string" ? errorData.detail : typeof errorData.message === "string" ? errorData.message : "Failed to subscribe";
        
        // Check if it's a reCAPTCHA error from backend
        if (errorMessage.toLowerCase().includes("recaptcha") || errorMessage.toLowerCase().includes("security verification")) {
          toast.error("Security verification failed. Please try again.");
          trackEvent("newsletter_signup_outcome", { source, outcome: "security_error" });
        } else {
          throw new Error(errorMessage);
        }
        setSubscribing(false);
        return;
      }

      const data = await response.json();
      if (data.success === false) throw new Error("Failed to subscribe. Please try again.");
      const outcome = data.message === "Email already subscribed" ? "already_subscribed" : data.message === "Subscription reactivated" ? "reactivated" : "subscribed";
      const message = outcome === "already_subscribed" ? "You’re already subscribed!" : outcome === "reactivated" ? "Your subscription is active again!" : "Successfully subscribed!";
      toast.success(message);
      setSuccessMessage(message);
      setIsSubscribed(true);
      trackEvent("newsletter_signup_outcome", { source, outcome });
      // Accepted submissions include existing subscribers; this is not net subscriber growth.
      trackNewsletterSignup(source);
    } catch (error) {
      trackEvent("newsletter_signup_outcome", { source, outcome: "request_error" });
      toast.error(error instanceof Error ? error.message : "Failed to subscribe to newsletter");
    } finally {
      submittingRef.current = false;
      setSubscribing(false);
    }
  }

  return (
    <>
      <RecaptchaScript />
      <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-40" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <Mail className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Get the GCB digest</h1>
          </div>
          <p className="text-muted-foreground">
            {NEWSLETTER_PROMISE}
          </p>
        </div>
      </div>

      <div className="container py-8 max-w-2xl">
        <Card className="border-primary/20 bg-gradient-to-br from-card to-card/50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Mail className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle>Get the GCB digest</CardTitle>
                <CardDescription>
                  Monthly digest, plus occasional highlights on important model releases.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {isSubscribed ? (
              <div role="status" className="p-6 rounded-lg bg-primary/10 border border-primary/20 text-center">
                <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-3" />
                <p className="text-lg font-medium text-primary mb-2">
                  {successMessage}
                </p>
                <p className="text-sm text-muted-foreground">
                  {NEWSLETTER_PROMISE}
                </p>
              </div>
            ) : (
              <form noValidate onSubmit={(event) => { event.preventDefault(); void handleSubscribe(); }} className="space-y-4">
                <div>
                  <Label htmlFor="newsletter-email">Email Address</Label>
                  <Input
                    id="newsletter-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="mt-1"
                    autoComplete="email"
                    name="email"
                    required
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {user 
                      ? "We'll use your account email. You can change it if needed."
                      : "No account required. Just enter your email to subscribe."}
                  </p>
                </div>
                <Button 
                  type="submit"
                  disabled={subscribing || !email}
                  className="w-full"
                  size="lg"
                >
                  {subscribing ? "Subscribing..." : "Subscribe to Newsletter"}
                </Button>
                <p className="text-xs text-center text-muted-foreground">
                  We respect your privacy. Unsubscribe at any time.
                </p>
              </form>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>What to Expect</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Monthly Digest:</span> New model evaluations and insights for Great Commission work
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Release Highlights:</span> Occasional emails covering important model releases
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Easy to Join:</span> No account required. Unsubscribe at any time.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
    </>
  );
}
