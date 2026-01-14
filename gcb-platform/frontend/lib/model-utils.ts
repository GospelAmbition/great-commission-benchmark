/**
 * Utility functions for formatting model and provider names
 */

import { getDisplayName } from "./providers";

/**
 * Format provider name with proper capitalization
 * e.g., "nvidia" -> "NVIDIA", "openai" -> "OpenAI"
 */
export function formatProvider(provider: string): string {
  return getDisplayName(provider);
}

/**
 * Extract and format display model name from model_id or model_name
 * e.g., "nvidia/nemotron-3-nano" -> "Nemotron 3 Nano"
 */
export function getDisplayModelName(modelName: string, modelId?: string): string {
  // Use model_id if it contains a slash (OpenRouter format), otherwise use modelName
  const source = modelId?.includes("/") ? modelId : modelName;
  
  // Remove provider prefix if present
  const namePart = source.includes("/") ? source.split("/").slice(1).join("/") : source;
  
  // Format the name: replace hyphens/underscores with spaces and title case
  return namePart
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    // Only add space between numbers and uppercase letters (indicating a new word like "3 Next")
    // Don't split number + lowercase letter (like "80b", "7b") - these are parameter counts
    // Don't split letter + number + letter (like "A3b") - these are version identifiers
    .replace(/(\d+)([A-Z])/g, "$1 $2");
}
