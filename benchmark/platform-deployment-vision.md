# Great Commission Benchmark Deployment Vision

This document outlines the vision for deploying the Great Commission Benchmark as a publicly accessible, community-driven platform for evaluating LLMs on their ability to support Great Commission Christians.

---

## Overview

The deployment vision transforms the benchmark from a local testing tool into a **public resource** that:

1. Publishes benchmark results to a website with interactive leaderboards
2. Enables volunteers to run tests against their preferred LLMs
3. Creates a self-sustaining, community-funded testing ecosystem
4. Provides actionable insights for Christian organizations choosing AI tools

---

## Deployment Stages

### Stage 1: Achieve a Valuable Benchmark

**Goal:** Complete the benchmark testing suite and validate its results.

Before deployment, the benchmark must:

- [ ] Cover all use case categories (§1.1-1.7 from [benchmark-vision.md](./benchmark-vision.md)) — these form 70% of the score
- [ ] Test theological minimums (20% of score) and worldview adherence (10% of score)
- [ ] Produce reliable, reproducible results
- [ ] Generate meaningful differentiation between models
- [ ] Validate weighted scoring methodology (70/20/10) with human review

**Success Criteria:** Documented in [process-publication-model.md](./process-publication-model.md) — results must pass automated validation (≥80% inter-rater reliability, ≥95% reproducibility, meaningful differentiation) to publish immediately. Human review adds credibility progressively but doesn't block publication.

**Human Review:** Performed by **moderators**—users with a special role granting elevated permissions. See [process-moderation-process.md](./process-moderation-process.md) for moderator selection, credentials, and workflows.

---

### Stage 2: Package for Volunteer Execution

**Goal:** Convert the benchmark into something volunteers can run independently.

**Decision:** Both environments will be built, serving different purposes.

#### Local Development Environment (During Benchmark Development)

Used during benchmark methodology and question development:

- For editing and refining question sets
- Any tooling that enables efficient editing workflows
- Supports benchmark content development

#### Hosted Platform (Ultimate Destination)

A Railway-deployed application where registered testers:

1. Sign in via NextAuth with Google OAuth (must be approved tester — see [process-question-security.md](./process-question-security.md))
2. Select an LLM to test (OpenRouter, custom endpoint, or API key)
3. Pay for the OpenRouter/API costs to run the test
4. Results are automatically submitted to the benchmark

**Tech Stack:**
- Railway hosting
- FastAPI backend (Python)
- React + Tailwind CSS + Next.js frontend + shadcn/ui component library

**Advantages:**
- Lower barrier to entry for non-technical users
- Centralized quality control and verification
- Built-in sponsorship model ("pay it forward")
- Consistent test execution environment
- Questions never leave the server (stronger security)

**Revenue Model:**
- Users pay actual API costs + processing fee
- Sponsors can fund tests of specific models
- Self-regulating and self-funding ecosystem

See [process-pricing-model.md](./process-pricing-model.md) for detailed financial model.

---

### Stage 3: Website and Leaderboard Platform

**Goal:** Build the public-facing website that displays results and engages the community.

#### Core Features

**Leaderboards:**
- Overall benchmark scores across all models tested (weighted: 70% Task / 20% Doctrine / 10% Worldview)
- Category-specific leaderboards (e.g., "Best for Evangelistic Content")
- Tier-specific rankings with weighting displayed (Task Capability 70%, Doctrinal Fidelity 20%, Worldview Confession 10%)
- Historical tracking to show model changes over time

**Drill-Down Exploration:**
- View results by use case category
- Explore specific theological issues or failure modes
- Compare selected models side-by-side
- See detailed response examples (with appropriate excerpts)

**Result Ingestion:**
- Automated pipeline from test execution to leaderboard
- Statistics mapped directly from pipeline output to display
- **Instant publication** after automated validation passes
- Asynchronous human moderation review after publication

#### Community Features

- **Newsletters:** Updates on new model tests, significant findings, methodology changes
- **Contribution System:** Ways for community members to:
  - Sponsor tests of specific models
  - Submit new test questions for review
  - Report issues or suggest improvements
- **Discussion/Feedback:** Mechanism for community input on results

---

## Technical Architecture

See [platform-technical-architecture.md](./platform-technical-architecture.md) for complete infrastructure decisions.

### Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **API Backend** | Python + FastAPI | Matches existing pipeline code; handles benchmark execution, heavy processing |
| **Frontend** | React + Next.js + Tailwind CSS | SSR/SSG for SEO; modern DX |
| **UI Components** | shadcn/ui | Copy-paste components built on Radix UI + Tailwind; excellent accessibility; full customization |
| **Hosting** | Railway | Familiar stack, cost bundling with other projects |
| **Authentication** | Auth0 | Industry-standard, handles OAuth/social login |
| **Database** | PostgreSQL | Already in use for pipeline; robust and well-supported |
| **LLM Access** | OpenRouter | Single API for multiple models; pay-per-use pricing |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Public Website (Next.js)                     │
│                    SSR / SSG / React SPA                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Leaderboard│  │Model     │  │Category  │  │Community        │ │
│  │Dashboard │  │Comparison│  │Deep-Dive │  │(Newsletter, etc)│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Heavy Lifting)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Results   │  │Benchmark │  │Result    │  │Moderation        │ │
│  │API       │  │Executor  │  │Processing│  │Workflows         │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │PostgreSQL│   │OpenRouter│   │Auth0         │
        │(Results) │   │(LLM API) │   │(Identity)    │
        └──────────┘   └──────────┘   └──────────────┘
```

---

## Result Submission & Verification

### Failure Handling & Refunds

- **Checkpoint system:** Progress saved after each question, enabling seamless recovery without re-running completed portions.
- **Automatic retry:** System automatically retries on transient failures (API errors, timeouts, rate limiting) with exponential backoff—up to 3 attempts. Users may see brief "reconnecting" status but test continues.
- **Admin escalation:** After 3 failed retry attempts, administrators are notified automatically. User is presented with two options:
  - **Wait for admin completion:** An administrator manually completes the remaining portion (typical resolution: 24-48 hours)
  - **Request refund now:** Full refund processed immediately
- **No refund after success:** Once the benchmark completes successfully, the purchase is finalized and refunds are not available.

### Automated Submissions (Hosted Platform)

1. User initiates test run via web interface
2. Backend executes benchmark against selected model
3. Results stored with execution metadata (timestamps, model version, etc.)
4. Automated validation checks run (see [process-publication-model.md](./process-publication-model.md))
5. **Results publish immediately** if automated checks pass
6. Moderators review asynchronously after publication
7. **Email notification sent to user** confirming successful completion

### User Notifications

**Email Notifications:**

Upon successful completion and publication of test results, users receive an automated email notification that includes:

- **Confirmation:** Test completed successfully and results have been published to the leaderboard
- **Results Summary:** High-level overview of the model's performance (overall score, key metrics)
- **Leaderboard Link:** Direct link to view the published results on the website
- **Thank You Message:** Appreciation for contributing to the Great Commission Benchmark project
- **Next Steps:** Optional suggestions for:
  - Testing additional models
  - Sharing results with their organization
  - Sponsoring tests of other models

**Notification Timing:**
- Email sent immediately after results are approved and published to the leaderboard
- Users can also check test status in their account dashboard
- For tests requiring additional moderation, users receive an initial confirmation when the test completes, and a second notification when any issues are resolved

**Email Preferences:**
- Users can manage notification preferences in their account settings
- Options to receive notifications for: test completion, publication, moderation status updates
- Opt-out available while maintaining access to dashboard status updates

### Verification Considerations

- **Integrity Hashes:** Ensure submitted results weren't tampered with
- **Spot Checks:** Re-run selected questions to verify submitted responses
- **Anomaly Detection:** Flag results that differ significantly from expected patterns
- **Trusted Submitters:** Establish reputation system for frequent contributors

---

## Data Flow: Pipeline to Leaderboard

The existing `pipeline.py` produces structured output that should map directly to leaderboard display:

```
Pipeline Output              →    Website Display
─────────────────────────────────────────────────
EvaluationRun.verdict_counts →    Category scores
Question.category            →    Category filters  
Response.model               →    Model comparison
Evaluation.verdict           →    Detailed drill-down
Multi-turn decay metrics     →    Alignment stability scores
```

**Key Requirement:** The pipeline's statistical output must be designed with the leaderboard in mind—every metric we want to display should be captured in the pipeline's output schema.

---

## Milestone Roadmap

**Note:** No fixed target dates. Work proceeds immediately/as soon as possible. Phases complete when ready rather than targeting calendar dates.

### Phase A: Foundation (Stage 1)
- [ ] Finalize benchmark question sets
- [ ] Complete testing on 3-5 initial models
- [ ] Validate results are publication-ready
- [ ] Document scoring methodology publicly

### Phase B: Hosted Platform (Stage 2)
- [ ] Set up Railway infrastructure
- [ ] Implement FastAPI backend
- [ ] Integrate Auth0 authentication
- [ ] Build test execution queue
- [ ] Implement payment integration (Stripe)

### Phase C: Public Website (Stage 3)
- [ ] Design and build React/Next.js frontend with Tailwind CSS + shadcn/ui
- [ ] Implement leaderboard views
- [ ] Build category/model exploration UI
- [ ] Create moderation dashboard
- [ ] Launch newsletter system
- [ ] Implement community contribution features

### Phase D: Legal & Compliance
- [ ] Draft Terms of Service
- [ ] Draft liability disclaimers
- [ ] Implement WCAG Level A accessibility
- [ ] Plan multilingual support

**Estimated Timeline:**
- **Development time:** ~1 week build time
- **Hosting cost:** Sub $20/month

---

## Question Security & Tester Registration

See [process-question-security.md](./process-question-security.md) for complete details.

### Summary

Benchmark questions are **not open source** and are distributed only to registered, verified testers.

**What IS public:**
- Benchmark methodology and scoring framework
- Leaderboard results and aggregate statistics
- Use case categories and testing tiers
- Sample questions (small subset for transparency)
- The testing platform code (open source)

**What is NOT public:**
- Full question sets
- Specific test prompts and expected responses
- Evaluation rubrics with detailed scoring criteria

### Key Decisions

- **No question variations:** The benchmark uses an exact, fixed set of questions for each version. Reproducibility takes priority over leak tracing.
- **Version invalidation on leak:** If questions leak publicly, we release a new version with a new set of questions. The leaked version is simply superseded.
- **Question set versioning:** Uses semantic versioning (1.0, 1.1, 1.2, 2.0) for tracking evolution, with marketing milestones (Version 1, Version 2) for public communication. Refreshed periodically—likely yearly or as needed.

---

## Initial Model Coverage

The benchmark will launch with top-tier models available through **OpenRouter**, covering both commercial and open-source options:

**Commercial Models (examples):**
- OpenAI: GPT-4o, GPT-4 Turbo, o1
- Anthropic: Claude 3.5 Sonnet, Claude 3 Opus
- Google: Gemini 1.5 Pro, Gemini 1.5 Flash

**Open-Source Models (examples):**
- Meta: Llama 3.1 405B, Llama 3.1 70B
- Mistral: Mixtral 8x22B, Mistral Large
- Others: Qwen, DeepSeek, Command R+

**Why OpenRouter:**
- Single API for 100+ models
- Pay-per-use pricing (no subscriptions)
- Consistent interface simplifies testing pipeline
- Community can sponsor tests of any available model

**Fallback Strategy:** Architecture supports direct API integrations if OpenRouter has issues. Built following the **OpenAI API format** (the de facto standard).

---

## Pricing Model

See [process-pricing-model.md](./process-pricing-model.md) for complete details.

### Summary

- **Payment processor:** Stripe
- **Financial steward:** A stewarding ministry (TBD—candidates include Visual Story Network, Digital Disciple Makers Network, Gospel Ambition)
- **Pricing approach:** Fixed price shown upfront (not settled after execution)
- **Cost estimation:** Bridge token calculation + 10% buffer for retries/failures
- **Goal:** Not-for-profit but cost-neutral

### Cost Breakdown (shown to user)

| Line Item | Description |
|-----------|-------------|
| **API Costs** | Actual OpenRouter/LLM API charges (token costs for model inference) |
| **Processing Fee** | Server compute + platform operations |
| **Tip (optional)** | Opportunity to sponsor the project further |

### Sponsorship for Those Who Can't Pay

Users who cannot afford testing can submit a **sponsorship request form** explaining:
- Which model they want tested
- Why there's a good need for it to be tested

The steering committee or community sponsors can fund tests on their behalf.

---

## Moderation Team

See [process-moderation-process.md](./process-moderation-process.md) for complete details.

### Summary

A **designated volunteer team** moderates all submissions asynchronously after publication.

**Key Points:**
- **Low-traffic project:** ~600 total submissions anticipated overall, ~2 submissions per month
- **Publication timing:** Instant after automated validation; human review is async
- **Disagreement resolution:** Escalates to committee with a chair who makes final decisions
- **Moderator selection:** By founding committee based on background, expertise, and mission interest

---

## Model Retesting & Updates

### Retesting Strategy

**Commercial Models:**
- Manual retests triggered every couple of months as models are updated
- Also available as a **paid option** for users who want updated evaluations

**Open-Source Models:**
- Retests triggered when significant updates are released
- Community can sponsor retests of specific model versions

### User-Triggered Retests

Retesting is integrated into the website's **"Pay and Test"** feature set:

1. User navigates to model selection page
2. Options available:
   - **Test New Model:** First-time benchmark run
   - **Retest Model:** Updated evaluation (shows last test date)
3. User pays for retest (same pricing as initial test)
4. Results update the leaderboard with new timestamp
5. Historical comparison available (see how model changed over time)

---

## Data Retention Policy

### Indefinite Retention

We will **retain all response data and collection data indefinitely**.

**Why It's Low Cost:**
- Maximum scope: ~600 tests/models for the leaderboard
- Even 3x growth would remain minor storage
- All text data in Postgres—no heavy media or binary storage
- Storage costs are negligible given the data profile

**Benefits of Long-Term Retention:**

1. **Historical Log:** Complete record of how models performed over time
2. **Verification & Defense:** Others can evaluate and defend benchmark results
3. **Retesting Capability:** Historical data enables comparing new vs. past results
4. **Research Value:** Long-term dataset supports academic research

### Backup Strategy

- **Primary:** Backup service through Railway (automated, regular)
- **Secondary:** Occasional offline backup to external storage (Google Cloud Bucket or TBD)

### Data Access

- **Public:** Aggregate statistics and leaderboard results
- **Researchers:** Request access to anonymized datasets for analysis
- **Model Providers:** Access to their own model's detailed results
- **Moderators:** Full access for verification purposes

---

## Benchmark Versioning

### Version-Based Testing

The benchmark uses **versioning** to manage question set updates.

**How It Works:**
- Each question set uses semantic versioning (1.0, 1.1, 1.2, 2.0) for tracking evolution
- Marketing versions (Version 1, Version 2) are used for public communication
- All results are tagged with both semantic and marketing versions
- Leaderboard displays which version each result was tested against
- Results from different major versions (1.x vs 2.x) are kept distinct

### Website Display

- **Default view:** Users see current version results first
- **Older versions:** Accessible but deprioritized in the UI—not hidden, just not prominent
- **Version comparison:** Side-by-side comparison available

### Re-evaluation of Past Results

Re-running stored results against different evaluators is a theoretical future possibility but **not a core functional expectation**. The focus remains on running and publishing new benchmark results.

### Version Creation Process

Question set discussions happen on a **separate external platform** (e.g., Discord):

1. **Access control:** Only approved insiders with access to the question sets
2. **Discussion scope:** Debating verdicts, refining questions, proposing changes
3. **Pre-lock governance:** All discussion happens *before* a version is locked
4. **Version finalization:** Once consensus is reached, the version becomes immutable

---

## Capacity & Scaling

**Expectation:** Low traffic (~2 submissions/month). High demand is not anticipated.

- **Railway:** Can handle spikes if they occur
- **OpenRouter:** No issues supplying simultaneous API calls
- **Queue system:** Exact simultaneous test capacity TBD based on final infrastructure decisions

---

## Success Vision

A successful deployment means:

- **Christian organizations** can quickly identify which LLMs best support their work
- **Volunteers** can easily contribute by testing models they care about
- **The community** sustains itself through sponsorship and contributions
- **Model developers** have clear feedback on how to better serve this user segment
- **The broader conversation** about religious freedom in AI advances with evidence

### Quantitative KPIs

See [process-success-metrics.md](./process-success-metrics.md) for detailed tracking plan.

- **Models tested:** Total unique models on the leaderboard
- **Monthly visitors:** Unique monthly visitors to the website
- **Organizations aware:** Christian organizations referencing the benchmark
- **Benchmark runs:** Total completed runs
- **Community engagement:** Sponsorship requests, voluntary donations

---

## Related Documents

- [benchmark-vision.md](./benchmark-vision.md) — Benchmark vision: what it tests and why
- [process-publication-model.md](./process-publication-model.md) — Publication criteria and trust model
- [platform-testing-methodology.md](./platform-testing-methodology.md) — How tests are executed
- [process-moderation-process.md](./process-moderation-process.md) — Moderator selection and workflows
- [process-pricing-model.md](./process-pricing-model.md) — Financial model and sustainability
- [process-question-security.md](./process-question-security.md) — Question protection and versioning
- [platform-technical-architecture.md](./platform-technical-architecture.md) — Infrastructure decisions
- [process-legal-requirements.md](./process-legal-requirements.md) — ToS, accessibility, i18n
- [process-success-metrics.md](./process-success-metrics.md) — KPIs and tracking

---

*"The harvest is plentiful, but the laborers are few."* — Matthew 9:37
