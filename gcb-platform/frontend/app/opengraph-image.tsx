/**
 * Default Open Graph Image
 * 
 * Note: For dynamic image generation, install @vercel/og:
 *   npm install @vercel/og
 * 
 * Then uncomment the ImageResponse code below and remove the static image reference.
 * 
 * For now, this file serves as a placeholder. Create a static og-image.png
 * file in the public directory (1200x630px) and reference it in metadata.
 */

import { SITE_CONFIG } from "@/lib/seo";

export const alt = SITE_CONFIG.name;
export const size = {
  width: 1200,
  height: 630,
};

export const contentType = "image/png";

// Static image approach - create public/og-image.png (1200x630px)
// For dynamic generation, install @vercel/og and use ImageResponse:
/*
import { ImageResponse } from "@vercel/og";

export default async function Image() {
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
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 20,
            padding: 40,
          }}
        >
          <div
            style={{
              fontSize: 72,
              fontWeight: "bold",
              background: "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent",
              textAlign: "center",
            }}
          >
            {SITE_CONFIG.name}
          </div>
          <div
            style={{
              fontSize: 32,
              color: "#a3a3a3",
              textAlign: "center",
              maxWidth: 900,
            }}
          >
            {SITE_CONFIG.description}
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
*/

// Placeholder - Next.js will look for opengraph-image.png in the same directory
// or use the metadata openGraph.image setting
export default function Image() {
  // This will be handled by Next.js metadata or a static image file
  return null;
}
