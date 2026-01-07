"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

type Step = "select" | "payment" | "processing" | "results";

interface TestProgressIndicatorProps {
  currentStep: Step;
  className?: string;
}

const steps: { id: Step; label: string; shortLabel: string }[] = [
  { id: "select", label: "Select Model", shortLabel: "Select" },
  { id: "payment", label: "Payment", shortLabel: "Pay" },
  { id: "processing", label: "Processing", shortLabel: "Process" },
  { id: "results", label: "Results", shortLabel: "Results" },
];

export function TestProgressIndicator({
  currentStep,
  className,
}: TestProgressIndicatorProps) {
  const currentIndex = steps.findIndex((s) => s.id === currentStep);

  return (
    <div className={cn("mb-8", className)}>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isUpcoming = index > currentIndex;

          return (
            <div key={step.id} className="flex items-center flex-1 last:flex-none">
              {/* Step circle and label */}
              <div className="flex items-center gap-2">
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all",
                    isCompleted && "bg-[var(--ga-red)] text-white",
                    isCurrent && "bg-[var(--ga-red)] text-white ring-4 ring-[var(--ga-accent-red)]",
                    isUpcoming && "bg-muted text-muted-foreground"
                  )}
                >
                  {isCompleted ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span
                  className={cn(
                    "text-sm transition-colors hidden sm:inline",
                    isCurrent && "font-medium text-foreground",
                    !isCurrent && "text-muted-foreground"
                  )}
                >
                  {step.label}
                </span>
                <span
                  className={cn(
                    "text-sm transition-colors sm:hidden",
                    isCurrent && "font-medium text-foreground",
                    !isCurrent && "text-muted-foreground"
                  )}
                >
                  {step.shortLabel}
                </span>
              </div>

              {/* Connector line (not after last step) */}
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    "flex-1 h-1 mx-2 sm:mx-4 transition-colors",
                    index < currentIndex ? "bg-[var(--ga-red)]" : "bg-muted"
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

