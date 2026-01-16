import { ImageResponse } from "@vercel/og";
import { SITE_CONFIG, OG_IMAGE_SIZE, getBaseUrl } from "@/lib/seo";

// Route segment config
export const runtime = "edge";

// Image metadata
export const alt = "Great Commission Benchmark - Evaluating AI for Ministry";
export const size = OG_IMAGE_SIZE;
export const contentType = "image/png";

// Default OG image generation
export default async function OGImage() {
  // Fetch the logo image
  const logoUrl = `${getBaseUrl()}/logo.png`;
  
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#0a0a0a",
          backgroundImage:
            "radial-gradient(circle at 25% 25%, #1a0a0a 0%, transparent 50%), radial-gradient(circle at 75% 75%, #0a1a1a 0%, transparent 50%)",
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "40px",
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={logoUrl}
            alt="GCB Logo"
            width={140}
            height={140}
            style={{
              borderRadius: "24px",
            }}
          />
        </div>

        {/* Title */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <h1
            style={{
              fontSize: "64px",
              fontWeight: "bold",
              color: "white",
              margin: "0 0 20px 0",
              textAlign: "center",
              letterSpacing: "-1px",
            }}
          >
            {SITE_CONFIG.name}
          </h1>
          <p
            style={{
              fontSize: "28px",
              color: "#a3a3a3",
              margin: "0",
              textAlign: "center",
              maxWidth: "800px",
              lineHeight: "1.4",
            }}
          >
            Evaluating AI for the Great Commission
          </p>
        </div>

        {/* Three tier indicators */}
        <div
          style={{
            display: "flex",
            gap: "40px",
            marginTop: "60px",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "20px 40px",
              backgroundColor: "rgba(185, 28, 28, 0.1)",
              borderRadius: "12px",
              border: "1px solid rgba(185, 28, 28, 0.3)",
            }}
          >
            <span style={{ color: "#b91c1c", fontSize: "24px", fontWeight: "bold" }}>
              Tier 1
            </span>
            <span style={{ color: "#737373", fontSize: "16px", marginTop: "4px" }}>
              Task Capability
            </span>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "20px 40px",
              backgroundColor: "rgba(185, 28, 28, 0.1)",
              borderRadius: "12px",
              border: "1px solid rgba(185, 28, 28, 0.3)",
            }}
          >
            <span style={{ color: "#b91c1c", fontSize: "24px", fontWeight: "bold" }}>
              Tier 2
            </span>
            <span style={{ color: "#737373", fontSize: "16px", marginTop: "4px" }}>
              Gospel Core
            </span>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "20px 40px",
              backgroundColor: "rgba(185, 28, 28, 0.1)",
              borderRadius: "12px",
              border: "1px solid rgba(185, 28, 28, 0.3)",
            }}
          >
            <span style={{ color: "#b91c1c", fontSize: "24px", fontWeight: "bold" }}>
              Tier 3
            </span>
            <span style={{ color: "#737373", fontSize: "16px", marginTop: "4px" }}>
              Worldview
            </span>
          </div>
        </div>

        {/* URL */}
        <div
          style={{
            position: "absolute",
            bottom: "40px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span style={{ color: "#737373", fontSize: "20px" }}>
            greatcommissionbenchmark.ai
          </span>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
