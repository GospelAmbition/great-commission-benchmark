"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MessageSquare, CheckCircle2, Send } from "lucide-react";
import { toast } from "sonner";
import { API_URL } from "@/lib/api";
import { useRecaptcha } from "@/hooks/useRecaptcha";

const CONTACT_SUBJECTS = [
  { value: "general", label: "General Inquiry" },
  { value: "technical", label: "Technical Support" },
  { value: "partnership", label: "Partnership Opportunity" },
  { value: "media", label: "Media Inquiry" },
  { value: "feedback", label: "Feedback" },
  { value: "other", label: "Other" },
];

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "general",
    message: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { executeRecaptcha } = useRecaptcha();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    // Validate form
    if (!formData.name.trim()) {
      toast.error("Please enter your name");
      return;
    }
    if (!formData.email || !formData.email.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }
    if (!formData.message.trim() || formData.message.length < 10) {
      toast.error("Please enter a message (at least 10 characters)");
      return;
    }

    setSubmitting(true);
    try {
      // Get reCAPTCHA token if configured
      const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
      let recaptchaToken: string | null = null;
      
      if (siteKey) {
        let retries = 2;
        
        while (!recaptchaToken && retries > 0) {
          recaptchaToken = await executeRecaptcha("contact_submit");
          if (!recaptchaToken && retries > 1) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
          retries--;
        }
        
        if (!recaptchaToken) {
          toast.error("Security verification failed. Please wait a moment and try again.");
          setSubmitting(false);
          return;
        }
      }

      const response = await fetch(`${API_URL}/api/contact/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          email: formData.email.trim(),
          subject: formData.subject,
          message: formData.message.trim(),
          recaptcha_token: recaptchaToken,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || "Failed to submit contact form";
        
        if (errorMessage.toLowerCase().includes("recaptcha") || errorMessage.toLowerCase().includes("security verification")) {
          toast.error("Security verification failed. Please try again.");
        } else {
          throw new Error(errorMessage);
        }
        setSubmitting(false);
        return;
      }

      const data = await response.json();
      toast.success(data.message || "Your message has been sent successfully");
      setIsSubmitted(true);
    } catch (error) {
      console.error("Failed to submit contact form:", error);
      toast.error(error instanceof Error ? error.message : "Failed to submit contact form");
    } finally {
      setSubmitting(false);
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
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Contact Us</h1>
          </div>
          <p className="text-muted-foreground">
            Get in touch with the Great Commission Benchmark team
          </p>
        </div>
      </div>

      <div className="container py-8 max-w-2xl">
        <Card className="border-primary/20 bg-gradient-to-br from-card to-card/50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Send className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle>Send Us a Message</CardTitle>
                <CardDescription>
                  Have questions, feedback, or want to partner with us? We'd love to hear from you.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isSubmitted ? (
              <div className="p-6 rounded-lg bg-primary/10 border border-primary/20 text-center">
                <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-3" />
                <p className="text-lg font-medium text-primary mb-2">
                  Message Sent Successfully!
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  Thank you for contacting us. We'll review your message and get back to you as soon as possible.
                </p>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsSubmitted(false);
                    setFormData({ name: "", email: "", subject: "general", message: "" });
                  }}
                >
                  Send Another Message
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Your name"
                      className="mt-1"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      className="mt-1"
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="subject">Subject *</Label>
                  <Select
                    value={formData.subject}
                    onValueChange={(value) => setFormData({ ...formData, subject: value })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CONTACT_SUBJECTS.map((subject) => (
                        <SelectItem key={subject.value} value={subject.value}>
                          {subject.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="message">Message *</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    placeholder="How can we help you?"
                    className="mt-1 min-h-[150px]"
                    required
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Minimum 10 characters
                  </p>
                </div>

                <Button
                  type="submit"
                  disabled={submitting}
                  className="w-full"
                  size="lg"
                >
                  {submitting ? (
                    "Sending..."
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Send Message
                    </>
                  )}
                </Button>
                
                <p className="text-xs text-center text-muted-foreground">
                  We typically respond within 1-2 business days.
                </p>
              </form>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>What We Can Help With</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Technical Questions:</span> Help with the GCB Runner, benchmark methodology, or platform features
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Partnership Opportunities:</span> Collaborate with us on AI safety research or ministry initiatives
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Media Inquiries:</span> Press coverage, interviews, or content collaboration
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-primary" />
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Feedback:</span> Share your experience or suggest improvements to help us serve you better
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
