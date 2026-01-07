"use client";

import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="bg-slate-50">
        <div className="container flex items-center justify-center min-h-screen py-12">
          <div className="max-w-md w-full text-center bg-white p-8 rounded-xl shadow-lg border border-slate-200">
            <div className="flex justify-center mb-4">
              <AlertTriangle className="h-16 w-16 text-red-700" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Something Went Wrong</h1>
            <p className="text-slate-600 mb-6">
              A critical error occurred. We apologize for the inconvenience.
            </p>
            {process.env.NODE_ENV === "development" && error.message && (
              <div className="p-3 bg-slate-100 rounded-lg text-left overflow-auto mb-4">
                <code className="text-xs text-slate-700">{error.message}</code>
              </div>
            )}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button onClick={reset} className="bg-red-700 text-white hover:bg-red-800">
                Try Again
              </Button>
              <Button variant="outline" asChild className="border-slate-300 text-slate-700">
                <a href="/">Go Home</a>
              </Button>
            </div>
            <p className="text-xs text-slate-500 mt-6">
              If this problem persists, please{" "}
              <a href="mailto:contact@greatcommissionbenchmark.ai" className="text-red-700 hover:underline">
                contact us
              </a>
              .
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
