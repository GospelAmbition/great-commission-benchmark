"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { API_URL } from "@/lib/api";
import { useRecaptcha } from "@/hooks/useRecaptcha";
import { trackNewsletterSignup } from "@/lib/analytics";

export default function NewsletterPage() {
  const { data: session } = useSession();
  const user = session?.user;
  const [email, setEmail] = useState("");
  const [subscribing, setSubscribing] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const { executeRecaptcha } = useRecaptcha();

  useEffect(() => {
    if (user?.email) {
      setEmail(user.email);
    }
  }, [user]);

  async function handleSubscribe() {
    if (!email || !email.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }
    setSubscribing(true);
    try {
      // Get reCAPTCHA token
      const recaptchaToken = await executeRecaptcha("newsletter_subscribe");
      
      if (!recaptchaToken) {
        toast.error("Security verification failed. Please try again.");
        setSubscribing(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/newsletter/subscribe`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, recaptcha_token: recaptchaToken }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || "Failed to subscribe");
      }

      const data = await response.json();
      toast.success(data.message || "Successfully subscribed to newsletter");
      setIsSubscribed(true);
      // Track conversion
      trackNewsletterSignup("newsletter_page");
    } catch (error) {
      console.error("Failed to subscribe to newsletter:", error);
      toast.error(error instanceof Error ? error.message : "Failed to subscribe to newsletter");
    } finally {
      setSubscribing(false);
    }
  }

  return (
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
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Newsletter</h1>
          </div>
          <p className="text-muted-foreground">
            Stay updated with the latest features, benchmark results, and announcements
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
                <CardTitle>Subscribe to Our Newsletter</CardTitle>
                <CardDescription>
                  Receive updates about new features, benchmark results, and important announcements
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {isSubscribed ? (
              <div className="p-6 rounded-lg bg-primary/10 border border-primary/20 text-center">
                <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-3" />
                <p className="text-lg font-medium text-primary mb-2">
                  Successfully Subscribed!
                </p>
                <p className="text-sm text-muted-foreground">
                  You'll receive updates about new features, benchmark results, and important announcements.
                </p>
              </div>
            ) : (
              <>
                <div>
                  <Label htmlFor="newsletter-email">Email Address</Label>
                  <Input
                    id="newsletter-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="mt-1"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !subscribing && email) {
                        handleSubscribe();
                      }
                    }}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {user 
                      ? "We'll use your account email. You can change it if needed."
                      : "No account required. Just enter your email to subscribe."}
                  </p>
                </div>
                <Button 
                  onClick={handleSubscribe} 
                  disabled={subscribing || !email}
                  className="w-full"
                  size="lg"
                >
                  {subscribing ? "Subscribing..." : "Subscribe to Newsletter"}
                </Button>
                <p className="text-xs text-center text-muted-foreground">
                  We respect your privacy. Unsubscribe at any time.
                </p>
              </>
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
                <span className="font-medium text-foreground">New Features:</span> Be the first to know about platform updates and improvements
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Benchmark Results:</span> Get notified when new models are tested and added to the leaderboard
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Announcements:</span> Stay informed about important updates and community news
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
