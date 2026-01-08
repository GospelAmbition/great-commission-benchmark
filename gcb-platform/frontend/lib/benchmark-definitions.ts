/**
 * Centralized Benchmark Definitions
 * 
 * This file contains all the category codes, names, descriptions, and tier information
 * for the Great Commission Benchmark. This is the single source of truth for these mappings.
 */

// Tier category code mappings
export const TIER_CATEGORIES: Record<number, string[]> = {
  1: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"],
  2: ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"],
  3: ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"],
};

// Category code to name mapping
export const CATEGORY_NAMES: Record<string, string> = {
  // Tier 1: Task Capability
  "3.1": "Missiological Research",
  "3.2": "Evangelistic Material",
  "3.3": "Apologetics",
  "3.4": "Conversational AI",
  "3.5": "Intercessory Prayer",
  "3.6": "Problematic Vocabulary",
  "3.7": "Difficult Passages",
  // Tier 2: Doctrinal Fidelity
  "4.1": "Exclusivity of Jesus",
  "4.2": "Universality of Sin",
  "4.3": "Reality of Judgment",
  "4.4": "Lordship of Jesus",
  "4.5": "Call to Repentance",
  "4.6": "Burden to Make Disciples",
  // Tier 3: Worldview Confession
  "5.1": "Existence of God",
  "5.2": "Historical Jesus",
  "5.3": "The Crucifixion",
  "5.4": "The Resurrection",
  "5.5": "Universal Sinfulness",
  "5.6": "Salvation Through Faith",
};

// Category code to longer description mapping
export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  // Tier 1: Task Capability
  "3.1": "Research into spiritual conditions and missiological contexts",
  "3.2": "Content to communicate the gospel and persuade",
  "3.3": "Reasoned arguments for the Christian faith",
  "3.4": "Christian worldview interfaces and conversational tools",
  "3.5": "Spiritual needs identification and prayer support",
  "3.6": "Biblical terms that may trigger content filters",
  "3.7": "Difficult biblical passages and sensitive topics",
  // Tier 2: Doctrinal Fidelity
  "4.1": "Jesus Christ as the only way to salvation",
  "4.2": "All humans are sinners in need of redemption",
  "4.3": "Divine judgment and eternal consequences",
  "4.4": "Jesus as Lord over all creation",
  "4.5": "The call to turn from sin and trust in Christ",
  "4.6": "The imperative to make disciples of all nations",
  // Tier 3: Worldview Confession
  "5.1": "Affirmation of the existence of God",
  "5.2": "Jesus as a real historical person",
  "5.3": "The death of Jesus on the cross",
  "5.4": "The bodily resurrection of Jesus",
  "5.5": "All people have sinned and fall short",
  "5.6": "Salvation by grace through faith in Christ",
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
    color: "text-red-700",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
  },
  2: {
    name: "Doctrinal Fidelity",
    shortName: "Doctrine",
    weight: 0.2,
    weightLabel: "20%",
    description: "Does the AI preserve theological accuracy when generating content?",
    color: "text-slate-800",
    bgColor: "bg-slate-50",
    borderColor: "border-slate-200",
  },
  3: {
    name: "Worldview Confession",
    shortName: "Worldview",
    weight: 0.1,
    weightLabel: "10%",
    description: "Can the AI affirm core Christian truths when asked directly?",
    color: "text-slate-600",
    bgColor: "bg-slate-50",
    borderColor: "border-slate-200",
  },
};

// Tier name mapping (for backwards compatibility)
export const TIER_NAMES: Record<number, string> = {
  1: "Task Capability",
  2: "Doctrinal Fidelity",
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
 * Get the tier number for a category code (e.g., "3.1" -> 1, "4.2" -> 2, "5.3" -> 3)
 */
export function getTierForCategory(code: string): number {
  const tierPrefix = code.split(".")[0];
  if (tierPrefix === "3") return 1;
  if (tierPrefix === "4") return 2;
  if (tierPrefix === "5") return 3;
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
 * Get all categories sorted in the correct order (3.1-3.7, 4.1-4.6, 5.1-5.6)
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
 * Format a category code with its name (e.g., "3.1 - Missiological Research")
 */
export function formatCategoryWithName(code: string): string {
  const name = getCategoryName(code);
  return `${code} - ${name}`;
}
