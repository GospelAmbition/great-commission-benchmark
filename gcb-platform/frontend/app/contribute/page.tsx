"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Link from "next/link";
import { Sparkles, Terminal, Shield } from "lucide-react";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

export default function VolunteerPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const router = useRouter();
  const { canAdmin, isAdmin } = useUserProfile();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    role: "moderator" as "moderator" | "advisor",
    background: "",
    motivation: "",
  });

  async function handleSubmit() {
    if (!formData.name || !formData.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.applyVolunteer({
        email: formData.email,
        name: formData.name,
        role: formData.role,
        background: formData.background || undefined,
        motivation: formData.motivation || undefined,
      });
      toast.success("Volunteer application submitted successfully!");
      setDialogOpen(false);
      setFormData({
        name: user?.name || "",
        email: user?.email || "",
        role: "moderator",
        background: "",
        motivation: "",
      });
    } catch (error) {
      console.error("Failed to submit application:", error);
      toast.error("Failed to submit application. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function handleOpenDialog() {
    if (!user) {
      // Route through login
      router.push(`/api/auth/signin?callbackUrl=${encodeURIComponent("/contribute")}`);
      return;
    }
    // Pre-fill form with user data
    setFormData({
      name: user.name || "",
      email: user.email || "",
      role: "moderator",
      background: "",
      motivation: "",
    });
    setDialogOpen(true);
  }
  return (
    <div className="container py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground">Volunteer</h1>
        <p className="mt-2 text-muted-foreground">
          Help advance the Great Commission Benchmark through various volunteer opportunities
        </p>
      </div>

      {/* Primary CTA - Sponsor a Test */}
      <Card className="mb-8 border-primary/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 gradient-red-glow opacity-10" />
        <CardHeader className="relative">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle>Sponsor a Test</CardTitle>
              <CardDescription>
                Help test AI models for the Great Commission by sponsoring a test run
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="relative space-y-4">
          <p className="text-muted-foreground">
            Sponsor a benchmark test for any AI model to help measure its effectiveness for Great Commission work. 
            Your sponsorship enables testing of models that might not otherwise be evaluated, expanding our 
            understanding of which AI models best serve the Great Commission.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="brand">
              <Link href="/sponsor">
                <Sparkles className="h-4 w-4 mr-2" />
                Sponsor a Test
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/sponsor">
                Learn More →
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Become a Tester */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Terminal className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle>Become a Tester</CardTitle>
              <CardDescription>
                Run benchmark tests and help measure AI models for Great Commission work
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Use our GCB Runner to run benchmark tests on any AI model—including local models, 
            fine-tuned models, or cloud APIs. Your results will be reviewed by moderators 
            and added to the public leaderboard.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="outline">
              <Link href="/dashboard">
                <Terminal className="h-4 w-4 mr-2" />
                Get Started
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/runner">
                Learn About GCB Runner →
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Join a Moderation or Advisory Team */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Shield className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle>Join a Moderation or Advisory Team</CardTitle>
              <CardDescription>
                Help review submissions, guide the project, and shape the future of the benchmark
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Join our moderation team to review and approve test submissions, or join our advisory 
            team to help guide the strategic direction of the Great Commission Benchmark. Your expertise 
            and time help ensure the quality and integrity of our benchmark results.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleOpenDialog} variant="brand">
              <Shield className="h-4 w-4 mr-2" />
              Apply to Volunteer
            </Button>
            {(canAdmin || isAdmin) && (
              <Button asChild variant="outline">
                <Link href="/admin/volunteers">
                  View Applications
                </Link>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Volunteer Application Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Volunteer Application</DialogTitle>
            <DialogDescription>
              Apply to join our moderation or advisory team. Please provide information about your background and motivation.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Your full name"
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
              />
            </div>
            <div>
              <Label htmlFor="role">Role *</Label>
              <Select
                value={formData.role}
                onValueChange={(value: "moderator" | "advisor") =>
                  setFormData({ ...formData, role: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="moderator">Moderator</SelectItem>
                  <SelectItem value="advisor">Advisor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="background">Background & Experience</Label>
              <Textarea
                id="background"
                value={formData.background}
                onChange={(e) => setFormData({ ...formData, background: e.target.value })}
                placeholder="Tell us about your background, expertise, and relevant experience..."
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="motivation">Motivation</Label>
              <Textarea
                id="motivation"
                value={formData.motivation}
                onChange={(e) => setFormData({ ...formData, motivation: e.target.value })}
                placeholder="Why do you want to volunteer for the Great Commission Benchmark?"
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting ? "Submitting..." : "Submit Application"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
