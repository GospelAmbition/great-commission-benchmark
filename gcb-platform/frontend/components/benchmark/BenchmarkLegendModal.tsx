"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { HelpCircle } from "lucide-react";
import {
  TIER_CATEGORIES,
  CATEGORY_NAMES,
  CATEGORY_DESCRIPTIONS,
  TIER_INFO,
} from "@/lib/benchmark-definitions";

interface BenchmarkLegendModalProps {
  /** Optional: highlight a specific category code */
  highlightCategory?: string;
  /** Custom trigger element (defaults to HelpCircle button) */
  trigger?: React.ReactNode;
  /** Whether the modal is open (controlled mode) */
  open?: boolean;
  /** Callback when open state changes (controlled mode) */
  onOpenChange?: (open: boolean) => void;
}

export function BenchmarkLegendModal({
  highlightCategory,
  trigger,
  open,
  onOpenChange,
}: BenchmarkLegendModalProps) {
  const [internalOpen, setInternalOpen] = useState(false);

  // Support both controlled and uncontrolled modes
  const isOpen = open !== undefined ? open : internalOpen;
  const setIsOpen = onOpenChange || setInternalOpen;

  const defaultTrigger = (
    <Button
      variant="ghost"
      size="icon"
      className="h-6 w-6 text-muted-foreground hover:text-foreground"
      title="View benchmark categories"
    >
      <HelpCircle className="h-4 w-4" />
      <span className="sr-only">View benchmark categories</span>
    </Button>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{trigger || defaultTrigger}</DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl">GCB Benchmark Categories</DialogTitle>
          <DialogDescription>
            The Great Commission Benchmark evaluates AI models across 19 categories in 3 tiers,
            weighted to prioritize practical ministry utility.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-4">
          {/* Tier 1 */}
          <TierSection
            tierNumber={1}
            highlightCategory={highlightCategory}
          />

          {/* Tier 2 */}
          <TierSection
            tierNumber={2}
            highlightCategory={highlightCategory}
          />

          {/* Tier 3 */}
          <TierSection
            tierNumber={3}
            highlightCategory={highlightCategory}
          />

          {/* Score formula */}
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-2">
              <strong className="text-foreground">Score Formula:</strong>
            </p>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 font-mono text-sm text-center text-foreground">
              GCB Score = (Tier 1 × 0.70) + (Tier 2 × 0.20) + (Tier 3 × 0.10)
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface TierSectionProps {
  tierNumber: 1 | 2 | 3;
  highlightCategory?: string;
}

function TierSection({ tierNumber, highlightCategory }: TierSectionProps) {
  const tierInfo = TIER_INFO[tierNumber];
  const categories = TIER_CATEGORIES[tierNumber];

  const tierColors = {
    1: {
      badge: "bg-primary text-white hover:bg-primary",
      container: "bg-red-500/10 border-red-500/20",
      dot: "bg-primary",
    },
    2: {
      badge: "bg-amber-500 text-white hover:bg-amber-500",
      container: "bg-amber-500/10 border-amber-500/20",
      dot: "bg-amber-500",
    },
    3: {
      badge: "bg-blue-500 text-white hover:bg-blue-500",
      container: "bg-blue-500/10 border-blue-500/20",
      dot: "bg-blue-500",
    },
  };

  const colors = tierColors[tierNumber];

  return (
    <div className={`rounded-lg border p-4 ${colors.container}`}>
      <div className="flex items-center gap-2 mb-3">
        <Badge className={colors.badge}>{tierInfo.weightLabel}</Badge>
        <h3 className="font-semibold text-base">
          Tier {tierNumber}: {tierInfo.name}
        </h3>
      </div>
      <p className="text-sm text-muted-foreground mb-3">{tierInfo.description}</p>
      <div className="space-y-2">
        {categories.map((code) => {
          const isHighlighted = highlightCategory === code;
          return (
            <div
              key={code}
              className={`flex items-start gap-3 text-sm ${
                isHighlighted
                  ? "bg-yellow-500/20 -mx-2 px-2 py-1 rounded"
                  : ""
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${colors.dot}`}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2">
                  <code className="font-mono text-xs bg-white/10 text-foreground px-1.5 py-0.5 rounded">
                    {code}
                  </code>
                  <span className="font-medium text-foreground">
                    {CATEGORY_NAMES[code]}
                  </span>
                </div>
                {CATEGORY_DESCRIPTIONS[code] && (
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {CATEGORY_DESCRIPTIONS[code]}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Export a simple inline legend for use in charts
export function BenchmarkInlineLegend({ className }: { className?: string }) {
  return (
    <div className={`text-xs text-muted-foreground ${className || ""}`}>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        <span>
          <span className="font-medium">3.x</span> = Task Capability
        </span>
        <span>
          <span className="font-medium">4.x</span> = Gospel Core
        </span>
        <span>
          <span className="font-medium">5.x</span> = Worldview Confession
        </span>
      </div>
    </div>
  );
}
