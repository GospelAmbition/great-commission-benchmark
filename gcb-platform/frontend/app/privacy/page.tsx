import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | Great Commission Benchmark",
  description: "Privacy Policy for the Great Commission Benchmark platform",
};

export default function PrivacyPage() {
  return (
    <div className="container py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Privacy Policy</CardTitle>
          <CardDescription>Last Updated: December 18, 2025</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none">
            <p className="text-muted-foreground">
              The full Privacy Policy document is available in the project repository. 
              For the complete legal text, please refer to{" "}
              <Link href="https://github.com/your-org/great-commission-benchmark/blob/main/documents/Privacy-Policy.md" 
                    className="text-[--ga-red] hover:underline">
                the Privacy Policy document
              </Link>.
            </p>
            
            <h2>Data We Collect</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>Account information (email, name) via Google OAuth</li>
              <li>Test results and model responses</li>
              <li>Usage data and analytics</li>
              <li>Payment information (processed by Stripe)</li>
            </ul>

            <h2>How We Use Your Data</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>To provide and improve the Service</li>
              <li>To publish benchmark results on leaderboards</li>
              <li>For research and analysis (anonymized)</li>
              <li>To comply with legal obligations</li>
            </ul>

            <h2>Third-Party Services</h2>
            <p>We use:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Google OAuth:</strong> Authentication and user management</li>
              <li><strong>Stripe:</strong> Payment processing</li>
              <li><strong>OpenRouter:</strong> AI model API access</li>
              <li><strong>Umami:</strong> Privacy-respecting analytics</li>
            </ul>

            <h2>Your Rights</h2>
            <p>You have the right to access, correct, and delete your personal information, 
            subject to limitations regarding published test results.</p>

            <h2>Contact</h2>
            <p>
              For privacy questions, please contact us at{" "}
              <a href="mailto:privacy@greatcommissionbenchmark.ai" className="text-[--ga-red] hover:underline">
                privacy@greatcommissionbenchmark.ai
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
