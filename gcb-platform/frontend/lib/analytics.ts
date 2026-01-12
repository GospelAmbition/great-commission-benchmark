/**
 * Analytics and Event Tracking
 * Integrates with Umami Analytics for event tracking and conversion measurement
 */

// Umami's global tracking function type
declare global {
  interface Window {
    umami?: {
      track: (event: string, data?: Record<string, unknown>) => void;
    };
  }
}

// Event categories for organization
export const EventCategory = {
  NAVIGATION: "navigation",
  ENGAGEMENT: "engagement",
  CONVERSION: "conversion",
  SOCIAL: "social",
  MODEL: "model",
  USER: "user",
} as const;

// Predefined event names for consistency
export const EventName = {
  // Navigation events
  PAGE_VIEW: "page_view",
  EXTERNAL_LINK_CLICK: "external_link_click",
  
  // Engagement events
  SEARCH: "search",
  FILTER_APPLIED: "filter_applied",
  MODEL_VIEW: "model_view",
  MODEL_COMPARE: "model_compare",
  CATEGORY_VIEW: "category_view",
  INSIGHTS_VIEW: "insights_view",
  FAQ_EXPAND: "faq_expand",
  
  // Conversion events
  NEWSLETTER_SIGNUP: "newsletter_signup",
  TEST_SUBMISSION: "test_submission",
  SPONSORSHIP_REQUEST: "sponsorship_request",
  DONATION_INITIATED: "donation_initiated",
  DONATION_COMPLETED: "donation_completed",
  CLI_DOWNLOAD: "cli_download",
  
  // Social events
  SOCIAL_SHARE: "social_share",
  COPY_LINK: "copy_link",
  
  // User events
  SIGN_UP: "sign_up",
  SIGN_IN: "sign_in",
  PROFILE_UPDATE: "profile_update",
  API_KEY_CREATED: "api_key_created",
} as const;

// Conversion types with estimated values (for tracking importance)
export const ConversionType = {
  NEWSLETTER_SIGNUP: { name: "newsletter_signup", value: 1 },
  TEST_SUBMISSION: { name: "test_submission", value: 10 },
  SPONSORSHIP_REQUEST: { name: "sponsorship_request", value: 50 },
  DONATION: { name: "donation", value: 100 },
  USER_REGISTRATION: { name: "user_registration", value: 5 },
} as const;

/**
 * Check if analytics is available
 */
function isAnalyticsAvailable(): boolean {
  return typeof window !== "undefined" && window.umami !== undefined;
}

/**
 * Track a custom event
 * @param eventName - Name of the event
 * @param properties - Additional properties to track
 */
export function trackEvent(
  eventName: string,
  properties?: Record<string, unknown>
): void {
  if (!isAnalyticsAvailable()) {
    // Log in development for debugging
    if (process.env.NODE_ENV === "development") {
      console.log("[Analytics]", eventName, properties);
    }
    return;
  }

  try {
    window.umami?.track(eventName, properties);
  } catch (error) {
    console.error("[Analytics] Error tracking event:", error);
  }
}

/**
 * Track a conversion event
 * @param conversionType - Type of conversion
 * @param metadata - Additional conversion metadata
 */
export function trackConversion(
  conversionType: (typeof ConversionType)[keyof typeof ConversionType],
  metadata?: Record<string, unknown>
): void {
  trackEvent(conversionType.name, {
    category: EventCategory.CONVERSION,
    value: conversionType.value,
    ...metadata,
  });
}

/**
 * Track a page view with additional context
 * @param url - Page URL
 * @param metadata - Additional page metadata
 */
export function trackPageView(
  url: string,
  metadata?: {
    title?: string;
    referrer?: string;
    modelName?: string;
    modelScore?: number;
    category?: string;
  }
): void {
  trackEvent(EventName.PAGE_VIEW, {
    url,
    ...metadata,
  });
}

/**
 * Track model view
 * @param modelId - Model identifier
 * @param modelName - Model display name
 * @param provider - Model provider
 * @param score - Model score
 */
