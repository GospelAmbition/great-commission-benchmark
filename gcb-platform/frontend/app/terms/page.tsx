import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | Great Commission Benchmark",
  description: "Terms of Service for the Great Commission Benchmark platform",
};

export default function TermsPage() {
  return (
    <div className="container py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Terms of Service</CardTitle>
          <CardDescription>Last Updated: December 18, 2025</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none">
            <p className="text-muted-foreground">
              The full Terms of Service document is available in the project repository. 
              For the complete legal text, please refer to{" "}
              <Link href="https://github.com/your-org/great-commission-benchmark/blob/main/documents/Terms-of-Service.md" 
                    className="text-[--ga-red] hover:underline">
                the Terms of Service document
              </Link>.
            </p>
            
            <h2>Key Points</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>By using the Service, you agree to be bound by these Terms</li>
              <li>The benchmark is for informational purposes only and does not constitute an endorsement</li>
              <li>You must maintain confidentiality of test questions</li>
              <li>Payments are processed through Stripe</li>
              <li>Refunds are available for failed tests, not for completed tests</li>
              <li>Published results cannot be deleted</li>
            </ul>

            <h2>Contact</h2>
            <p>
              For questions about these Terms, please contact us at{" "}
              <a href="mailto:contact@gcb.app" className="text-[--ga-red] hover:underline">
                contact@gcb.app
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
