import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Terminal, Download, Settings, BarChart3, Upload, Server, Laptop, Apple, Monitor, RefreshCw } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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
                The GCB Runner is the official command-line tool for running the Great Commission Benchmark 
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
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download Section */}
      <Card className="mb-8 border-[--ga-red]/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Download
          </CardTitle>
          <CardDescription>
            Download the standalone executable - no Python required
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="macos" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="macos" className="flex items-center gap-2">
                <Apple className="h-4 w-4" />
                macOS
              </TabsTrigger>
              <TabsTrigger value="linux" className="flex items-center gap-2">
                <Monitor className="h-4 w-4" />
                Linux
              </TabsTrigger>
              <TabsTrigger value="windows" className="flex items-center gap-2">
                <Monitor className="h-4 w-4" />
                Windows
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="macos" className="mt-4 space-y-4">
              <div className="grid gap-3">
                <Button variant="brand" size="lg" className="w-full justify-start" asChild>
                  <a href="/downloads/gcb-runner-macos-arm64" download>
                    <Download className="h-4 w-4 mr-2" />
                    Download for Apple Silicon (M1/M2/M3)
                  </a>
                </Button>
                <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                  <Download className="h-4 w-4 mr-2" />
                  Intel Mac — Coming Soon
                </Button>
              </div>
              <div className="bg-muted p-4 rounded-lg text-sm space-y-2">
                <p className="font-medium">After downloading:</p>
                <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                  <li>Open Terminal and navigate to your Downloads folder</li>
                  <li>Run: <code className="bg-background px-1 rounded">chmod +x gcb-runner-macos-arm64</code></li>
                  <li>Run: <code className="bg-background px-1 rounded">./gcb-runner-macos-arm64</code></li>
                </ol>
                <p className="text-muted-foreground mt-2">
                  <strong>Note:</strong> You may need to allow the app in System Settings → Privacy & Security.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="linux" className="mt-4 space-y-4">
              <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                <Download className="h-4 w-4 mr-2" />
                Linux (x64) — Coming Soon
              </Button>
              <div className="bg-muted p-4 rounded-lg text-sm">
                <p className="text-muted-foreground">
                  Linux builds are in development. Check back soon or contact us if you need early access.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="windows" className="mt-4 space-y-4">
              <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                <Download className="h-4 w-4 mr-2" />
                Windows (x64) — Coming Soon
              </Button>
              <div className="bg-muted p-4 rounded-lg text-sm">
                <p className="text-muted-foreground">
                  Windows builds are in development. Check back soon or contact us if you need early access.
                </p>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-6 pt-6 border-t">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
              <RefreshCw className="h-4 w-4" />
              <span>Auto-updates included - gcb-runner will notify you when updates are available</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Verify downloads using SHA256 hashes from{" "}
              <a href="/downloads/manifest.json" className="text-[--ga-red] hover:underline">
                manifest.json
              </a>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Start */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Quick Start</CardTitle>
          <CardDescription>Get up and running in under a minute</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">1. Configure</h3>
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
            <h3 className="font-medium mb-2">2. Run</h3>
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
          <CardTitle>Platform Tests vs GCB Runner Submissions</CardTitle>
          <CardDescription>Choose the right approach for your needs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-2 font-medium">Aspect</th>
                  <th className="text-left py-3 px-2 font-medium">Platform Tests</th>
                  <th className="text-left py-3 px-2 font-medium">GCB Runner Submissions</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-2 text-muted-foreground">Where run</td>
                  <td className="py-3 px-2">On the platform</td>
                  <td className="py-3 px-2">Locally via GCB Runner</td>
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
                <code className="bg-muted px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner update</code>
                <span className="text-sm text-muted-foreground">Check for and install updates</span>
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
              <a href="/dashboard/settings">Get API Key</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
