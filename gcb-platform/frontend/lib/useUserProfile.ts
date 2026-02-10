"use client";

import { useUserProfileContext } from "@/components/providers/UserProfileProvider";
import type { UserProfileData } from "@/components/providers/UserProfileProvider";

export type { UserProfileData };

function deriveFlags(profile: UserProfileData | null) {
  const canViewBenchmark = profile?.can_view_benchmark ?? false;
  const canEditBenchmark = profile?.can_edit_benchmark ?? false;
  const canModerate = profile?.can_moderate ?? false;
  const canManageBlog = profile?.can_manage_blog ?? false;
  const canAdmin = profile?.can_admin ?? false;
  const isAdmin = canAdmin || profile?.role === "admin";
  const isModerator = canModerate || profile?.role === "moderator" || profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin";
  const isBlogManager = canManageBlog || profile?.role === "blog_manager" || profile?.role === "benchmark_developer" || profile?.role === "admin";
  const isBenchmarkDeveloper = canEditBenchmark || profile?.role === "benchmark_developer" || profile?.role === "admin";
  return {
    canViewBenchmark,
    canEditBenchmark,
    canModerate,
    canManageBlog,
    canAdmin,
    isAdmin,
    isModerator,
    isBlogManager,
    isBenchmarkDeveloper,
  };
}

export function useUserProfile() {
  const { profile, loading, error, refetch } = useUserProfileContext();
  return {
    profile,
    loading,
    error,
    refetch,
    ...deriveFlags(profile),
  };
}
