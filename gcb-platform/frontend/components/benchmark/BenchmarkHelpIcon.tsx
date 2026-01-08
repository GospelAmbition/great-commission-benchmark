"use client";

import { HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BenchmarkLegendModal } from "./BenchmarkLegendModal";

interface BenchmarkHelpIconProps {
  /** Size variant */
  size?: "sm" | "default" | "lg";
  /** Optional: highlight a specific category code in the modal */
  highlightCategory?: string;
  /** Additional CSS classes */
  className?: string;
  /** Show as inline (no button wrapper) */
  inline?: boolean;
}

/**
 * A small help icon that opens the BenchmarkLegendModal when clicked.
 * Place this near any chart, table, or score display that shows benchmark data.
 */
export function BenchmarkHelpIcon({
  size = "default",
  highlightCategory,
  className = "",
  inline = false,
}: BenchmarkHelpIconProps) {
  const sizeClasses = {
    sm: { button: "h-5 w-5", icon: "h-3 w-3" },
    default: { button: "h-6 w-6", icon: "h-4 w-4" },
    lg: { button: "h-8 w-8", icon: "h-5 w-5" },
  };

  const sizes = sizeClasses[size];

  const trigger = inline ? (
    <button
      className={`inline-flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors ${className}`}
      title="View benchmark categories"
    >
      <HelpCircle className={sizes.icon} />
      <span className="sr-only">View benchmark categories</span>
    </button>
  ) : (
    <Button
      variant="ghost"
      size="icon"
      className={`${sizes.button} text-muted-foreground hover:text-foreground ${className}`}
      title="View benchmark categories"
    >
      <HelpCircle className={sizes.icon} />
      <span className="sr-only">View benchmark categories</span>
    </Button>
  );

  return (
    <BenchmarkLegendModal
      trigger={trigger}
      highlightCategory={highlightCategory}
    />
  );
}

// Export an index file helper
export { BenchmarkLegendModal, BenchmarkInlineLegend } from "./BenchmarkLegendModal";
