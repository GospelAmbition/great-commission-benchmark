"use client";

import {
  createContext,
  useContext,
  type ReactNode,
} from "react";

export interface LeaderboardDataItem {
  id: string;
  model_id: string;
  model_name: string;
  provider: string;
  overall_score: number;
  tier1_score?: number;
  tier2_score?: number;
  tier3_score?: number;
  trust_tier?: string;
  category_scores?: Record<string, number>;
}

interface LeaderboardDataContextValue {
  initialItems: LeaderboardDataItem[] | null;
  initialTotal: number;
}

const LeaderboardDataContext = createContext<LeaderboardDataContextValue>({
  initialItems: null,
  initialTotal: 0,
});

export function LeaderboardDataProvider({
  initialItems,
  initialTotal,
  children,
}: {
  initialItems: LeaderboardDataItem[] | null;
  initialTotal: number;
  children: ReactNode;
}) {
  return (
    <LeaderboardDataContext.Provider value={{ initialItems, initialTotal }}>
      {children}
    </LeaderboardDataContext.Provider>
  );
}

export function useLeaderboardInitialData() {
  return useContext(LeaderboardDataContext);
}
