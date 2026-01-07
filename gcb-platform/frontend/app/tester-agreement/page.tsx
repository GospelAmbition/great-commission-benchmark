import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Shield, AlertTriangle, CheckCircle, XCircle, Eye, FileText, Scale, Mail } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tester Agreement | Great Commission Benchmark",
  description: "Tester Agreement governing participation in the Great Commission Benchmark",
};

export default function TesterAgreementPage() {
  return (
    <div className="container py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Tester Agreement</h1>
        <p className="mt-2 text-muted-foreground">
          Governing your participation as a benchmark tester
        </p>
        <p className="mt-1 text-sm text-muted-foreground">Last Updated: December 18, 2025</p>
      </div>

      {/* Important Notice */}
      <Alert className="mb-8 border-[--ga-red]/30 bg-[--ga-red]/5">
        <Shield className="h-4 w-4 text-[--ga-red]" />
        <AlertDescription className="text-sm">
          <strong>Why This Matters:</strong> The integrity of the Great Commission Benchmark depends on 
          maintaining the confidentiality of test questions. If questions become publicly available or 
          are shared with AI model providers, they may be incorporated into training data, rendering 
          our benchmark ineffective at providing accurate, unbiased evaluations.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="obligations">Obligations</TabsTrigger>
          <TabsTrigger value="permitted">Permitted Uses</TabsTrigger>
          <TabsTrigger value="consequences">Consequences</TabsTrigger>
          <TabsTrigger value="legal">Legal</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-[--ga-red]" />
                <div>
                  <CardTitle>Introduction and Purpose</CardTitle>
                  <CardDescription>Why this agreement exists</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                This Tester Agreement governs your participation as a tester in the Great Commission 
                Benchmark. By running benchmark tests through the Service, you agree to be bound by 
                this Agreement in addition to our Terms of Service and Privacy Policy.
              </p>
              <p className="text-muted-foreground">
                This Agreement establishes your obligations to protect the confidentiality of benchmark 
                materials and outlines the consequences of violating these terms.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Key Definitions</CardTitle>
              <CardDescription>Important terms used throughout this agreement</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="space-y-4">
                <div className="border-l-2 border-[--ga-red]/30 pl-4">
                  <dt className="font-semibold">&quot;Confidential Information&quot;</dt>
                  <dd className="text-sm text-muted-foreground mt-1">
                    All benchmark test questions, prompts, scenarios, evaluation criteria, expected 
                    responses, scoring rubrics, and any other materials used in the testing process 
                    that are not publicly available on our leaderboards or website.
                  </dd>
                </div>
                <div className="border-l-2 border-[--ga-red]/30 pl-4">
                  <dt className="font-semibold">&quot;Test Questions&quot;</dt>
                  <dd className="text-sm text-muted-foreground mt-1">
                    The specific questions, prompts, and scenarios presented to AI models during 
                    benchmark testing.
                  </dd>
                </div>
                <div className="border-l-2 border-[--ga-red]/30 pl-4">
                  <dt className="font-semibold">&quot;Model Provider&quot;</dt>
                  <dd className="text-sm text-muted-foreground mt-1">
                    Any company, organization, or individual that creates, trains, fine-tunes, or 
                    distributes AI models, including but not limited to OpenAI, Anthropic, Google, 
                    Meta, Mistral, and their employees, contractors, or affiliates.
                  </dd>
                </div>
                <div className="border-l-2 border-[--ga-red]/30 pl-4">
                  <dt className="font-semibold">&quot;Public Disclosure&quot;</dt>
                  <dd className="text-sm text-muted-foreground mt-1">
                    Sharing, publishing, posting, or otherwise making information available to any 
                    third party, whether through social media, websites, forums, academic papers, 
                    presentations, or any other medium.
                  </dd>
                </div>
                <div className="border-l-2 border-[--ga-red]/30 pl-4">
                  <dt className="font-semibold">&quot;Training Use&quot;</dt>
                  <dd className="text-sm text-muted-foreground mt-1">
                    Using information to train, fine-tune, improve, or otherwise enhance any AI 
                    model or system.
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Obligations Tab */}
        <TabsContent value="obligations" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-[--ga-red]" />
                <div>
                  <CardTitle>Confidentiality Obligations</CardTitle>
                  <CardDescription>Your responsibilities as a tester</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">General Obligation</h3>
                <p className="text-sm text-muted-foreground">
                  You agree to maintain the confidentiality of all Confidential Information and to 
                  use it solely for the purpose of running benchmark tests through the Service.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <XCircle className="h-5 w-5 text-red-500" />
                <CardTitle className="text-red-600 dark:text-red-400">No Public Disclosure</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">You shall not:</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Post, share, or publish Test Questions on any website, forum, social media platform, or other public venue</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Include Test Questions in blog posts, articles, videos, podcasts, or other content</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Discuss specific Test Questions in public conversations, whether online or offline</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Share screenshots, recordings, or copies of Test Questions</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Reproduce or paraphrase Test Questions in any publicly accessible format</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <XCircle className="h-5 w-5 text-red-500" />
                <CardTitle className="text-red-600 dark:text-red-400">No Sharing with Model Providers</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">You shall not:</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Share Test Questions with any Model Provider, directly or indirectly</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Communicate Test Questions to employees, contractors, or representatives of Model Providers</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Submit Test Questions to AI models outside of the official benchmark testing process</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Include Test Questions in bug reports, feature requests, or other communications with Model Providers</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Post Test Questions in any forum or channel monitored by Model Providers</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <XCircle className="h-5 w-5 text-red-500" />
                <CardTitle className="text-red-600 dark:text-red-400">No Training Use</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">You shall not:</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Use Test Questions to train, fine-tune, or improve any AI model</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Include Test Questions in any dataset intended for AI training</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Contribute Test Questions to any open-source training dataset</span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Share Test Questions with anyone who might use them for training purposes</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-[--ga-red]" />
                <CardTitle>Protection of Materials</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">You agree to:</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Store any locally retained Confidential Information securely</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Not make copies of Confidential Information except as necessary for testing</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Delete any local copies of Test Questions after testing is complete</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Protect your account credentials to prevent unauthorized access</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Eye className="h-5 w-5 text-[--ga-red]" />
                <CardTitle>Reporting Obligations</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Duty to Report</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  You agree to promptly report to us if you:
                </p>
                <ul className="space-y-1 text-sm text-muted-foreground list-disc list-inside">
                  <li>Discover Test Questions have been publicly disclosed</li>
                  <li>Become aware of any breach of this Agreement by others</li>
                  <li>Suspect that Test Questions have been shared with Model Providers</li>
                  <li>Observe Test Questions appearing in AI training datasets</li>
                  <li>Encounter any other threat to the confidentiality of benchmark materials</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-2">How to Report</h3>
                <p className="text-sm text-muted-foreground">
                  Reports should be submitted to{" "}
                  <a href="mailto:contact@greatcommissionbenchmark.ai" className="text-[--ga-red] hover:underline">
                    contact@greatcommissionbenchmark.ai
                  </a>{" "}
                  and should include: description of the suspected breach, location where Confidential 
                  Information was found (URLs, screenshots if possible), any information about the source 
                  of the breach, and date and time of discovery.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permitted Uses Tab */}
        <TabsContent value="permitted" className="space-y-6">
          <Card className="border-green-200 dark:border-green-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <CardTitle className="text-green-600 dark:text-green-400">What You Can Discuss</CardTitle>
                  <CardDescription>Permitted uses of benchmark information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Notwithstanding the restrictions above, you may discuss:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Your overall test scores and results</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>General impressions of model performance</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>The categories and types of questions tested (in general terms)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Published leaderboard data and publicly available information</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-green-200 dark:border-green-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <CardTitle className="text-green-600 dark:text-green-400">Private Discussion</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                You may discuss specific Test Questions:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>With other verified testers who have signed this Agreement</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>With Great Commission Benchmark staff or moderators</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>When reporting a suspected breach or security concern</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-green-200 dark:border-green-900">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <CardTitle className="text-green-600 dark:text-green-400">Academic Research</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Researchers may reference the benchmark in academic work, provided they:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Do not include actual Test Questions in publications</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Contact us for guidance on appropriate citation and discussion</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Comply with any additional research agreements we may require</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Consequences Tab */}
        <TabsContent value="consequences" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-[--ga-red]" />
                <div>
                  <CardTitle>Violation Categories</CardTitle>
                  <CardDescription>How we classify violations of this agreement</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800">
                <h3 className="font-semibold text-yellow-700 dark:text-yellow-300 mb-2">Minor/Accidental Violations</h3>
                <ul className="text-sm text-yellow-800 dark:text-yellow-200 space-y-1 list-disc list-inside">
                  <li>Inadvertent disclosure of limited information</li>
                  <li>Immediate self-reporting and cooperation</li>
                  <li>No evidence of intent to harm</li>
                </ul>
              </div>

              <div className="p-4 rounded-lg bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800">
                <h3 className="font-semibold text-orange-700 dark:text-orange-300 mb-2">Major/Deliberate Violations</h3>
                <ul className="text-sm text-orange-800 dark:text-orange-200 space-y-1 list-disc list-inside">
                  <li>Intentional sharing of Test Questions</li>
                  <li>Failure to report known breaches</li>
                  <li>Repeated minor violations after warning</li>
                </ul>
              </div>

              <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
                <h3 className="font-semibold text-red-700 dark:text-red-300 mb-2">Severe/Malicious Violations</h3>
                <ul className="text-sm text-red-800 dark:text-red-200 space-y-1 list-disc list-inside">
                  <li>Systematic leaking of questions</li>
                  <li>Sharing with Model Providers</li>
                  <li>Use in training datasets</li>
                  <li>Commercial exploitation of Confidential Information</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Consequences by Severity</CardTitle>
              <CardDescription>Actions we may take depending on the violation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2 text-yellow-600 dark:text-yellow-400">For Minor Violations:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>Written warning</li>
                  <li>Required re-confirmation of this Agreement</li>
                  <li>Additional monitoring of your testing activity</li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold mb-2 text-orange-600 dark:text-orange-400">For Major Violations:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>Immediate suspension of testing privileges</li>
                  <li>Permanent revocation of access to the Service</li>
                  <li>Removal of any contributions or credits</li>
                  <li>Notification to affected parties</li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold mb-2 text-red-600 dark:text-red-400">For Severe Violations:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>All consequences listed above</li>
                  <li>Public disclosure of the violation (without necessarily identifying you personally, unless legally required)</li>
                  <li>Pursuit of legal remedies, including injunctive relief and damages</li>
                  <li>Referral to appropriate authorities if criminal conduct is suspected</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Investigation Process</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Before imposing consequences for alleged violations:
              </p>
              <ul className="text-sm text-muted-foreground space-y-2 list-disc list-inside">
                <li>We will notify you of the alleged violation</li>
                <li>You will have an opportunity to respond and provide your account of events</li>
                <li>We will consider all relevant factors, including intent, harm caused, and cooperation</li>
                <li>Final decisions rest with Great Commission Benchmark at our sole discretion</li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4 border-l-2 border-muted-foreground/30 pl-4">
                <strong>Note:</strong> The consequences listed above are in addition to, and do not limit, 
                any legal remedies available to us under applicable law.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Duration of Obligations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Your confidentiality obligations under this Agreement:
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Begin when you first run a benchmark test</li>
                <li>Continue indefinitely, regardless of whether you continue using the Service</li>
                <li>Survive termination of your account or this Agreement</li>
              </ul>
              <p className="text-sm text-muted-foreground border-l-2 border-[--ga-red]/30 pl-4">
                <strong>Rationale:</strong> The indefinite nature of these obligations reflects the 
                permanent harm that could result from disclosure. Once Test Questions are leaked, 
                they cannot be &quot;unleaked,&quot; and their value for accurate benchmarking is permanently compromised.
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Question Retirement:</strong> When we retire specific Test Questions from active 
                use and replace them with new questions, we may, at our sole discretion, release some 
                retired questions from confidentiality obligations. Any such release will be communicated in writing.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Legal Tab */}
        <TabsContent value="legal" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Scale className="h-5 w-5 text-[--ga-red]" />
                <div>
                  <CardTitle>Intellectual Property</CardTitle>
                  <CardDescription>Ownership of benchmark materials</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Ownership</h3>
                <p className="text-sm text-muted-foreground">
                  All Test Questions, evaluation criteria, scoring methodologies, and other Confidential 
                  Information remain the exclusive property of the Great Commission Benchmark project. 
                  This Agreement does not grant you any ownership rights or license to use Confidential 
                  Information except as expressly permitted herein.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">No Derivative Works</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  You may not create derivative works based on Test Questions or other Confidential Information, including:
                </p>
                <ul className="text-sm text-muted-foreground list-disc list-inside">
                  <li>Modified versions of questions</li>
                  <li>Translations into other languages</li>
                  <li>Adaptations for different testing purposes</li>
                  <li>Compilations or collections</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Representations and Warranties</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                By agreeing to this Agreement, you represent and warrant that:
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>You are at least 18 years old (or the age of majority in your jurisdiction)</li>
                <li>You have the legal capacity to enter into this Agreement</li>
                <li>You are not acting on behalf of, or employed by, any Model Provider (or you have disclosed such affiliation)</li>
                <li>You will comply with all applicable laws in your use of the Service</li>
                <li>You understand the importance of confidentiality to the benchmark&apos;s integrity</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Disclosure of Affiliations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Required Disclosure</h3>
                <p className="text-sm text-muted-foreground mb-2">You must disclose to us if you:</p>
                <ul className="text-sm text-muted-foreground list-disc list-inside">
                  <li>Are employed by or contracted with any Model Provider</li>
                  <li>Have a financial interest in any Model Provider</li>
                  <li>Are conducting testing on behalf of a Model Provider</li>
                  <li>Have any other relationship that could create a conflict of interest</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Effect of Affiliation</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Disclosure of an affiliation does not automatically disqualify you from testing. We will evaluate each situation and may:
                </p>
                <ul className="text-sm text-muted-foreground list-disc list-inside">
                  <li>Allow testing with additional safeguards</li>
                  <li>Limit the scope of tests you may run</li>
                  <li>Decline to permit testing</li>
                  <li>Require additional agreements</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Modifications and Severability</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Modifications</h3>
                <p className="text-sm text-muted-foreground">
                  We may modify this Agreement from time to time. If we make material changes, we will 
                  notify you via email or through the Service. Continued use of testing features after 
                  notification constitutes acceptance. If you do not agree to the modified terms, you 
                  must stop using testing features.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Severability</h3>
                <p className="text-sm text-muted-foreground">
                  If any provision of this Agreement is found to be unenforceable, the remaining 
                  provisions will remain in full force and effect. The unenforceable provision will 
                  be modified to the minimum extent necessary to make it enforceable while preserving its intent.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-[--ga-red]" />
                <CardTitle>Contact Information</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                For questions about this Agreement, to report violations, or to disclose affiliations, please contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong>{" "}
                <a href="mailto:contact@greatcommissionbenchmark.ai" className="text-[--ga-red] hover:underline">
                  contact@greatcommissionbenchmark.ai
                </a>
              </p>
            </CardContent>
          </Card>

          <Card className="bg-muted/50">
            <CardHeader>
              <CardTitle>Acknowledgment</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm font-medium mb-3">
                BY RUNNING BENCHMARK TESTS THROUGH THE SERVICE, YOU ACKNOWLEDGE THAT:
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>You have read and understood this Agreement in its entirety</li>
                <li>You agree to be bound by all terms and conditions herein</li>
                <li>You understand the importance of confidentiality to the benchmark&apos;s integrity</li>
                <li>You accept the consequences of violating this Agreement</li>
                <li>This Agreement is legally binding and enforceable</li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4">
                Your acceptance of this Agreement is indicated by clicking &quot;I Agree&quot; or similar 
                acknowledgment when prompted during the testing process, running any benchmark test 
                through the Service, or accessing Test Questions or other Confidential Information.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
