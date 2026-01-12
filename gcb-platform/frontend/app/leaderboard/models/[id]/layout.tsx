import type { Metadata } from "next";
import { generateModelMetadata } from "@/lib/seo";
import { buildSoftwareApplicationSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { apiClient } from "@/lib/api";
import { getDisplayModelName } from "@/lib/model-utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  
  try {
    const model = await apiClient.getModel(id);
    const modelName = getDisplayModelName(model.model_name || model.name || "", model.model_id);
    
    return generateModelMetadata({
      modelName,
      modelId: model.model_id,
      provider: model.provider,
      score: model.overall_score || model.score || 0,
      description: model.description,
      tier1Score: model.tier1_score,
      tier2Score: model.tier2_score,
      tier3Score: model.tier3_score,
    });
  } catch {
    // Fallback metadata if model fetch fails
    return {
      title: "Model Details",
      description: "View detailed benchmark results for this AI model.",
    };
  }
}

export default async function ModelLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  
  try {
    const model = await apiClient.getModel(id);
    const modelName = getDisplayModelName(model.model_name || model.name || "", model.model_id);
    const overallScore = model.overall_score || model.score || 0;
    
    const softwareSchema = buildSoftwareApplicationSchema({
      name: modelName,
      modelId: model.model_id,
      provider: model.provider,
      description: model.description,
      score: overallScore,
      testCount: model.test_count,
    });
    
    const breadcrumbSchema = buildBreadcrumbSchema([
      { name: "Home", path: "/" },
      { name: "Leaderboard", path: "/leaderboard" },
      { name: modelName, path: `/leaderboard/models/${encodeURIComponent(model.model_id)}` },
    ]);
    
    return (
      <>
        <JsonLdScript data={[softwareSchema, breadcrumbSchema]} />
        {children}
      </>
    );
  } catch {
    return <>{children}</>;
  }
}
