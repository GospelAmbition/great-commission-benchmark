import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Terminal, Upload, Code, Heart, Users } from "lucide-react";

export default function ContributePage() {
  return (
    <div className="container py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Contribute</h1>
        <p className="mt-2 text-muted-foreground">
          Help build the Great Commission Benchmark community
        </p>
      </div>

      {/* Primary CTA - Become a Tester */}
      <Card className="mb-8 border-[--ga-red]/20 bg-gradient-to-br from-background to-muted/30">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Terminal className="h-6 w-6 text-[--ga-red]" />
            <div>
              <CardTitle>Become a Tester</CardTitle>
              <CardDescription>
                Run benchmark tests and help measure AI models for Great Commission work
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Use our CLI tool to run benchmark tests on any AI model—including local models, 
            fine-tuned models, or cloud APIs. Your results will be reviewed by moderators 
            and added to the public leaderboard.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="brand">
              <Link href="/dashboard">
                <Terminal className="h-4 w-4 mr-2" />
                Get Started
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/runner">
                Learn About CLI Tool →
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-[--ga-red]" />
              <CardTitle>Submit Test Results</CardTitle>
            </div>
            <CardDescription>
              Share your benchmark results with the community
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Have you run tests with the CLI tool? Upload your results for moderator review.
              Approved results are added to the public leaderboard.
            </p>
            <Button asChild variant="outline">
              <Link href="/dashboard">Upload Results →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Code className="h-5 w-5 text-[--ga-red]" />
              <CardTitle>Contribute to Development</CardTitle>
            </div>
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
            <div className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-[--ga-red]" />
              <CardTitle>Support the Project</CardTitle>
            </div>
            <CardDescription>
              Help keep the benchmark running
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              The Great Commission Benchmark is a community project. Your support helps cover 
              infrastructure costs and enables continued development.
            </p>
            <Button asChild variant="outline">
              <Link href="/contribute/support">Donate →</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-[--ga-red]" />
              <CardTitle>Volunteer</CardTitle>
            </div>
            <CardDescription>
              Join the team as a moderator or developer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Help review submissions, develop new features, write documentation, or spread 
              the word about the benchmark.
            </p>
            <Button asChild variant="outline">
              <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
                Join Discord →
              </a>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Community Banner */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Join the Community</CardTitle>
          <CardDescription>
            Connect with others working on Great Commission AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Join our Discord server to discuss results, share insights, get help with the CLI tool, 
            and collaborate with others in the community.
          </p>
          <Button asChild variant="outline">
            <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
              Join Discord →
            </a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
