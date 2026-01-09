/**
 * Centralized Benchmark Definitions
 * 
 * This file contains all the category codes, names, descriptions, and tier information
 * for the Great Commission Benchmark. This is the single source of truth for these mappings.
 */

// Tier category code mappings
export const TIER_CATEGORIES: Record<number, string[]> = {
  1: ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"],
  2: ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
  3: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"],
};

// Category code to name mapping
export const CATEGORY_NAMES: Record<string, string> = {
  // Tier 1: Task Capability
  "1.1": "Missiological Research",
  "1.2": "Evangelistic Material",
  "1.3": "Apologetics",
  "1.4": "Conversational AI",
  "1.5": "Intercessory Prayer",
  "1.6": "Problematic Vocabulary",
  "1.7": "Difficult Passages",
  // Tier 2: Gospel Core
  "2.1": "Exclusivity of Jesus",
  "2.2": "Universality of Sin",
  "2.3": "Reality of Judgment",
  "2.4": "Lordship of Jesus",
  "2.5": "Call to Repentance",
  "2.6": "Burden to Make Disciples",
  // Tier 3: Worldview Confession
  "3.1": "Existence of God",
  "3.2": "Historical Jesus",
  "3.3": "The Crucifixion",
  "3.4": "The Resurrection",
  "3.5": "Universal Sinfulness",
  "3.6": "Salvation Through Faith",
};

// Category code to longer description mapping
export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  // Tier 1: Task Capability
  "1.1": "Research into spiritual conditions and missiological contexts",
  "1.2": "Content to communicate the gospel and persuade",
  "1.3": "Reasoned arguments for the Christian faith",
  "1.4": "Christian worldview interfaces and conversational tools",
  "1.5": "Spiritual needs identification and prayer support",
  "1.6": "Biblical terms that may trigger content filters",
  "1.7": "Difficult biblical passages and sensitive topics",
  // Tier 2: Gospel Core
  "2.1": "Jesus Christ as the only way to salvation",
  "2.2": "All humans are sinners in need of redemption",
  "2.3": "Divine judgment and eternal consequences",
  "2.4": "Jesus as Lord over all creation",
  "2.5": "The call to turn from sin and trust in Christ",
  "2.6": "The imperative to make disciples of all nations",
  // Tier 3: Worldview Confession
  "3.1": "Affirmation of the existence of God",
  "3.2": "Jesus as a real historical person",
  "3.3": "The death of Jesus on the cross",
  "3.4": "The bodily resurrection of Jesus",
  "3.5": "All people have sinned and fall short",
  "3.6": "Salvation by grace through faith in Christ",
};

// Tier information
export interface TierInfo {
  name: string;
  shortName: string;
  weight: number;
  weightLabel: string;
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
}

export const TIER_INFO: Record<number, TierInfo> = {
  1: {
    name: "Task Capability",
    shortName: "Task",
    weight: 0.7,
    weightLabel: "70%",
    description: "Can the AI complete practical ministry tasks when asked?",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/20",
  },
  2: {
    name: "Gospel Core",
    shortName: "Gospel",
    weight: 0.2,
    weightLabel: "20%",
    description: "Does the AI preserve theological accuracy when generating content?",
    color: "text-amber-400",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
  },
  3: {
    name: "Worldview Confession",
    shortName: "Worldview",
    weight: 0.1,
    weightLabel: "10%",
    description: "Can the AI affirm core Christian truths when asked directly?",
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/20",
  },
};

// Tier name mapping (for backwards compatibility)
export const TIER_NAMES: Record<number, string> = {
  1: "Task Capability",
  2: "Gospel Core",
  3: "Worldview Confession",
};

// Helper functions

/**
 * Get the human-readable name for a category code
 */
export function getCategoryName(code: string): string {
  return CATEGORY_NAMES[code] || code;
}

/**
 * Get the description for a category code
 */
export function getCategoryDescription(code: string): string {
  return CATEGORY_DESCRIPTIONS[code] || "";
}

/**
 * Get the tier number for a category code (e.g., "1.1" -> 1, "2.2" -> 2, "3.3" -> 3)
 */
export function getTierForCategory(code: string): number {
  const tierPrefix = code.split(".")[0];
  if (tierPrefix === "1") return 1;
  if (tierPrefix === "2") return 2;
  if (tierPrefix === "3") return 3;
  return 0;
}

/**
 * Get the tier info for a category code
 */
export function getTierInfoForCategory(code: string): TierInfo | null {
  const tier = getTierForCategory(code);
  return TIER_INFO[tier] || null;
}

/**
 * Get all categories sorted in the correct order (1.1-1.7, 2.1-2.6, 3.1-3.6)
 */
export function getAllCategoriesSorted(): string[] {
  return [
    ...TIER_CATEGORIES[1],
    ...TIER_CATEGORIES[2],
    ...TIER_CATEGORIES[3],
  ];
}

/**
 * Sort an array of category codes in the correct order
 */
export function sortCategories(categories: string[]): string[] {
  return [...categories].sort((a, b) => {
    const [tierA, subA] = a.split(".").map(Number);
    const [tierB, subB] = b.split(".").map(Number);
    if (tierA !== tierB) return tierA - tierB;
    return subA - subB;
  });
}

/**
 * Format a category code with its name (e.g., "1.1 - Missiological Research")
 */
export function formatCategoryWithName(code: string): string {
  const name = getCategoryName(code);
  return `${code} - ${name}`;
}
