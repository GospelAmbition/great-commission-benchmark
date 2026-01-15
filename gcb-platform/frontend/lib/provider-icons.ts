/**
 * Provider icon utilities using Simple Icons CDN
 * Uses centralized provider registry for icon slug lookups
 * Automatically falls back to trying provider name as slug if not in registry
 */

import { getIconSlug, getProvider, PROVIDER_ALIASES } from "./providers";

const SIMPLE_ICONS_CDN = "https://cdn.jsdelivr.net/npm/simple-icons@14/icons";

/**
 * Get potential icon slugs to try for a provider
 * @param provider - The provider identifier (case-insensitive)
 * @returns Array of slugs to try (in order of preference)
 */
function getIconSlugsToTry(provider: string): string[] {
  const normalizedId = provider.toLowerCase();
  const canonicalId = PROVIDER_ALIASES[normalizedId] || normalizedId;
  
  // First, check if provider is in registry with a confirmed slug
  const registeredProvider = getProvider(provider);
  if (registeredProvider?.simpleIconSlug) {
    return [registeredProvider.simpleIconSlug];
  }
  
  // If provider is registered but has null slug, don't try any slugs
  if (registeredProvider?.simpleIconSlug === null) {
    return [];
  }
  
  // Provider not in registry - try common variations
  const slugsToTry = [
    canonicalId,
    canonicalId.replace(/-/g, ""),
    canonicalId.replace(/_/g, ""),
  ];
  
  // Remove duplicates while preserving order
  return [...new Set(slugsToTry)];
}

/**
 * Get the Simple Icons CDN URL for a provider
 * Tries multiple slug variations automatically
 * @param provider - The provider identifier (case-insensitive)
 * @returns The CDN URL for the icon SVG, or null if not available
 */
export function getProviderIconUrl(provider: string): string | null {
  const slugs = getIconSlugsToTry(provider);
  if (slugs.length === 0) {
    return null;
  }
  // Return the first slug to try - the component will handle errors
  return `${SIMPLE_ICONS_CDN}/${slugs[0]}.svg`;
}

/**
 * Check if a provider has an icon available
 * @param provider - The provider identifier (case-insensitive)
 * @returns True if we should try to load an icon (may still fail, but we'll try)
 */
export function hasProviderIcon(provider: string): boolean {
  const slugs = getIconSlugsToTry(provider);
  return slugs.length > 0;
}

/**
 * Get the Simple Icons slug for a provider
 * @param provider - The provider identifier (case-insensitive)
 * @returns The Simple Icons slug, or null if not available
 */
export function getProviderIconSlug(provider: string): string | null {
  return getIconSlug(provider);
}
