/**
 * Provider icon utilities using Simple Icons CDN
 * Uses centralized provider registry for icon slug lookups
 */

import { getIconSlug, hasIcon } from "./providers";

const SIMPLE_ICONS_CDN = "https://cdn.jsdelivr.net/npm/simple-icons@14/icons";

/**
 * Get the Simple Icons CDN URL for a provider
 * @param provider - The provider identifier (case-insensitive)
 * @returns The CDN URL for the icon SVG, or null if not available
 */
export function getProviderIconUrl(provider: string): string | null {
  const slug = getIconSlug(provider);
  return slug ? `${SIMPLE_ICONS_CDN}/${slug}.svg` : null;
}

/**
 * Check if a provider has an icon available
 * @param provider - The provider identifier (case-insensitive)
 * @returns True if an icon is available
 */
export function hasProviderIcon(provider: string): boolean {
  return hasIcon(provider);
}

/**
 * Get the Simple Icons slug for a provider
 * @param provider - The provider identifier (case-insensitive)
 * @returns The Simple Icons slug, or null if not available
 */
export function getProviderIconSlug(provider: string): string | null {
  return getIconSlug(provider);
}
