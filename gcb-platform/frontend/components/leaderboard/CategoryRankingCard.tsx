"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { ProviderIcon } from "@/components/ui/provider-icon";
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

  return (
    <Link 
      href={`/categories/${encodeURIComponent(categoryCode.toLowerCase())}`}
      className="block rounded-lg border border-white/[0.08] bg-card overflow-hidden hover:border-white/[0.12] hover:bg-white/[0.02] transition-colors"
    >
      {/* Header */}
      <div className="p-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-foreground leading-tight">
            <span className="text-muted-foreground">{categoryCode}</span> {categoryName}
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
              <div
                key={`${model.model_id}-${index}`}
                className="flex items-center gap-2 py-1 px-1 -mx-1 rounded"
              >
                {/* Rank */}
                <span className="w-4 text-xs font-medium text-muted-foreground tabular-nums">
                  {index + 1}
                </span>

                {/* Provider icon */}
                <ProviderIcon provider={model.provider} size={16} />

                {/* Model name */}
                <span className="flex-1 text-sm text-foreground truncate">
                  {getDisplayModelName(model.model_name, model.model_id)}
                </span>

                {/* Score */}
                <span className={`text-sm font-medium tabular-nums ${getScoreColor(model.score)}`}>
                  {model.score.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/[0.06] flex items-center justify-between">
        {description ? (
          <p className="text-xs text-muted-foreground leading-relaxed flex-1">
            {description}
          </p>
        ) : (
          <span />
        )}
        {totalModels != null && totalModels > 0 && (
          <span className="text-xs text-muted-foreground/70 ml-2">
            {totalModels} models
          </span>
        )}
      </div>
    </Link>
  );
}
