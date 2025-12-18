"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@auth0/nextjs-auth0/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { TesterAgreementModal } from "@/components/tester-agreement/TesterAgreementModal";

export default function NewTestPage() {
  const { user, isLoading: userLoading } = useUser();
  const router = useRouter();
  const [models, setModels] = useState<any[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedVersion, setSelectedVersion] = useState<string>("");
  const [systemPrompt, setSystemPrompt] = useState<string>("");
  const [costEstimate, setCostEstimate] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showAgreementModal, setShowAgreementModal] = useState(false);
  const [agreementAccepted, setAgreementAccepted] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/login");
      return;
    }
    if (user) {
      loadData();
    }
  }, [user, userLoading, router]);

  async function loadData() {
    setLoading(true);
    try {
      const [modelsData, versionsData, profile] = await Promise.all([
        apiClient.getModels({ limit: 100 }),
        apiClient.getVersions(),
        apiClient.getProfile().catch(() => null),
      ]);
      if (modelsData.items) {
        setModels(modelsData.items);
      }
      if (versionsData.versions) {
        setVersions(versionsData.versions);
        if (versionsData.versions.length > 0) {
          setSelectedVersion(versionsData.versions[0].version);
        }
      }
      // Check if tester agreement is accepted
      if (profile && !profile.tester_agreement_accepted) {
        setShowAgreementModal(true);
      } else {
        setAgreementAccepted(true);
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTest() {
    if (!selectedModel || !selectedVersion) return;
    
    // Check agreement before creating test
    if (!agreementAccepted) {
      setShowAgreementModal(true);
      return;
    }

    setCreating(true);
    try {
      const test = await apiClient.createTest({
        model_id: selectedModel,
        version: selectedVersion,
        system_prompt: systemPrompt || undefined,
      });
      router.push(`/tests/${test.id}/payment`);
    } catch (error) {
      console.error("Failed to create test:", error);
      alert("Failed to create test. Please try again.");
    } finally {
      setCreating(false);
    }
  }

  function handleAgreementAccepted() {
    setAgreementAccepted(true);
    setShowAgreementModal(false);
  }

  useEffect(() => {
    // Calculate cost estimate when model/version changes
    if (selectedModel) {
      const model = models.find((m) => m.id === selectedModel || m.model_id === selectedModel);
      if (model?.estimated_cost_per_test) {
        setCostEstimate(model.estimated_cost_per_test);
      }
    }
  }, [selectedModel, models]);

  if (userLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="container py-8 max-w-3xl">
      <TesterAgreementModal
        open={showAgreementModal}
        onAccept={handleAgreementAccepted}
      />
      
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Run a Benchmark Test</h1>
        <p className="mt-2 text-muted-foreground">
          Select a model and version to test
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[--ga-red] text-white flex items-center justify-center font-bold">
              1
            </div>
            <span className="font-medium">Select Model</span>
          </div>
          <div className="flex-1 h-1 bg-muted mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-bold">
              2
            </div>
            <span className="text-muted-foreground">Payment</span>
          </div>
          <div className="flex-1 h-1 bg-muted mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-bold">
              3
            </div>
            <span className="text-muted-foreground">Processing</span>
          </div>
          <div className="flex-1 h-1 bg-muted mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-bold">
              4
            </div>
            <span className="text-muted-foreground">Results</span>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Model Selection</CardTitle>
          <CardDescription>
            Choose the AI model and benchmark version to test
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="model">Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger id="model">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem
                    key={model.id || model.model_id}
                    value={model.id || model.model_id}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span>{model.name || model.model_name}</span>
                      <Badge variant="secondary" className="ml-2">
                        {model.provider}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="version">Benchmark Version</Label>
            <Select value={selectedVersion} onValueChange={setSelectedVersion}>
              <SelectTrigger id="version">
                <SelectValue placeholder="Select a version" />
              </SelectTrigger>
              <SelectContent>
                {versions.map((version) => (
                  <SelectItem key={version.version} value={version.version}>
                    {version.version}
                    {version.is_current && (
                      <Badge variant="outline" className="ml-2">
                        Current
                      </Badge>
                    )}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="system-prompt">System Prompt (Optional)</Label>
            <Input
              id="system-prompt"
              placeholder="Enter a custom system prompt..."
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Optional: Provide a custom system prompt to test the model with specific instructions
            </p>
          </div>

          {costEstimate && (
            <Card className="bg-muted">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-muted-foreground">Estimated Cost</div>
                    <div className="text-2xl font-bold">${costEstimate.toFixed(2)}</div>
                  </div>
                  <Badge variant="outline">Approximate</Badge>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="flex gap-4">
            <Button
              onClick={handleCreateTest}
              disabled={!selectedModel || !selectedVersion || creating}
              className="bg-[--ga-red] hover:bg-[--ga-dark-red]"
            >
              {creating ? "Creating..." : "Continue to Payment →"}
            </Button>
            <Button asChild variant="outline">
              <a href="/research">Cancel</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
