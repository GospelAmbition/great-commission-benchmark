"use client";

import { useEffect, useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { Copy, Key, Trash2, Plus, Eye, EyeOff } from "lucide-react";

interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
  expires_at: string | null;
}

export function APIKeysCard() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [apiKeysLoading, setApiKeysLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState("");
  const [creatingKey, setCreatingKey] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
  const [showNewKey, setShowNewKey] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadAPIKeys();
  }, []);

  // Focus input when hash is #api-keys
  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash === "#api-keys" && inputRef.current) {
        // Small delay to ensure smooth scroll completes
        setTimeout(() => {
          inputRef.current?.focus();
        }, 300);
      }
    };

    // Check on mount
    handleHashChange();

    // Listen for hash changes
    window.addEventListener("hashchange", handleHashChange);

    return () => {
      window.removeEventListener("hashchange", handleHashChange);
    };
  }, []);

  async function loadAPIKeys() {
    setApiKeysLoading(true);
    try {
      const response = await apiClient.getAPIKeys();
      setApiKeys(response.api_keys);
    } catch (error) {
      console.error("Failed to load API keys:", error);
    } finally {
      setApiKeysLoading(false);
    }
  }

  async function handleCreateAPIKey() {
    if (!newKeyName.trim()) {
      toast.error("Please enter a name for the API key");
      return;
    }

    setCreatingKey(true);
    try {
      const response = await apiClient.createAPIKey(newKeyName.trim());
      setNewlyCreatedKey(response.key);
      setShowNewKey(true);
      setNewKeyName("");
      await loadAPIKeys();
      toast.success("API key created successfully");
    } catch (error: any) {
      console.error("Failed to create API key:", error);
      toast.error(error.message || "Failed to create API key");
    } finally {
      setCreatingKey(false);
    }
  }

  async function handleRevokeAPIKey(keyId: string, keyName: string) {
    if (!confirm(`Are you sure you want to revoke the API key "${keyName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await apiClient.revokeAPIKey(keyId);
      await loadAPIKeys();
      toast.success("API key revoked successfully");
    } catch (error: any) {
      console.error("Failed to revoke API key:", error);
      toast.error(error.message || "Failed to revoke API key");
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  }

  function formatDate(dateString: string | null): string {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  return (
    <Card id="api-keys">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Key className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg">API Keys</CardTitle>
        </div>
        <CardDescription>
          Create keys to authenticate the GCB Runner
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* New Key Created Alert */}
        {newlyCreatedKey && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
            <p className="text-sm font-medium text-emerald-400 mb-2">
              🎉 API Key Created
            </p>
            <p className="text-xs text-muted-foreground mb-2">
              Copy now — it won&apos;t be shown again.
            </p>
            <div className="flex items-center gap-2">
              <code className="flex-1 p-2 bg-white/[0.06] rounded border border-white/[0.08] text-xs font-mono overflow-x-auto text-foreground">
                {showNewKey ? newlyCreatedKey : "••••••••••••••••••••••••••••••••"}
              </code>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setShowNewKey(!showNewKey)}
              >
                {showNewKey ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => copyToClipboard(newlyCreatedKey)}
              >
                <Copy className="h-3 w-3" />
              </Button>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2 h-7 text-xs"
              onClick={() => {
                setNewlyCreatedKey(null);
                setShowNewKey(false);
              }}
            >
              Dismiss
            </Button>
          </div>
        )}

        {/* Create New Key */}
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            placeholder="Key name (e.g., My Laptop)"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreateAPIKey()}
            disabled={creatingKey}
            className="h-9 text-sm"
          />
          <Button
            onClick={handleCreateAPIKey}
            disabled={creatingKey || !newKeyName.trim()}
            size="sm"
            className="h-9"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        <Separator />

        {/* Existing Keys */}
        {apiKeysLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-14" />
          </div>
        ) : apiKeys.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-2">
            No API keys yet
          </p>
        ) : (
          <div className="space-y-2">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className={`flex items-center justify-between p-2 rounded-lg border border-white/[0.08] ${
                  key.is_active
                    ? "bg-white/[0.02]"
                    : "bg-muted/50 opacity-60"
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate">{key.name}</p>
                    {!key.is_active && (
                      <Badge variant="secondary" className="text-xs">
                        Revoked
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                    <code className="bg-white/[0.06] px-1 py-0.5 rounded text-xs">
                      {key.key_prefix}...
                    </code>
                    <span>{formatDate(key.created_at)}</span>
                  </div>
                </div>
                {key.is_active && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => handleRevokeAPIKey(key.id, key.name)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
