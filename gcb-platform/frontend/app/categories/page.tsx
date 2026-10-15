import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { CategoryRankingCard, type CategoryModel } from "@/components/leaderboard";
import { CategoriesHeader } from "./categories-header";
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

async function loadCategoryRankings(): Promise<Record<string, CategoryRankingData>> {
  const rankingsMap: Record<string, CategoryRankingData> = {};
  try {
    // Use the optimized single-request endpoint instead of 19 parallel calls
    const response = await apiClient.getCategoryRankings({ limit_per_category: 5 });
    for (const categoryCode of getAllCategoryCodes()) {
      const categoryData = response.categories[categoryCode];
      rankingsMap[categoryCode] = {
        categoryCode,
        models: (categoryData?.models || []).map((m) => ({
          model_id: m.model_id,
          model_name: m.model_name,
          provider: m.provider,
          score: m.score,
        })),
        totalModels: categoryData?.total_models || 0,
      };
    }
  } catch (error) {
    console.error("Failed to load category rankings:", error);
  }
  return rankingsMap;
}

// Render per request so data is never frozen at build time.
export const dynamic = "force-dynamic";

export default async function CategoriesPage() {
  const categoryRankings = await loadCategoryRankings();

  return (
    <div className="flex flex-col">
      <CategoriesHeader />

      <div className="container py-6 space-y-6">
        <>
            {/* Tier 1: Task Capability */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl md:text-3xl font-bold text-foreground">Task Capability</h2>
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
            <div className="mt-8">
              <hr className="border-white/[0.08] mb-6" />
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl md:text-3xl font-bold text-foreground">Gospel Core</h2>
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
            <div className="mt-8">
              <hr className="border-white/[0.08] mb-6" />
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl md:text-3xl font-bold text-foreground">Worldview Confession</h2>
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
