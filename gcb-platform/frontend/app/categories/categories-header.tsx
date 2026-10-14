import { Grid3X3 } from "lucide-react";
import { GuardrailsAnimation } from "@/components/home/GuardrailsAnimation";

export function CategoriesHeader() {
  return (
    <div className="relative border-b border-white/[0.06] overflow-x-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 gradient-hero" />
      <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-40" />

      <div className="container relative py-8">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <Grid3X3 className="h-5 w-5 text-primary" />
              </div>
              <h1 className="text-3xl md:text-4xl font-light text-foreground">Categories</h1>
            </div>
            <p className="text-muted-foreground max-w-2xl font-light">
              Browse benchmark categories and see how AI models perform in each area of ministry and theological understanding
            </p>
          </div>
        </div>
      </div>

      {/* Guardrails Animation - positioned on right, allowed to overflow */}
      <div className="hidden lg:block absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none">
        <GuardrailsAnimation />
      </div>
    </div>
  );
}
