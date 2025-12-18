import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function ContributePage() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Contribute</h1>
        <p className="mt-2 text-muted-foreground">
          Help build the Great Commission Benchmark community
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Run Benchmark Tests</CardTitle>
            <CardDescription>
              Test AI models and contribute results to the leaderboard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Run comprehensive benchmark tests on any AI model. Your results will be reviewed by
              moderators and added to the public leaderboard.
            </p>
            <Button asChild className="bg-[--ga-red] hover:bg-[--ga-dark-red]">
              <Link href="/tests/new">Run a Test →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Submit Fine-Tuned Model</CardTitle>
            <CardDescription>
              Share your custom fine-tuned model results
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Have a fine-tuned model you've tested? Submit your results via the CLI tool for
              community review.
            </p>
            <Button asChild variant="outline">
              <Link href="/contribute/submit">Submit Results →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contribute to Development</CardTitle>
            <CardDescription>
              Help improve the platform and benchmark
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Contribute code, report bugs, suggest features, or help with documentation.
            </p>
            <div className="flex gap-2">
              <Button asChild variant="outline">
                <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  GitHub →
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
                  Discord →
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Support the Project</CardTitle>
            <CardDescription>
              Help keep the benchmark running
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Running tests costs money. Consider adding a tip when you run a test, or support the
              project directly.
            </p>
            <Button asChild variant="outline">
              <Link href="/contribute/support">Learn More →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Join the Community</CardTitle>
            <CardDescription>
              Connect with others working on Great Commission AI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Join our Discord server to discuss results, share insights, and collaborate with
              others in the community.
            </p>
            <Button asChild variant="outline">
              <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
                Join Discord →
              </a>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
