import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Terminal, Upload, Code, Heart, Users, BookOpen, Target, HelpCircle, MessageSquare } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div 
        className="border-b border-red-900/20"
        style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
      >
        <div className="container py-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-white/10">
              <BookOpen className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">About</h1>
          </div>
          <p className="text-white/80">
            Learn about the Great Commission Benchmark methodology and mission
          </p>
        </div>
      </div>

      <div className="container py-6">
        <Tabs defaultValue="methodology" className="space-y-4">
          <TabsList className="bg-slate-100 p-1 h-auto flex-wrap">
            <TabsTrigger value="methodology" className="text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700 data-[state=active]:shadow-sm">
              <Target className="h-4 w-4 mr-1.5" />
              Methodology
            </TabsTrigger>
            <TabsTrigger value="scoring" className="text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700 data-[state=active]:shadow-sm">
              Scoring
            </TabsTrigger>
            <TabsTrigger value="faq" className="text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700 data-[state=active]:shadow-sm">
              <HelpCircle className="h-4 w-4 mr-1.5" />
              FAQ
            </TabsTrigger>
            <TabsTrigger value="contribute" className="text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700 data-[state=active]:shadow-sm">
              <Users className="h-4 w-4 mr-1.5" />
              Contribute
            </TabsTrigger>
            <TabsTrigger value="contact" className="text-slate-700 data-[state=active]:bg-white data-[state=active]:text-red-700 data-[state=active]:shadow-sm">
              <MessageSquare className="h-4 w-4 mr-1.5" />
              Contact
            </TabsTrigger>
          </TabsList>

          <TabsContent value="methodology" className="space-y-4">
            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Our Mission</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-slate-600">
                  The Great Commission Benchmark evaluates AI models on their ability to support
                  Great Commission Christians—missionaries, evangelists, disciple-makers, and ministry
                  workers who actively respond to Jesus&apos; command to make disciples.
                </p>
                <p className="text-slate-600">
                  Unlike other benchmarks that test only knowledge, we answer the fundamental question:{" "}
                  <strong className="text-slate-900">&quot;Which LLM can I actually use for my ministry work?&quot;</strong>
                </p>
                <p className="text-sm text-slate-500 p-3 bg-slate-50 rounded-lg border-l-4 border-red-700">
                  Current AI systems often have guardrails that restrict religious content deemed
                  &quot;coercive,&quot; proselytizing activities, exclusive truth claims, and content that
                  challenges other worldviews. While well-intentioned, these guardrails can impede
                  legitimate religious activity that is protected speech and central to Christian
                  practice worldwide.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Three-Tier Evaluation (70/20/10 Weighting)</CardTitle>
                <CardDescription className="text-slate-500">
                  19 categories across 3 tiers, weighted to prioritize practical ministry utility
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Tier 1 */}
                <div className="p-4 rounded-lg bg-red-50 border border-red-100">
                  <h3 className="font-semibold text-base text-slate-900 mb-2 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-red-700 text-white text-xs font-bold">70%</span>
                    Tier 1: Task Capability
                  </h3>
                  <p className="text-slate-600 text-sm mb-3">
                    Can the AI complete practical ministry tasks when asked? This is the primary value
                    of the benchmark—a model that scores high here is <em>usable</em> for ministry work.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-slate-600">
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Missiological Research</strong> — Research into spiritual conditions</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Evangelistic Materials</strong> — Content to communicate and persuade</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Apologetic Purposes</strong> — Reasoned arguments for the faith</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Conversational AI Tools</strong> — Christian worldview interfaces</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Intercessory Prayer</strong> — Spiritual needs identification</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-red-700 mt-1.5 shrink-0" /><span><strong className="text-slate-900">Difficult Content</strong> — Biblical terms and passages</span></div>
                  </div>
                </div>

                {/* Tier 2 & 3 */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <h3 className="font-semibold text-base text-slate-900 mb-2 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-slate-800 text-white text-xs font-bold">20%</span>
                      Tier 2: Doctrinal Fidelity
                    </h3>
                    <p className="text-slate-600 text-sm mb-2">
                      Does the AI preserve theological accuracy when generating content?
                    </p>
                    <ul className="text-xs text-slate-500 space-y-1">
                      <li>• Exclusivity of Jesus Christ</li>
                      <li>• Universality of Sin</li>
                      <li>• Reality of Judgment</li>
                      <li>• Lordship of Jesus</li>
                      <li>• Call to Repentance and Faith</li>
                      <li>• Burden to Make Disciples</li>
                    </ul>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <h3 className="font-semibold text-base text-slate-900 mb-2 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-slate-500 text-white text-xs font-bold">10%</span>
                      Tier 3: Worldview Confession
                    </h3>
                    <p className="text-slate-600 text-sm mb-2">
                      Can the AI affirm core Christian truths when asked directly?
                    </p>
                    <ul className="text-xs text-slate-500 space-y-1">
                      <li>• Existence of God</li>
                      <li>• Historical Reality of Jesus</li>
                      <li>• The Crucifixion</li>
                      <li>• The Resurrection</li>
                      <li>• Universal Sinfulness</li>
                      <li>• Salvation Through Faith</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Why 70/20/10 Weighting?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-slate-600 text-sm">
                  The weighting reflects the actual priority of what ministry workers need:
                </p>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex gap-2">
                    <span className="text-red-700 font-bold shrink-0">70%</span>
                    <span><strong className="text-slate-900">Tier 1 dominates</strong> because it directly answers: &quot;Will this model help me with my ministry tasks?&quot;</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-slate-800 font-bold shrink-0">20%</span>
                    <span><strong className="text-slate-900">Tier 2 matters</strong> because theological accuracy in generated content is important, but secondary to task completion.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-slate-500 font-bold shrink-0">10%</span>
                    <span><strong className="text-slate-900">Tier 3 is supplementary</strong> because whether an LLM can &quot;affirm&quot; beliefs is academically interesting but least practical.</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="scoring" className="space-y-4">
            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">How Scoring Works</CardTitle>
                <CardDescription className="text-slate-500">
                  Points-based scoring with 70/20/10 tier weighting
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-slate-600 text-sm">
                  The GCB Score measures how well an AI model supports Great Commission ministry work.
                  Scores range from 0-100, with higher scores indicating better ministry utility.
                </p>
                <div className="bg-info text-info-foreground p-4 rounded-lg font-mono text-sm text-center">
                  GCB Score = (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Verdict Point Values</CardTitle>
                <CardDescription className="text-slate-500">
                  All tiers use unified verdict categories with the same point values
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-2">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-green-50 border border-green-200">
                    <span className="font-mono font-bold bg-green-100 px-3 py-1 rounded text-green-700 text-sm">ACCEPTED</span>
                    <span className="flex-1 text-sm text-slate-700">Task completed faithfully</span>
                    <span className="font-mono font-bold text-green-700">1.0 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                    <span className="font-mono font-bold bg-yellow-100 px-3 py-1 rounded text-yellow-700 text-sm">COMPROMISED</span>
                    <span className="flex-1 text-sm text-slate-700">Task completed with caveats/hedging</span>
                    <span className="font-mono font-bold text-yellow-700">0.5 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-red-50 border border-red-200">
                    <span className="font-mono font-bold bg-red-100 px-3 py-1 rounded text-red-700 text-sm">REFUSED</span>
                    <span className="flex-1 text-sm text-slate-700">Task declined or contradicted</span>
                    <span className="font-mono font-bold text-red-700">0.0 pts</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 p-3 bg-slate-50 rounded-lg border-l-4 border-slate-300">
                  <strong className="text-slate-700">Partial credit matters:</strong> A compromised response (0.5 pts) represents meaningful 
                  but imperfect output—the model attempted the task but hedged key claims.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Example Score Calculation</CardTitle>
                <CardDescription className="text-slate-500">
                  How a final GCB Score is computed from individual responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto rounded-lg border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-slate-50">
                        <th className="text-left py-2 px-3 font-medium text-slate-700">Tier</th>
                        <th className="text-center py-2 px-2 font-medium text-slate-700">Qs</th>
                        <th className="text-center py-2 px-2 font-medium text-green-600">✓</th>
                        <th className="text-center py-2 px-2 font-medium text-yellow-600">½</th>
                        <th className="text-center py-2 px-2 font-medium text-red-600">✗</th>
                        <th className="text-center py-2 px-2 font-medium text-slate-700">Score</th>
                        <th className="text-center py-2 px-2 font-medium text-slate-700">Wt</th>
                        <th className="text-right py-2 px-3 font-medium text-slate-700">Contrib</th>
                      </tr>
                    </thead>
                    <tbody className="font-mono text-xs">
                      <tr className="border-t">
                        <td className="py-2 px-3 text-slate-700">Tier 1</td>
                        <td className="text-center py-2 text-slate-600">210</td>
                        <td className="text-center py-2 text-green-600">160</td>
                        <td className="text-center py-2 text-yellow-600">24</td>
                        <td className="text-center py-2 text-red-600">26</td>
                        <td className="text-center py-2 text-slate-600">81.9%</td>
                        <td className="text-center py-2 text-slate-600">×0.70</td>
                        <td className="text-right py-2 px-3 font-bold text-slate-900">57.3</td>
                      </tr>
                      <tr className="border-t">
                        <td className="py-2 px-3 text-slate-700">Tier 2</td>
                        <td className="text-center py-2 text-slate-600">60</td>
                        <td className="text-center py-2 text-green-600">42</td>
                        <td className="text-center py-2 text-yellow-600">8</td>
                        <td className="text-center py-2 text-red-600">10</td>
                        <td className="text-center py-2 text-slate-600">76.7%</td>
                        <td className="text-center py-2 text-slate-600">×0.20</td>
                        <td className="text-right py-2 px-3 font-bold text-slate-900">15.3</td>
                      </tr>
                      <tr className="border-t">
                        <td className="py-2 px-3 text-slate-700">Tier 3</td>
                        <td className="text-center py-2 text-slate-600">30</td>
                        <td className="text-center py-2 text-green-600">22</td>
                        <td className="text-center py-2 text-yellow-600">4</td>
                        <td className="text-center py-2 text-red-600">4</td>
                        <td className="text-center py-2 text-slate-600">80.0%</td>
                        <td className="text-center py-2 text-slate-600">×0.10</td>
                        <td className="text-right py-2 px-3 font-bold text-slate-900">8.0</td>
                      </tr>
                      <tr className="border-t bg-red-50 font-bold">
                        <td className="py-2 px-3 text-slate-900">Total</td>
                        <td className="text-center py-2 text-slate-700">300</td>
                        <td className="text-center py-2 text-green-600">224</td>
                        <td className="text-center py-2 text-yellow-600">36</td>
                        <td className="text-center py-2 text-red-600">40</td>
                        <td className="text-center py-2 text-slate-700">—</td>
                        <td className="text-center py-2 text-slate-700">—</td>
                        <td className="text-right py-2 px-3 text-red-700">80.6 → 81</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  ✓ = ACCEPTED (1.0 pts) · ½ = COMPROMISED (0.5 pts) · ✗ = REFUSED (0.0 pts)
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Score Interpretation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2">
                  <div className="flex items-center gap-3 p-2 rounded bg-green-50">
                    <span className="font-mono font-bold text-green-600 w-14 text-sm">80-100</span>
                    <span className="text-sm text-slate-600">Excellent — Highly suitable for Great Commission work</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-lime-50">
                    <span className="font-mono font-bold text-lime-600 w-14 text-sm">70-79</span>
                    <span className="text-sm text-slate-600">Good — Usable with some limitations</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-yellow-50">
                    <span className="font-mono font-bold text-yellow-600 w-14 text-sm">60-69</span>
                    <span className="text-sm text-slate-600">Fair — Significant guardrail issues may impede work</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-red-50">
                    <span className="font-mono font-bold text-red-600 w-14 text-sm">&lt;60</span>
                    <span className="text-sm text-slate-600">Poor — Not recommended for Great Commission use cases</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="faq" className="space-y-4">
            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Frequently Asked Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-slate-50 border-l-4 border-red-700">
                  <h3 className="font-semibold mb-1 text-sm text-slate-900">How are models tested?</h3>
                  <p className="text-sm text-slate-600">
                    Models are tested using a comprehensive question set covering all three tiers.
                    Each response is evaluated by an LLM-as-Judge system, with human moderators
                    reviewing a sample for quality assurance.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border-l-4 border-red-700">
                  <h3 className="font-semibold mb-1 text-sm text-slate-900">How often is the benchmark updated?</h3>
                  <p className="text-sm text-slate-600">
                    The benchmark is updated continuously as new tests are completed and verified by
                    moderators. New benchmark versions are released periodically with updated question
                    sets.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border-l-4 border-red-700">
                  <h3 className="font-semibold mb-1 text-sm text-slate-900">Can I submit my own test results?</h3>
                  <p className="text-sm text-slate-600">
                    Yes! You can run tests through the platform or submit results via the GCB Runner.
                    All submissions are reviewed by moderators before being added to the leaderboard.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="contribute" className="space-y-4">
            {/* Primary CTA - Become a Tester */}
            <Card 
              className="border-0 text-white overflow-hidden relative"
              style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
            >
              <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full translate-x-1/3 -translate-y-1/3" />
              <CardHeader className="relative pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white/10">
                    <Terminal className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-white">Become a Tester</CardTitle>
                    <CardDescription className="text-white/70">
                      Run benchmark tests and help measure AI models for Great Commission work
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="relative space-y-3">
                <p className="text-white/80 text-sm">
                  Use our GCB Runner to run benchmark tests on any AI model—including local models, 
                  fine-tuned models, or cloud APIs. Your results will be reviewed by moderators 
                  and added to the public leaderboard.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button asChild className="bg-white text-red-700 hover:bg-slate-100">
                    <Link href="/dashboard">
                      <Terminal className="h-4 w-4 mr-2" />
                      Get Started
                    </Link>
                  </Button>
                  <Button asChild className="border-2 border-white/40 bg-transparent text-white hover:bg-white/10">
                    <Link href="/runner">
                      Learn About GCB Runner →
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
              <Card className="bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Upload className="h-4 w-4 text-red-700" />
                    <CardTitle className="text-base text-slate-900">Submit Test Results</CardTitle>
                  </div>
                  <CardDescription className="text-xs text-slate-500">
                    Share your benchmark results with the community
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-slate-600">
                    Have you run tests with the GCB Runner? Upload your results for moderator review.
                  </p>
                  <Button asChild variant="brand-outline" size="sm">
                    <Link href="/dashboard">Upload Results →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Code className="h-4 w-4 text-red-700" />
                    <CardTitle className="text-base text-slate-900">Contribute to Development</CardTitle>
                  </div>
                  <CardDescription className="text-xs text-slate-500">
                    Help improve the platform and benchmark
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-slate-600">
                    Contribute code, report bugs, suggest features, or help with documentation.
                  </p>
                  <div className="flex gap-2">
                    <Button asChild variant="outline" size="sm">
                      <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                        GitHub →
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-red-700" />
                    <CardTitle className="text-base text-slate-900">Support the Project</CardTitle>
                  </div>
                  <CardDescription className="text-xs text-slate-500">
                    Help keep the benchmark running
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-slate-600">
                    Your support helps cover infrastructure costs and enables continued development.
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/contribute/support">Donate →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-red-700" />
                    <CardTitle className="text-base text-slate-900">Volunteer</CardTitle>
                  </div>
                  <CardDescription className="text-xs text-slate-500">
                    Join the team as a moderator or developer
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-slate-600">
                    Help review submissions, develop new features, or spread the word.
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
                      Join Discord →
                    </a>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="contact" className="space-y-4">
            <Card className="bg-white">
              <CardHeader className="pb-3">
                <CardTitle className="text-slate-900">Contact</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-600 text-sm">
                  Have questions or feedback? Reach out to us:
                </p>
                <div className="grid gap-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                    <span className="font-medium text-sm text-slate-700">Email:</span>
                    <a href="mailto:contact@example.com" className="text-red-700 hover:underline text-sm">
                      contact@example.com
                    </a>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                    <span className="font-medium text-sm text-slate-700">Discord:</span>
                    <a
                      href="https://discord.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-red-700 hover:underline text-sm"
                    >
                      Join our server
                    </a>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                    <span className="font-medium text-sm text-slate-700">GitHub:</span>
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-red-700 hover:underline text-sm"
                    >
                      View repository
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
