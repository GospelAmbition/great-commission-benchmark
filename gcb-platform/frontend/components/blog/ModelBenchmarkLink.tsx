"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ProviderIcon } from "@/components/ui/provider-icon";
import { ChevronRight, BarChart3 } from "lucide-react";
import { formatProvider } from "@/lib/model-utils";

interface RelatedModel {
  id: string;
  model_id: string;
  name: string;
  provider: string;
}

interface ModelBenchmarkLinkProps {
  models: RelatedModel[];
}

export function ModelBenchmarkLink({ models }: ModelBenchmarkLinkProps) {
  if (!models || models.length === 0) return null;

  return (
    <Card className="bg-muted/50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Benchmark Results
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          View detailed benchmark scores and performance data for the
          {models.length === 1 ? " model" : " models"} discussed in this article.
        </p>
        <div className="space-y-3">
          {models.map((model) => (
            <Link
              key={model.id}
              href={`/leaderboard/models/${encodeURIComponent(model.model_id)}`}
              className="flex items-center gap-3 group rounded-lg p-3 bg-background/50 border border-white/[0.06] hover:border-primary/30 transition-all"
            >
              <ProviderIcon provider={model.provider} size={24} />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm group-hover:text-primary transition-colors truncate">
                  {model.name}
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatProvider(model.provider)}
                </div>
              </div>
              <Badge variant="outline" className="text-xs shrink-0">
                View Results
              </Badge>
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
            </Link>
          ))}
        </div>
        {models.length === 1 && (
          <div className="mt-3">
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href={`/leaderboard/providers/${encodeURIComponent(models[0].provider)}`}>
                View all {formatProvider(models[0].provider)} models
              </Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
