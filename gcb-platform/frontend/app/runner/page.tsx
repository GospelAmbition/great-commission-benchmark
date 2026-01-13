import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Terminal, Download, BarChart3, Upload, Server, Laptop, Apple, Monitor, RefreshCw, Play } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";

export const metadata: Metadata = generatePageMetadata({
  title: "GCB Runner - Command Line Tool",
  description: "Run benchmark tests on any AI model using the GCB Runner CLI tool. Test local models, fine-tuned models, or cloud APIs. Submit results to the public leaderboard.",
  path: "/runner",
  keywords: ["CLI", "command line", "runner", "testing", "local models", "API", "benchmark tool"],
});

export default function RunnerPage() {
  return (
    <div className="container py-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Terminal className="h-10 w-10 text-primary" />
          <h1 className="text-4xl font-bold text-foreground">GCB Runner</h1>
        </div>
        <p className="mt-2 text-lg text-muted-foreground">
          Run the Great Commission Benchmark locally on any AI model
        </p>
      </div>

      {/* Hero Card */}
      <Card className="mb-8 border-primary/20 bg-primary/5">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-semibold text-foreground mb-3">Test Any Model, Anywhere</h2>
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
            <div className="w-full md:w-96 flex-shrink-0">
              <div className="aspect-video bg-white/[0.03] border border-white/[0.08] rounded-lg flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center border-2 border-primary/40">
                    <Play className="h-8 w-8 text-primary ml-1" fill="currentColor" />
                  </div>
                </div>
                <div className="absolute bottom-4 left-4 right-4 text-center">
                  <p className="text-xs text-muted-foreground">Video coming soon</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download Section */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Download className="h-5 w-5" />
            Download
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Download the standalone executable - no Python required
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="macos" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-white/[0.03] border border-white/[0.08]">
              <TabsTrigger value="macos" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                <Apple className="h-4 w-4" />
                macOS
              </TabsTrigger>
              <TabsTrigger value="linux" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                <Monitor className="h-4 w-4" />
                Linux
              </TabsTrigger>
              <TabsTrigger value="windows" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                <Monitor className="h-4 w-4" />
                Windows
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="macos" className="mt-4 space-y-4">
              <div className="grid gap-3">
                <Button variant="brand" size="lg" className="w-full justify-start" asChild>
                  <a href="/downloads/gcb-runner-macos-arm64" download>
                    <Download className="h-4 w-4 mr-2" />
                    Download for Apple Silicon (M series)
                  </a>
                </Button>
              </div>
              <div className="bg-white/[0.03] border border-white/[0.08] p-4 rounded-lg text-sm space-y-2">
                <p className="font-medium text-foreground">After downloading:</p>
                <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                  <li>Open Terminal and navigate to your Downloads folder</li>
                  <li>Run: <code className="bg-white/[0.05] text-foreground px-1 rounded">chmod +x gcb-runner-macos-arm64</code></li>
                  <li>Run: <code className="bg-white/[0.05] text-foreground px-1 rounded">./gcb-runner-macos-arm64</code></li>
                </ol>
                <p className="text-muted-foreground mt-2">
                  <strong className="text-foreground">Note:</strong> You may need to allow the app in System Settings → Privacy & Security.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="linux" className="mt-4 space-y-4">
              <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                <Download className="h-4 w-4 mr-2" />
                Linux (x64) — Coming Soon
              </Button>
              <div className="bg-white/[0.03] border border-white/[0.08] p-4 rounded-lg text-sm">
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
              <div className="bg-white/[0.03] border border-white/[0.08] p-4 rounded-lg text-sm">
                <p className="text-muted-foreground">
                  Windows builds are in development. Check back soon or contact us if you need early access.
                </p>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-6 pt-6 border-t border-border">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
              <RefreshCw className="h-4 w-4" />
              <span>Auto-updates included - gcb-runner will notify you when updates are available</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Verify downloads using SHA256 hashes from{" "}
              <a href="/downloads/manifest.json" className="text-primary hover:underline">
                manifest.json
              </a>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Laptop className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg text-foreground">Local Models</CardTitle>
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
              <Server className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg text-foreground">Cloud APIs</CardTitle>
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
              <BarChart3 className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg text-foreground">Local Dashboard</CardTitle>
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
              <Upload className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg text-foreground">Submit to Leaderboard</CardTitle>
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
    </div>
  );
}
