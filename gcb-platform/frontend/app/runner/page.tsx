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
          <Terminal className="h-10 w-10 text-red-700" />
          <h1 className="text-4xl font-bold text-slate-900">GCB Runner</h1>
        </div>
        <p className="mt-2 text-lg text-slate-600">
          Run the Great Commission Benchmark locally on any AI model
        </p>
      </div>

      {/* Hero Card */}
      <Card className="mb-8 border-red-200 bg-red-50/50">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-semibold text-slate-900 mb-3">Test Any Model, Anywhere</h2>
              <p className="text-slate-600 mb-4">
                The GCB Runner is the official command-line tool for running the Great Commission Benchmark 
                on your own infrastructure. Perfect for testing local models, fine-tuned models, 
                or models not available through the platform.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">OpenRouter</Badge>
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">OpenAI</Badge>
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">Anthropic</Badge>
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">LM Studio</Badge>
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">Ollama</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download Section */}
      <Card className="mb-8 border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900">
            <Download className="h-5 w-5" />
            Download
          </CardTitle>
          <CardDescription className="text-slate-600">
            Download the standalone executable - no Python required
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="macos" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-100">
              <TabsTrigger value="macos" className="flex items-center gap-2 text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700">
                <Apple className="h-4 w-4" />
                macOS
              </TabsTrigger>
              <TabsTrigger value="linux" className="flex items-center gap-2 text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700">
                <Monitor className="h-4 w-4" />
                Linux
              </TabsTrigger>
              <TabsTrigger value="windows" className="flex items-center gap-2 text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700">
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
              <div className="bg-slate-100 p-4 rounded-lg text-sm space-y-2">
                <p className="font-medium text-slate-900">After downloading:</p>
                <ol className="list-decimal list-inside space-y-1 text-slate-600">
                  <li>Open Terminal and navigate to your Downloads folder</li>
                  <li>Run: <code className="bg-white text-slate-800 px-1 rounded">chmod +x gcb-runner-macos-arm64</code></li>
                  <li>Run: <code className="bg-white text-slate-800 px-1 rounded">./gcb-runner-macos-arm64</code></li>
                </ol>
                <p className="text-slate-500 mt-2">
                  <strong className="text-slate-700">Note:</strong> You may need to allow the app in System Settings → Privacy & Security.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="linux" className="mt-4 space-y-4">
              <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                <Download className="h-4 w-4 mr-2" />
                Linux (x64) — Coming Soon
              </Button>
              <div className="bg-slate-100 p-4 rounded-lg text-sm">
                <p className="text-slate-600">
                  Linux builds are in development. Check back soon or contact us if you need early access.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="windows" className="mt-4 space-y-4">
              <Button variant="outline" size="lg" className="w-full justify-start" disabled>
                <Download className="h-4 w-4 mr-2" />
                Windows (x64) — Coming Soon
              </Button>
              <div className="bg-slate-100 p-4 rounded-lg text-sm">
                <p className="text-slate-600">
                  Windows builds are in development. Check back soon or contact us if you need early access.
                </p>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-6 pt-6 border-t border-slate-200">
            <div className="flex items-center gap-2 text-sm text-slate-500 mb-3">
              <RefreshCw className="h-4 w-4" />
              <span>Auto-updates included - gcb-runner will notify you when updates are available</span>
            </div>
            <p className="text-xs text-slate-500">
              Verify downloads using SHA256 hashes from{" "}
              <a href="/downloads/manifest.json" className="text-red-700 hover:underline">
                manifest.json
              </a>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Start */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-slate-900">Quick Start</CardTitle>
          <CardDescription className="text-slate-600">Get up and running in under a minute</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-medium text-slate-900 mb-2">1. Configure</h3>
            <div className="bg-slate-100 p-4 rounded-lg font-mono text-sm text-slate-800">
              gcb-runner config
            </div>
            <p className="text-sm text-slate-600 mt-2">
              You&apos;ll need an API key from your{" "}
              <a href="/dashboard/settings" className="text-red-700 hover:underline">
                dashboard settings
              </a>.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-slate-900 mb-2">2. Run</h3>
            <div className="bg-slate-100 p-4 rounded-lg font-mono text-sm text-slate-800">
              gcb-runner
            </div>
            <p className="text-sm text-slate-600 mt-2">
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
              <Laptop className="h-5 w-5 text-red-700" />
              <CardTitle className="text-lg text-slate-900">Local Models</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Test models running on LM Studio, Ollama, or any OpenAI-compatible endpoint. 
              Perfect for fine-tuned models or private deployments.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-5 w-5 text-red-700" />
              <CardTitle className="text-lg text-slate-900">Cloud APIs</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Connect to OpenRouter, OpenAI, or Anthropic APIs directly. Access 100+ models 
              with your own API keys and usage limits.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-red-700" />
              <CardTitle className="text-lg text-slate-900">Local Dashboard</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              View results in a local web dashboard. Generate HTML reports, compare runs, 
              and analyze performance before submitting.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-red-700" />
              <CardTitle className="text-lg text-slate-900">Submit to Leaderboard</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">
              Upload verified results to the platform leaderboard. Submissions are reviewed 
              by moderators to ensure benchmark integrity.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Platform vs CLI */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-slate-900">Platform Tests vs GCB Runner Submissions</CardTitle>
          <CardDescription className="text-slate-600">Choose the right approach for your needs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-2 font-medium text-slate-700">Aspect</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-700">Platform Tests</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-700">GCB Runner Submissions</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-100">
                  <td className="py-3 px-2 text-slate-500">Where run</td>
                  <td className="py-3 px-2 text-slate-700">On the platform</td>
                  <td className="py-3 px-2 text-slate-700">Locally via GCB Runner</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="py-3 px-2 text-slate-500">Publishing</td>
                  <td className="py-3 px-2 text-slate-700">Automatic</td>
                  <td className="py-3 px-2 text-slate-700">Requires moderator review</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="py-3 px-2 text-slate-500">Cost</td>
                  <td className="py-3 px-2 text-slate-700">Platform fee + model API cost</td>
                  <td className="py-3 px-2 text-slate-700">Submission fee (you pay model costs)</td>
                </tr>
                <tr>
                  <td className="py-3 px-2 text-slate-500">Best for</td>
                  <td className="py-3 px-2 text-slate-700">Quick results, individual testers</td>
                  <td className="py-3 px-2 text-slate-700">Organizations, custom/local models</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Commands Reference */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-slate-900">Command Reference</CardTitle>
          <CardDescription className="text-slate-600">Common commands to get you started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-2">
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner</code>
                <span className="text-sm text-slate-600">Launch interactive menu</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner config</code>
                <span className="text-sm text-slate-600">Configure API keys and backends</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner test --model gpt-4o</code>
                <span className="text-sm text-slate-600">Run benchmark on a model</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner results</code>
                <span className="text-sm text-slate-600">View test results</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner view</code>
                <span className="text-sm text-slate-600">Open local web dashboard</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner update</code>
                <span className="text-sm text-slate-600">Check for and install updates</span>
              </div>
              <div className="flex items-start gap-4">
                <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono shrink-0">gcb-runner upload --run 3</code>
                <span className="text-sm text-slate-600">Submit results to platform</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Get API Key CTA */}
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Settings className="h-8 w-8 text-red-700" />
              <div>
                <h3 className="font-semibold text-slate-900">Ready to get started?</h3>
                <p className="text-sm text-slate-600">
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
