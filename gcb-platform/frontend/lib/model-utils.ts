/**
 * Utility functions for formatting model and provider names
 */

// Provider name formatting - maps lowercase provider IDs to display names
const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
  nvidia: "NVIDIA",
  openai: "OpenAI",
  anthropic: "Anthropic",
  google: "Google",
  meta: "Meta",
  "meta-llama": "Meta",
  mistral: "Mistral",
  mistralai: "Mistral AI",
  cohere: "Cohere",
  ai21: "AI21",
  amazon: "Amazon",
  microsoft: "Microsoft",
  qwen: "Qwen",
  deepseek: "DeepSeek",
  perplexity: "Perplexity",
  groq: "Groq",
  together: "Together",
  fireworks: "Fireworks",
  anyscale: "Anyscale",
  replicate: "Replicate",
  huggingface: "Hugging Face",
  "hugging-face": "Hugging Face",
  databricks: "Databricks",
  inflection: "Inflection",
  x: "xAI",
  xai: "xAI",
  "01-ai": "01.AI",
  yi: "Yi",
  zhipu: "Zhipu",
  baichuan: "Baichuan",
  moonshot: "Moonshot",
  minimax: "MiniMax",
};

/**
 * Format provider name with proper capitalization
 * e.g., "nvidia" -> "NVIDIA", "openai" -> "OpenAI"
 */
export function formatProvider(provider: string): string {
  const lower = provider.toLowerCase();
  return PROVIDER_DISPLAY_NAMES[lower] || provider.charAt(0).toUpperCase() + provider.slice(1);
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
    .replace(/(\d+)([a-z])/gi, "$1 $2") // Add space between numbers and letters
    .replace(/([a-z])(\d)/gi, "$1 $2"); // Add space between letters and numbers
}
