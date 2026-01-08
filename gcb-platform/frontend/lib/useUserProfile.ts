"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { apiClient, UserProfile } from "./api";

export interface UserProfileData extends UserProfile {
  tester_agreement_accepted?: boolean;
}

export function useUserProfile() {
  const { data: session, status } = useSession();
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProfile() {
      if (status === "loading") return;
      
      if (!session?.user) {
        setProfile(null);
        setLoading(false);
        return;
      }

      try {
        const data = await apiClient.getProfile();
        setProfile(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch profile");
        setProfile(null);
      } finally {
        setLoading(false);
      }
    }

    fetchProfile();
  }, [session, status]);

  return {
    profile,
    loading: loading || status === "loading",
    error,
    isAdmin: profile?.role === "admin",
    isModerator: profile?.role === "moderator" || profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin",
    isBlogManager: profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin",
    isBenchmarkDeveloper: profile?.role === "benchmark_developer" || profile?.role === "admin",
  };
}