export function trackModelView(
  modelId: string,
  modelName: string,
  provider: string,
  score: number
): void {
  trackEvent(EventName.MODEL_VIEW, {
    category: EventCategory.MODEL,
    modelId,
    modelName,
    provider,
    score: Math.round(score * 10) / 10, // Round to 1 decimal
  });
}

/**
 * Track model comparison
 * @param modelIds - Array of model IDs being compared
 * @param modelCount - Number of models compared
 */
export function trackModelCompare(modelIds: string[], modelCount: number): void {
  trackEvent(EventName.MODEL_COMPARE, {
    category: EventCategory.MODEL,
    modelIds: modelIds.join(","),
    modelCount,
  });
}

/**
 * Track social share
 * @param platform - Social platform (twitter, linkedin, facebook, email, copy)
 * @param contentType - Type of content being shared
 * @param contentId - ID of the content
 */
export function trackSocialShare(
  platform: string,
  contentType: "model" | "article" | "page",
  contentId?: string
): void {
  trackEvent(EventName.SOCIAL_SHARE, {
    category: EventCategory.SOCIAL,
    platform,
    contentType,
    contentId,
  });
}

/**
 * Track newsletter signup
 * @param source - Where the signup originated
 */
export function trackNewsletterSignup(source: string = "newsletter_page"): void {
  trackConversion(ConversionType.NEWSLETTER_SIGNUP, { source });
}

/**
 * Track test submission
 * @param modelName - Name of the model tested
 * @param submissionType - Type of submission (cli, manual)
 */
export function trackTestSubmission(
  modelName: string,
  submissionType: "cli" | "manual" = "cli"
): void {
  trackConversion(ConversionType.TEST_SUBMISSION, {
    modelName,
    submissionType,
  });
}

/**
 * Track sponsorship request
 * @param requestType - Type of request (sponsorship, request)
 * @param modelName - Model name if applicable
 */
export function trackSponsorshipRequest(
  requestType: "sponsorship" | "request",
  modelName?: string
): void {
  trackConversion(ConversionType.SPONSORSHIP_REQUEST, {
    requestType,
    modelName,
  });
}

/**
 * Track donation initiation
 * @param amount - Donation amount
 */
export function trackDonationInitiated(amount: number): void {
  trackEvent(EventName.DONATION_INITIATED, {
    category: EventCategory.CONVERSION,
    amount,
  });
}

/**
 * Track donation completion
 * @param amount - Donation amount
 */
export function trackDonationCompleted(amount: number): void {
  trackConversion(ConversionType.DONATION, { amount });
}

/**
 * Track search
 * @param query - Search query
 * @param resultCount - Number of results
 */
export function trackSearch(query: string, resultCount?: number): void {
  trackEvent(EventName.SEARCH, {
    category: EventCategory.ENGAGEMENT,
    query: query.substring(0, 100), // Limit query length
    resultCount,
  });
}

/**
 * Track filter application
 * @param filterType - Type of filter (provider, category, tier, etc.)
 * @param filterValue - Value of the filter
 */
export function trackFilterApplied(filterType: string, filterValue: string): void {
  trackEvent(EventName.FILTER_APPLIED, {
    category: EventCategory.ENGAGEMENT,
    filterType,
    filterValue,
  });
}

/**
 * Track CLI download
 * @param platform - Platform (macos-arm64, macos-x64, linux, windows)
 */
export function trackCliDownload(platform: string): void {
  trackEvent(EventName.CLI_DOWNLOAD, {
    category: EventCategory.ENGAGEMENT,
    platform,
  });
}

/**
 * Track external link click
 * @param url - External URL
 * @param linkText - Link text or description
 */
export function trackExternalLinkClick(url: string, linkText?: string): void {
  trackEvent(EventName.EXTERNAL_LINK_CLICK, {
    category: EventCategory.NAVIGATION,
    url,
    linkText,
  });
}

/**
 * Track user registration
 */
export function trackUserRegistration(): void {
  trackConversion(ConversionType.USER_REGISTRATION, {});
}

/**
 * Create an onClick handler for tracking
 * Useful for inline event tracking
 */
export function createTrackingHandler(
  eventName: string,
  properties?: Record<string, unknown>
): () => void {
  return () => trackEvent(eventName, properties);
}
