"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";

// Signed-in / internal areas where the public help widget should not appear.
const HIDDEN_PATH_PREFIXES = [
  "/admin",
  "/blog-manager",
  "/moderator",
  "/dashboard",
  "/profile",
  "/runner",
];

function isHiddenPath(pathname: string | null) {
  if (!pathname) return false;
  return HIDDEN_PATH_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );
}

export function HelpinatorWidget() {
  const pathname = usePathname();
  const host = process.env.NEXT_PUBLIC_HELPINATOR_HOST;
  const widgetId = process.env.NEXT_PUBLIC_HELPINATOR_WIDGET_ID;

  if (!host || !widgetId || isHiddenPath(pathname)) {
    return null;
  }

  // Styling overrides (--helpinator-*) live in app/globals.css.
  return (
    <>
      <Script
        src={`${host.replace(/\/$/, "")}/js/helpinator-widget.iife.js`}
        strategy="lazyOnload"
      />
      <helpinator-widget host={host} widget-id={widgetId} />
    </>
  );
}
