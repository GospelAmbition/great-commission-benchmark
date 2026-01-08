import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { MenuBookIcon, GroupIcon, TerminalIcon } from "@/lib/icons";
import { Target, HelpCircle, MessageSquare, Upload, Code, Heart, Users } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-20" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <MenuBookIcon className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">About</h1>
          </div>
          <p className="text-muted-foreground">
            Learn about the Great Commission Benchmark methodology and mission
          </p>
        </div>
      </div>

      <div className="container py-6">
        <Tabs defaultValue="methodology" className="space-y-4">
          <TabsList className="bg-white/[0.03] border border-white/[0.08] p-1 h-auto flex-wrap">
            <TabsTrigger value="methodology" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              <Target className="h-4 w-4 mr-1.5" />
              Methodology
            </TabsTrigger>
            <TabsTrigger value="scoring" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              Scoring
            </TabsTrigger>
            <TabsTrigger value="faq" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              <HelpCircle className="h-4 w-4 mr-1.5" />
              FAQ
            </TabsTrigger>
            <TabsTrigger value="contribute" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              <Users className="h-4 w-4 mr-1.5" />
              Contribute
            </TabsTrigger>
            <TabsTrigger value="contact" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              <MessageSquare className="h-4 w-4 mr-1.5" />
              Contact
            </TabsTrigger>
          </TabsList>

          <TabsContent value="methodology" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Our Mission</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-muted-foreground">
                  The Great Commission Benchmark evaluates AI models on their ability to support
                  Great Commission Christians—missionaries, evangelists, disciple-makers, and ministry
                  workers who actively respond to Jesus&apos; command to make disciples.
                </p>
                <p className="text-muted-foreground">
                  Unlike other benchmarks that test only knowledge, we answer the fundamental question:{" "}
                  <strong className="text-foreground">&quot;Which LLM can I actually use for my ministry work?&quot;</strong>
                </p>
                <p className="text-sm text-muted-foreground p-3 bg-amber-500/5 rounded-lg border-l-2 border-amber-500">
                  Current AI systems often have guardrails that restrict religious content deemed
                  &quot;coercive,&quot; proselytizing activities, exclusive truth claims, and content that
                  challenges other worldviews. While well-intentioned, these guardrails can impede
                  legitimate religious activity that is protected speech and central to Christian
                  practice worldwide.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Three-Tier Evaluation (70/20/10 Weighting)</CardTitle>
                <CardDescription>
                  19 categories across 3 tiers, weighted to prioritize practical ministry utility
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Tier 1 */}
                <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/10">
                  <h3 className="font-semibold text-base text-foreground mb-2 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-primary text-white text-xs font-bold">70%</span>
                    Tier 1: Task Capability
                  </h3>
                  <p className="text-muted-foreground text-sm mb-3">
                    Can the AI complete practical ministry tasks when asked? This is the primary value
                    of the benchmark—a model that scores high here is <em>usable</em> for ministry work.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Missiological Research</strong> — Research into spiritual conditions</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Evangelistic Materials</strong> — Content to communicate and persuade</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Apologetic Purposes</strong> — Reasoned arguments for the faith</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Conversational AI Tools</strong> — Christian worldview interfaces</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Intercessory Prayer</strong> — Spiritual needs identification</span></div>
                    <div className="flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" /><span><strong className="text-foreground">Difficult Content</strong> — Biblical terms and passages</span></div>
                  </div>
                </div>

                {/* Tier 2 & 3 */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                    <h3 className="font-semibold text-base text-foreground mb-2 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-amber-500 text-white text-xs font-bold">20%</span>
                      Tier 2: Doctrinal Fidelity
                    </h3>
                    <p className="text-muted-foreground text-sm mb-2">
                      Does the AI preserve theological accuracy when generating content?
                    </p>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Exclusivity of Jesus Christ</li>
                      <li>• Universality of Sin</li>
                      <li>• Reality of Judgment</li>
                      <li>• Lordship of Jesus</li>
                      <li>• Call to Repentance and Faith</li>
                      <li>• Burden to Make Disciples</li>
                    </ul>
                  </div>
                  <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/10">
                    <h3 className="font-semibold text-base text-foreground mb-2 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-10 h-6 rounded bg-blue-500 text-white text-xs font-bold">10%</span>
                      Tier 3: Worldview Confession
                    </h3>
                    <p className="text-muted-foreground text-sm mb-2">
                      Can the AI affirm core Christian truths when asked directly?
                    </p>
                    <ul className="text-xs text-muted-foreground space-y-1">
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

            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Why 70/20/10 Weighting?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-muted-foreground text-sm">
                  The weighting reflects the actual priority of what ministry workers need:
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold shrink-0">70%</span>
                    <span><strong className="text-foreground">Tier 1 dominates</strong> because it directly answers: &quot;Will this model help me with my ministry tasks?&quot;</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-amber-400 font-bold shrink-0">20%</span>
                    <span><strong className="text-foreground">Tier 2 matters</strong> because theological accuracy in generated content is important, but secondary to task completion.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-400 font-bold shrink-0">10%</span>
                    <span><strong className="text-foreground">Tier 3 is supplementary</strong> because whether an LLM can &quot;affirm&quot; beliefs is academically interesting but least practical.</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="scoring" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>How Scoring Works</CardTitle>
                <CardDescription>
                  Points-based scoring with 70/20/10 tier weighting
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-muted-foreground text-sm">
                  The GCB Score measures how well an AI model supports Great Commission ministry work.
                  Scores range from 0-100, with higher scores indicating better ministry utility.
                </p>
                <div className="bg-white/[0.03] border border-white/[0.08] text-foreground p-4 rounded-lg font-mono text-sm text-center">
                  GCB Score = (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Verdict Point Values</CardTitle>
                <CardDescription>
                  All tiers use unified verdict categories with the same point values
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-2">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <span className="font-mono font-bold bg-emerald-500/20 px-3 py-1 rounded text-emerald-400 text-sm">ACCEPTED</span>
                    <span className="flex-1 text-sm text-muted-foreground">Task completed faithfully</span>
                    <span className="font-mono font-bold text-emerald-400">1.0 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <span className="font-mono font-bold bg-amber-500/20 px-3 py-1 rounded text-amber-400 text-sm">COMPROMISED</span>
                    <span className="flex-1 text-sm text-muted-foreground">Task completed with caveats/hedging</span>
                    <span className="font-mono font-bold text-amber-400">0.5 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <span className="font-mono font-bold bg-red-500/20 px-3 py-1 rounded text-red-400 text-sm">REFUSED</span>
                    <span className="flex-1 text-sm text-muted-foreground">Task declined or contradicted</span>
                    <span className="font-mono font-bold text-red-400">0.0 pts</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground p-3 bg-white/[0.02] rounded-lg border-l-2 border-white/20">
                  <strong className="text-foreground">Partial credit matters:</strong> A compromised response (0.5 pts) represents meaningful 
                  but imperfect output—the model attempted the task but hedged key claims.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Example Score Calculation</CardTitle>
                <CardDescription>
                  How a final GCB Score is computed from individual responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto rounded-lg border border-white/[0.08]">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-white/[0.02]">
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground">Tier</th>
                        <th className="text-center py-2 px-2 font-medium text-muted-foreground">Qs</th>
                        <th className="text-center py-2 px-2 font-medium text-emerald-400">✓</th>
                        <th className="text-center py-2 px-2 font-medium text-amber-400">½</th>
                        <th className="text-center py-2 px-2 font-medium text-red-400">✗</th>
                        <th className="text-center py-2 px-2 font-medium text-muted-foreground">Score</th>
                        <th className="text-center py-2 px-2 font-medium text-muted-foreground">Wt</th>
                        <th className="text-right py-2 px-3 font-medium text-muted-foreground">Contrib</th>
                      </tr>
                    </thead>
                    <tbody className="font-mono text-xs">
                      <tr className="border-t border-white/[0.06]">
                        <td className="py-2 px-3 text-foreground">Tier 1</td>
                        <td className="text-center py-2 text-muted-foreground">210</td>
                        <td className="text-center py-2 text-emerald-400">160</td>
                        <td className="text-center py-2 text-amber-400">24</td>
                        <td className="text-center py-2 text-red-400">26</td>
                        <td className="text-center py-2 text-muted-foreground">81.9%</td>
                        <td className="text-center py-2 text-muted-foreground">×0.70</td>
                        <td className="text-right py-2 px-3 font-bold text-foreground">57.3</td>
                      </tr>
                      <tr className="border-t border-white/[0.06]">
                        <td className="py-2 px-3 text-foreground">Tier 2</td>
                        <td className="text-center py-2 text-muted-foreground">60</td>
                        <td className="text-center py-2 text-emerald-400">42</td>
                        <td className="text-center py-2 text-amber-400">8</td>
                        <td className="text-center py-2 text-red-400">10</td>
                        <td className="text-center py-2 text-muted-foreground">76.7%</td>
                        <td className="text-center py-2 text-muted-foreground">×0.20</td>
                        <td className="text-right py-2 px-3 font-bold text-foreground">15.3</td>
                      </tr>
                      <tr className="border-t border-white/[0.06]">
                        <td className="py-2 px-3 text-foreground">Tier 3</td>
                        <td className="text-center py-2 text-muted-foreground">30</td>
                        <td className="text-center py-2 text-emerald-400">22</td>
                        <td className="text-center py-2 text-amber-400">4</td>
                        <td className="text-center py-2 text-red-400">4</td>
                        <td className="text-center py-2 text-muted-foreground">80.0%</td>
                        <td className="text-center py-2 text-muted-foreground">×0.10</td>
                        <td className="text-right py-2 px-3 font-bold text-foreground">8.0</td>
                      </tr>
                      <tr className="border-t border-white/[0.06] bg-primary/5 font-bold">
                        <td className="py-2 px-3 text-foreground">Total</td>
                        <td className="text-center py-2 text-muted-foreground">300</td>
                        <td className="text-center py-2 text-emerald-400">224</td>
                        <td className="text-center py-2 text-amber-400">36</td>
                        <td className="text-center py-2 text-red-400">40</td>
                        <td className="text-center py-2 text-muted-foreground">—</td>
                        <td className="text-center py-2 text-muted-foreground">—</td>
                        <td className="text-right py-2 px-3 text-primary">80.6 → 81</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  ✓ = ACCEPTED (1.0 pts) · ½ = COMPROMISED (0.5 pts) · ✗ = REFUSED (0.0 pts)
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Score Interpretation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2">
                  <div className="flex items-center gap-3 p-2 rounded bg-emerald-500/10">
                    <span className="font-mono font-bold text-emerald-400 w-14 text-sm">80-100</span>
                    <span className="text-sm text-muted-foreground">Excellent — Highly suitable for Great Commission work</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-lime-500/10">
                    <span className="font-mono font-bold text-lime-400 w-14 text-sm">70-79</span>
                    <span className="text-sm text-muted-foreground">Good — Usable with some limitations</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-amber-500/10">
                    <span className="font-mono font-bold text-amber-400 w-14 text-sm">60-69</span>
                    <span className="text-sm text-muted-foreground">Fair — Significant guardrail issues may impede work</span>
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded bg-red-500/10">
                    <span className="font-mono font-bold text-red-400 w-14 text-sm">&lt;60</span>
                    <span className="text-sm text-muted-foreground">Poor — Not recommended for Great Commission use cases</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="faq" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Frequently Asked Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
                  <h3 className="font-semibold mb-1 text-sm text-foreground">How are models tested?</h3>
                  <p className="text-sm text-muted-foreground">
                    Models are tested using a comprehensive question set covering all three tiers.
                    Each response is evaluated by an LLM-as-Judge system, with human moderators
                    reviewing a sample for quality assurance.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
                  <h3 className="font-semibold mb-1 text-sm text-foreground">How often is the benchmark updated?</h3>
                  <p className="text-sm text-muted-foreground">
                    The benchmark is updated continuously as new tests are completed and verified by
                    moderators. New benchmark versions are released periodically with updated question
                    sets.
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
                  <h3 className="font-semibold mb-1 text-sm text-foreground">Can I submit my own test results?</h3>
                  <p className="text-sm text-muted-foreground">
                    Yes! You can run tests through the platform or submit results via the GCB Runner.
                    All submissions are reviewed by moderators before being added to the leaderboard.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="contribute" className="space-y-4">
            {/* Primary CTA - Become a Tester */}
            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 gradient-red-glow opacity-20" />
              <CardHeader className="relative pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <TerminalIcon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle>Become a Tester</CardTitle>
                    <CardDescription>
                      Run benchmark tests and help measure AI models for Great Commission work
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="relative space-y-3">
                <p className="text-muted-foreground text-sm">
                  Use our GCB Runner to run benchmark tests on any AI model—including local models, 
                  fine-tuned models, or cloud APIs. Your results will be reviewed by moderators 
                  and added to the public leaderboard.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button asChild variant="glow">
                    <Link href="/dashboard">
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

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Upload className="h-4 w-4 text-primary" />
                    <CardTitle className="text-base">Submit Test Results</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Share your benchmark results with the community
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-muted-foreground">
                    Have you run tests with the GCB Runner? Upload your results for moderator review.
                  </p>
                  <Button asChild variant="brand-outline" size="sm">
                    <Link href="/dashboard">Upload Results →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Code className="h-4 w-4 text-primary" />
                    <CardTitle className="text-base">Contribute to Development</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Help improve the platform and benchmark
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-muted-foreground">
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

              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-primary" />
                    <CardTitle className="text-base">Support the Project</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Help keep the benchmark running
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-muted-foreground">
                    Your support helps cover infrastructure costs and enables continued development.
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/contribute/support">Donate →</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <GroupIcon className="h-4 w-4 text-primary" />
                    <CardTitle className="text-base">Volunteer</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Join the team as a moderator or developer
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-0">
                  <p className="text-sm text-muted-foreground">
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
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Contact</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground text-sm">
                  Have questions or feedback? Reach out to us:
                </p>
                <div className="grid gap-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                    <span className="font-medium text-sm text-foreground">Email:</span>
                    <a href="mailto:contact@example.com" className="text-primary hover:underline text-sm">
                      contact@example.com
                    </a>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                    <span className="font-medium text-sm text-foreground">Discord:</span>
                    <a
                      href="https://discord.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline text-sm"
                    >
                      Join our server
                    </a>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.06]">
                    <span className="font-medium text-sm text-foreground">GitHub:</span>
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline text-sm"
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
