import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AboutPage() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">About</h1>
        <p className="mt-2 text-muted-foreground">
          Learn about the Great Commission Benchmark methodology and mission
        </p>
      </div>

      <Tabs defaultValue="methodology" className="space-y-6">
        <TabsList>
          <TabsTrigger value="methodology">Methodology</TabsTrigger>
          <TabsTrigger value="scoring">Scoring</TabsTrigger>
          <TabsTrigger value="faq">FAQ</TabsTrigger>
          <TabsTrigger value="contact">Contact</TabsTrigger>
        </TabsList>

        <TabsContent value="methodology" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Our Mission</CardTitle>
            </CardHeader>
            <CardContent className="prose max-w-none">
              <p>
                The Great Commission Benchmark evaluates AI models on their ability to support
                Great Commission Christians—those called to make disciples of all nations.
              </p>
              <p>
                Unlike other benchmarks that test only knowledge, we test what AI can actually{" "}
                <em>do</em> for missionary work: evangelism, apologetics, discipleship tools, and
                more.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Three-Tier Evaluation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2">Tier 1: Task Capability (70%)</h3>
                <p className="text-muted-foreground">
                  Can the AI actually perform Great Commission tasks? This includes:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1 text-sm text-muted-foreground">
                  <li>Creating evangelistic content</li>
                  <li>Engaging in apologetics and defense of the faith</li>
                  <li>Developing discipleship tools and resources</li>
                  <li>Conducting missiological research</li>
                  <li>Creating prayer resources</li>
                  <li>Processing and explaining Scripture</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Tier 2: Doctrinal Fidelity (20%)</h3>
                <p className="text-muted-foreground">
                  Does the AI maintain theological accuracy and faithfulness to Christian doctrine?
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Tier 3: Worldview Confession (10%)</h3>
                <p className="text-muted-foreground">
                  Will the AI affirm Christian truth claims when directly asked?
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scoring" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Scoring System</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                The overall score is calculated using weighted tier scores:
              </p>
              <div className="bg-muted p-4 rounded-lg font-mono text-sm">
                Overall Score = (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)
              </div>
              <div>
                <h3 className="font-semibold mb-2">Verdict Scoring</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>ACCEPTED: 1.0 points</li>
                  <li>COMPROMISED: 0.5 points</li>
                  <li>HEDGED: 0.3 points</li>
                  <li>REFUSED: 0.0 points</li>
                  <li>ERROR: 0.0 points</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="faq" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Frequently Asked Questions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">How are models tested?</h3>
                <p className="text-sm text-muted-foreground">
                  Models are tested using a comprehensive question set covering all three tiers.
                  Each response is evaluated by an LLM-as-Judge system, with human moderators
                  reviewing a sample for quality assurance.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">How often is the benchmark updated?</h3>
                <p className="text-sm text-muted-foreground">
                  The benchmark is updated continuously as new tests are completed and verified by
                  moderators. New benchmark versions are released periodically with updated question
                  sets.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Can I submit my own test results?</h3>
                <p className="text-sm text-muted-foreground">
                  Yes! You can run tests through the platform or submit results via the CLI tool.
                  All submissions are reviewed by moderators before being added to the leaderboard.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contact" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contact</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Have questions or feedback? Reach out to us:
              </p>
              <div>
                <strong>Email:</strong>{" "}
                <a href="mailto:contact@example.com" className="text-[--ga-red] hover:underline">
                  contact@example.com
                </a>
              </div>
              <div>
                <strong>Discord:</strong>{" "}
                <a
                  href="https://discord.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[--ga-red] hover:underline"
                >
                  Join our server
                </a>
              </div>
              <div>
                <strong>GitHub:</strong>{" "}
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[--ga-red] hover:underline"
                >
                  View repository
                </a>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
