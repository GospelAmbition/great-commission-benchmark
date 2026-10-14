export interface VersionInfo {
  semantic_version: string;
  marketing_version: string;
  status: string;
  release_date?: string;
  question_count: number;
  tier_distribution?: {
    tier1: number;
    tier2: number;
    tier3: number;
  };
  models_tested?: number;
}

export function toVersionInfo(versions: unknown[]): VersionInfo[] {
  // The API returns versions with a different structure than VersionsResponse
  // declares; pick out the fields this page renders.
  return (versions as VersionInfo[]).map((v) => ({
    semantic_version: v.semantic_version,
    marketing_version: v.marketing_version,
    status: v.status,
    release_date: v.release_date,
    question_count: v.question_count,
    tier_distribution: v.tier_distribution,
    models_tested: v.models_tested,
  }));
}
