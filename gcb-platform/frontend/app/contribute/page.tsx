import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Terminal, Upload, Code, Heart, Users } from "lucide-react";

export default function ContributePage() {
  return (
    <div className="container py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900">Contribute</h1>
        <p className="mt-2 text-slate-600">
          Help build the Great Commission Benchmark community
        </p>
      </div>

      {/* Primary CTA - Become a Tester */}
      <Card className="mb-8 border-red-200 bg-red-50/50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Terminal className="h-6 w-6 text-red-700" />
            <div>
              <CardTitle className="text-slate-900">Become a Tester</CardTitle>
              <CardDescription className="text-slate-600">
                Run benchmark tests and help measure AI models for Great Commission work
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-600">
            Use our GCB Runner to run benchmark tests on any AI model—including local models, 
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
                Learn About GCB Runner →
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-red-700" />
              <CardTitle className="text-slate-900">Submit Test Results</CardTitle>
            </div>
            <CardDescription className="text-slate-600">
              Share your benchmark results with the community
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600">
              Have you run tests with the GCB Runner? Upload your results for moderator review.
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
              <Code className="h-5 w-5 text-red-700" />
              <CardTitle className="text-slate-900">Contribute to Development</CardTitle>
            </div>
            <CardDescription className="text-slate-600">
              Help improve the platform and benchmark
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600">
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
              <Heart className="h-5 w-5 text-red-700" />
              <CardTitle className="text-slate-900">Support the Project</CardTitle>
            </div>
            <CardDescription className="text-slate-600">
              Help keep the benchmark running
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600">
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
              <Users className="h-5 w-5 text-red-700" />
              <CardTitle className="text-slate-900">Volunteer</CardTitle>
            </div>
            <CardDescription className="text-slate-600">
              Join the team as a moderator or developer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600">
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
          <CardTitle className="text-slate-900">Join the Community</CardTitle>
          <CardDescription className="text-slate-600">
            Connect with others working on Great Commission AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-600">
            Join our Discord server to discuss results, share insights, get help with the GCB Runner, 
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
