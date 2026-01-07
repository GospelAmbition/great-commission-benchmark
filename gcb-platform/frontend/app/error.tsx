"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="container flex items-center justify-center min-h-[60vh] py-12">
      <Card className="max-w-md w-full text-center">
        <CardHeader>
          <div className="flex justify-center mb-4">
            <AlertCircle className="h-16 w-16 text-red-700" />
          </div>
          <CardTitle className="text-2xl text-slate-900">Something Went Wrong</CardTitle>
          <CardDescription className="text-slate-600">
            An error occurred while loading this page.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {process.env.NODE_ENV === "development" && error.message && (
            <div className="p-3 bg-slate-100 rounded-lg text-left overflow-auto">
              <code className="text-xs text-slate-700">{error.message}</code>
            </div>
          )}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button onClick={reset}>Try Again</Button>
            <Button asChild variant="outline">
              <a href="/">Go Home</a>
            </Button>
          </div>
          <p className="text-xs text-slate-500 mt-4">
            If this problem persists, please{" "}
            <a href="mailto:contact@greatcommissionbenchmark.ai" className="text-red-700 hover:underline">
              contact us
            </a>
            .
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
