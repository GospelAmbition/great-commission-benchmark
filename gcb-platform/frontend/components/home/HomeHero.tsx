import Link from "next/link";
import { NewsletterButton } from "@/components/marketing/NewsletterOffer";
import { Button } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import { GuardrailsAnimation } from "@/components/home/GuardrailsAnimation";

export function HomeHero() {
  return (
    <section className="relative overflow-hidden">
      {/* Background with subtle gradient */}
      <div className="absolute inset-0 gradient-hero" />

      {/* Red glow effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] gradient-red-glow opacity-50" />

      {/* Grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '60px 60px'
        }}
      />

      <div className="container relative py-16 md:py-24">
        <div className="flex items-center justify-between">
          <div className="max-w-3xl animate-fade-in-up">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-light text-foreground mb-6 leading-tight tracking-tight">
              Evaluating AI for the
              <span className="block text-primary font-light text-5xl md:text-6xl lg:text-7xl">Great Commission</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl leading-relaxed">
              We measure which AI models meaningfully support gospel outreach and which oppose it.
            </p>
            <div className="flex flex-wrap gap-3">
            <Button asChild size="lg" className="text-base px-8">
              <Link href="/leaderboard">
                View Full Leaderboard
                <ChevronRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <NewsletterButton source="home_hero" variant="outline" size="lg">Get the GCB digest</NewsletterButton>
            </div>
          </div>

          {/* Guardrails Animation - hidden on smaller screens */}
          <div className="hidden lg:block shrink-0">
            <GuardrailsAnimation />
          </div>
        </div>
      </div>
    </section>
  );
}
