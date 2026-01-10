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
        const data = await apiClient.getUserProfile();
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

  // Permission-based checks (preferred)
  const canViewBenchmark = profile?.can_view_benchmark ?? false;
  const canEditBenchmark = profile?.can_edit_benchmark ?? false;
  const canModerate = profile?.can_moderate ?? false;
  const canManageBlog = profile?.can_manage_blog ?? false;
  const canAdmin = profile?.can_admin ?? false;
  
  // Legacy role-based checks for backward compatibility
  const isAdmin = canAdmin || profile?.role === "admin";
  const isModerator = canModerate || profile?.role === "moderator" || profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin";
  const isBlogManager = canManageBlog || profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin";
  const isBenchmarkDeveloper = canEditBenchmark || profile?.role === "benchmark_developer" || profile?.role === "admin";
  
  return {
    profile,
    loading: loading || status === "loading",
    error,
    // Permission flags
    canViewBenchmark,
    canEditBenchmark,
    canModerate,
    canManageBlog,
    canAdmin,
    // Legacy role-based flags (for backward compatibility)
    isAdmin,
    isModerator,
    isBlogManager,
    isBenchmarkDeveloper,
  };
}
