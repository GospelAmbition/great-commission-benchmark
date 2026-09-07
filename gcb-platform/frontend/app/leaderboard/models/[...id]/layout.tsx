import type { Metadata } from "next";
import { generateModelMetadata, getBaseUrl } from "@/lib/seo";
import { buildSoftwareApplicationSchema, buildBreadcrumbSchema, JsonLdScript } from "@/lib/structured-data";
import { getModel, type ModelParams } from "../model-data";
import { getDisplayModelName } from "@/lib/model-utils";

export async function generateMetadata({
  params,
}: ModelParams): Promise<Metadata> {
  const { id } = await params;
  
  try {
    const model = await getModel(id.join("/"));
    const modelName = getDisplayModelName(model.model_name || model.name || "", model.model_id);
    if (model.is_active === false) {
      const title = `${modelName} - Archived Model`;
      const description = `${modelName} is archived on Great Commission Benchmark. Learn why and explore other reviewed models from its family and provider.`;
      const url = `${getBaseUrl()}/leaderboard/models/${encodeURIComponent(model.model_id)}`;
      return {
        title, description, alternates: { canonical: url },
        openGraph: { title, description, url },
        twitter: { card: "summary", title, description },
      };
    }
    
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
  params: Promise<{ id: string[] }>;
}) {
  const { id } = await params;
  
  try {
    const model = await getModel(id.join("/"));
    if (model.is_active === false) return <>{children}</>;
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
