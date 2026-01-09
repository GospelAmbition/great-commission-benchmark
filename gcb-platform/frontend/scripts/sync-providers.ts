#!/usr/bin/env npx ts-node

/**
 * Provider Sync Script
 * 
 * Fetches providers from OpenRouter's model list and checks which have
 * Simple Icons available. Outputs a report and can update the registry.
 * 
 * Usage:
 *   npx ts-node scripts/sync-providers.ts
 *   npm run sync-providers
 */

import * as fs from "fs";
import * as path from "path";

const OPENROUTER_API = "https://openrouter.ai/api/v1/models";
const SIMPLE_ICONS_CDN = "https://cdn.jsdelivr.net/npm/simple-icons@14/icons";

interface OpenRouterModel {
  id: string;
  name: string;
  // Other fields exist but we only need id
}

interface ProviderResult {
  id: string;
  hasIcon: boolean;
  iconSlug: string | null;
}

/**
 * Extract provider slug from OpenRouter model ID
 * e.g., "openai/gpt-4" -> "openai"
 */
function extractProvider(modelId: string): string {
  const parts = modelId.split("/");
  return parts[0].toLowerCase();
}

/**
 * Check if a Simple Icons slug exists via HEAD request
 */
async function checkSimpleIcon(slug: string): Promise<boolean> {
  const url = `${SIMPLE_ICONS_CDN}/${slug}.svg`;
  try {
    const response = await fetch(url, { method: "HEAD" });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Try common slug variations for a provider
 */
async function findIconSlug(providerId: string): Promise<string | null> {
  // Slugs to try (in order of preference)
  const slugsToTry = [
    providerId,
    providerId.replace(/-/g, ""),
    providerId.replace(/_/g, ""),
  ];

  // Special mappings for known providers
  const specialMappings: Record<string, string[]> = {
    "meta-llama": ["meta"],
    "mistralai": ["mistral"],
    "hugging-face": ["huggingface"],
    "x-ai": ["x"],
    "xai": ["x"],
  };

  if (specialMappings[providerId]) {
    slugsToTry.unshift(...specialMappings[providerId]);
  }

  for (const slug of slugsToTry) {
    if (await checkSimpleIcon(slug)) {
      return slug;
    }
  }

  return null;
}

/**
 * Load current providers from registry
 */
function loadCurrentProviders(): Set<string> {
  const registryPath = path.join(__dirname, "../lib/providers.ts");
  try {
    const content = fs.readFileSync(registryPath, "utf-8");
    const providerIds = new Set<string>();
    
    // Extract provider IDs from PROVIDERS object
    const providerMatches = content.matchAll(/^\s*["']?(\w[\w-]*)["']?\s*:\s*\{/gm);
    for (const match of providerMatches) {
      if (match[1] && !["id", "displayName", "simpleIconSlug"].includes(match[1])) {
        providerIds.add(match[1]);
      }
    }
    
    // Also check PROVIDER_ALIASES
    const aliasMatches = content.matchAll(/["'](\w[\w-]*)["']\s*:\s*["'](\w[\w-]*)["']/g);
    for (const match of aliasMatches) {
      if (match[1]) providerIds.add(match[1]);
    }
    
    return providerIds;
  } catch {
    console.warn("Could not load current providers registry");
    return new Set();
  }
}

async function main() {
  console.log("=== Provider Sync Report ===\n");

  // Fetch OpenRouter models
  console.log("Fetching models from OpenRouter...");
  let models: OpenRouterModel[];
  try {
    const response = await fetch(OPENROUTER_API);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    models = data.data || [];
  } catch (error) {
    console.error("Failed to fetch OpenRouter models:", error);
    process.exit(1);
  }

  // Extract unique providers
  const providerIds = new Set<string>();
  for (const model of models) {
    const provider = extractProvider(model.id);
    if (provider) {
      providerIds.add(provider);
    }
  }

  console.log(`Found ${models.length} models from ${providerIds.size} providers\n`);

  // Check each provider for Simple Icons
  const results: ProviderResult[] = [];
  console.log("Checking Simple Icons availability...\n");

  for (const providerId of Array.from(providerIds).sort()) {
    const iconSlug = await findIconSlug(providerId);
    results.push({
      id: providerId,
      hasIcon: iconSlug !== null,
      iconSlug,
    });
    // Rate limit to be nice to the CDN
    await new Promise((resolve) => setTimeout(resolve, 50));
  }

  // Load current providers for comparison
  const currentProviders = loadCurrentProviders();

  // Categorize results
  const withIcons = results.filter((r) => r.hasIcon);
  const withoutIcons = results.filter((r) => !r.hasIcon);
  const newProviders = results.filter((r) => !currentProviders.has(r.id));

  // Print report
  console.log(`OpenRouter Providers Found: ${results.length}\n`);

  console.log(`With Simple Icons (${withIcons.length}):`);
  for (const r of withIcons) {
    console.log(`  ✓ ${r.id} -> ${r.iconSlug}`);
  }

  console.log(`\nWithout Simple Icons (${withoutIcons.length}):`);
  for (const r of withoutIcons) {
    console.log(`  ✗ ${r.id} (no icon)`);
  }

  if (newProviders.length > 0) {
    console.log(`\nNew Providers (not in registry): ${newProviders.length}`);
    for (const r of newProviders) {
      const iconInfo = r.hasIcon ? `icon: "${r.iconSlug}"` : "no icon";
      console.log(`  - ${r.id} (${iconInfo})`);
    }
  }

  // Generate code snippet for new providers
  if (newProviders.length > 0) {
    console.log("\n--- Code to add to lib/providers.ts ---\n");
    for (const r of newProviders) {
      const displayName = r.id.charAt(0).toUpperCase() + r.id.slice(1);
      const iconSlug = r.iconSlug ? `"${r.iconSlug}"` : "null";
      console.log(`  "${r.id}": { id: "${r.id}", displayName: "${displayName}", simpleIconSlug: ${iconSlug} },`);
    }
  }

  console.log("\n=== Sync Complete ===");
}

main().catch(console.error);
