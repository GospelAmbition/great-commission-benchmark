import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  // Prevent double _next in asset URLs (can occur with encoded slashes in path or proxy config)
  basePath: "",
  assetPrefix: "",
  async rewrites() {
    return [
      // Fix erroneous /_next/_next/* requests → serve from /_next/*
      { source: "/_next/_next/:path*", destination: "/_next/:path*" },
    ];
  },
  images: {
    remotePatterns: [
      // Production backend (custom domain)
      {
        protocol: "https",
        hostname: "api.greatcommissionbenchmark.ai",
        pathname: "/api/files/**",
      },
      // Production backend (Railway URL - fallback)
      {
        protocol: "https",
        hostname: "backend-production-ba51.up.railway.app",
        pathname: "/api/files/**",
      },
      // Local development (backend on 8001)
      {
        protocol: "http",
        hostname: "localhost",
        port: "8001",
        pathname: "/api/files/**",
      },
    ],
  },
  async headers() {
    return [
      // Ensure CSS is served with correct MIME type (fixes text/plain on some hosts/CDNs)
      {
        source: "/_next/static/chunks/:file(.+\\.css)",
        headers: [
          { key: "Content-Type", value: "text/css; charset=utf-8" },
        ],
      },
      {
        source: "/_next/static/css/:file(.+\\.css)",
        headers: [
          { key: "Content-Type", value: "text/css; charset=utf-8" },
        ],
      },
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "geolocation=(), microphone=(), camera=()",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
