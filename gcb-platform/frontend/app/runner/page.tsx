import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Terminal, Download, BarChart3, Upload, Server, Laptop, Apple, RefreshCw, Play, Code, ChevronDown, ExternalLink } from "lucide-react";
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

      {/* Quick Install for macOS */}
      <Card className="mb-6 border-green-500/30 bg-green-500/5">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Apple className="h-5 w-5 text-green-500" />
            <CardTitle className="text-lg text-foreground">Quick Install for macOS</CardTitle>
            <Badge variant="outline" className="ml-2 border-green-500/50 text-green-500">Recommended</Badge>
          </div>
          <CardDescription className="text-muted-foreground">
            One command installs everything — no Python required
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-black/40 border border-white/10 rounded-lg p-4 font-mono text-sm">
            <div className="flex items-center justify-between gap-4">
              <code className="text-green-400 break-all">
                curl -fsSL https://greatcommissionbenchmark.ai/install.sh | bash
              </code>
            </div>
          </div>
          <div className="mt-4 text-sm text-muted-foreground space-y-2">
            <p>This installer will:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Detect your Mac type (Apple Silicon or Intel)</li>
              <li>Download and verify the latest GCB Runner</li>
              <li>Handle macOS security settings automatically</li>
              <li>Install to your PATH for easy access</li>
            </ul>
          </div>
          <div className="mt-4 pt-4 border-t border-white/10">
            <p className="text-xs text-muted-foreground">
              Works on Apple Silicon (M1/M2/M3/M4) Macs.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Manual Download Section */}
      <Card className="mb-6">
        <details className="group">
          <summary className="cursor-pointer list-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-foreground">
                <Download className="h-5 w-5" />
                Manual Download
                <ChevronDown className="h-4 w-4 ml-auto group-open:rotate-180 transition-transform" />
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Download the standalone executable directly
              </CardDescription>
            </CardHeader>
          </summary>
          <CardContent>
            <div className="space-y-4">
              <Button variant="brand" size="lg" className="w-full justify-start" asChild>
                <a href="/downloads/gcb-runner-macos-arm64" download>
                  <Apple className="h-4 w-4 mr-2" />
                  Download for macOS (Apple Silicon)
                </a>
              </Button>

              {/* Manual installation steps */}
              <details className="group">
                <summary className="flex items-center gap-2 cursor-pointer text-sm text-muted-foreground hover:text-foreground transition-colors">
                  <ChevronDown className="h-4 w-4 group-open:rotate-180 transition-transform" />
                  Manual installation steps
                </summary>
                <div className="mt-3 bg-white/[0.03] border border-white/[0.08] p-4 rounded-lg text-sm space-y-3">
                  <p className="font-medium text-foreground">After downloading:</p>
                  <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
                    <li>Open Terminal and navigate to your Downloads folder:
                      <code className="block mt-1 ml-5 bg-black/30 text-foreground px-2 py-1 rounded text-xs">cd ~/Downloads</code>
                    </li>
                    <li>Remove macOS quarantine and make executable:
                      <code className="block mt-1 ml-5 bg-black/30 text-foreground px-2 py-1 rounded text-xs">xattr -d com.apple.quarantine gcb-runner-macos-arm64 && chmod +x gcb-runner-macos-arm64</code>
                    </li>
                    <li>Move to your PATH (optional):
                      <code className="block mt-1 ml-5 bg-black/30 text-foreground px-2 py-1 rounded text-xs">sudo mv gcb-runner-macos-arm64 /usr/local/bin/gcb-runner</code>
                    </li>
                    <li>Run the tool:
                      <code className="block mt-1 ml-5 bg-black/30 text-foreground px-2 py-1 rounded text-xs">gcb-runner</code>
                    </li>
                  </ol>
                </div>
              </details>
            </div>

            <div className="mt-6 pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                <RefreshCw className="h-4 w-4" />
                <span>Auto-updates included — gcb-runner will notify you when updates are available</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Verify downloads using SHA256 hashes from{" "}
                <a href="/downloads/manifest.json" className="text-primary hover:underline">
                  manifest.json
                </a>
              </p>
            </div>
          </CardContent>
        </details>
      </Card>

      {/* Developer Installation */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Code className="h-5 w-5" />
            Developer Installation
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Install from source for development or customization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              For developers who want to run from source, contribute, or customize the runner:
            </p>
            
            <div className="bg-black/40 border border-white/10 rounded-lg p-4 font-mono text-sm space-y-2">
              <div className="text-muted-foreground"># Clone the repository</div>
              <code className="text-foreground block">git clone https://github.com/GospelAmbition/gcb-runner.git</code>
              <code className="text-foreground block">cd gcb-runner</code>
              <div className="text-muted-foreground mt-3"># Install with pip (editable mode)</div>
              <code className="text-foreground block">pip install -e &quot;.[dev]&quot;</code>
              <div className="text-muted-foreground mt-3"># Run the tool</div>
              <code className="text-foreground block">gcb-runner</code>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <Button variant="outline" size="sm" asChild>
                <a href="https://github.com/GospelAmbition/gcb-runner" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View on GitHub
                </a>
              </Button>
            </div>

            <div className="bg-white/[0.03] border border-white/[0.08] p-3 rounded-lg text-xs text-muted-foreground">
              <strong className="text-foreground">Requirements:</strong> Python 3.10 or higher
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <h2 className="text-2xl font-semibold text-foreground mb-4">Features</h2>
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

      {/* Quick Start */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Terminal className="h-5 w-5" />
            Quick Start
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-black/40 border border-white/10 rounded-lg p-4 font-mono text-sm space-y-1">
            <div className="text-muted-foreground"># Launch interactive menu</div>
            <code className="text-foreground block">gcb-runner</code>
            <div className="text-muted-foreground mt-3"># Or use commands directly</div>
            <code className="text-foreground block">gcb-runner config                              <span className="text-muted-foreground"># Set up API keys</span></code>
            <code className="text-foreground block">gcb-runner test --model gpt-4o --backend openrouter  <span className="text-muted-foreground"># Run benchmark</span></code>
            <code className="text-foreground block">gcb-runner view                                <span className="text-muted-foreground"># Open dashboard</span></code>
            <code className="text-foreground block">gcb-runner export                              <span className="text-muted-foreground"># Export results</span></code>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
