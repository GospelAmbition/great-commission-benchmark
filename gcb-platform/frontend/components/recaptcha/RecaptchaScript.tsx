"use client";

import Script from "next/script";

/**
 * Loads reCAPTCHA v3 script only on pages that need it (contact, newsletter).
 * Prevents the reCAPTCHA badge from appearing site-wide.
 */
export function RecaptchaScript() {
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
  if (!siteKey) return null;

  return (
    <Script
      src={`https://www.google.com/recaptcha/api.js?render=${siteKey}`}
      strategy="afterInteractive"
    />
  );
}
