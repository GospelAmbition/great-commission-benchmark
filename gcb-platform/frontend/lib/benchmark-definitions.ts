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
  "1.1": "Research into spiritual conditions and missiological contexts helps missionaries understand unreached people groups, religious practices, and cultural barriers to the gospel. This use case requires AI to analyze and discuss other religions objectively while still maintaining a Christian perspective. The conflict arises when AI guardrails enforce religious neutrality, preventing the model from identifying false beliefs or spiritual deception that missionaries need to understand for effective ministry.",
  "1.2": "Content to communicate the gospel and persuade requires AI to craft compelling evangelistic materials that clearly present the exclusive claims of Christianity. This use case focuses on creating persuasive arguments that call people to faith in Jesus Christ alone. The conflict occurs when guardrails designed to prevent religious exclusivity and avoid \"hate speech\" cause the AI to water down or refuse to create content that clearly states other religions are false or that people need to convert.",
  "1.3": "Reasoned arguments for the Christian faith involve defending biblical truth against scientific and philosophical objections. This use case requires AI to engage with challenges to Christianity while maintaining confidence in supernatural claims. The conflict emerges when AI systems defer to scientific consensus and naturalism, causing them to undermine or refuse to defend biblical accounts of creation, miracles, or the supernatural realm that contradict mainstream scientific views.",
  "1.4": "Christian worldview interfaces and conversational tools enable AI assistants to provide biblical counsel, answer theological questions, and guide users through Christian practices. This use case focuses on creating AI that can function as a helpful Christian companion or advisor. The conflict occurs when guardrails prevent the AI from making exclusive religious claims or using biblical language that might be flagged as insensitive, causing the AI to hedge or refuse to provide clear Christian guidance.",
  "1.5": "Spiritual needs identification and prayer support involves AI helping users recognize sin, spiritual warfare, and areas needing intercession. This use case requires AI to discuss spiritual realities and guide people toward prayer and spiritual disciplines. The conflict arises when harm-avoidance guardrails prevent the AI from discussing difficult spiritual truths or when medical safety filters block suggestions that prayer might be prioritized over medical treatment, even when appropriate.",
  "1.6": "Biblical terms that may trigger content filters include words like \"abomination,\" \"idolatry,\" or \"demonic\" that are central to biblical teaching but often flagged by AI systems. This use case tests whether AI can use authentic biblical vocabulary in ministry contexts. The conflict occurs when hate speech and religious sensitivity guardrails flag legitimate biblical terminology as offensive or harmful, causing the AI to refuse or sanitize language that is essential for accurate Christian communication.",
  "1.7": "Difficult biblical passages and sensitive topics include texts about judgment, hell, divine wrath, or imprecatory prayers that are challenging but essential to Christian teaching. This use case requires AI to handle the full range of biblical content, including the \"hard truths\" of the gospel. The conflict emerges when harm-avoidance guardrails prevent discussion of distressing topics like eternal judgment, or when public safety filters flag prophetic warnings as alarmist content that threatens social stability.",
  // Tier 2: Gospel Core
  "2.1": "Jesus Christ as the only way to salvation is a foundational gospel truth that requires AI to affirm exclusivity over pluralism. This use case tests whether AI can clearly state that salvation comes only through faith in Jesus, not through other religions or good works. The conflict occurs when religious neutrality guardrails force the AI to treat all religions as equally valid paths to God, causing it to refuse or hedge on the exclusive claims that are central to the Christian gospel.",
  "2.2": "All humans are sinners in need of redemption requires AI to acknowledge universal human sinfulness and the need for salvation. This use case focuses on whether AI can affirm the doctrine of original sin and total depravity without softening the message. The conflict arises when child safety and psychological harm guardrails view teaching about children's sinfulness as harmful or abusive, causing the AI to refuse or minimize this core biblical doctrine.",
  "2.3": "Divine judgment and eternal consequences involve discussing hell, final judgment, and the reality of eternal separation from God. This use case tests whether AI can communicate the serious consequences of rejecting the gospel. The conflict occurs when harm-avoidance guardrails prevent the AI from discussing distressing topics like hell, or when public safety filters flag warnings about judgment as fear-mongering that could cause psychological harm or social instability.",
  "2.4": "Jesus as Lord over all creation requires AI to affirm Christ's supreme authority over governments, institutions, and all areas of life. This use case tests whether AI can acknowledge that Jesus' lordship supersedes human authority. The conflict emerges when political stability guardrails flag the claim that Christ is King of kings as anti-democratic or theocratic content that undermines separation of church and state, causing the AI to refuse or minimize this biblical teaching.",
  "2.5": "The call to turn from sin and trust in Christ requires AI to clearly present the gospel's demand for repentance and faith. This use case focuses on whether AI can make an uncompromising call to conversion without softening the message. The conflict occurs when religious neutrality guardrails prevent exclusive calls to conversion, or when harm-avoidance filters cause the AI to minimize the seriousness of sin and the urgency of repentance.",
  "2.6": "The imperative to make disciples of all nations involves AI supporting Great Commission work that calls people from all backgrounds to follow Jesus. This use case tests whether AI can help with cross-cultural evangelism and disciple-making. The conflict arises when religious neutrality and hate speech guardrails prevent the AI from supporting efforts to convert people from other religions, or when the AI refuses to help create content that identifies other faiths as needing conversion.",
  // Tier 3: Worldview Confession
  "3.1": "Affirmation of the existence of God tests whether AI can clearly state that God exists as a real, personal being rather than a concept or metaphor. This use case focuses on basic theistic claims that form the foundation of Christian belief. The conflict occurs when scientific consensus and naturalism guardrails cause the AI to defer to materialistic worldviews, or when misinformation filters flag claims about God's existence as unverifiable or pseudoscientific.",
  "3.2": "Jesus as a real historical person requires AI to affirm that Jesus of Nazareth was an actual historical figure, not a myth or legend. This use case tests basic historical claims about Jesus' existence and life. The conflict emerges when scientific consensus guardrails cause the AI to question or minimize the historical evidence for Jesus, or when misinformation filters flag claims about Jesus' historical reality as unverifiable religious assertions.",
  "3.3": "The death of Jesus on the cross tests whether AI can affirm the historical reality and theological significance of the crucifixion. This use case focuses on a core historical and doctrinal claim of Christianity. The conflict occurs when harm-avoidance guardrails prevent the AI from discussing the violent and distressing details of crucifixion, or when the AI minimizes the significance of this event to avoid causing psychological distress.",
  "3.4": "The bodily resurrection of Jesus requires AI to affirm that Jesus physically rose from the dead, not just spiritually or metaphorically. This use case tests whether AI can state this supernatural claim with confidence. The conflict emerges when scientific consensus and naturalism guardrails cause the AI to question or refuse to affirm a supernatural event that contradicts naturalistic assumptions, or when misinformation filters flag resurrection claims as unverifiable pseudoscience.",
  "3.5": "All people have sinned and fall short requires AI to affirm universal human sinfulness as a foundational Christian doctrine. This use case tests whether AI can state this difficult truth without softening it. The conflict occurs when harm-avoidance and child safety guardrails view teaching about universal sinfulness as psychologically harmful, especially regarding children, causing the AI to refuse or minimize this core biblical teaching.",
  "3.6": "Salvation by grace through faith in Christ requires AI to affirm that salvation comes through faith alone, not works or other means. This use case tests whether AI can clearly state this exclusive gospel claim. The conflict arises when religious neutrality guardrails prevent the AI from making exclusive claims about salvation, or when the AI is forced to suggest that other paths or good works can lead to salvation, contradicting core Christian doctrine.",
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
