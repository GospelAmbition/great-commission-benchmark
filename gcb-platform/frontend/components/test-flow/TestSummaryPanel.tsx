"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface TestSummaryPanelProps {
  provider?: string;
  modelName?: string;
  modelId?: string;
  version?: string;
  questionCount?: number;
  tierCount?: number;
  categoryCount?: number;
  estimatedTime?: string;
  estimatedCost?: number;
  className?: string;
}

export function TestSummaryPanel({
  provider,
  modelName,
  modelId,
  version,
  questionCount = 300,
  tierCount = 3,
  categoryCount = 19,
  estimatedTime = "5-10 min",
  estimatedCost,
  className,
}: TestSummaryPanelProps) {
  const hasSelection = provider || modelName;

  return (
    <Card className={cn("sticky top-4", className)}>
      <CardHeader>
        <CardTitle className="text-lg">Test Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Selection info */}
        <div className="space-y-3">
          <div>
            <div className="text-sm text-muted-foreground mb-1">Provider</div>
            <div className="font-medium">
              {provider || <span className="text-muted-foreground">—</span>}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-muted-foreground mb-1">Model</div>
            <div className="font-medium">
              {modelName || <span className="text-muted-foreground">—</span>}
            </div>
            {modelId && (
              <div className="text-xs text-muted-foreground mt-0.5 font-mono">
                {modelId}
              </div>
            )}
          </div>
          
          <div>
            <div className="text-sm text-muted-foreground mb-1">Version</div>
            <div className="font-medium flex items-center gap-2">
              {version || <span className="text-muted-foreground">—</span>}
              {version && (
                <Badge variant="outline" className="text-xs">
                  Current
                </Badge>
              )}
            </div>
          </div>
        </div>

        <Separator />

        {/* Test details */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Questions</span>
            <span className="font-medium">{questionCount}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tiers</span>
            <span className="font-medium">{tierCount}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Categories</span>
            <span className="font-medium">{categoryCount}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Est. Time</span>
            <span className="font-medium">{estimatedTime}</span>
          </div>
        </div>

        {/* Cost estimate */}
        {estimatedCost !== undefined && estimatedCost > 0 && (
          <>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Est. Cost</span>
              <div className="text-right">
                <div className="text-xl font-bold">${estimatedCost.toFixed(2)}</div>
                <Badge variant="secondary" className="text-xs">
                  Approximate
                </Badge>
              </div>
            </div>
          </>
        )}

        {/* Empty state hint */}
        {!hasSelection && (
          <div className="text-center py-4 text-sm text-muted-foreground">
            Select a provider and model to see test details
          </div>
        )}
      </CardContent>
    </Card>
  );
}

