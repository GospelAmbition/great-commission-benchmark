"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { BarChart3, X, Loader2 } from "lucide-react";
import { apiClient, LeaderboardItem } from "@/lib/api";
import { formatProvider } from "@/lib/model-utils";

interface ModelPickerProps {
  value: string[];
  onChange: (ids: string[]) => void;
}

export function ModelPicker({ value, onChange }: ModelPickerProps) {
  const [allModels, setAllModels] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Backend GET /api/public/leaderboard enforces limit <= 100; higher values return 422.
    apiClient
      .getLeaderboard({ limit: 100 })
      .then((res) => {
        setAllModels(res.items);
        setLoadError(null);
      })
      .catch((err) => {
        setLoadError(err instanceof Error ? err.message : "Failed to load models");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectedModels = allModels.filter((m) => value.includes(m.model_id));

  const query = search.toLowerCase();
  const filtered = allModels
    .filter((m) => !value.includes(m.model_id))
    .filter(
      (m) =>
        m.model_name.toLowerCase().includes(query) ||
        m.model_id.toLowerCase().includes(query) ||
        m.provider.toLowerCase().includes(query)
    )
    .slice(0, 10);

  function addModel(modelId: string) {
    onChange([...value, modelId]);
    setSearch("");
    setOpen(false);
  }

  function removeModel(modelId: string) {
    onChange(value.filter((id) => id !== modelId));
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Linked Models
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        ) : loadError ? (
          <p className="text-sm text-destructive" role="alert">
            {loadError}
          </p>
        ) : (
          <>
            {selectedModels.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {selectedModels.map((m) => (
                  <Badge
                    key={m.model_id}
                    variant="secondary"
                    className="flex items-center gap-1 pr-1"
                  >
                    <ProviderIcon provider={m.provider} size={14} />
                    <span className="max-w-[120px] truncate text-xs">
                      {m.model_name}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeModel(m.model_id)}
                      className="ml-0.5 rounded-full p-0.5 hover:bg-muted-foreground/20 transition-colors"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            <div className="relative" ref={wrapperRef}>
              <Input
                placeholder="Search models..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setOpen(true);
                }}
                onFocus={() => setOpen(true)}
              />
              {open && (search.length > 0 || filtered.length > 0) && (
                <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg max-h-[240px] overflow-y-auto">
                  {filtered.length === 0 ? (
                    <div className="px-3 py-2 text-sm text-muted-foreground">
                      No models found
                    </div>
                  ) : (
                    filtered.map((m) => (
                      <button
                        key={m.model_id}
                        type="button"
                        className="flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-accent transition-colors"
                        onClick={() => addModel(m.model_id)}
                      >
                        <ProviderIcon provider={m.provider} size={18} />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium truncate">
                            {m.model_name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {formatProvider(m.provider)}
                          </div>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {value.length === 0 && (
              <p className="text-xs text-muted-foreground mt-2">
                Link benchmark models discussed in this article.
              </p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
