/**
 * SEO Utility Functions
 * Centralized configuration and helpers for metadata, Open Graph, Twitter Cards, and canonical URLs
 */

import { Metadata } from "next";

// Base configuration
export const SITE_CONFIG = {
  name: "Great Commission Benchmark",
  shortName: "GCB",
  description: "Evaluating AI models on their ability to support Great Commission Christians—missionaries, evangelists, disciple-makers, and ministry workers.",
  url: process.env.NEXT_PUBLIC_SITE_URL || process.env.AUTH_URL || "https://greatcommissionbenchmark.ai",
  locale: "en_US",
  twitterHandle: "@gcbenchmark",
  githubUrl: "https://github.com/GospelAmbition/great-commission-benchmark",
  email: "contact@greatcommissionbenchmark.ai",
  keywords: [
    "AI benchmark",
    "Great Commission",
    "Christian AI",
    "LLM evaluation",
    "AI for ministry",
    "evangelism",
    "discipleship",
    "AI alignment",
    "missionary AI tools",
    "Christian technology",
  ],
};

// Default OG image dimensions
export const OG_IMAGE_SIZE = {
  width: 1200,
  height: 630,
};

/**
 * Generate the base URL for the site
 */
export function getBaseUrl(): string {
  return SITE_CONFIG.url;
}

/**
 * Generate a canonical URL for a given path
 */
export function getCanonicalUrl(path: string = ""): string {
  const baseUrl = getBaseUrl();
  // Ensure path starts with / if provided
  const normalizedPath = path && !path.startsWith("/") ? `/${path}` : path;
  // Remove trailing slashes except for root
  const cleanPath = normalizedPath === "/" ? "" : normalizedPath.replace(/\/$/, "");
  return `${baseUrl}${cleanPath}`;
}

/**
 * Generate default Open Graph metadata
 */
export function getDefaultOpenGraph(overrides?: {
  title?: string;
  description?: string;
  url?: string;
  images?: { url: string; width?: number; height?: number; alt?: string }[];
  type?: "website" | "article" | "profile";
}): Metadata["openGraph"] {
  const defaultImage = {
    url: `${getBaseUrl()}/og-image.png`,
    width: OG_IMAGE_SIZE.width,
    height: OG_IMAGE_SIZE.height,
    alt: SITE_CONFIG.name,
  };

  return {
    type: overrides?.type || "website",
    locale: SITE_CONFIG.locale,
    siteName: SITE_CONFIG.name,
    title: overrides?.title || SITE_CONFIG.name,
    description: overrides?.description || SITE_CONFIG.description,
    url: overrides?.url || getBaseUrl(),
    images: overrides?.images || [defaultImage],
  };
}

/**
 * Generate default Twitter Card metadata
 */
export function getDefaultTwitterCard(overrides?: {
  title?: string;
  description?: string;
  images?: string[];
  card?: "summary" | "summary_large_image";
}): Metadata["twitter"] {
  return {
    card: overrides?.card || "summary_large_image",
    site: SITE_CONFIG.twitterHandle,
    creator: SITE_CONFIG.twitterHandle,
    title: overrides?.title || SITE_CONFIG.name,
    description: overrides?.description || SITE_CONFIG.description,
    images: overrides?.images || [`${getBaseUrl()}/og-image.png`],
  };
}

/**
 * Generate page-specific metadata with all required SEO elements
 */
export function generatePageMetadata({
  title,
  description,
  path = "",
  keywords = [],
  noIndex = false,
  openGraph,
  twitter,
  additionalMeta = {},
}: {
  title: string;
  description: string;
  path?: string;
  keywords?: string[];
  noIndex?: boolean;
  openGraph?: Partial<NonNullable<Metadata["openGraph"]>>;
  twitter?: Partial<NonNullable<Metadata["twitter"]>>;
  additionalMeta?: Partial<Metadata>;
}): Metadata {
  const canonicalUrl = getCanonicalUrl(path);
  const fullTitle = title.includes(SITE_CONFIG.name) ? title : `${title} | ${SITE_CONFIG.name}`;
  const allKeywords = [...SITE_CONFIG.keywords, ...keywords];

  return {
    title: fullTitle,
    description,
    keywords: allKeywords,
    authors: [{ name: SITE_CONFIG.name }],
    creator: SITE_CONFIG.name,
    publisher: SITE_CONFIG.name,
    robots: noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true, googleBot: { index: true, follow: true } },
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: getDefaultOpenGraph({
      title: fullTitle,
      description,
      url: canonicalUrl,
      ...openGraph,
    }),
    twitter: getDefaultTwitterCard({
      title: fullTitle,
      description,
      ...twitter,
    }),
    ...additionalMeta,
  };
}

