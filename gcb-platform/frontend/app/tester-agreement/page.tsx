import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tester Agreement | Great Commission Benchmark",
  description: "Tester Agreement for the Great Commission Benchmark platform",
};

export default function TesterAgreementPage() {
  return (
    <div className="container py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Tester Agreement</CardTitle>
          <CardDescription>Last Updated: December 18, 2025</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none">
            <p className="text-muted-foreground">
              The full Tester Agreement document is available in the project repository. 
              For the complete legal text, please refer to{" "}
              <Link href="https://github.com/your-org/great-commission-benchmark/blob/main/documents/Tester-Agreement.md" 
                    className="text-[--ga-red] hover:underline">
                the Tester Agreement document
              </Link>.
            </p>
            
            <h2>Confidentiality Obligations</h2>
            <p>As a tester, you agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Not share test questions publicly</strong> - Do not post questions online or in forums</li>
              <li><strong>Not share with model providers</strong> - Do not share questions with AI companies</li>
              <li><strong>Not use for training</strong> - Do not use questions to train or fine-tune models</li>
              <li><strong>Report leaks</strong> - Report any suspected breaches of confidentiality</li>
            </ul>

            <h2>Consequences of Violation</h2>
            <p>Violations may result in:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Minor violations:</strong> Warning and re-confirmation</li>
              <li><strong>Major violations:</strong> Access revocation</li>
              <li><strong>Severe violations:</strong> Permanent ban and possible legal action</li>
            </ul>

            <h2>Why Confidentiality Matters</h2>
            <p>
              The integrity of the Great Commission Benchmark depends on maintaining the confidentiality 
              of test questions. If questions become publicly available or are shared with AI model 
              providers, they may be incorporated into training data, rendering our benchmark ineffective 
              at providing accurate, unbiased evaluations.
            </p>

            <h2>Contact</h2>
            <p>
              For questions about this Agreement, please contact us at{" "}
              <a href="mailto:contact@greatcommissionbenchmark.ai" className="text-[--ga-red] hover:underline">
                contact@greatcommissionbenchmark.ai
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
