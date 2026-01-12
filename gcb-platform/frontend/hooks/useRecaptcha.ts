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

/**
 * Wait for reCAPTCHA to be loaded with a timeout
 */
function waitForRecaptcha(timeout: number = 5000): Promise<boolean> {
  return new Promise((resolve) => {
    if (typeof window === "undefined") {
      resolve(false);
      return;
    }

    // If already loaded, resolve immediately
    if (window.grecaptcha) {
      resolve(true);
      return;
    }

    // Wait for script to load
    const startTime = Date.now();
    const checkInterval = setInterval(() => {
      if (window.grecaptcha) {
        clearInterval(checkInterval);
        resolve(true);
      } else if (Date.now() - startTime > timeout) {
        clearInterval(checkInterval);
        resolve(false);
      }
    }, 100);
  });
}

export function useRecaptcha() {
  const executeRecaptcha = useCallback(async (action: string = "newsletter_subscribe"): Promise<string | null> => {
    const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
    
    if (!siteKey) {
      console.warn("reCAPTCHA site key not configured");
      return null;
    }

    // Wait for reCAPTCHA to be loaded (up to 5 seconds)
    const isLoaded = await waitForRecaptcha(5000);
    if (!isLoaded) {
      console.error("reCAPTCHA script failed to load within timeout");
      return null;
    }

    if (typeof window === "undefined" || !window.grecaptcha) {
      console.error("reCAPTCHA not available");
      return null;
    }

    return new Promise((resolve) => {
      try {
        window.grecaptcha.ready(() => {
          window.grecaptcha
            .execute(siteKey, { action })
            .then((token: string) => {
              resolve(token);
            })
            .catch((error: Error) => {
              console.error("reCAPTCHA execution error:", error);
              resolve(null);
            });
        });
      } catch (error) {
        console.error("reCAPTCHA error:", error);
        resolve(null);
      }
    });
  }, []);

  return { executeRecaptcha };
}
