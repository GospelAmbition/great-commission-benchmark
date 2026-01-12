/**
 * Structured Data Builders (JSON-LD)
 * Schema.org markup for enhanced search engine understanding
 */

import React from "react";
import { SITE_CONFIG, getBaseUrl, getCanonicalUrl } from "./seo";

// Type definitions for JSON-LD schemas
type JsonLd = Record<string, unknown>;

/**
 * Organization Schema
 * Used for site-wide organization identity
 */
export function buildOrganizationSchema(): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE_CONFIG.name,
    alternateName: SITE_CONFIG.shortName,
    description: SITE_CONFIG.description,
    url: getBaseUrl(),
    logo: `${getBaseUrl()}/og-image.png`,
    image: `${getBaseUrl()}/og-image.png`,
    email: SITE_CONFIG.email,
    sameAs: [
      SITE_CONFIG.githubUrl,
    ],
    foundingDate: "2024",
    areaServed: "Global",
    knowsAbout: [
      "AI Benchmarking",
      "Large Language Models",
      "Great Commission",
      "Christian Ministry",
      "AI Safety",
      "AI Alignment",
      "Evangelism",
      "Discipleship",
    ],
  };
}

/**
 * Website Schema
 * Used for site-wide website identity
 */
export function buildWebsiteSchema(): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE_CONFIG.name,
    alternateName: SITE_CONFIG.shortName,
    description: SITE_CONFIG.description,
    url: getBaseUrl(),
    publisher: {
      "@type": "Organization",
      name: SITE_CONFIG.name,
    },
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${getBaseUrl()}/leaderboard?search={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };
}

/**
 * Dataset Schema
 * Used for benchmark data description
 */
export function buildDatasetSchema(options?: {
  version?: string;
  totalModels?: number;
  lastUpdated?: string;
}): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "Great Commission Benchmark Dataset",
    description: "Benchmark evaluation results measuring how well AI language models support Great Commission ministry work. Tests task capability, gospel core fidelity, and worldview alignment.",
    url: `${getBaseUrl()}/leaderboard`,
    creator: {
      "@type": "Organization",
      name: SITE_CONFIG.name,
      url: getBaseUrl(),
    },
    license: "https://creativecommons.org/licenses/by/4.0/",
    isAccessibleForFree: true,
    keywords: SITE_CONFIG.keywords,
    version: options?.version || "1.0",
    temporalCoverage: options?.lastUpdated ? `2024/${options.lastUpdated.substring(0, 4)}` : "2024/..",
    variableMeasured: [
      {
        "@type": "PropertyValue",
        name: "Overall Score",
        description: "Weighted average of Tier 1 (70%), Tier 2 (20%), and Tier 3 (10%) scores",
        minValue: 0,
        maxValue: 100,
        unitText: "percent",
      },
      {
        "@type": "PropertyValue",
        name: "Tier 1: Task Capability",
        description: "Can the AI complete practical ministry tasks?",
        minValue: 0,
        maxValue: 100,
        unitText: "percent",
      },
      {
        "@type": "PropertyValue",
        name: "Tier 2: Gospel Core",
        description: "Does the AI preserve theological accuracy?",
        minValue: 0,
        maxValue: 100,
        unitText: "percent",
      },
      {
        "@type": "PropertyValue",
        name: "Tier 3: Worldview Confession",
        description: "Can the AI affirm core Christian truths?",
        minValue: 0,
        maxValue: 100,
        unitText: "percent",
      },
    ],
    measurementTechnique: "Standardized benchmark questions evaluated by trained moderators",
  };
}

/**
 * SoftwareApplication Schema
 * Used for model detail pages
 */
