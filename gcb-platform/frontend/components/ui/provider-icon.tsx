"use client";

import { useState } from "react";
import { getProviderIconUrl } from "@/lib/provider-icons";
import { cn } from "@/lib/utils";

export interface ProviderIconProps {
  /** The provider identifier (e.g., "openai", "anthropic") */
  provider: string;
  /** Icon size in pixels (default: 16) */
  size?: number;
  /** Additional CSS classes */
  className?: string;
  /** Whether to show fallback letter in a styled container (default: true) */
  showFallbackContainer?: boolean;
}

/**
 * Get initials from provider name (handles multi-word names)
 * e.g., "mistral-ai" -> "MA", "openai" -> "O"
 */
function getInitials(provider: string): string {
  // Handle provider names with separators (hyphens, underscores, spaces)
  const parts = provider.split(/[-_\s]+/);
  if (parts.length > 1) {
    // Multi-word: use first letter of each word (max 2)
    return parts
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("");
  }
  // Single word: use first letter
  return provider.charAt(0).toUpperCase();
}

/**
 * Fallback component that shows provider initials
 */
function InitialsFallback({
  provider,
  size,
  className,
  showFallbackContainer,
}: ProviderIconProps) {
  const initials = getInitials(provider);
  
  if (showFallbackContainer) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded bg-white/[0.08] shrink-0",
          className
        )}
        style={{ width: size! + 4, height: size! + 4 }}
      >
        <span
          className="font-medium text-muted-foreground uppercase"
          style={{ fontSize: (size || 16) * 0.6 }}
        >
          {initials}
        </span>
      </div>
    );
  }
  return (
    <span
      className={cn("font-medium text-muted-foreground uppercase", className)}
      style={{ fontSize: (size || 16) * 0.6 }}
    >
      {initials}
    </span>
  );
}

/**
 * Displays a provider's brand icon from Simple Icons CDN
 * Automatically falls back to initials when icon is unavailable or fails to load
 * No manual updates needed - unknown providers automatically get initials
 */
export function ProviderIcon({
  provider,
  size = 16,
  className,
  showFallbackContainer = true,
}: ProviderIconProps) {
  const [imageError, setImageError] = useState(false);
  const iconUrl = getProviderIconUrl(provider);

  // If no URL to try, or image failed to load, show initials
  if (!iconUrl || imageError) {
    return (
      <InitialsFallback
        provider={provider}
        size={size}
        className={className}
        showFallbackContainer={showFallbackContainer}
      />
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={iconUrl}
      alt={`${provider} logo`}
      width={size}
      height={size}
      className={cn(
        "shrink-0 invert brightness-[0.7] opacity-80",
        className
      )}
      loading="lazy"
      onError={() => {
        // If image fails to load, fall back to initials
        setImageError(true);
      }}
    />
  );
}
