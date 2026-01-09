"use client";

import { useCallback } from "react";

declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (siteKey: string, options: { action: string }) => Promise<string>;
    };
  }
}

export function useRecaptcha() {
  const executeRecaptcha = useCallback(async (action: string = "newsletter_subscribe"): Promise<string | null> => {
    const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
    
    if (!siteKey) {
      console.warn("reCAPTCHA site key not configured");
      return null;
    }

    return new Promise((resolve) => {
      if (typeof window === "undefined" || !window.grecaptcha) {
        console.warn("reCAPTCHA not loaded");
        resolve(null);
        return;
      }

      window.grecaptcha.ready(() => {
        window.grecaptcha
          .execute(siteKey, { action })
          .then((token: string) => {
            resolve(token);
          })
          .catch((error: Error) => {
            console.error("reCAPTCHA error:", error);
            resolve(null);
          });
      });
    });
  }, []);

  return { executeRecaptcha };
}
