"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";
import { isNewsletterActionPath } from "@/lib/newsletter-privacy";

export function UmamiAnalytics() {
  const pathname = usePathname();
  const scriptUrl = process.env.NEXT_PUBLIC_UMAMI_SCRIPT_URL;
  const websiteId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

  if (!scriptUrl || !websiteId || !pathname || isNewsletterActionPath(pathname)) {
    return null;
  }

  return (
    <Script
      src={scriptUrl}
      data-website-id={websiteId}
      strategy="afterInteractive"
    />
  );
}