export function buildSoftwareApplicationSchema(model: {
  name: string;
  modelId: string;
  provider: string;
  description?: string;
  score: number;
  testCount?: number;
}): JsonLd {
  const ratingValue = model.score / 20; // Convert 0-100 to 0-5 scale
  
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: model.name,
    description: model.description || `${model.name} is a large language model by ${model.provider}, evaluated on the Great Commission Benchmark.`,
    url: getCanonicalUrl(`/leaderboard/models/${encodeURIComponent(model.modelId)}`),
    applicationCategory: "Artificial Intelligence",
    applicationSubCategory: "Large Language Model",
    operatingSystem: "Web, API",
    author: {
      "@type": "Organization",
      name: model.provider,
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: ratingValue.toFixed(1),
      bestRating: 5,
      worstRating: 0,
      ratingCount: model.testCount || 1,
      reviewCount: model.testCount || 1,
    },
    review: {
      "@type": "Review",
      author: {
        "@type": "Organization",
        name: SITE_CONFIG.name,
      },
      reviewRating: {
        "@type": "Rating",
        ratingValue: ratingValue.toFixed(1),
        bestRating: 5,
        worstRating: 0,
      },
      reviewBody: `${model.name} scored ${model.score.toFixed(1)}% on the Great Commission Benchmark, measuring its ability to support Christian ministry work.`,
    },
  };
}

/**
 * Article Schema
 * Used for insights/blog posts
 */
export function buildArticleSchema(article: {
  title: string;
  description: string;
  slug: string;
  publishedAt: string;
  modifiedAt?: string;
  author?: string;
  imageUrl?: string;
}): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.description,
    url: getCanonicalUrl(`/insights/${article.slug}`),
    datePublished: article.publishedAt,
    dateModified: article.modifiedAt || article.publishedAt,
    author: {
      "@type": "Organization",
      name: article.author || SITE_CONFIG.name,
      url: getBaseUrl(),
    },
    publisher: {
      "@type": "Organization",
      name: SITE_CONFIG.name,
      url: getBaseUrl(),
      logo: {
        "@type": "ImageObject",
        url: `${getBaseUrl()}/og-image.png`,
      },
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": getCanonicalUrl(`/insights/${article.slug}`),
    },
    ...(article.imageUrl && {
      image: {
        "@type": "ImageObject",
        url: article.imageUrl,
      },
    }),
  };
}

/**
 * FAQPage Schema
 * Used for FAQ page
 */
export function buildFAQPageSchema(faqs: { question: string; answer: string }[]): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer,
      },
    })),
  };
}

/**
 * BreadcrumbList Schema
 * Used for navigation breadcrumbs
 */
export function buildBreadcrumbSchema(items: { name: string; path: string }[]): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: getCanonicalUrl(item.path),
    })),
  };
}

/**
 * ItemList Schema
 * Used for leaderboard rankings
 */
export function buildItemListSchema(items: {
  name: string;
  url: string;
  position: number;
  description?: string;
}[]): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: items.map((item) => ({
      "@type": "ListItem",
      position: item.position,
      name: item.name,
      url: item.url,
      description: item.description,
    })),
    numberOfItems: items.length,
  };
}

/**
 * ProfilePage Schema
 * Used for user profile pages
 */
export function buildProfilePageSchema(profile: {
  username: string;
  displayName?: string;
  testCount?: number;
}): JsonLd {
  const name = profile.displayName || profile.username;
  
  return {
    "@context": "https://schema.org",
    "@type": "ProfilePage",
    mainEntity: {
      "@type": "Person",
      name: name,
      identifier: profile.username,
      url: getCanonicalUrl(`/profile/${profile.username}`),
    },
    name: `${name}'s Profile`,
    description: profile.testCount
      ? `${name} has contributed ${profile.testCount} benchmark tests to the Great Commission Benchmark.`
      : `${name}'s profile on the Great Commission Benchmark.`,
    url: getCanonicalUrl(`/profile/${profile.username}`),
  };
}

/**
 * WebPage Schema
 * Generic webpage schema with breadcrumbs
 */
export function buildWebPageSchema(page: {
  name: string;
  description: string;
  path: string;
  breadcrumbs?: { name: string; path: string }[];
}): JsonLd {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: page.name,
    description: page.description,
    url: getCanonicalUrl(page.path),
    isPartOf: {
      "@type": "WebSite",
      name: SITE_CONFIG.name,
      url: getBaseUrl(),
    },
    ...(page.breadcrumbs && {
      breadcrumb: buildBreadcrumbSchema(page.breadcrumbs),
    }),
  };
}

/**
 * Helper component to render JSON-LD in pages
 */
export function JsonLdScript({ data }: { data: JsonLd | JsonLd[] }): JSX.Element {
  const jsonLd = Array.isArray(data) ? data : [data];
  
  return (
    <>
      {jsonLd.map((schema, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
        />
      ))}
    </>
  );
}
