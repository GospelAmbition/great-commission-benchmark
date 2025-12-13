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

- [ ] Cover all use case categories (§3.1-3.6 from vision document)
- [ ] Test theological minimums and worldview adherence
- [ ] Produce reliable, reproducible results
- [ ] Generate meaningful differentiation between models
- [ ] Validate scoring methodology with human review

**Success Criteria:** The benchmark produces results we're confident publishing and defending publicly.

---

### Stage 2: Package for Volunteer Execution

**Goal:** Convert the benchmark into something volunteers can run independently.

Two packaging approaches:

#### Option A: Local Python Script

A self-contained Python package that registered testers run locally:

```
# Example usage
pip install great-commission-benchmark
gcb login                                    # Authenticate to receive questions
gcb run --model-url https://api.openrouter.ai/v1 --model gpt-4o
gcb export --format json > results.json
```

**Advantages:**
- No hosting costs for the project
- Volunteers can test private/local models
- Full control over API keys and costs
- Results submitted via templated export

**Requirements:**
- Authentication required to download question sets (see Question Security section)
- Clear documentation and setup instructions
- Standardized output format for result submission
- Validation checksums to ensure test integrity

#### Option B: Hosted Platform (Recommended)

A Railway-deployed application where registered testers:

1. Sign in via Auth0 (must be approved tester — see Question Security section)
2. Select an LLM to test (OpenRouter, custom endpoint, or API key)
3. Pay for the OpenRouter/API costs to run the test
4. Results are automatically submitted to the benchmark

**Advantages:**
- Lower barrier to entry for non-technical users
- Centralized quality control and verification
- Built-in sponsorship model ("pay it forward")
- Consistent test execution environment
- Questions never leave the server (stronger security)

**Revenue Model:**
- Users pay actual API costs + small platform fee
- Sponsors can fund tests of specific models
- Self-regulating and self-funding ecosystem

---

### Stage 3: Website and Leaderboard Platform

**Goal:** Build the public-facing website that displays results and engages the community.

#### Core Features

**Leaderboards:**
- Overall benchmark scores across all models tested
- Category-specific leaderboards (e.g., "Best for Evangelistic Content")
- Tier-specific rankings (Task Capability, Doctrinal Fidelity, Worldview Confession)
- Historical tracking to show model changes over time

**Drill-Down Exploration:**
- View results by use case category
- Explore specific theological issues or failure modes
- Compare selected models side-by-side
- See detailed response examples (with appropriate excerpts)

**Result Ingestion:**
- Automated pipeline from test execution to leaderboard
- Statistics mapped directly from pipeline output to display
- Moderation queue for submitted results before publication
- Verification step to ensure result integrity

#### Community Features

- **Newsletters:** Updates on new model tests, significant findings, methodology changes
- **Contribution System:** Ways for community members to:
  - Sponsor tests of specific models
  - Submit new test questions for review
  - Report issues or suggest improvements
- **Discussion/Feedback:** Mechanism for community input on results

---

## Technical Architecture

### Recommended Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **API Backend** | Python + FastAPI | Matches existing pipeline code; handles benchmark execution, heavy processing |
| **Frontend** | Nuxt (Vue.js) | SSR/SSG for SEO; file-based routing; can handle light API routes |
| **Hosting** | Railway | Simple deployment, good Python/Node support, cost-effective |
| **Authentication** | Auth0 | Industry-standard, handles OAuth/social login, free tier available |
| **Database** | PostgreSQL | Already in use for pipeline; robust and well-supported |
| **LLM Access** | OpenRouter | Single API for multiple models; pay-per-use pricing |

### Why Nuxt?

Nuxt extends Vue.js with features valuable for this project:

- **Server-Side Rendering (SSR):** Leaderboard pages are SEO-friendly and shareable
- **Static Generation (SSG):** Leaderboard snapshots can be pre-rendered for fast loading
- **File-Based Routing:** Simpler organization for category pages, model pages, etc.
- **API Routes:** Light backend tasks (auth callbacks, simple queries) without hitting FastAPI
- **Full-Stack Option:** Could potentially handle more of the stack as the project matures

### Backend Responsibilities Split

| Nuxt (Node.js) | FastAPI (Python) |
|----------------|------------------|
| Page rendering & routing | Benchmark execution |
| Auth0 integration | LLM API calls |
| Light data queries | Heavy computation |
| Static asset serving | Result processing |
| Newsletter signup | Database writes |
| Simple CRUD | Moderation workflows |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Public Website (Nuxt)                       │
│                    SSR / SSG / Vue.js SPA                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │Leaderboard│  │Model     │  │Category  │  │Community        ││
│  │Dashboard │  │Comparison│  │Deep-Dive │  │(Newsletter, etc)││
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            Nuxt Server Routes (light API tasks)             ││
│  │    Auth callbacks · Simple queries · Newsletter signup      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Heavy Lifting)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │Results   │  │Benchmark │  │Result    │  │Moderation        ││
│  │API       │  │Executor  │  │Processing│  │Workflows         ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘│
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

