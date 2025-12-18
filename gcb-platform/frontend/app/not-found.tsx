"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Home, Search, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="container py-16 max-w-2xl">
      <Card>
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 text-6xl font-bold text-[--ga-red]">404</div>
          <CardTitle className="text-2xl">Page Not Found</CardTitle>
          <CardDescription>
            The page you're looking for doesn't exist or has been moved.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild className="bg-[--ga-red] hover:bg-[--ga-dark-red]">
              <Link href="/">
                <Home className="mr-2 h-4 w-4" />
                Go Home
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/research">
                <Search className="mr-2 h-4 w-4" />
                Browse Leaderboard
              </Link>
            </Button>
            <Button
              variant="ghost"
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Button>
          </div>
          
          <div className="mt-8 pt-8 border-t">
            <p className="text-sm text-muted-foreground text-center">
              If you believe this is an error, please{" "}
              <a href="mailto:contact@gcb.app" className="text-[--ga-red] hover:underline">
                contact us
              </a>
              .
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
