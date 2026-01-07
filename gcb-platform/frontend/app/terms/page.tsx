import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
          <CardTitle className="text-2xl">Terms of Service</CardTitle>
          <CardDescription>Last Updated: January 7, 2026</CardDescription>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none dark:prose-invert">
          
          {/* Section 1 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">1. Acceptance of Terms</h2>
            <p className="text-muted-foreground">
              By accessing or using the Great Commission Benchmark platform (the &quot;Service&quot;), you agree to be 
              bound by these Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, you may not access 
              or use the Service.
            </p>
            <p className="text-muted-foreground">
              We reserve the right to modify these Terms at any time. Material changes will be communicated through 
              the Service or via email. Your continued use of the Service after such modifications constitutes 
              acceptance of the updated Terms.
            </p>
          </section>

          {/* Section 2 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">2. Description of Service</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">2.1 What We Provide</h3>
            <p className="text-muted-foreground mb-2">The Great Commission Benchmark is a public-facing platform that:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Evaluates Large Language Models (LLMs) on their ability to support Great Commission Christians</li>
              <li>Publishes benchmark results to interactive leaderboards</li>
              <li>Enables volunteers to run tests against their preferred LLMs</li>
              <li>Provides informational insights for Christian organizations choosing AI tools</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">2.2 Important Disclaimers</h3>
            <p className="text-muted-foreground">
              <strong>This benchmark is for informational purposes only</strong> and does not constitute an endorsement 
              or recommendation of any AI model or service.
            </p>
            <p className="text-muted-foreground">
              <strong>Results reflect performance</strong> on specific test questions at a point in time and may not 
              predict performance on other tasks or future model versions.
            </p>
            <p className="text-muted-foreground">
              <strong>The Great Commission Benchmark is an independent project</strong> and is not affiliated with 
              any AI company or model provider.
            </p>
          </section>

          {/* Section 3 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">3. User Accounts and Registration</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">3.1 Account Creation</h3>
            <p className="text-muted-foreground mb-2">To use certain features of the Service, you must create an account. You agree to:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Provide accurate, current, and complete information during registration</li>
              <li>Maintain and promptly update your account information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Accept responsibility for all activities under your account</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">3.2 Account Eligibility</h3>
            <p className="text-muted-foreground">
              You must be at least 18 years old (or the age of majority in your jurisdiction) to create an account. 
              By creating an account, you represent and warrant that you meet this requirement.
            </p>
          </section>

          {/* Section 4 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">4. User Obligations and Acceptable Use</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">4.1 Acceptable Use</h3>
            <p className="text-muted-foreground mb-2">
              You agree to use the Service only for lawful purposes and in accordance with these Terms. You agree not to:
            </p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Violate any applicable laws or regulations</li>
              <li>Infringe upon the rights of others</li>
              <li>Transmit any harmful, offensive, or illegal content</li>
              <li>Attempt to gain unauthorized access to the Service or related systems</li>
              <li>Interfere with or disrupt the Service or servers</li>
              <li>Use automated systems to access the Service without permission</li>
              <li>Share test questions publicly or with AI model providers (see Section 4.2)</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">4.2 Tester Agreement and Confidentiality</h3>
            <p className="text-muted-foreground mb-2">If you run benchmark tests, you must agree to additional confidentiality terms:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li><strong>No public sharing:</strong> You may not post test questions online or in public forums</li>
              <li><strong>No provider sharing:</strong> You may not share questions with AI companies or model providers</li>
              <li><strong>No training use:</strong> You may not use questions to train or fine-tune models</li>
              <li><strong>Report leaks:</strong> You must report any suspected breaches of question confidentiality</li>
            </ul>
            <p className="text-muted-foreground mt-3 mb-2">Violation of these confidentiality terms may result in:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Warning and re-confirmation of agreement (minor/accidental violations)</li>
              <li>Access revocation (major/deliberate violations)</li>
              <li>Permanent ban and possible public disclosure (severe/malicious violations)</li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">5. Payment Terms</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">5.1 Pricing</h3>
            <p className="text-muted-foreground mb-2">The Service charges fees for running benchmark tests. Pricing includes:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li><strong>API costs:</strong> Pass-through costs for input and output tokens based on the selected model</li>
              <li><strong>Benchmark hosting contribution:</strong> A fixed $20 contribution per test to cover infrastructure and operations</li>
              <li><strong>Optional round-up:</strong> You may optionally round up your payment to support the initiative</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              All prices are displayed upfront before you commit to a test. You will see a detailed breakdown of costs before payment.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">5.2 Payment Processing</h3>
            <p className="text-muted-foreground">
              Payments are processed through Stripe. By making a payment, you agree to Stripe&apos;s terms of service. 
              We are not responsible for Stripe&apos;s services or any issues arising from payment processing.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">5.3 Refund Policy</h3>
            <p className="text-muted-foreground mb-2">Refunds are available in the following circumstances:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li><strong>Test failed to complete:</strong> If a test fails due to technical issues</li>
              <li><strong>Test stuck in error state:</strong> If a test becomes stuck and cannot complete</li>
              <li><strong>User reports issue before completion:</strong> If you report a problem before the test finishes</li>
            </ul>
            <p className="text-muted-foreground mt-3 mb-2">Refunds are <strong>not available</strong> for:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Successfully completed tests</li>
              <li>Dissatisfaction with test results</li>
              <li>Changes of mind after test completion</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              Before processing a refund, the system will attempt automatic retries for transient errors (API errors, timeouts, rate limiting).
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">5.4 No Guarantee of Results</h3>
            <p className="text-muted-foreground">
              We do not guarantee that any test will produce specific results or that results will meet your expectations. 
              Payment is for the execution of the test, not for any particular outcome.
            </p>
          </section>

          {/* Section 6 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">6. Intellectual Property</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">6.1 Our Intellectual Property</h3>
            <p className="text-muted-foreground mb-2">The Service, including but not limited to:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Benchmark methodology and test questions</li>
              <li>Website design and user interface</li>
              <li>Documentation and specifications</li>
              <li>Trademarks and logos</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              are owned by the Great Commission Benchmark project and its licensors. You may not copy, modify, 
              distribute, or create derivative works without explicit written permission.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">6.2 Open Source Components</h3>
            <p className="text-muted-foreground">
              Certain components of the Service may be released under open source licenses. Use of such components 
              is governed by their respective licenses.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">6.3 User-Submitted Content</h3>
            <p className="text-muted-foreground">
              By submitting test results, comments, or other content to the Service, you grant us a non-exclusive, 
              worldwide, royalty-free license to use, display, and distribute such content in connection with the Service. 
              You represent that you have the right to grant such license.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">6.4 Published Results</h3>
            <p className="text-muted-foreground">
              Once test results are published to the leaderboard, they become part of the public record and cannot be 
              deleted, even if you request account deletion. This ensures the integrity and historical accuracy of 
              benchmark data.
            </p>
          </section>

          {/* Section 7 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">7. Privacy and Data</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">7.1 Data Collection</h3>
            <p className="text-muted-foreground">
              We collect and process data as described in our Privacy Policy. By using the Service, you consent 
              to such collection and processing.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">7.2 Data Sharing</h3>
            <p className="text-muted-foreground mb-2">We may share data with:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li><strong>Public:</strong> Aggregate results published on leaderboards</li>
              <li><strong>Researchers:</strong> Anonymized data for research purposes (upon request)</li>
              <li><strong>Model providers:</strong> Their own model&apos;s results for transparency</li>
              <li><strong>Moderators:</strong> Full test data for verification purposes</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">7.3 Data Retention</h3>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Test data is retained indefinitely to maintain historical records</li>
              <li>User account data is retained until you request deletion</li>
              <li>Payment records are retained as required by law</li>
            </ul>
          </section>

          {/* Section 8 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">8. Disclaimers and Limitation of Liability</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">8.1 Service Provided &quot;As Is&quot;</h3>
            <p className="text-muted-foreground uppercase text-xs">
              THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS 
              OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, 
              OR NON-INFRINGEMENT.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">8.2 No Warranties</h3>
            <p className="text-muted-foreground mb-2">We do not warrant that:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>The Service will be uninterrupted, secure, or error-free</li>
              <li>Results will be accurate, complete, or reliable</li>
              <li>Defects will be corrected</li>
              <li>The Service is free of viruses or other harmful components</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">8.3 Results Disclaimer</h3>
            <p className="text-muted-foreground mb-2">Benchmark results are provided for informational purposes only. They do not:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Constitute professional advice or recommendations</li>
              <li>Guarantee future model performance</li>
              <li>Predict performance on tasks outside the benchmark scope</li>
              <li>Endorse or recommend any particular model or service</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              You acknowledge that you rely on results at your own risk and make decisions based on your own judgment.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">8.4 Third-Party Services</h3>
            <p className="text-muted-foreground mb-2">We are not responsible for:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Services provided by third parties (including but not limited to OpenRouter, model providers, Stripe)</li>
              <li>Issues arising from third-party service failures</li>
              <li>Content or services available through links to external sites</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">8.5 Limitation of Liability</h3>
            <p className="text-muted-foreground uppercase text-xs mb-3">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, OUR TOTAL LIABILITY FOR ANY CLAIMS ARISING FROM OR RELATED TO 
              THE SERVICE SHALL NOT EXCEED THE AMOUNT YOU PAID TO US IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM, 
              OR $100, WHICHEVER IS GREATER.
            </p>
            <p className="text-muted-foreground uppercase text-xs">WE SHALL NOT BE LIABLE FOR:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground text-xs uppercase">
              <li>Indirect, incidental, special, consequential, or punitive damages</li>
              <li>Loss of profits, data, or business opportunities</li>
              <li>Actions or omissions of third-party service providers</li>
              <li>Decisions made based on benchmark results</li>
            </ul>
          </section>

          {/* Section 9 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">9. Indemnification</h2>
            <p className="text-muted-foreground mb-2">
              You agree to indemnify, defend, and hold harmless the Great Commission Benchmark project, its operators, 
              and affiliates from any claims, damages, losses, liabilities, and expenses (including reasonable 
              attorneys&apos; fees) arising from:
            </p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Your use of the Service</li>
              <li>Your violation of these Terms</li>
              <li>Your violation of any rights of another party</li>
              <li>Content you submit to the Service</li>
            </ul>
          </section>

          {/* Section 10 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">10. Termination</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">10.1 Termination by You</h3>
            <p className="text-muted-foreground">
              You may stop using the Service at any time. You may request deletion of your account, subject to the 
              limitations in Section 6.4 regarding published results.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">10.2 Termination by Us</h3>
            <p className="text-muted-foreground mb-2">
              We may suspend or terminate your access to the Service at any time, with or without notice, for:
            </p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Violation of these Terms</li>
              <li>Violation of the tester agreement (Section 4.2)</li>
              <li>Fraudulent, abusive, or illegal activity</li>
              <li>Any other reason we deem necessary to protect the Service or its users</li>
            </ul>

            <h3 className="text-lg font-medium mt-4 mb-2">10.3 Effect of Termination</h3>
            <p className="text-muted-foreground mb-2">Upon termination:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Your right to use the Service immediately ceases</li>
              <li>Published results remain public (see Section 6.4)</li>
              <li>Provisions that by their nature should survive termination will remain in effect</li>
            </ul>
          </section>

          {/* Section 11 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">11. Modifications to the Service</h2>
            <p className="text-muted-foreground mb-2">We reserve the right to:</p>
            <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
              <li>Modify, suspend, or discontinue any aspect of the Service at any time</li>
              <li>Change pricing with reasonable notice</li>
              <li>Update features, functionality, or content</li>
              <li>Implement new policies or procedures</li>
            </ul>
            <p className="text-muted-foreground mt-2">
              We will make reasonable efforts to notify users of material changes, but are not obligated to do so 
              for all changes.
            </p>
          </section>

          {/* Section 12 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">12. Dispute Resolution</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">12.1 Governing Law</h3>
            <p className="text-muted-foreground">
              These Terms shall be governed by and construed in accordance with the laws of the State of Texas, 
              United States, without regard to its conflict of law provisions.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">12.2 Dispute Process</h3>
            <p className="text-muted-foreground mb-2">If you have a dispute with us, you agree to:</p>
            <ol className="list-decimal pl-6 space-y-1 text-muted-foreground">
              <li>First contact us directly to attempt to resolve the dispute</li>
              <li>Provide a written description of the issue</li>
              <li>Allow us a reasonable opportunity to address your concerns</li>
            </ol>

            <h3 className="text-lg font-medium mt-4 mb-2">12.3 Informal Resolution</h3>
            <p className="text-muted-foreground">
              We encourage informal resolution of disputes through direct communication before pursuing formal legal action.
            </p>
          </section>

          {/* Section 13 */}
          <section className="mb-8">
            <h2 className="text-xl font-semibold mt-6 mb-3">13. General Provisions</h2>
            
            <h3 className="text-lg font-medium mt-4 mb-2">13.1 Entire Agreement</h3>
            <p className="text-muted-foreground">
              These Terms, together with our Privacy Policy and any additional agreements you enter into (such as 
              the Tester Agreement), constitute the entire agreement between you and us regarding the Service.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">13.2 Severability</h3>
            <p className="text-muted-foreground">
              If any provision of these Terms is found to be unenforceable, the remaining provisions will remain 
              in full force and effect.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">13.3 Waiver</h3>
            <p className="text-muted-foreground">
              Our failure to enforce any provision of these Terms does not constitute a waiver of that provision 
              or any other provision.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">13.4 Assignment</h3>
            <p className="text-muted-foreground">
              You may not assign or transfer your rights or obligations under these Terms without our prior written 
              consent. We may assign or transfer these Terms without restriction.
            </p>

            <h3 className="text-lg font-medium mt-4 mb-2">13.5 Contact Information</h3>
            <p className="text-muted-foreground">
              For questions about these Terms, please contact us at{" "}
              <a href="mailto:legal@greatcommissionbenchmark.ai" className="text-[--ga-red] hover:underline">
                legal@greatcommissionbenchmark.ai
              </a>
            </p>
          </section>

          {/* Section 14 */}
          <section className="mb-4 p-4 bg-muted rounded-lg">
            <h2 className="text-xl font-semibold mb-3">14. Acknowledgment</h2>
            <p className="text-muted-foreground uppercase text-sm font-medium">
              BY USING THE SERVICE, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND AGREE TO BE BOUND BY 
              THESE TERMS OF SERVICE.
            </p>
          </section>

        </CardContent>
      </Card>
    </div>
  );
}
