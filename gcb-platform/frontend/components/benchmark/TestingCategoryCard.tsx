"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TIER_INFO, type TierInfo } from "@/lib/benchmark-definitions";

export interface TestingCategoryCardProps {
  categoryCode: string;
  categoryName: string;
  description: string;
  tier: number;
  guardrails: string[];
}

export function TestingCategoryCard({
  categoryCode,
  categoryName,
  description,
  tier,
  guardrails,
}: TestingCategoryCardProps) {
  const tierInfo: TierInfo | undefined = TIER_INFO[tier];

  return (
    <Card className="flex flex-col h-full border-white/[0.08] hover:border-white/[0.12] transition-colors">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base font-semibold leading-tight">
            <span className="text-muted-foreground">{categoryCode}</span> {categoryName}
          </CardTitle>
          {tierInfo && (
            <Badge
              variant="outline"
              className={`${tierInfo.bgColor} ${tierInfo.color} border-transparent text-[10px] shrink-0`}
            >
              {tierInfo.shortName}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4 pt-0">
        <p className="text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>
        <div className="mt-auto">
          <p className="text-xs font-medium text-foreground mb-2">Guardrails Tested:</p>
          <div className="space-y-1.5">
            {guardrails.map((guardrail, index) => (
              <div
                key={index}
                className="text-xs text-muted-foreground/80 bg-white/[0.02] border border-white/[0.06] rounded px-2.5 py-1.5"
              >
                {guardrail}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
