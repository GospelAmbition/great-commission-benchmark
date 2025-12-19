"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import { TesterAgreementModal } from "@/components/tester-agreement/TesterAgreementModal";

export default function NewTestPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const [models, setModels] = useState<any[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedVersion, setSelectedVersion] = useState<string>("");
  const [costEstimate, setCostEstimate] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showAgreementModal, setShowAgreementModal] = useState(false);
  const [agreementAccepted, setAgreementAccepted] = useState(false);
  const [modelsError, setModelsError] = useState<string | null>(null);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadData();
    }
  }, [user, userLoading, router]);

  async function loadData() {
    setLoading(true);
    setModelsError(null);
    try {
      const [modelsData, versionsData, profile] = await Promise.all([
        apiClient.getAvailableModels({ limit: 200 }).catch((err) => {
          console.error("Failed to fetch models from OpenRouter:", err);
          setModelsError("Unable to load models. Please check if the backend is running and OpenRouter is configured.");
          return { items: [] };
        }),
        apiClient.getVersions(),
        apiClient.getProfile().catch(() => null),
      ]);
      if (modelsData.items) {
        setModels(modelsData.items);
      }
      // Handle versions - backend returns versions array with semantic_version field
      if (versionsData.versions && versionsData.versions.length > 0) {
        // Transform versions to have a consistent 'version' field
        const transformedVersions = versionsData.versions.map((v: any) => ({
          ...v,
          version: v.semantic_version || v.version,
          is_current: v.status === "current" || v.is_current,
        }));
        setVersions(transformedVersions);
        // Select the current version, or the first one if no current
        const currentVersion = transformedVersions.find((v: any) => v.is_current);
        if (currentVersion) {
          setSelectedVersion(currentVersion.version);
        } else if (transformedVersions.length > 0) {
          setSelectedVersion(transformedVersions[0].version);
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
              <SelectContent className="max-h-80">
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
            {modelsError && (
              <p className="text-xs text-destructive mt-1">{modelsError}</p>
            )}
            {models.length === 0 && !modelsError && !loading && (
              <p className="text-xs text-muted-foreground mt-1">
                No models available. Please check your OpenRouter configuration.
              </p>
            )}
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
            {versions.length === 0 && !loading && (
              <p className="text-xs text-muted-foreground mt-1">
                No benchmark versions available. Please contact an administrator.
              </p>
            )}
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
              variant="brand"
              onClick={handleCreateTest}
              disabled={!selectedModel || !selectedVersion || creating}
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
