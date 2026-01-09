"use client";

import { SponsorModelCard } from "@/components/sponsor-model-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

export default function SponsorPage() {
  return (
    <div className="container py-8 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-foreground">Sponsor a Model Test</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          Help test AI models for the Great Commission. Sponsor a test run for any available model, or request a custom model to be added to the benchmark.
        </p>
      </div>

      {/* Sponsor Card */}
      <SponsorModelCard />
    </div>
  );
}
