import { ImageResponse } from "@vercel/og";

// Route segment config
export const runtime = "edge";

// Image metadata
export const size = {
  width: 32,
  height: 32,
};
export const contentType = "image/png";

// Image generation - Create a simple GCB icon with a cross/checkmark symbol
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 20,
          background: "linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%)",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "6px",
          color: "white",
          fontWeight: "bold",
        }}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {/* Cross symbol representing Great Commission */}
          <line x1="12" y1="4" x2="12" y2="20" />
          <line x1="5" y1="9" x2="19" y2="9" />
        </svg>
      </div>
    ),
    {
      ...size,
    }
  );
}
