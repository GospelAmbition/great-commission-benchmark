/**
 * Centralized Provider Registry
 * Single source of truth for AI provider information including display names and icons
 */

export interface ProviderInfo {
  /** Canonical provider identifier */
  id: string;
  /** Human-readable display name */
  displayName: string;
  /** Simple Icons slug for brand icon, or null if no icon available */
  simpleIconSlug: string | null;
}

/**
 * Registry of known AI providers with their display names and icon availability
 * Icon slugs are verified against Simple Icons CDN
 */
export const PROVIDERS: Record<string, ProviderInfo> = {
  // Major AI providers (with icons)
  openai: { id: "openai", displayName: "OpenAI", simpleIconSlug: "openai" },
  anthropic: { id: "anthropic", displayName: "Anthropic", simpleIconSlug: "anthropic" },
  google: { id: "google", displayName: "Google", simpleIconSlug: "google" },
  meta: { id: "meta", displayName: "Meta", simpleIconSlug: "meta" },
  nvidia: { id: "nvidia", displayName: "NVIDIA", simpleIconSlug: "nvidia" },
  microsoft: { id: "microsoft", displayName: "Microsoft", simpleIconSlug: "microsoft" },
  amazon: { id: "amazon", displayName: "Amazon", simpleIconSlug: "amazon" },

  // AI labs and platforms (with icons)
  mistral: { id: "mistral", displayName: "Mistral", simpleIconSlug: "mistral" },
  deepseek: { id: "deepseek", displayName: "DeepSeek", simpleIconSlug: "deepseek" },
  perplexity: { id: "perplexity", displayName: "Perplexity", simpleIconSlug: "perplexity" },
  cohere: { id: "cohere", displayName: "Cohere", simpleIconSlug: "cohere" },
  huggingface: { id: "huggingface", displayName: "Hugging Face", simpleIconSlug: "huggingface" },
  replicate: { id: "replicate", displayName: "Replicate", simpleIconSlug: "replicate" },
  databricks: { id: "databricks", displayName: "Databricks", simpleIconSlug: "databricks" },

  // xAI (with icon)
  xai: { id: "xai", displayName: "xAI", simpleIconSlug: "x" },

  // Infrastructure providers (with icons)
  groq: { id: "groq", displayName: "Groq", simpleIconSlug: "groq" },

  // Providers without Simple Icons (fallback to letter)
  qwen: { id: "qwen", displayName: "Qwen", simpleIconSlug: null },
  ai21: { id: "ai21", displayName: "AI21", simpleIconSlug: null },
  together: { id: "together", displayName: "Together", simpleIconSlug: null },
  fireworks: { id: "fireworks", displayName: "Fireworks", simpleIconSlug: null },
  anyscale: { id: "anyscale", displayName: "Anyscale", simpleIconSlug: null },
  inflection: { id: "inflection", displayName: "Inflection", simpleIconSlug: null },
  yi: { id: "yi", displayName: "Yi", simpleIconSlug: null },
  zhipu: { id: "zhipu", displayName: "Zhipu", simpleIconSlug: null },
  baichuan: { id: "baichuan", displayName: "Baichuan", simpleIconSlug: null },
  moonshot: { id: "moonshot", displayName: "Moonshot", simpleIconSlug: null },
  minimax: { id: "minimax", displayName: "MiniMax", simpleIconSlug: null },
  "01-ai": { id: "01-ai", displayName: "01.AI", simpleIconSlug: null },
};

/**
 * Alias mapping for provider name variations
 * Maps alternative identifiers to canonical provider IDs
 */
export const PROVIDER_ALIASES: Record<string, string> = {
  // Meta variations
  "meta-llama": "meta",

  // Mistral variations
  mistralai: "mistral",

  // Hugging Face variations
  "hugging-face": "huggingface",

  // xAI variations
  x: "xai",
};

/**
 * Get provider info by ID (handles aliases)
 * @param id - Provider identifier (case-insensitive)
 * @returns ProviderInfo or null if not found
 */
export function getProvider(id: string): ProviderInfo | null {
  const normalizedId = id.toLowerCase();
  const canonicalId = PROVIDER_ALIASES[normalizedId] || normalizedId;
  return PROVIDERS[canonicalId] || null;
}

/**
 * Get display name for a provider
 * @param id - Provider identifier (case-insensitive)
 * @returns Display name or title-cased ID if not found
 */
export function getDisplayName(id: string): string {
  const provider = getProvider(id);
  if (provider) {
    return provider.displayName;
  }
  // Fallback: title case the ID
  return id.charAt(0).toUpperCase() + id.slice(1);
}

/**
 * Get Simple Icons slug for a provider
 * @param id - Provider identifier (case-insensitive)
 * @returns Icon slug or null if no icon available
 */
export function getIconSlug(id: string): string | null {
  const provider = getProvider(id);
  return provider?.simpleIconSlug || null;
}

/**
 * Check if a provider has an icon available
 * @param id - Provider identifier (case-insensitive)
 * @returns True if provider has a Simple Icons icon
 */
export function hasIcon(id: string): boolean {
  return getIconSlug(id) !== null;
}

/**
 * Get all registered provider IDs
 * @returns Array of canonical provider IDs
 */
export function getAllProviderIds(): string[] {
  return Object.keys(PROVIDERS);
}

/**
 * Get all providers with icons
 * @returns Array of ProviderInfo for providers with icons
 */
export function getProvidersWithIcons(): ProviderInfo[] {
  return Object.values(PROVIDERS).filter((p) => p.simpleIconSlug !== null);
}

/**
 * Get all providers without icons
 * @returns Array of ProviderInfo for providers without icons
 */
export function getProvidersWithoutIcons(): ProviderInfo[] {
  return Object.values(PROVIDERS).filter((p) => p.simpleIconSlug === null);
}
