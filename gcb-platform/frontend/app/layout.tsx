import type { Metadata, Viewport } from "next";
import Script from "next/script";
import { SessionProvider } from "@/components/providers/SessionProvider";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { UmamiAnalytics } from "@/components/analytics/UmamiAnalytics";
import { SITE_CONFIG, getBaseUrl, getDefaultOpenGraph, getDefaultTwitterCard } from "@/lib/seo";
import { buildOrganizationSchema, buildWebsiteSchema, JsonLdScript } from "@/lib/structured-data";
import "./globals.css";

const baseUrl = getBaseUrl();

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: {
    default: "Evaluating AI for the Great Commission",
    template: `%s | ${SITE_CONFIG.name}`,
  },
  description: "Which AI models will actually help you make disciples? We measure task capability, gospel core fidelity, and worldview alignment. Compare AI models on the Great Commission Benchmark.",
  keywords: SITE_CONFIG.keywords,
  authors: [{ name: SITE_CONFIG.name, url: baseUrl }],
  creator: SITE_CONFIG.name,
  publisher: SITE_CONFIG.name,
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: baseUrl,
    types: {
      "application/rss+xml": [{ url: "/feed.xml", title: "Great Commission Benchmark RSS Feed" }],
    },
  },
  openGraph: getDefaultOpenGraph(),
  twitter: getDefaultTwitterCard(),
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/android-chrome-192x192.png", sizes: "192x192", type: "image/png" },
      { url: "/android-chrome-512x512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
  },
  manifest: "/manifest.json",
  category: "technology",
  classification: "AI Benchmark",
  referrer: "origin-when-cross-origin",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  other: {
    "msapplication-TileColor": "#b91c1c",
    "theme-color": "#0a0a0a",
    "application-name": SITE_CONFIG.name,
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "black-translucent",
    "mobile-web-app-capable": "yes",
    ...(process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION && {
      "google-site-verification": process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
    }),
    ...(process.env.NEXT_PUBLIC_BING_VERIFICATION && {
      "msvalidate.01": process.env.NEXT_PUBLIC_BING_VERIFICATION,
    }),
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const organizationSchema = buildOrganizationSchema();
  const websiteSchema = buildWebsiteSchema();

  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600&display=swap"
          rel="stylesheet"
        />
        {/* DNS prefetch for external resources */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//fonts.gstatic.com" />
        {/* Structured Data - Organization and Website schemas */}
        <JsonLdScript data={[organizationSchema, websiteSchema]} />
      </head>
      <body className="antialiased font-sans bg-background text-foreground">
        <SessionProvider>
          {/* Skip to main content link for accessibility */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-red-700 focus:text-white focus:rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-700"
          >
            Skip to main content
          </a>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main id="main-content" className="flex-1" role="main" tabIndex={-1}>
              {children}
            </main>
            <Footer />
          </div>
          <Toaster />
          <UmamiAnalytics />
          {process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY && (
            <Script
              src={`https://www.google.com/recaptcha/api.js?render=${process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY}`}
              strategy="afterInteractive"
            />
          )}
        </SessionProvider>
      </body>
    </html>
  );
}
