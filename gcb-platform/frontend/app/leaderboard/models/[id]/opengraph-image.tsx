/**
 * Dynamic Open Graph Image Generator for Model Pages
 * 
 * Note: For dynamic image generation, install @vercel/og:
 *   npm install @vercel/og
 * 
 * Then uncomment the ImageResponse code below.
 * 
 * For now, model pages will use the default OG image or can reference
 * a static image in the metadata.
 */

import { apiClient } from "@/lib/api";
import { getDisplayModelName } from "@/lib/model-utils";
import { getScoreVerdict } from "@/lib/seo";

export const alt = "Model Benchmark Results";
export const size = {
  width: 1200,
  height: 630,
};

export const contentType = "image/png";

// For dynamic generation, install @vercel/og and use ImageResponse:
/*
import { ImageResponse } from "@vercel/og";

export default async function Image({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  
  try {
    const model = await apiClient.getModel(id);
    const modelName = getDisplayModelName(model.model_name || model.name || "", model.model_id);
    const score = model.overall_score || model.score || 0;
    const verdict = getScoreVerdict(score);
    
    // Color based on score
    let scoreColor = "#dc2626"; // red
    if (score >= 80) scoreColor = "#10b981"; // green
    else if (score >= 61) scoreColor = "#3b82f6"; // blue
    else if (score >= 40) scoreColor = "#f59e0b"; // amber
    
    return new ImageResponse(
      (
        <div
          style={{
            fontSize: 60,
            background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)",
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontFamily: "Inter, sans-serif",
            padding: 60,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 30,
              width: "100%",
            }}
          >
            <div
              style={{
                fontSize: 48,
                color: "#a3a3a3",
                marginBottom: 10,
              }}
            >
              Great Commission Benchmark
            </div>
            <div
              style={{
                fontSize: 64,
                fontWeight: "bold",
                textAlign: "center",
                maxWidth: 1000,
                marginBottom: 20,
              }}
            >
              {modelName}
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 40,
                marginTop: 20,
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <div
                  style={{
                    fontSize: 32,
                    color: "#a3a3a3",
                  }}
                >
                  Score
                </div>
                <div
                  style={{
                    fontSize: 96,
                    fontWeight: "bold",
                    color: scoreColor,
                  }}
                >
                  {score.toFixed(1)}%
                </div>
              </div>
              <div
                style={{
                  width: 2,
                  height: 120,
                  background: "#333",
                }}
              />
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <div
                  style={{
                    fontSize: 32,
                    color: "#a3a3a3",
                  }}
                >
                  Verdict
                </div>
                <div
                  style={{
                    fontSize: 48,
                    fontWeight: "bold",
                    color: scoreColor,
                  }}
                >
                  {verdict}
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
      {
        ...size,
      }
    );
  } catch (error) {
    // Fallback to default
    return null;
  }
}
*/

// Placeholder - will use default OG image or metadata setting
export default async function Image({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // This will be handled by Next.js metadata or fallback to default image
  return null;
}
