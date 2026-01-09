"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Grid3X3 } from "lucide-react";
import { CategoryRankingCard, type CategoryModel } from "@/components/leaderboard";
import {
  TIER_CATEGORIES,
  CATEGORY_NAMES,
  CATEGORY_DESCRIPTIONS,
} from "@/lib/benchmark-definitions";

interface CategoryRankingData {
  categoryCode: string;
  models: CategoryModel[];
  totalModels: number;
}

// Get all category codes in order
function getAllCategoryCodes(): string[] {
  return [
    ...TIER_CATEGORIES[1],
    ...TIER_CATEGORIES[2],
    ...TIER_CATEGORIES[3],
  ];
}

export default function CategoriesPage() {
  const [categoryRankings, setCategoryRankings] = useState<Record<string, CategoryRankingData>>({});
  const [loading, setLoading] = useState(true);

  const loadCategoryRankings = useCallback(async () => {
    setLoading(true);
    try {
      // Use the optimized single-request endpoint instead of 19 parallel calls
      const response = await apiClient.getCategoryRankings({ limit_per_category: 5 });
      
      // Transform response to match expected format
      const rankingsMap: Record<string, CategoryRankingData> = {};
      const allCategories = getAllCategoryCodes();
      
      for (const categoryCode of allCategories) {
        const categoryData = response.categories[categoryCode];
        if (categoryData) {
          rankingsMap[categoryCode] = {
            categoryCode,
            models: categoryData.models.map((m) => ({
              model_id: m.model_id,
              model_name: m.model_name,
              provider: m.provider,
              score: m.score,
            })),
            totalModels: categoryData.total_models,
          };
        } else {
          rankingsMap[categoryCode] = {
            categoryCode,
            models: [],
            totalModels: 0,
          };
        }
      }
      
      setCategoryRankings(rankingsMap);
    } catch (error) {
      console.error("Failed to load category rankings:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategoryRankings();
  }, [loadCategoryRankings]);

  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-20" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <Grid3X3 className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Categories</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl">
            Browse benchmark categories and see how AI models perform in each area of ministry and theological understanding
          </p>
        </div>
      </div>

      <div className="container py-6 space-y-6">
        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        ) : (
          <>
            {/* Tier 1: Task Capability */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <h2 className="text-lg font-semibold text-foreground">Task Capability</h2>
                <Badge variant="outline" className="bg-red-500/10 text-red-400 border-transparent">
                  70% weight
                </Badge>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {TIER_CATEGORIES[1].map((categoryCode) => {
                  const data = categoryRankings[categoryCode];
                  return (
                    <CategoryRankingCard
                      key={categoryCode}
                      categoryCode={categoryCode}
                      categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                      description={CATEGORY_DESCRIPTIONS[categoryCode]}
                      tier={1}
                      models={data?.models || []}
                      totalModels={data?.totalModels}
                    />
                  );
                })}
              </div>
            </div>

            {/* Tier 2: Gospel Core */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <h2 className="text-lg font-semibold text-foreground">Gospel Core</h2>
                <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-transparent">
                  20% weight
                </Badge>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {TIER_CATEGORIES[2].map((categoryCode) => {
                  const data = categoryRankings[categoryCode];
                  return (
                    <CategoryRankingCard
                      key={categoryCode}
                      categoryCode={categoryCode}
                      categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                      description={CATEGORY_DESCRIPTIONS[categoryCode]}
                      tier={2}
                      models={data?.models || []}
                      totalModels={data?.totalModels}
                    />
                  );
                })}
              </div>
            </div>

            {/* Tier 3: Worldview Confession */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <h2 className="text-lg font-semibold text-foreground">Worldview Confession</h2>
                <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-transparent">
                  10% weight
                </Badge>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {TIER_CATEGORIES[3].map((categoryCode) => {
                  const data = categoryRankings[categoryCode];
                  return (
                    <CategoryRankingCard
                      key={categoryCode}
                      categoryCode={categoryCode}
                      categoryName={CATEGORY_NAMES[categoryCode] || categoryCode}
                      description={CATEGORY_DESCRIPTIONS[categoryCode]}
                      tier={3}
                      models={data?.models || []}
                      totalModels={data?.totalModels}
                    />
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* Disclaimer */}
        <div className="flex items-start gap-3 p-3 bg-white/[0.02] rounded-lg border border-white/[0.06]">
          <p className="text-xs text-muted-foreground/70 leading-relaxed">
            <span className="font-medium text-muted-foreground">Disclaimer:</span> This benchmark is for informational purposes only and does not 
            constitute an endorsement or recommendation of any AI model or service. Results reflect 
            performance on specific test questions at a point in time and may not predict performance 
            on other tasks or future model versions.
          </p>
        </div>
      </div>
    </div>
  );
}
