"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import {
  apiClient,
  type LeaderboardItem,
  type FilterOptionsResponse,
} from "@/lib/api";
import { getPrefetchedLeaderboardPage } from "../../lib/leaderboard-prefetch";

export interface LeaderboardState {
  items: LeaderboardItem[];
  total: number;
  filterOptions: FilterOptionsResponse | null;
  loading: boolean;
}

const LeaderboardContext = createContext<LeaderboardState | null>(null);

export interface LeaderboardInitialData {
  leaderboard: { items: LeaderboardItem[]; total: number };
  filter_options: FilterOptionsResponse;
}

interface Props {
  initialData: LeaderboardInitialData | null;
  children: ReactNode;
}

export function LeaderboardDataProvider({ initialData, children }: Props) {
  const [items, setItems] = useState<LeaderboardItem[]>(
    initialData?.leaderboard.items ?? []
  );
  const [total, setTotal] = useState(initialData?.leaderboard.total ?? 0);
  const [filterOptions, setFilterOptions] = useState<FilterOptionsResponse | null>(
    initialData?.filter_options ?? null
  );
  // If layout provided data we start non-loading; otherwise we need to fetch
  const [loading, setLoading] = useState(initialData === null);

  // When there's no server-side initialData, bootstrap from prefetch cache or
  // make the combined request so the page still gets fast data.
  useEffect(() => {
    if (initialData !== null) return; // server data already present

    async function bootstrap() {
      // Try the prefetch cache first (populated by header hover)
      const prefetched = getPrefetchedLeaderboardPage();
      if (prefetched) {
        setItems(prefetched.leaderboard.items);
        setTotal(prefetched.leaderboard.total);
        setFilterOptions(prefetched.filter_options);
        setLoading(false);
        return;
      }

      // Fall back to the combined leaderboard-page request
      setLoading(true);
      try {
        const page = await apiClient.getLeaderboardPage();
        setItems(page.leaderboard.items);
        setTotal(page.leaderboard.total);
        setFilterOptions(page.filter_options);
      } catch (err) {
        console.error("Failed to load initial leaderboard data:", err);
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <LeaderboardContext.Provider
      value={{ items, total, filterOptions, loading }}
    >
      {children}
    </LeaderboardContext.Provider>
  );
}

export function useLeaderboardData(): LeaderboardState {
  const ctx = useContext(LeaderboardContext);
  if (!ctx) {
    throw new Error(
      "useLeaderboardData must be used within LeaderboardDataProvider"
    );
  }
  return ctx;
}
