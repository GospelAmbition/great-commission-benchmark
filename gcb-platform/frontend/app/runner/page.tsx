import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Terminal, Download, Settings, BarChart3, Upload, Server, Laptop } from "lucide-react";

export default function RunnerPage() {
  return (
    <div className="container py-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Terminal className="h-10 w-10 text-[--ga-red]" />
          <h1 className="text-4xl font-bold">GCB Runner</h1>
        </div>
        <p className="mt-2 text-lg text-muted-foreground">
          Run the Great Commission Benchmark locally on any AI model
        </p>
      </div>

      {/* Hero Card */}
      <Card className="mb-8 border-[--ga-red]/20 bg-gradient-to-br from-background to-muted/30">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-semibold mb-3">Test Any Model, Anywhere</h2>
              <p className="text-muted-foreground mb-4">
                The GCB Runner is the official CLI tool for running the Great Commission Benchmark 
                on your own infrastructure. Perfect for testing local models, fine-tuned models, 
                or models not available through the platform.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                <Badge variant="secondary">OpenRouter</Badge>
                <Badge variant="secondary">OpenAI</Badge>
                <Badge variant="secondary">Anthropic</Badge>
                <Badge variant="secondary">LM Studio</Badge>
                <Badge variant="secondary">Ollama</Badge>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button variant="brand" size="lg" asChild>
                  <a href="https://pypi.org/project/gcb-runner/" target="_blank" rel="noopener noreferrer">
                    <Download className="h-4 w-4" />
                    Install from PyPI
                  </a>
                </Button>
                <Button variant="outline" size="lg" asChild>
                  <a href="https://github.com/great-commission-benchmark/gcb-runner" target="_blank" rel="noopener noreferrer">
                    View on GitHub
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Install */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Quick Start</CardTitle>
          <CardDescription>Get up and running in under a minute</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">1. Install</h3>
            <div className="bg-muted p-4 rounded-lg font-mono text-sm">
              pip install gcb-runner
            </div>
          </div>
          <div>
            <h3 className="font-medium mb-2">2. Configure</h3>
            <div className="bg-muted p-4 rounded-lg font-mono text-sm">
              gcb-runner config
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              You&apos;ll need an API key from your{" "}
              <a href="/dashboard/settings" className="text-[--ga-red] hover:underline">
                dashboard settings
              </a>.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">3. Run</h3>
            <div className="bg-muted p-4 rounded-lg font-mono text-sm">
              gcb-runner
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Launch the interactive menu and follow the guided setup.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Laptop className="h-5 w-5 text-[--ga-red]" />
              <CardTitle className="text-lg">Local Models</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Test models running on LM Studio, Ollama, or any OpenAI-compatible endpoint. 
              Perfect for fine-tuned models or private deployments.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-5 w-5 text-[--ga-red]" />
              <CardTitle className="text-lg">Cloud APIs</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Connect to OpenRouter, OpenAI, or Anthropic APIs directly. Access 100+ models 
              with your own API keys and usage limits.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[--ga-red]" />
              <CardTitle className="text-lg">Local Dashboard</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              View results in a local web dashboard. Generate HTML reports, compare runs, 
              and analyze performance before submitting.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-[--ga-red]" />
              <CardTitle className="text-lg">Submit to Leaderboard</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Upload verified results to the platform leaderboard. Submissions are reviewed 
              by moderators to ensure benchmark integrity.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Platform vs CLI */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Platform Tests vs CLI Submissions</CardTitle>
          <CardDescription>Choose the right approach for your needs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-2 font-medium">Aspect</th>
                  <th className="text-left py-3 px-2 font-medium">Platform Tests</th>
                  <th className="text-left py-3 px-2 font-medium">CLI Submissions</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-2 text-muted-foreground">Where run</td>
                  <td className="py-3 px-2">On the platform</td>
                  <td className="py-3 px-2">Locally via CLI</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-2 text-muted-foreground">Publishing</td>
                  <td className="py-3 px-2">Automatic</td>
                  <td className="py-3 px-2">Requires moderator review</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-2 text-muted-foreground">Cost</td>
                  <td className="py-3 px-2">Platform fee + model API cost</td>
                  <td className="py-3 px-2">Submission fee (you pay model costs)</td>
                </tr>
                <tr>
                  <td className="py-3 px-2 text-muted-foreground">Best for</td>
                  <td className="py-3 px-2">Quick results, individual testers</td>
                  <td className="py-3 px-2">Organizations, custom/local models</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Commands Reference */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Command Reference</CardTitle>
          <CardDescription>Common commands to get you started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-2">
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner</code>
                <span className="text-sm text-muted-foreground">Launch interactive menu</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner config</code>
                <span className="text-sm text-muted-foreground">Configure API keys and backends</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner test --model gpt-4o</code>
                <span className="text-sm text-muted-foreground">Run benchmark on a model</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner results</code>
                <span className="text-sm text-muted-foreground">View test results</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner view</code>
                <span className="text-sm text-muted-foreground">Open local web dashboard</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner upload --run 3</code>
                <span className="text-sm text-muted-foreground">Submit results to platform</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Get API Key CTA */}
      <Card className="border-[--ga-red]/30 bg-[--ga-red]/5">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Settings className="h-8 w-8 text-[--ga-red]" />
              <div>
                <h3 className="font-semibold">Ready to get started?</h3>
                <p className="text-sm text-muted-foreground">
                  Generate an API key in your dashboard settings
                </p>
              </div>
            </div>
            <Button variant="brand" asChild>
              <a href="/dashboard/settings">Get API Key →</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
