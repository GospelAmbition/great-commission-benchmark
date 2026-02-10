"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useSession } from "next-auth/react";
import { apiClient, UserProfile } from "@/lib/api";

export type UserProfileData = UserProfile;

type UserProfileState = {
  profile: UserProfileData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
};

const UserProfileContext = createContext<UserProfileState | null>(null);

export function UserProfileProvider({ children }: { children: ReactNode }) {
  const { data: session, status } = useSession();
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!session?.user) return;
    try {
      const data = await apiClient.getUserProfile();
      setProfile(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch profile");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, [session?.user]);

  useEffect(() => {
    if (status === "loading") return;

    if (!session?.user) {
      setProfile(null);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    let cancelled = false;

    // Defer so priority loads (leaderboard, etc.) can run first
    const timeoutMs = 300;
    const id =
      typeof requestIdleCallback !== "undefined"
        ? requestIdleCallback(() => {
            if (cancelled) return;
            fetchProfile();
          }, { timeout: timeoutMs })
        : (setTimeout(() => {
            if (cancelled) return;
            fetchProfile();
          }, timeoutMs) as unknown as number);

    return () => {
      cancelled = true;
      if (typeof requestIdleCallback !== "undefined" && typeof id === "number") {
        cancelIdleCallback(id);
      } else if (typeof id === "number") {
        clearTimeout(id);
      }
    };
  }, [session, status, fetchProfile]);

  const refetch = useCallback(async () => {
    if (!session?.user) return;
    setLoading(true);
    await fetchProfile();
  }, [session?.user, fetchProfile]);

  const value: UserProfileState = {
    profile,
    loading: loading || status === "loading",
    error,
    refetch,
  };

  return (
    <UserProfileContext.Provider value={value}>
      {children}
    </UserProfileContext.Provider>
  );
}

export function useUserProfileContext(): UserProfileState {
  const ctx = useContext(UserProfileContext);
  if (ctx === null) {
    throw new Error("useUserProfileContext must be used within UserProfileProvider");
  }
  return ctx;
}
