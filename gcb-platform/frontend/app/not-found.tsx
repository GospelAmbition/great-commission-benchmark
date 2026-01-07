import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function NotFound() {
  return (
    <div className="container flex items-center justify-center min-h-[60vh] py-12">
      <Card className="max-w-md w-full text-center">
        <CardHeader>
          <div className="mx-auto mb-4 text-6xl font-bold text-red-700">404</div>
          <CardTitle className="text-2xl text-slate-900">Page Not Found</CardTitle>
          <CardDescription className="text-slate-600">
            The page you&apos;re looking for doesn&apos;t exist or has been moved.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild>
              <Link href="/">Go Home</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/research">View Research</Link>
            </Button>
          </div>
          <p className="text-xs text-slate-500 mt-4">
            If you believe this is an error, please{" "}
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
