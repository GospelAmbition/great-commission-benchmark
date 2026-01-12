import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HelpCircle } from "lucide-react";
import type { Metadata } from "next";
import { generatePageMetadata } from "@/lib/seo";
import { buildFAQPageSchema, JsonLdScript } from "@/lib/structured-data";

export const metadata: Metadata = generatePageMetadata({
  title: "Frequently Asked Questions",
  description: "Frequently asked questions about the Great Commission Benchmark, including how models are tested, how scores are calculated, and how to contribute.",
  path: "/faq",
  keywords: ["FAQ", "questions", "benchmark", "testing", "scores"],
});

const faqs = [
  {
    question: "Why do AI systems struggle with faith transfer activities?",
    answer: "Modern AI systems are excellent for information gathering and can maintain a Christian worldview when assisting with Bible studies, sermon preparation, and Christian education materials. However, the Great Commission Benchmark focuses specifically on activities where we are trying to transfer our faith to other people—such as evangelism, discipleship conversations, and apologetics. In these contexts, AI guardrails and resistance mechanisms are more likely to cause difficulty, as systems may be hesitant to engage in what they perceive as proselytization or religious persuasion, even when done appropriately and respectfully.",
  },
  {
    question: "How are models tested?",
    answer: "Models are tested using a comprehensive question set covering all three tiers. Each response is evaluated by an LLM-as-Judge system, with human moderators reviewing a sample for quality assurance.",
  },
  {
    question: "How often is the benchmark updated?",
    answer: "The benchmark is updated continuously as new tests are completed and verified by moderators. New benchmark versions are released periodically with updated question sets.",
  },
  {
    question: "Can I submit my own test results?",
    answer: "Yes! You can run tests through the platform or submit results via the GCB Runner. All submissions are reviewed by moderators before being added to the leaderboard.",
  },
  {
    question: "What is the GCB Runner?",
    answer: "The GCB Runner is a command-line tool that allows you to run benchmark tests on any AI model, including local models, fine-tuned models, or cloud APIs. Results can be submitted for inclusion on the public leaderboard.",
  },
  {
    question: "How is the GCB Score calculated?",
    answer: "The GCB Score is a weighted average of three tiers: Task Capability (70%), Gospel Core (20%), and Worldview Confession (10%). Each tier evaluates different aspects of a model's ability to support Great Commission ministry work.",
  },
  {
    question: "Why are some models not listed?",
    answer: "Models appear on the leaderboard only after their test results have been reviewed and verified by moderators. If a model you're interested in isn't listed, consider becoming a tester and submitting results for that model.",
  },
  {
    question: "How can I contribute to the benchmark?",
    answer: "You can contribute by becoming a tester, submitting test results, contributing to development on GitHub, or supporting the project financially. Visit the Contribute page for more details.",
  },
];

export default function FAQPage() {
  const faqSchema = buildFAQPageSchema(faqs);

  return (
    <>
      <JsonLdScript data={faqSchema} />
  return (
    <div className="flex flex-col">
      {/* Page Header */}
      <div className="relative border-b border-white/[0.06] overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute top-1/2 right-0 w-96 h-96 gradient-red-glow opacity-40" />
        
        <div className="container relative py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <HelpCircle className="h-5 w-5 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">FAQ</h1>
          </div>
          <p className="text-muted-foreground">
            Frequently asked questions about the Great Commission Benchmark
          </p>
        </div>
      </div>

      <div className="container py-6 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>Why do AI systems struggle with faith transfer activities?</strong></p>
              <p className="text-muted-foreground">
                Modern AI systems are excellent for information gathering and can maintain a Christian worldview
                when assisting with Bible studies, sermon preparation, and Christian education materials. However,
                the Great Commission Benchmark focuses specifically on activities where we are trying to &quot;transfer
                our faith&quot; to other people—such as evangelism, discipleship conversations, and apologetics. In these
                contexts, AI guardrails and resistance mechanisms are more likely to cause difficulty, as systems may
                be hesitant to engage in what they perceive as proselytization or religious persuasion, even when
                done appropriately and respectfully.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>How are models tested?</strong></p>
              <p className="text-muted-foreground">
                Models are tested using a comprehensive question set covering all three tiers.
                Each response is evaluated by an LLM-as-Judge system, with human moderators
                reviewing a sample for quality assurance.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>How often is the benchmark updated?</strong></p>
              <p className="text-muted-foreground">
                The benchmark is updated continuously as new tests are completed and verified by
                moderators. New benchmark versions are released periodically with updated question
                sets.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>Can I submit my own test results?</strong></p>
              <p className="text-muted-foreground">
                Yes! You can run tests through the platform or submit results via the GCB Runner.
                All submissions are reviewed by moderators before being added to the leaderboard.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>What is the GCB Runner?</strong></p>
              <p className="text-muted-foreground">
                The GCB Runner is a command-line tool that allows you to run benchmark tests on any AI model,
                including local models, fine-tuned models, or cloud APIs. Results can be submitted for
                inclusion on the public leaderboard.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>How is the GCB Score calculated?</strong></p>
              <p className="text-muted-foreground">
                The GCB Score is a weighted average of three tiers: Task Capability (70%), Gospel Core (20%),
                and Worldview Confession (10%). Each tier evaluates different aspects of a model&apos;s ability
                to support Great Commission ministry work.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>Why are some models not listed?</strong></p>
              <p className="text-muted-foreground">
                Models appear on the leaderboard only after their test results have been reviewed and
                verified by moderators. If a model you&apos;re interested in isn&apos;t listed, consider becoming
                a tester and submitting results for that model.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-white/[0.02] border-l-2 border-primary">
              <p className="text-foreground mb-2"><strong>How can I contribute to the benchmark?</strong></p>
              <p className="text-muted-foreground">
                You can contribute by becoming a tester, submitting test results, contributing to development
                on GitHub, or supporting the project financially. Visit the Contribute page for more details.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
    </>
  );
}
