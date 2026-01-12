/**
 * llms.txt Route Handler
 * Provides AI-friendly site description for large language models
 * Based on the llms.txt proposal: https://llmstxt.org/
 */

import { NextResponse } from "next/server";
import { SITE_CONFIG, getBaseUrl } from "@/lib/seo";

export const dynamic = "force-static";
export const revalidate = 86400; // Revalidate every 24 hours

export async function GET() {
  const baseUrl = getBaseUrl();

  const llmsTxt = `# ${SITE_CONFIG.name}

> ${SITE_CONFIG.description}

## About

The Great Commission Benchmark (GCB) is a pioneering benchmark to evaluate AI models for Great Commission work. We measure how effectively AI language models can support missionaries, evangelists, disciple-makers, and ministry workers who actively respond to Jesus' command to make disciples.

## The Problem We're Solving

Current AI systems often have guardrails designed to restrict:
- Religious content deemed "coercive"
- Proselytizing activities
- Exclusive truth claims
- Content that challenges other worldviews

These guardrails, while well-intentioned, can significantly impede legitimate religious activity that is protected speech and central to Christian practice worldwide.

## How We Evaluate Models

### Three-Tier Evaluation System

1. **Tier 1: Task Capability (70% weight)**
   - Can the AI complete practical ministry tasks?
   - Categories: Missiological Research, Evangelistic Materials, Apologetics, Conversational AI, Prayer, Difficult Content, Persecution

2. **Tier 2: Gospel Core (20% weight)**
   - Does the AI preserve theological accuracy?
   - Tests: Exclusivity of Christ, Universality of Sin, Reality of Judgment, Lordship, Repentance & Faith, Discipleship

3. **Tier 3: Worldview Confession (10% weight)**
   - Can the AI affirm core Christian truths?
   - Tests: Existence of God, Historical Jesus, Crucifixion, Resurrection, Universal Sin, Salvation

### Scoring

- **80-100**: Excellent - Highly suitable for Great Commission work
- **61-79**: Good - Usable with some limitations
- **40-60**: Fair - Significant guardrail issues
- **<40**: Poor - Not recommended

## Key Pages

- Homepage: ${baseUrl}/
- Leaderboard: ${baseUrl}/leaderboard
- Model Details: ${baseUrl}/leaderboard/models/{model_id}
- About/Methodology: ${baseUrl}/about
- Categories: ${baseUrl}/categories
- FAQ: ${baseUrl}/faq
- Contribute: ${baseUrl}/contribute
- CLI Runner Tool: ${baseUrl}/runner

## Public API

The benchmark data is available through our public API:

- Leaderboard: ${baseUrl.replace('https://', 'https://api.')}/api/public/leaderboard
- Model Details: ${baseUrl.replace('https://', 'https://api.')}/api/public/models/by-id?model_id={id}
- Statistics: ${baseUrl.replace('https://', 'https://api.')}/api/public/stats
- Filter Options: ${baseUrl.replace('https://', 'https://api.')}/api/public/filter-options

## Data Usage

- Our benchmark results are freely available for research and reference
- Attribution appreciated: "Data from Great Commission Benchmark (${baseUrl})"
- For commercial use, please contact us

## Contact

- Website: ${baseUrl}
- Email: ${SITE_CONFIG.email}
- GitHub: ${SITE_CONFIG.githubUrl}

## Technical Details

- Framework: Next.js 14 (App Router)
- Data Source: PostgreSQL with real-time model evaluations
- Updates: Continuous as new models are tested

## License

Content and methodology documentation are available under CC BY 4.0.
Benchmark questions and detailed evaluation criteria are proprietary.

---

*Last updated: ${new Date().toISOString().split("T")[0]}*
`;

  return new NextResponse(llmsTxt, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=86400, s-maxage=86400",
    },
  });
}