### Automated Submissions (Hosted Platform)

1. User initiates test run via web interface
2. Backend executes benchmark against selected model
3. Results stored with execution metadata (timestamps, model version, etc.)
4. Results enter moderation queue
5. Moderator reviews for anomalies or manipulation
6. Approved results published to leaderboard

### Manual Submissions (Local Script)

1. User runs local benchmark script
2. Script generates standardized JSON output with integrity hash
3. User submits results via web form or API
4. System validates hash and format
5. Results enter moderation queue
6. Moderator verifies plausibility (e.g., results consistent with known model behavior)
7. Approved results published to leaderboard

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

### Phase A: Foundation (Stage 1)
- [ ] Finalize benchmark question sets
- [ ] Complete testing on 3-5 initial models
- [ ] Validate results are publication-ready
- [ ] Document scoring methodology publicly

### Phase B: Local Package (Stage 2a)
- [ ] Refactor pipeline for standalone execution
- [ ] Create pip-installable package
- [ ] Write user documentation
- [ ] Define result submission format

### Phase C: Hosted Platform (Stage 2b)
- [ ] Set up Railway infrastructure
- [ ] Implement FastAPI backend
- [ ] Integrate Auth0 authentication
- [ ] Build test execution queue
- [ ] Implement OpenRouter billing integration

### Phase D: Public Website (Stage 3)
- [ ] Design and build Vue.js frontend
- [ ] Implement leaderboard views
- [ ] Build category/model exploration UI
- [ ] Create moderation dashboard
- [ ] Launch newsletter system
- [ ] Implement community contribution features

---

## Question Security & Tester Registration

### The Contamination Problem

If benchmark questions are publicly accessible, LLM providers could:
- Discover the questions through web scraping
- Fine-tune models specifically to perform well on these exact questions
- Game the benchmark without genuinely improving Great Commission support

This would undermine the benchmark's validity and usefulness.

### Solution: Controlled Distribution

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

### Tester Registration Process

1. **Application:** User registers interest on the website
2. **Information Collection:** We collect contact and identity information
3. **Agreement:** Tester agrees to terms:
   - Not to publish questions publicly (web, social media, forums)
   - Not to share questions with LLM providers
   - Not to use questions for model training
   - To report any suspected leaks
4. **Verification:** Manual review of application (prevent bot/spam registrations)
5. **Approval:** Tester granted access to question sets
6. **Distribution:** Questions delivered via authenticated download or secure API

### Enforcement Considerations

- **Watermarking:** Subtle variations in question sets per tester to trace leaks
- **Rotation:** Periodically refresh question sets to limit contamination impact
- **Monitoring:** Watch for questions appearing in training data or online
- **Revocation:** Ability to revoke access for terms violations

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

As the benchmark matures, direct API access or local model testing may be added for models not on OpenRouter.

---

## Pricing Model

A transparent, sustainable pricing approach:

### Cost Breakdown (shown to user)

| Line Item | Description |
|-----------|-------------|
| **API Costs** | Actual OpenRouter charges (shown transparently) |
| **Processing Fee** | Fixed fee to support the team and infrastructure |
| **Tip (optional)** | Opportunity to sponsor the project further |

### Example Checkout

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  API Cost (OpenRouter)         $12.40
  Processing Fee                 $2.50
  ─────────────────────────────────────
  Subtotal                      $14.90
  
  💡 Help with server & hosting costs (optional)
     ○ $5   ○ $10   ○ $20   ○ $100
  ─────────────────────────────────────
  Total                         $14.90
