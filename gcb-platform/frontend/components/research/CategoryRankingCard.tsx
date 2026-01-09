"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { TIER_INFO, type TierInfo } from "@/lib/benchmark-definitions";
import { formatProvider, getDisplayModelName } from "@/lib/model-utils";

export interface CategoryModel {
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

export interface CategoryRankingCardProps {
  categoryCode: string;
  categoryName: string;
  description?: string;
  tier: number;
  models: CategoryModel[];
  totalModels?: number;
}

// Get score color based on value
function getScoreColor(score: number): string {
  if (score >= 75) return "text-emerald-400";
  if (score >= 50) return "text-amber-400";
  return "text-red-400";
}

export function CategoryRankingCard({
  categoryCode,
  categoryName,
  description,
  tier,
  models,
  totalModels,
}: CategoryRankingCardProps) {
  const tierInfo: TierInfo | undefined = TIER_INFO[tier];
  const modelCount = totalModels ?? models.length;

  return (
    <div className="rounded-lg border border-white/[0.08] bg-card overflow-hidden hover:border-white/[0.12] transition-colors">
      {/* Header */}
      <div className="p-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-semibold text-foreground leading-tight">
            {categoryName}
          </h3>
          {tierInfo && (
            <Badge
              variant="outline"
              className={`${tierInfo.bgColor} ${tierInfo.color} border-transparent text-[10px] shrink-0`}
            >
              {tierInfo.shortName}
            </Badge>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {description}
          </p>
        )}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-xs text-muted-foreground">
            {modelCount} model{modelCount !== 1 ? "s" : ""}
          </span>
          <span className="text-muted-foreground/50">•</span>
          <span className="text-xs text-muted-foreground">Text</span>
        </div>
      </div>

      {/* Model Rankings */}
      <div className="p-3">
        {models.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">
            No models tested yet
          </p>
        ) : (
          <div className="space-y-1.5">
            {models.slice(0, 5).map((model, index) => (
              <Link
                key={`${model.model_id}-${index}`}
                href={`/research/models/${encodeURIComponent(model.model_id)}`}
                className="group flex items-center gap-2 py-1 px-1 -mx-1 rounded hover:bg-white/[0.04] transition-colors"
              >
                {/* Rank */}
                <span className="w-4 text-xs font-medium text-muted-foreground tabular-nums">
                  {index + 1}
                </span>

                {/* Provider icon placeholder - simple letter badge */}
                <div className="w-5 h-5 rounded bg-white/[0.08] flex items-center justify-center shrink-0">
                  <span className="text-[10px] font-medium text-muted-foreground uppercase">
                    {model.provider.charAt(0)}
                  </span>
                </div>

                {/* Model name */}
                <span className="flex-1 text-sm text-foreground truncate group-hover:text-primary transition-colors">
                  {getDisplayModelName(model.model_name, model.model_id)}
                </span>

                {/* Score */}
                <span className={`text-sm font-medium tabular-nums ${getScoreColor(model.score)}`}>
                  {model.score.toFixed(1)}
                </span>
              </Link>
            ))}
          </div>
        )}

        {/* View more link */}
        {models.length > 0 && (
          <Link
            href={`/research/category/${encodeURIComponent(categoryCode)}`}
            className="block text-xs text-muted-foreground hover:text-primary mt-3 pt-2 border-t border-white/[0.06] transition-colors"
          >
            +{Math.max(0, modelCount - 5)} more
          </Link>
        )}
      </div>
    </div>
  );
}
