"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
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
import { 
  HelpCircle, 
  ShieldAlert, 
  Search, 
  ChevronRight,
  Check,
  Building2
} from "lucide-react";
import { useUserProfile } from "@/lib/useUserProfile";
import { toast } from "sonner";
import { TestProgressIndicator, TestSummaryPanel } from "@/components/test-flow";
import { cn } from "@/lib/utils";

interface ModelItem {
  id?: string;
  model_id: string;
  name?: string;
  model_name?: string;
  provider: string;
  estimated_cost_per_test?: number;
}

interface ProviderGroup {
  provider: string;
  models: ModelItem[];
}

export default function NewTestPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();
  const { isAdmin, loading: profileLoading } = useUserProfile();
  const [models, setModels] = useState<ModelItem[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedVersion, setSelectedVersion] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showAgreementModal, setShowAgreementModal] = useState(false);
  const [agreementAccepted, setAgreementAccepted] = useState(false);
  const [modelsError, setModelsError] = useState<string | null>(null);

  // Group models by provider
  const providerGroups = useMemo<ProviderGroup[]>(() => {
    const groups: Record<string, ModelItem[]> = {};
    
    models.forEach((model) => {
      const provider = model.provider || "Other";
      if (!groups[provider]) {
        groups[provider] = [];
      }
      groups[provider].push(model);
    });

    // Sort providers alphabetically, with common ones first
    const priorityProviders = ["OpenAI", "Anthropic", "Google", "Meta", "Mistral"];
    
    return Object.entries(groups)
      .map(([provider, models]) => ({ provider, models }))
      .sort((a, b) => {
        const aIndex = priorityProviders.indexOf(a.provider);
        const bIndex = priorityProviders.indexOf(b.provider);
        if (aIndex >= 0 && bIndex >= 0) return aIndex - bIndex;
        if (aIndex >= 0) return -1;
        if (bIndex >= 0) return 1;
        return a.provider.localeCompare(b.provider);
      });
  }, [models]);

  // Filter providers by search query
  const filteredProviders = useMemo(() => {
    if (!searchQuery.trim()) return providerGroups;
    
    const query = searchQuery.toLowerCase();
    return providerGroups
      .map(group => ({
        ...group,
        models: group.models.filter(
          model => 
            (model.name || model.model_name || "").toLowerCase().includes(query) ||
            model.provider.toLowerCase().includes(query) ||
            model.model_id.toLowerCase().includes(query)
        )
      }))
      .filter(group => group.models.length > 0);
  }, [providerGroups, searchQuery]);

  // Get models for selected provider
  const providerModels = useMemo(() => {
    if (!selectedProvider) return [];
    const group = providerGroups.find(g => g.provider === selectedProvider);
    return group?.models || [];
  }, [selectedProvider, providerGroups]);

  // Get selected model details
  const selectedModelData = useMemo(() => {
    if (!selectedModel) return null;
    return models.find(m => (m.id || m.model_id) === selectedModel);
  }, [selectedModel, models]);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    
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
        apiClient.getUserProfile().catch(() => null),
      ]);
      if (modelsData.items) {
        setModels(modelsData.items);
      }
      if (versionsData.versions && versionsData.versions.length > 0) {
        const transformedVersions = versionsData.versions.map((v: any) => ({
          ...v,
          version: v.semantic_version || v.version,
          is_current: v.status === "current" || v.is_current,
        }));
        setVersions(transformedVersions);
        const currentVersion = transformedVersions.find((v: any) => v.is_current);
        if (currentVersion) {
          setSelectedVersion(currentVersion.version);
        } else if (transformedVersions.length > 0) {
          setSelectedVersion(transformedVersions[0].version);
        }
      }
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
      toast.error("Failed to create test. Please try again.");
    } finally {
      setCreating(false);
    }
  }

  function handleAgreementAccepted() {
    setAgreementAccepted(true);
    setShowAgreementModal(false);
  }

  function handleProviderSelect(provider: string) {
    setSelectedProvider(provider);
    setSelectedModel("");
  }

  function handleModelSelect(modelId: string) {
    setSelectedModel(modelId);
  }

  if (userLoading || profileLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid lg:grid-cols-[1fr_320px] gap-8">
          <Skeleton className="h-[600px]" />
          <Skeleton className="h-[400px]" />
        </div>
      </div>
    );
  }

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
              To run benchmark tests, please use the GCB Runner. You can install it and upload your results from your dashboard.
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
        <div className="grid lg:grid-cols-[1fr_320px] gap-8">
          <Skeleton className="h-[600px]" />
          <Skeleton className="h-[400px]" />
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <TesterAgreementModal
        open={showAgreementModal}
        onAccept={handleAgreementAccepted}
      />
      
      {/* Admin Notice */}
      <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-lg max-w-4xl">
        <div className="flex items-center gap-2 text-amber-800 dark:text-amber-200">
          <ShieldAlert className="h-5 w-5" />
          <span className="font-medium">Admin-Only Feature</span>
        </div>
        <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
          Platform tests are restricted to administrators. Regular users should use the GCB Runner.
        </p>
      </div>
      
      {/* Header */}
      <div className="mb-8 max-w-4xl">
        <h1 className="text-4xl font-bold">Run a New Benchmark Test</h1>
        <p className="mt-2 text-muted-foreground">
          Select the AI model you want to evaluate against the Great Commission Benchmark.
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="max-w-4xl">
        <TestProgressIndicator currentStep="select" />
      </div>

      {/* Two-column layout */}
      <div className="grid lg:grid-cols-[1fr_320px] gap-8">
        {/* Left column - Selection */}
        <div className="space-y-6">
          {/* Provider Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Select Provider</CardTitle>
              <CardDescription>
                Choose an AI provider to see available models
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search providers or models..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {modelsError && (
                <p className="text-sm text-destructive">{modelsError}</p>
              )}

              {/* Provider list */}
              <div className="space-y-1 max-h-[300px] overflow-y-auto">
                {filteredProviders.map((group) => (
                  <button
                    key={group.provider}
                    type="button"
                    onClick={() => handleProviderSelect(group.provider)}
                    className={cn(
                      "w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors",
                      selectedProvider === group.provider
                        ? "bg-[var(--ga-accent-red)] border-l-4 border-[var(--ga-red)]"
                        : "hover:bg-muted"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Building2 className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{group.provider}</div>
                        <div className="text-sm text-muted-foreground">
                          {group.models.length} model{group.models.length !== 1 ? "s" : ""}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className={cn(
                      "h-5 w-5 text-muted-foreground transition-transform",
                      selectedProvider === group.provider && "rotate-90"
                    )} />
                  </button>
                ))}
                {filteredProviders.length === 0 && !modelsError && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No providers match your search.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Model Selection (shown after provider is selected) */}
          {selectedProvider && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Select Model</CardTitle>
                    <CardDescription>
                      Choose a model from {selectedProvider}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedProvider("");
                      setSelectedModel("");
                    }}
                  >
                    Change Provider
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-1 max-h-[250px] overflow-y-auto">
                  {providerModels.map((model) => {
                    const modelId = model.id || model.model_id;
                    const modelName = model.name || model.model_name || model.model_id;
                    const isSelected = selectedModel === modelId;
                    
                    return (
                      <button
                        key={modelId}
                        type="button"
                        onClick={() => handleModelSelect(modelId)}
                        className={cn(
                          "w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors",
                          isSelected
                            ? "bg-[var(--ga-accent-red)] border-l-4 border-[var(--ga-red)]"
                            : "hover:bg-muted"
                        )}
                      >
                        <div>
                          <div className="font-medium">{modelName}</div>
                          <div className="text-xs text-muted-foreground font-mono">
                            {model.model_id}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {model.estimated_cost_per_test && (
                            <span className="text-sm text-muted-foreground">
                              ~${model.estimated_cost_per_test.toFixed(2)}
                            </span>
                          )}
                          {isSelected && (
                            <Check className="h-5 w-5 text-[var(--ga-red)]" />
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Version Selection (shown after model is selected) */}
          {selectedModel && (
            <Card>
              <CardHeader>
                <CardTitle>Select Version</CardTitle>
                <CardDescription>
                  Choose the benchmark methodology version
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  {versions.map((version) => (
                    <button
                      key={version.version}
                      type="button"
                      onClick={() => setSelectedVersion(version.version)}
                      className={cn(
                        "w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors",
                        selectedVersion === version.version
                          ? "bg-[var(--ga-accent-red)] border-l-4 border-[var(--ga-red)]"
                          : "hover:bg-muted"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{version.version}</span>
                        {version.is_current && (
                          <Badge variant="outline">Current</Badge>
                        )}
                      </div>
                      {selectedVersion === version.version && (
                        <Check className="h-5 w-5 text-[var(--ga-red)]" />
                      )}
                    </button>
                  ))}
                </div>
                {versions.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    No benchmark versions available. Please contact an administrator.
                  </p>
                )}

                {/* Model not listed hint */}
                <div className="pt-4 border-t">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground cursor-help">
                        <HelpCircle className="h-4 w-4" />
                        <span>Model not listed?</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="max-w-xs">
                      <p>
                        Use the{" "}
                        <a
                          href="/runner"
                          className="underline font-medium hover:text-[var(--ga-red)]"
                        >
                          GCB Runner
                        </a>{" "}
                        to run tests locally with any model.
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action buttons */}
          <div className="flex gap-4">
            <Button
              variant="brand"
              size="lg"
              onClick={handleCreateTest}
              disabled={!selectedModel || !selectedVersion || creating}
            >
              {creating ? "Creating..." : "Continue to Payment →"}
            </Button>
            <Button asChild variant="outline" size="lg">
              <a href="/dashboard">Cancel</a>
            </Button>
          </div>
        </div>

        {/* Right column - Summary */}
        <div className="lg:block">
          <TestSummaryPanel
            provider={selectedProvider || undefined}
            modelName={selectedModelData?.name || selectedModelData?.model_name || undefined}
            modelId={selectedModelData?.model_id}
            version={selectedVersion || undefined}
            estimatedCost={selectedModelData?.estimated_cost_per_test}
          />
        </div>
      </div>
    </div>
  );
}