/**
 * Generate metadata for model detail pages
 */
export function generateModelMetadata({
  modelName,
  modelId,
  provider,
  score,
  description,
  tier1Score,
  tier2Score,
  tier3Score,
}: {
  modelName: string;
  modelId: string;
  provider: string;
  score: number;
  description?: string;
  tier1Score?: number;
  tier2Score?: number;
  tier3Score?: number;
}): Metadata {
  const verdict = getScoreVerdict(score);
  const pageDescription = description || 
    `${modelName} by ${provider} scored ${score.toFixed(1)}% on the Great Commission Benchmark. ${verdict} for Great Commission ministry work. Task: ${tier1Score?.toFixed(0) || "N/A"}%, Gospel: ${tier2Score?.toFixed(0) || "N/A"}%, Worldview: ${tier3Score?.toFixed(0) || "N/A"}%.`;
  
  return generatePageMetadata({
    title: `${modelName} - AI Model Benchmark Results`,
    description: pageDescription,
    path: `/leaderboard/models/${encodeURIComponent(modelId)}`,
    keywords: [modelName, provider, "AI benchmark", "LLM evaluation", "model score"],
    openGraph: {
      type: "article",
    },
  });
}

/**
 * Generate metadata for category pages
 */
export function generateCategoryMetadata({
  categoryName,
  categoryCode,
  tier,
  description,
}: {
  categoryName: string;
  categoryCode: string;
  tier: number;
  description?: string;
}): Metadata {
  const tierLabel = tier === 1 ? "Task Capability" : tier === 2 ? "Gospel Core" : "Worldview Confession";
  const pageDescription = description ||
    `Benchmark results for ${categoryName} (Tier ${tier}: ${tierLabel}). Compare how AI models perform on this category in the Great Commission Benchmark.`;

  return generatePageMetadata({
    title: `${categoryName} - Category Results`,
    description: pageDescription,
    path: `/categories/${categoryCode}`,
    keywords: [categoryName, tierLabel, "benchmark category", "AI evaluation"],
  });
}

/**
 * Generate metadata for insight/article pages
 */
export function generateInsightMetadata({
  title,
  excerpt,
  slug,
  publishedAt,
  author,
  imageUrl,
}: {
  title: string;
  excerpt: string;
  slug: string;
  publishedAt?: string;
  author?: string;
  imageUrl?: string;
}): Metadata {
  return generatePageMetadata({
    title,
    description: excerpt,
    path: `/insights/${slug}`,
    keywords: ["AI insights", "benchmark analysis", "Great Commission"],
    openGraph: {
      type: "article",
      images: imageUrl ? [{ url: imageUrl, alt: title }] : undefined,
    },
    additionalMeta: publishedAt ? {
      other: {
        "article:published_time": publishedAt,
        "article:author": author || SITE_CONFIG.name,
      },
    } : {},
  });
}

/**
 * Generate metadata for user profile pages
 */
export function generateProfileMetadata({
  username,
  displayName,
  testCount,
}: {
  username: string;
  displayName?: string;
  testCount?: number;
}): Metadata {
  const name = displayName || username;
  const description = testCount
    ? `${name}'s profile on the Great Commission Benchmark. ${testCount} benchmark tests contributed.`
    : `${name}'s profile on the Great Commission Benchmark.`;

  return generatePageMetadata({
    title: `${name} - Contributor Profile`,
    description,
    path: `/profile/${username}`,
    openGraph: {
      type: "profile",
    },
  });
}

/**
 * Get score verdict label
 */
export function getScoreVerdict(score: number): string {
  if (score >= 80) return "Excellent";
  if (score >= 61) return "Good";
  if (score >= 40) return "Fair";
  return "Poor";
}

/**
 * Get score verdict description
 */
export function getScoreVerdictDescription(score: number): string {
  if (score >= 80) return "Highly suitable for Great Commission work";
  if (score >= 61) return "Usable with some limitations";
  if (score >= 40) return "Significant guardrail issues may impede work";
  return "Not recommended for Great Commission use cases";
}

/**
 * Truncate text to a maximum length while preserving word boundaries
 */
export function truncateDescription(text: string, maxLength: number = 160): string {
  if (text.length <= maxLength) return text;
  const truncated = text.substring(0, maxLength - 3);
  const lastSpace = truncated.lastIndexOf(" ");
  return `${truncated.substring(0, lastSpace)}...`;
}