─────────────────────────────────────────
```

### Why This Model

- **Transparency:** Users see exactly what they're paying for
- **Sustainability:** Processing fee covers hosting, development, moderation
- **Community Support:** Optional contributions help with server and hosting costs
- **Low Barrier:** No subscriptions; pay only when you test
- **Sponsorship:** Larger contributions ($100+) can fund tests of specific models for the community

---

## Moderation Team

A **designated volunteer team** will moderate all submissions before they're published to the leaderboard.

### Moderation Responsibilities

- Review submitted test results for anomalies or manipulation
- Verify result integrity (spot-check responses, validate checksums)
- Approve or reject submissions based on quality standards
- Monitor for benchmark contamination (questions appearing in training data)
- Handle tester agreement violations

### Team Structure

- **Volunteer-based:** Community members committed to maintaining benchmark quality
- **Designated roles:** Clear assignment of moderation duties
- **Training:** Guidelines and processes for consistent moderation decisions
- **Escalation path:** Process for handling edge cases or disputes

---

## Model Retesting & Updates

### Retesting Strategy

**Commercial Models:**
- Manual retests triggered every couple of months as models are updated
- Also available as a **paid option** for users who want updated evaluations
- Users can select "Retest Model" from the website's testing interface
- Same pricing structure: API costs + processing fee + optional contribution

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

### Why Retests Matter

- Models are frequently updated (GPT-4 → GPT-4 Turbo → GPT-4o)
- Guardrails and capabilities change over time
- Users need current information to make decisions
- Historical tracking shows model evolution

---

## Data Retention Policy

### Indefinite Retention

We will **retain all response data and collection data indefinitely** for the following reasons:

**No Privacy Concerns:**
- No personally identifiable information (PII) is collected in the testing process
- Responses are from LLMs, not human users
- Test metadata (model, timestamp, verdicts) contains no sensitive data

**Benefits of Long-Term Retention:**

1. **Historical Log:** Complete record of how models performed over time
   - Track model evolution and improvements
   - Identify when guardrails changed
   - Document benchmark methodology changes

2. **Verification & Defense:** Others can evaluate and defend benchmark results
   - Researchers can audit our methodology
   - Model providers can review their evaluations
   - Community can verify claims about model performance

3. **Retesting Capability:** Historical data enables:
   - Comparing new results against past results
   - Identifying anomalies or inconsistencies
   - Re-evaluating past results with updated criteria

4. **Research Value:** Long-term dataset supports:
   - Academic research on LLM behavior
   - Analysis of guardrail changes over time
   - Understanding model drift and updates

### Data Access

- **Public:** Aggregate statistics and leaderboard results
- **Researchers:** Request access to anonymized datasets for analysis
- **Model Providers:** Access to their own model's detailed results
- **Moderators:** Full access for verification purposes

---

## Benchmark Versioning

### Version-Based Testing

The benchmark will use **versioning** to manage question set updates and improvements over time.

**Version 1:**
- Initial question set and methodology
- First published leaderboard
- Foundation for all future versions

**Version 2+ (Future):**
- Created by a team of volunteers and leaders
- Re-examination and refinement of the question set
- New results and separate leaderboard
- May include new questions, updated evaluation criteria, or methodology improvements

### Why Versioning Matters

- **Preserves Comparability:** Version 1 results remain valid and comparable
- **Enables Evolution:** Question sets can improve without invalidating past work
- **Clear Communication:** Users know which version they're viewing
- **Historical Context:** Shows how the benchmark methodology has evolved

### Website Requirements

The platform must support versioning from the start:

- **Version Selection:** Users can view leaderboards by version
- **Version Comparison:** Side-by-side comparison of results across versions
- **Clear Labeling:** All results and leaderboards clearly marked with version number
- **Version Documentation:** Each version has documentation explaining:
  - What changed from previous version
  - Why changes were made
  - How to interpret results

### Version Creation Process

1. **Volunteer Team Formation:** Leaders and volunteers assemble to review current version
2. **Question Set Re-examination:** Team evaluates existing questions for:
   - Relevance and accuracy
   - Coverage gaps
   - Evaluation criteria effectiveness
3. **Proposed Changes:** Team proposes new questions, modifications, or methodology updates
4. **Review & Approval:** Changes reviewed and approved by broader community/leadership
5. **Version Publication:** New version released with:
   - Updated question set
   - New leaderboard (previous version remains accessible)
   - Documentation of changes

### Technical Implementation

The database and pipeline must be designed with versioning in mind:

- **Question Versioning:** Questions linked to version numbers
- **Result Versioning:** All test results tagged with benchmark version
- **Leaderboard Versioning:** Separate leaderboards per version
- **Migration Path:** Ability to re-run old tests on new versions for comparison

---

## Remaining Considerations

The deployment vision is largely complete. Future refinements may include:
- Specific versioning cadence (annual? as-needed?)
- Process for volunteer team selection
- Community input mechanisms for version proposals

---

## Success Vision

A successful deployment means:

- **Christian organizations** can quickly identify which LLMs best support their work
- **Volunteers** can easily contribute by testing models they care about
- **The community** sustains itself through sponsorship and contributions
- **Model developers** have clear feedback on how to better serve this user segment
- **The broader conversation** about religious freedom in AI advances with evidence

The Great Commission Benchmark becomes the authoritative resource for understanding LLM support for Great Commission activities—publicly accessible, community-driven, and continuously updated.

---

*"The harvest is plentiful, but the laborers are few."* — Matthew 9:37
