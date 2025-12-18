"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Home, RefreshCw, AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console or error reporting service
    console.error("Global application error:", error);
  }, [error]);

  return (
    <html lang="en">
      <body>
        <div className="container py-16 max-w-2xl">
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4">
                <AlertTriangle className="h-16 w-16 text-[--ga-red] mx-auto" />
              </div>
              <CardTitle className="text-2xl">Critical Error</CardTitle>
              <CardDescription>
                A critical error occurred. Please refresh the page or contact support.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={reset}
                  className="bg-[--ga-red] hover:bg-[--ga-dark-red]"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Page
                </Button>
                <Button asChild variant="outline">
                  <Link href="/">
                    <Home className="mr-2 h-4 w-4" />
                    Go Home
                  </Link>
                </Button>
              </div>

              <div className="mt-8 pt-8 border-t">
                <p className="text-sm text-muted-foreground text-center">
                  If this problem persists, please{" "}
                  <a href="mailto:contact@gcb.app" className="text-[--ga-red] hover:underline">
                    contact support
                  </a>
                  .
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </body>
    </html>
  );
}
