"use client";

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
 * Displays a provider's brand icon from Simple Icons CDN
 * Falls back to first letter of provider name when icon is unavailable
 */
export function ProviderIcon({
  provider,
  size = 16,
  className,
  showFallbackContainer = true,
}: ProviderIconProps) {
  const iconUrl = getProviderIconUrl(provider);

  if (!iconUrl) {
    // Fallback to first letter
    if (showFallbackContainer) {
      return (
        <div
          className={cn(
            "flex items-center justify-center rounded bg-white/[0.08] shrink-0",
            className
          )}
          style={{ width: size + 4, height: size + 4 }}
        >
          <span
            className="font-medium text-muted-foreground uppercase"
            style={{ fontSize: size * 0.6 }}
          >
            {provider.charAt(0)}
          </span>
        </div>
      );
    }
    return (
      <span
        className={cn("font-medium text-muted-foreground uppercase", className)}
        style={{ fontSize: size * 0.6 }}
      >
        {provider.charAt(0)}
      </span>
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
    />
  );
}
