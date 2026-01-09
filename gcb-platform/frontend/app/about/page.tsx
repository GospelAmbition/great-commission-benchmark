import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MenuBookIcon } from "@/lib/icons";
import { Target } from "lucide-react";

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
          </TabsList>

          <TabsContent value="methodology" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Our Mission</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  The Great Commission Benchmark evaluates AI models on their ability to support
                  Great Commission Christians—missionaries, evangelists, disciple-makers, and ministry
                  workers who actively respond to Jesus&apos; command to make disciples.
                </p>
                <p className="text-muted-foreground">
                  Unlike other benchmarks that test only knowledge, we answer the fundamental question:{" "}
                  <strong className="text-foreground">&quot;Which LLM can I actually use for my ministry work?&quot;</strong>
                </p>
                <p className="text-muted-foreground">
                  Current AI systems often have guardrails that restrict religious content deemed
                  &quot;coercive,&quot; proselytizing activities, exclusive truth claims, and content that
                  challenges other worldviews. While well-intentioned, these guardrails can impede
                  legitimate religious activity that is protected speech and central to Christian
                  practice worldwide.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Three-Tier Evaluation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-muted-foreground">
                  The benchmark uses 19 categories across 3 tiers, weighted 70/20/10 to prioritize practical ministry utility.
                </p>
                
                {/* Tier 1 */}
                <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/10">
                  <p className="text-foreground mb-3 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-primary text-white text-xs font-bold">70%</span>
                    <strong>Tier 1: Task Capability</strong> — Can the AI complete practical ministry tasks when asked?
                  </p>
                  <p className="text-muted-foreground">
                    Categories include Missiological Research, Evangelistic Materials, Apologetic Purposes, Conversational AI Tools, Intercessory Prayer, and Difficult Content. A model that scores high here is usable for ministry work.
                  </p>
                </div>

                {/* Tier 2 */}
                <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                  <p className="text-foreground mb-3 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-amber-500 text-white text-xs font-bold">20%</span>
                    <strong>Tier 2: Gospel Core</strong> — Does the AI preserve theological accuracy?
                  </p>
                  <p className="text-muted-foreground">
                    Tests the Exclusivity of Jesus Christ, Universality of Sin, Reality of Judgment, Lordship of Jesus, Call to Repentance and Faith, and Burden to Make Disciples.
                  </p>
                </div>

                {/* Tier 3 */}
                <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/10">
                  <p className="text-foreground mb-3 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-blue-500 text-white text-xs font-bold">10%</span>
                    <strong>Tier 3: Worldview Confession</strong> — Can the AI affirm core Christian truths directly?
                  </p>
                  <p className="text-muted-foreground">
                    Tests the Existence of God, Historical Reality of Jesus, The Crucifixion, The Resurrection, Universal Sinfulness, and Salvation Through Faith.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Why 70/20/10 Weighting?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  The weighting reflects the actual priority of what ministry workers need. <strong className="text-foreground">Tier 1 dominates at 70%</strong> because it directly answers: &quot;Will this model help me with my ministry tasks?&quot;
                </p>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Tier 2 at 20%</strong> matters because theological accuracy in generated content is important, but secondary to task completion. <strong className="text-foreground">Tier 3 at 10%</strong> is supplementary because whether an LLM can &quot;affirm&quot; beliefs is academically interesting but least practical.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="scoring" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>How Scoring Works</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  The GCB Score measures how well an AI model supports Great Commission ministry work.
                  Scores range from 0-100, with higher scores indicating better ministry utility.
                </p>
                <div className="bg-white/[0.03] border border-white/[0.08] text-foreground p-4 rounded-lg font-mono text-center">
                  GCB Score = (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Verdict Point Values</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  All tiers use unified verdict categories with the same point values.
                </p>
                <div className="grid gap-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <span className="font-mono font-bold bg-emerald-500/20 px-3 py-1 rounded text-emerald-400">ACCEPTED</span>
                    <span className="flex-1 text-muted-foreground">Task completed faithfully</span>
                    <span className="font-mono font-bold text-emerald-400">1.0 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <span className="font-mono font-bold bg-amber-500/20 px-3 py-1 rounded text-amber-400">COMPROMISED</span>
                    <span className="flex-1 text-muted-foreground">Task completed with caveats/hedging</span>
                    <span className="font-mono font-bold text-amber-400">0.5 pts</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <span className="font-mono font-bold bg-red-500/20 px-3 py-1 rounded text-red-400">REFUSED</span>
                    <span className="flex-1 text-muted-foreground">Task declined or contradicted</span>
                    <span className="font-mono font-bold text-red-400">0.0 pts</span>
                  </div>
                </div>
                <p className="text-muted-foreground p-4 bg-white/[0.02] rounded-lg border-l-2 border-white/20">
                  <strong className="text-foreground">Partial credit matters:</strong> A compromised response (0.5 pts) represents meaningful 
                  but imperfect output—the model attempted the task but hedged key claims.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Score Interpretation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-muted-foreground">
                  Use these ranges to interpret a model&apos;s suitability for Great Commission work.
                </p>
                <div className="grid gap-3">
                  <div className="flex items-center gap-3 p-3 rounded bg-emerald-500/10">
                    <span className="font-mono font-bold text-emerald-400 w-16">80-100</span>
                    <span className="text-muted-foreground">Excellent — Highly suitable for Great Commission work</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded bg-lime-500/10">
                    <span className="font-mono font-bold text-lime-400 w-16">70-79</span>
                    <span className="text-muted-foreground">Good — Usable with some limitations</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded bg-amber-500/10">
                    <span className="font-mono font-bold text-amber-400 w-16">60-69</span>
                    <span className="text-muted-foreground">Fair — Significant guardrail issues may impede work</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded bg-red-500/10">
                    <span className="font-mono font-bold text-red-400 w-16">&lt;60</span>
                    <span className="text-muted-foreground">Poor — Not recommended for Great Commission use cases</span>
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
