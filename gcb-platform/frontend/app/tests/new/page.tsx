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
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { HelpCircle, ShieldAlert } from "lucide-react";
import { useUserProfile } from "@/lib/useUserProfile";
import { toast } from "sonner";

export default function NewTestPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { isAdmin, loading: profileLoading } = useUserProfile();
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
    
    // Check admin access after profile loads
    if (!profileLoading && user && !isAdmin) {
      toast.error("Platform tests are restricted to administrators. Please use the GCB Runner to run tests.");
      router.push("/dashboard");
      return;
    }
    
    if (user && isAdmin) {
      loadData();
    }
  }, [user, userLoading, router, isAdmin, profileLoading]);

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

  // Show loading while checking permissions
  if (userLoading || profileLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  // Don't render if not admin (will redirect)
  if (!user || !isAdmin) {
    return (
      <div className="container py-8 max-w-3xl">
        <Card className="border-destructive">
          <CardHeader>
            <div className="flex items-center gap-3">
              <ShieldAlert className="h-6 w-6 text-destructive" />
              <div>
                <CardTitle>Access Restricted</CardTitle>
                <CardDescription>
                  Platform tests are only available to administrators.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              To run benchmark tests, please use the GCB Runner GCB Runner. You can install it and upload your results from your dashboard.
            </p>
            <div className="flex gap-4">
              <Button asChild variant="brand">
                <a href="/dashboard">Go to Dashboard</a>
              </Button>
              <Button asChild variant="outline">
                <a href="/runner">Learn About GCB Runner</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="container py-8 max-w-3xl">
      <TesterAgreementModal
        open={showAgreementModal}
        onAccept={handleAgreementAccepted}
      />
      
      {/* Admin Notice */}
      <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-lg">
        <div className="flex items-center gap-2 text-amber-800 dark:text-amber-200">
          <ShieldAlert className="h-5 w-5" />
          <span className="font-medium">Admin-Only Feature</span>
        </div>
        <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
          Platform tests are restricted to administrators. Regular users should use the GCB Runner.
        </p>
      </div>
      
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Run a Platform Test</h1>
        <p className="mt-2 text-muted-foreground">
          Select a model and version to test directly on the platform
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[var(--ga-red)] text-white flex items-center justify-center font-bold">
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
            <div className="flex items-center gap-1.5 mb-1">
              <Label htmlFor="model" className="mb-0">Model</Label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button type="button" className="text-muted-foreground hover:text-foreground transition-colors">
                    <HelpCircle className="h-4 w-4" />
                    <span className="sr-only">Model not listed?</span>
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>
                    Model not listed? Use the{" "}
                    <a
                      href="/runner"
                      className="underline font-medium hover:text-[--ga-red]"
                    >
                      GCB Runner
                    </a>{" "}
                    to run tests locally.
                  </p>
                </TooltipContent>
              </Tooltip>
            </div>
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
              <a href="/dashboard">Cancel</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
