"use client";

import { Suspense, useEffect, useRef, type RefObject, type ComponentProps } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { trackEvent } from "@/lib/analytics";
import { NEWSLETTER_PROMISE, type NewsletterSource } from "@/lib/newsletter";

type NewsletterButtonProps = {
  source: NewsletterSource;
  children?: React.ReactNode;
  variant?: ComponentProps<typeof Button>["variant"];
  size?: ComponentProps<typeof Button>["size"];
  className?: string;
};

function NewsletterImpression({ source, anchor }: { source: NewsletterSource; anchor: RefObject<HTMLAnchorElement | null> }) {
  const pathname = usePathname();
  const query = useSearchParams()?.toString() ?? "";
  const ref = anchor;
  useEffect(() => {
    const element = ref.current;
    if (!element || typeof IntersectionObserver === "undefined") return;
    let recorded = false;
    const observer = new IntersectionObserver(entries => {
      if (!recorded && entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= 0.5)) {
        recorded = true;
        trackEvent("newsletter_offer_impression", { source, path: pathname });
        observer.disconnect();
      }
    }, { threshold: 0.5 });
    observer.observe(element);
    return () => observer.disconnect();
  }, [source, pathname, query, ref]);
  return null;
}

export function NewsletterButton({ source, children = "Subscribe", variant = "default", size = "default", className }: NewsletterButtonProps) {
  const pathname = usePathname();
  const ref = useRef<HTMLAnchorElement>(null);
  if (pathname === "/newsletter" && (source === "header" || source === "footer")) return null;
  return <Button asChild variant={variant} size={size} className={className}>
    <Link ref={ref} href={`/newsletter?source=${source}`} onClick={() => trackEvent("newsletter_cta_click", { source, path: pathname })}>{children}<Suspense fallback={null}><NewsletterImpression source={source} anchor={ref} /></Suspense></Link>
  </Button>;
}

export function NewsletterOffer({ source, title = "Get the GCB digest", compact = false }: { source: NewsletterSource; title?: string; compact?: boolean }) {
  const pathname = usePathname();
  if (pathname === "/newsletter" && source === "footer") return null;
  return <aside aria-label="GCB newsletter" className={`rounded-xl border border-primary/20 bg-primary/5 ${compact ? "p-4" : "p-6 md:p-8"} flex flex-col sm:flex-row sm:items-center justify-between gap-5`}>
    <div className="min-w-0 max-w-2xl">
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      <p className="mt-2 text-sm text-muted-foreground">{NEWSLETTER_PROMISE}</p>
    </div>
    <NewsletterButton source={source} className="w-full sm:w-auto" />
  </aside>;
}
