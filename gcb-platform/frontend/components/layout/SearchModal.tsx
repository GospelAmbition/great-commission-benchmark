"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { apiClient, LeaderboardItem } from "@/lib/api";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";
import { SearchIcon } from "@/lib/icons";
import { cn } from "@/lib/utils";

interface SearchModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface SearchResult {
  type: "model" | "provider";
  id: string;
  name: string;
  provider?: string;
  modelId?: string;
  href: string;
}

export function SearchModal({ open, onOpenChange }: SearchModalProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [models, setModels] = useState<LeaderboardItem[]>([]);
  const [providers, setProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Fetch data when modal opens
  useEffect(() => {
    if (open) {
      loadData();
      // Focus input when modal opens
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      // Reset state when modal closes
      setQuery("");
      setSelectedIndex(0);
    }
  }, [open]);

  async function loadData() {
    if (models.length > 0 && providers.length > 0) return; // Already loaded
    
    setLoading(true);
    try {
      const [leaderboardData, filterOptions] = await Promise.all([
        apiClient.getLeaderboard({ limit: 100 }),
        apiClient.getFilterOptions(),
      ]);
      
      if (leaderboardData.items) {
        setModels(leaderboardData.items);
      }
      if (filterOptions.providers) {
        setProviders(filterOptions.providers);
      }
    } catch (error) {
      console.error("Failed to load search data:", error);
    } finally {
      setLoading(false);
    }
  }

  // Filter results based on query
  const results = useMemo((): SearchResult[] => {
    if (!query.trim()) {
      // Show empty state until user starts typing
      return [];
    }

    const q = query.toLowerCase();
    const searchResults: SearchResult[] = [];

    // Filter providers first
    const matchingProviders = providers
      .filter((provider) => {
        const name = formatProvider(provider).toLowerCase();
        return name.includes(q) || provider.toLowerCase().includes(q);
      })
      .slice(0, 3)
      .map((provider) => ({
        type: "provider" as const,
        id: provider,
        name: formatProvider(provider),
        href: `/leaderboard/providers/${encodeURIComponent(provider)}`,
      }));

    searchResults.push(...matchingProviders);

    // Filter models by provider name and model name
    const matchingModels = models
      .filter((model) => {
        const name = getDisplayModelName(model.model_name, model.model_id).toLowerCase();
        const providerName = formatProvider(model.provider).toLowerCase();
        return name.includes(q) || providerName.includes(q);
      })
      .slice(0, 8)
      .map((model) => ({
        type: "model" as const,
        id: model.id,
        name: getDisplayModelName(model.model_name, model.model_id),
        provider: model.provider,
        modelId: model.model_id,
        href: `/leaderboard/models/${encodeURIComponent(model.model_id)}`,
      }));

    searchResults.push(...matchingModels);

    return searchResults;
  }, [query, models, providers]);

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (results[selectedIndex]) {
            navigateToResult(results[selectedIndex]);
          }
          break;
        case "Escape":
          e.preventDefault();
          onOpenChange(false);
          break;
      }
    },
    [results, selectedIndex, onOpenChange]
  );

  // Scroll selected item into view
  useEffect(() => {
    const selectedElement = resultsRef.current?.querySelector(
      `[data-index="${selectedIndex}"]`
    );
    if (selectedElement) {
      selectedElement.scrollIntoView({ block: "nearest" });
    }
  }, [selectedIndex]);

  function navigateToResult(result: SearchResult) {
    router.push(result.href);
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="sm:max-w-lg p-0 gap-0 overflow-hidden"
        showCloseButton={false}
      >
        <DialogTitle className="sr-only">Search providers and models</DialogTitle>
        <DialogDescription className="sr-only">
          Search for AI models and providers on the leaderboard.
        </DialogDescription>
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
          <SearchIcon className="h-5 w-5 text-muted-foreground shrink-0" />
          <Input
            ref={inputRef}
            type="text"
            placeholder="Search models and providers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
            className="border-0 bg-transparent p-0 h-auto focus-visible:ring-0 focus-visible:border-0 text-base placeholder:text-muted-foreground/60"
          />
          <button
            onClick={() => onOpenChange(false)}
            className="h-5 w-5 flex items-center justify-center rounded hover:bg-white/10 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Close search"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Results */}
        <div
          ref={resultsRef}
          className="max-h-[300px] overflow-y-auto py-2"
        >
          {loading ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Loading...
            </div>
          ) : results.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              {query ? (
                <>No results found for &quot;{query}&quot;</>
              ) : (
                <>Start typing to search providers and models...</>
              )}
            </div>
          ) : (
            <>
              {/* Providers Section */}
              {results.some((r) => r.type === "provider") && (
                <div className="mb-2">
                  <div className="px-4 py-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Providers
                  </div>
                  {results
                    .filter((r) => r.type === "provider")
                    .map((result) => {
                      const globalIndex = results.findIndex(
                        (r) => r.id === result.id && r.type === result.type
                      );
                      return (
                        <button
                          key={`provider-${result.id}`}
                          data-index={globalIndex}
                          onClick={() => navigateToResult(result)}
                          className={cn(
                            "w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors",
                            globalIndex === selectedIndex
                              ? "bg-primary/10 text-foreground"
                              : "hover:bg-white/5 text-foreground"
                          )}
                        >
                          <ProviderIcon provider={result.id} size={18} />
                          <div className="flex-1 min-w-0">
                            <div className="font-medium truncate">
                              {result.name}
                            </div>
                          </div>
                          <span className="text-xs text-muted-foreground/60 shrink-0">
                            Provider
                          </span>
                        </button>
                      );
                    })}
                </div>
              )}

              {/* Models Section */}
              {results.some((r) => r.type === "model") && (
                <div>
                  <div className="px-4 py-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Models
                  </div>
                  {results
                    .filter((r) => r.type === "model")
                    .map((result, idx) => {
                      const globalIndex = results.findIndex(
                        (r) => r.id === result.id && r.type === result.type
                      );
                      return (
                        <button
                          key={`model-${result.id}`}
                          data-index={globalIndex}
                          onClick={() => navigateToResult(result)}
                          className={cn(
                            "w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors",
                            globalIndex === selectedIndex
                              ? "bg-primary/10 text-foreground"
                              : "hover:bg-white/5 text-foreground"
                          )}
                        >
                          <ProviderIcon
                            provider={result.provider || ""}
                            size={18}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="font-medium truncate">
                              {result.name}
                            </div>
                            <div className="text-xs text-muted-foreground truncate">
                              {formatProvider(result.provider || "")}
                            </div>
                          </div>
                          <span className="text-xs text-muted-foreground/60 shrink-0">
                            Model
                          </span>
                        </button>
                      );
                    })}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-4 py-2 border-t border-white/10 bg-white/[0.02] text-xs text-muted-foreground">
          <span>
            {results.length} result{results.length !== 1 ? "s" : ""}
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
