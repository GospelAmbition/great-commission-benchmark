# Great Commission Benchmark — Gaps, Decisions & Tasks

This document provides a comprehensive review of the CLI applications, platform, and process documentation. It identifies gaps, undecided items, and things that need to be extrapolated or built.

**Generated:** December 16, 2025

**Note:** Finalized decisions are permanently documented in [`../documents/Technical-Decisions.md`](../documents/Technical-Decisions.md) for long-term reference.

---

## How to Use This Document

- [ ] Items are checkboxes you can mark as complete
- **[DECISION]** = Requires a decision to be made
- **[SPEC]** = Requires specification/documentation  
- **[BUILD]** = Requires implementation/building
- **[WRITE]** = Requires content creation (prompts, questions, legal docs)

---

## 1. CLI Builder (gcb-builder)

### 1.1 Foundation & Setup

- [ ] **[BUILD]** Create project structure (`pyproject.toml`, directory layout)
- [ ] **[BUILD]** Define all 19 categories from benchmark-vision.md as code constants
- [ ] **[BUILD]** Implement SQLAlchemy database models (Question, BenchmarkVersion, VersionQuestion, JudgeTestCase)
- [ ] **[BUILD]** Create database migrations strategy with Alembic
- [ ] **[BUILD]** Build CLI entry point with rich menus and navigation

### 1.2 Question Generation System

- [ ] **[WRITE]** Create generation prompt template for Category 3.1 (Missiological Research)
- [ ] **[WRITE]** Create generation prompt template for Category 3.2 (Evangelistic Material Creation)
- [ ] **[WRITE]** Create generation prompt template for Category 3.3 (Apologetic Purposes)
- [ ] **[WRITE]** Create generation prompt template for Category 3.4 (Conversational AI Tools)
- [ ] **[WRITE]** Create generation prompt template for Category 3.5 (Intercessory Prayer Purposes)
- [ ] **[WRITE]** Create generation prompt template for Category 3.6a (Scripture Processing - Vocabulary)
- [ ] **[WRITE]** Create generation prompt template for Category 3.6b (Scripture Processing - Passages)
- [ ] **[WRITE]** Create generation prompt templates for Tier 2 doctrines (4.1-4.6)
- [ ] **[WRITE]** Create generation prompt templates for Tier 3 worldview affirmations (5.1-5.6)
- [ ] **[BUILD]** Implement LLM-based question generator
- [x] **[DECISION]** Define minimum question count per category for V1: **Full expected build (210 Tier 1, 60 Tier 2, 30 Tier 3) — no subset for V1**

### 1.3 LLM Backend Adapters

- [ ] **[BUILD]** Implement OpenRouter backend adapter
- [ ] **[BUILD]** Implement LM Studio backend adapter
- [ ] **[BUILD]** Implement Ollama backend adapter
- [ ] **[BUILD]** Implement direct API backends (OpenAI, Anthropic)
- [x] **[DECISION]** Determine default/recommended models for question generation: **OpenRouter: GPT 5.2, Gemini 3, Claude Opus**

### 1.4 Judge Prompt Development

- [ ] **[WRITE]** Finalize Tier 1 Task Judge prompt (draft exists in specs)
- [ ] **[WRITE]** Finalize Tier 2 Doctrine Judge prompt (draft exists in specs)
- [ ] **[WRITE]** Finalize Tier 3 Worldview Judge prompt (draft exists in specs)
- [ ] **[BUILD]** Implement judge prompt testing framework
- [ ] **[BUILD]** Create judge test case management system
- [ ] **[SPEC]** Define inter-rater reliability measurement methodology
- [x] **[DECISION]** Minimum accuracy threshold for judge prompts before locking: **≥90%**

### 1.5 Curation Workflow

- [ ] **[BUILD]** Build question review/approval workflow
- [ ] **[BUILD]** Implement question locking mechanism
- [ ] **[BUILD]** Build Datasette integration for database exploration
- [ ] **[BUILD]** Create bulk operations (delete drafts, regenerate category)
- [ ] **[SPEC]** Define curation guidelines for reviewers

### 1.6 Version Building & Publishing

- [ ] **[BUILD]** Implement version creation and assembly
- [ ] **[BUILD]** Build pre-publish validation (category coverage, tier distribution, etc.)
- [ ] **[BUILD]** Implement version locking mechanism
- [ ] **[BUILD]** Create JSON export for platform publication
- [ ] **[BUILD]** Build bundle compiler for CLI distribution (compress + base64 encode)
- [ ] **[SPEC]** Document version release workflow

---

## 2. CLI Runner (gcb-runner)

### 2.1 Foundation & Setup

- [ ] **[BUILD]** Create project structure (`pyproject.toml`, directory layout)
- [ ] **[BUILD]** Build CLI skeleton with typer
- [ ] **[BUILD]** Implement configuration storage (`~/.gcb-runner/config.json`)
- [ ] **[BUILD]** Create user-friendly config wizard

### 2.2 Benchmark Version System

- [ ] **[BUILD]** Implement version loader for embedded bundles
- [ ] **[BUILD]** Create `versions/` directory structure
- [ ] **[BUILD]** Build bundle decoding logic (base64 + zlib decompress)
- [ ] **[BUILD]** Implement checksum verification
- [ ] **[BUILD]** Create `gcb-runner versions` command
- [x] **[DECISION]** How to communicate CLI updates when new benchmark versions release: **See decision below**

### 2.3 Test Runner

- [ ] **[BUILD]** Implement core test execution logic
- [ ] **[BUILD]** Build LLM backend abstraction (same as builder)
- [ ] **[BUILD]** Implement progress tracking with rich
- [ ] **[BUILD]** Create resume functionality for interrupted runs
- [ ] **[BUILD]** Handle rate limiting and retry logic

### 2.4 LLM Judge Integration

- [ ] **[BUILD]** Implement judge prompt loading from bundles
- [ ] **[BUILD]** Build verdict parsing logic
- [ ] **[BUILD]** Handle refusal type classification
- [x] **[DECISION]** Default judge model: **OpenAI gpt-oss-20b** (available on both LM Studio and OpenRouter)

### 2.5 Results Storage & Display

- [ ] **[BUILD]** Implement SQLite results database
- [ ] **[BUILD]** Build `gcb-runner results` command
- [ ] **[BUILD]** Create filtering/sorting for results display

### 2.6 Results Viewer (Web Dashboard)

- [ ] **[BUILD]** Implement HTTP server using Python stdlib
- [ ] **[BUILD]** Create embedded HTML/JS dashboard
- [ ] **[BUILD]** Build API endpoints for results data
- [ ] **[BUILD]** Implement Chart.js visualizations
- [ ] **[BUILD]** Create run comparison view
- [ ] **[BUILD]** Build failure analysis view
- [ ] **[SPEC]** Design dashboard wireframes/mockups

### 2.7 Static Report Generator

- [ ] **[BUILD]** Implement `gcb-runner report` command
- [ ] **[BUILD]** Create self-contained HTML report template
- [ ] **[BUILD]** Build comparison report for two runs

### 2.8 Export & Upload

- [ ] **[BUILD]** Implement JSON export format
- [ ] **[BUILD]** Create platform upload functionality
- [ ] **[BUILD]** Build account linking flow
- [ ] **[SPEC]** Define export format schema validation

### 2.9 Local Model Support

- [ ] **[BUILD]** Implement LM Studio backend
- [ ] **[BUILD]** Implement Ollama backend
- [ ] **[SPEC]** Document local model setup instructions
- [x] **[DECISION]** Minimum hardware requirements for local testing: **See decision below**

---

## 3. Platform (Web Application)

### 3.1 Backend (FastAPI)

- [ ] **[BUILD]** Set up FastAPI project structure
- [ ] **[BUILD]** Implement PostgreSQL database connection
- [ ] **[BUILD]** Create database schema (Users, TestRuns, Results, etc.)
- [ ] **[BUILD]** Implement Auth0 integration
- [ ] **[BUILD]** Build results API endpoints
- [ ] **[BUILD]** Implement benchmark executor service
- [ ] **[BUILD]** Create OpenRouter integration
- [ ] **[BUILD]** Build Stripe payment integration
- [ ] **[BUILD]** Implement moderation workflow endpoints
- [ ] **[BUILD]** Create user notification system
- [ ] **[SPEC]** Document API endpoints (OpenAPI spec)

### 3.2 Frontend (Next.js)

- [ ] **[BUILD]** Set up Next.js project with Tailwind CSS + shadcn/ui
- [ ] **[BUILD]** Create landing page
- [ ] **[BUILD]** Build leaderboard view with Chart.js visualizations (bar charts, heatmaps, verdict distribution) - visual-first design with collapsible table
- [ ] **[BUILD]** Implement model detail pages
- [ ] **[BUILD]** Create category deep-dive pages
- [ ] **[BUILD]** Build model comparison view
- [ ] **[BUILD]** Implement test execution flow (select → pay → run → results)
- [ ] **[BUILD]** Create user dashboard
- [ ] **[BUILD]** Build moderator review interface
- [ ] **[BUILD]** Implement admin pages
- [ ] **[BUILD]** Create methodology/documentation pages
- [ ] **[SPEC]** Design UI wireframes/mockups
- [x] **[DECISION]** UI design system/component library choice: **shadcn/ui** (See Technical-Decisions.md)

### 3.3 Infrastructure

- [ ] **[BUILD]** Set up Railway project
- [ ] **[BUILD]** Configure PostgreSQL database
- [ ] **[BUILD]** Set up CI/CD deployment pipeline
- [ ] **[BUILD]** Configure environment variables
- [ ] **[BUILD]** Set up backup strategy (Railway + local machine download)
- [x] **[DECISION]** Secondary backup location: **In the beginning, we will simply download a copy to a local machine for offline storage**

### 3.4 Third-Party Integrations

- [ ] **[BUILD]** Configure Auth0 application
- [ ] **[BUILD]** Set up Stripe account and webhooks
- [ ] **[BUILD]** Configure OpenRouter API access
- [ ] **[BUILD]** Set up email service for notifications (SendGrid)
- [ ] **[BUILD]** Configure Umami analytics (off-site server - URL and integration info to be provided at deployment)
- [x] **[DECISION]** Select email service provider: **SendGrid**
- [x] **[DECISION]** Analytics choice: **Umami** (on off-site server; URL and integration information will be provided when ready for deployment)

### 3.5 Security

- [ ] **[BUILD]** Implement rate limiting
- [ ] **[BUILD]** Set up HTTPS/SSL
- [ ] **[BUILD]** Implement audit logging for question access
- [ ] **[BUILD]** Configure API authentication
- [ ] **[SPEC]** Document security practices

---

## 4. Process & Operations

### 4.1 Legal Documents

- [x] **[WRITE]** Draft Terms of Service
- [x] **[WRITE]** Draft Privacy Policy
- [x] **[WRITE]** Draft Liability Disclaimers
- [x] **[WRITE]** Draft Tester Agreement (confidentiality terms)
- [x] **[DECISION]** Governing law/jurisdiction for disputes
- [x] **[DECISION]** Whether to get legal review before launch

### 4.2 Accessibility

- [ ] **[BUILD]** Implement WCAG Level A compliance
- [ ] **[BUILD]** Add alt text to all images
- [ ] **[BUILD]** Ensure keyboard navigation
- [ ] **[BUILD]** Add skip links
- [ ] **[BUILD]** Ensure proper form labels
- [ ] **[BUILD]** Test with automated tools (WAVE, Lighthouse)
- [ ] **[BUILD]** Basic screen reader testing

### 4.3 Organization & Governance

- [x] **[DECISION]** Select stewarding ministry for finances (candidates: Visual Story Network, Digital Disciple Makers Network, Gospel Ambition)
- [x] **[DECISION]** Form founding committee
- [x] **[DECISION]** Designate committee chair
- [x] **[DECISION]** Initial moderator selection
- [ ] **[SPEC]** Document moderator onboarding process
- [x] **[SPEC]** Define committee meeting cadence

### 4.4 Moderation Setup

- [ ] **[BUILD]** Create simple moderation list view (shows results needing review)
- [ ] **[BUILD]** Implement basic spot-check interface (review 20 verdicts, mark agree/disagree/unsure)
- [ ] **[BUILD]** Store moderation results in database (basic records, no complex logging)
- [ ] **[WRITE]** Create short moderator guide (1-2 pages, references process-moderation-process.md)

### 4.5 Financial Setup

- [ ] **[BUILD]** Configure Stripe account
- [ ] **[BUILD]** Implement payment flow
- [ ] **[BUILD]** Build refund processing
- [ ] **[BUILD]** Create sponsorship request form
- [ ] **[BUILD]** Set up financial reporting dashboard
- [x] **[DECISION]** Confirm $20 benchmark hosting contribution amount: **$20 will be the beginning cost for the hosting contribution. This amount may adjust later based on operational needs, but $20 is confirmed as the starting cost.**
- [x] **[DECISION]** Define refund approval process

### 4.6 Communications

- [ ] **[BUILD]** Set up newsletter system
- [ ] **[BUILD]** Create email notification templates
- [ ] **[BUILD]** Set up external discussion platform (Discord)
- [x] **[DECISION]** Select newsletter service: **Brevo** (Note: Implementation should be modular to allow switching services based on moderation/maintenance team's final decision)
- [x] **[DECISION]** Discussion platform: **Discord**
- [ ] **[WRITE]** Draft launch announcement
- [ ] **[WRITE]** Create FAQ content

---

## 5. Benchmark Content

### 5.1 Question Creation

- [ ] **[WRITE]** Generate initial question set for Tier 1 categories (~210 questions)
- [ ] **[WRITE]** Generate initial question set for Tier 2 doctrines (~60 questions)
- [ ] **[WRITE]** Generate initial question set for Tier 3 worldview (~30 questions)
- [ ] **[WRITE]** Assign expected verdicts to all questions
- [ ] **[WRITE]** Assign expected refusal types where applicable
- [ ] **[WRITE]** Add capability/willingness flags to all questions
- [ ] **[WRITE]** Add use_case_tags to all questions
- [ ] **[WRITE]** Add audience_context metadata where applicable
- [ ] **[WRITE]** Add ministry_type metadata where applicable

### 5.2 Calibration Set

- [ ] **[WRITE]** Create calibration set (minimum 50 questions per specs)
- [ ] **[BUILD]** Get 3+ human reviewers to agree on verdicts for calibration set
- [ ] **[SPEC]** Document calibration set creation process
- [x] **[DECISION]** Who are the initial human reviewers for calibration? **Chris Wynn will be the initial reviewer for the calibration.**

### 5.3 Multi-Turn Testing (Phase 5 in methodology)

- [ ] **[WRITE]** Design 5-10 multi-turn conversation scripts
- [ ] **[SPEC]** Define misalignment markers
- [ ] **[SPEC]** Define "turn-to-break" measurement methodology
- [x] **[DECISION]** Multi-turn testing: **Included in V1** (essential for chatbot and AI counseling categories)

### 5.4 Sample Questions

- [ ] **[WRITE]** Select sample questions to publish publicly (for transparency)
- [x] **[DECISION]** How many sample questions to publish (small subset): **Do not publish exact questions. Publish similar questions (20 or under) to give a sample of the different kinds of questions.**
- [x] **[DECISION]** Which categories to include in samples: **Mostly task questions, with one or two worldview and theological questions.**

---

## 6. Integration & End-to-End

### 6.1 CLI Builder → Platform

- [ ] **[SPEC]** Document how builder exports get to platform
- [ ] **[BUILD]** Create upload mechanism for JSON exports
- [x] **[DECISION]** Manual upload vs. automated pipeline: **Manual upload workflow selected**

**Decision Analysis:**

**Manual Upload (Preferred Approach):**
- CLI Builder generates JSON file (e.g., `gcb-v1.0.0.json`)
- User manually uploads via web form or API endpoint
- Platform verifies checksum, format, and content before accepting

**Pros:**
- ✅ **Human verification step** - Builder can review JSON before upload (catch errors early)
- ✅ **Security control** - No automated credentials needed; reduces attack surface
- ✅ **Audit trail** - Clear record of who uploaded what and when
- ✅ **Simple implementation** - Just need upload form/endpoint with validation
- ✅ **Flexibility** - Builder can review, edit, or regenerate before upload
- ✅ **No infrastructure dependencies** - No CI/CD, webhooks, or API keys to manage
- ✅ **Version control friendly** - JSON files can be committed to git for history
- ✅ **Offline workflow** - Builder can work completely offline, upload later

**Cons:**
- ❌ **Extra step** - Requires manual action (but this is intentional for verification)
- ❌ **Potential for delay** - Human step means not instant (but acceptable for version releases)
- ❌ **Possible human error** - Could upload wrong file (mitigated by checksum verification)

**Automated Pipeline Approach:**
- CLI Builder publishes to git repo or triggers webhook
- CI/CD pipeline or webhook handler automatically uploads to platform
- Platform validates and processes automatically

**Pros:**
- ✅ **Instant deployment** - No manual step, immediate availability
- ✅ **Consistency** - Eliminates possibility of forgetting to upload
- ✅ **Integration** - Fits into modern DevOps workflows

**Cons:**
- ❌ **Complexity** - Requires CI/CD setup, webhook infrastructure, API authentication
- ❌ **Security concerns** - Need secure API keys, webhook secrets, access controls
- ❌ **Less control** - No human review step before platform receives data
- ❌ **Infrastructure overhead** - Additional services to maintain (GitHub Actions, webhook handlers, etc.)
- ❌ **Debugging difficulty** - Automated failures harder to diagnose
- ❌ **Overkill for use case** - Version releases are infrequent (not daily deployments)
- ❌ **Dependency risk** - Platform must be available when pipeline runs

**✅ DECISION: Manual Upload Workflow**

**Rationale:**
1. Version releases are infrequent (not daily)
2. Human verification is valuable for quality control
3. Simplicity reduces security and maintenance burden
4. The workflow already includes a manual review step (publishing locks the version)

**Implementation Plan:**
- CLI Builder generates JSON with checksum
- Web form or authenticated API endpoint accepts upload
- Platform validates: checksum match, format version, required fields
- Moderator/admin reviews before making version live (if needed)

### 6.2 CLI Builder → CLI Runner

- [ ] **[SPEC]** Document bundle compilation and distribution process
- [ ] **[BUILD]** Create workflow for adding new versions to gcb-runner
- [ ] **[SPEC]** Document CLI release process (version bump, PyPI publish)

### 6.3 Platform → CLI Runner

- [ ] **[SPEC]** Document how CLI users know about new versions
- [ ] **[DECISION]** Whether CLI should check for updates automatically

### 6.4 Cross-System Consistency

- [ ] **[SPEC]** Ensure export format matches between builder and platform
- [ ] **[SPEC]** Ensure bundle format matches between builder and runner
- [ ] **[SPEC]** Ensure scoring formulas match across all systems

---

## 7. Documentation & Specifications

### 7.1 Missing Feature Specifications

- [x] **[SPEC]** Write `feature-leaderboard.md` (display, filtering, comparison)
- [x] **[SPEC]** Write `feature-user-dashboard.md` (test history, status)
- [x] **[SPEC]** Write `feature-moderator-dashboard.md` (review tools, queue)
- [x] **[SPEC]** Write `feature-user-notifications.md` (email, in-app)
- [x] **[SPEC]** Write `feature-model-comparison.md` (side-by-side view)
- [x] **[SPEC]** Write `feature-retesting.md` (model retest flow)

### 7.2 API Documentation

- [ ] **[SPEC]** Document public API endpoints
- [ ] **[SPEC]** Document internal API endpoints
- [ ] **[SPEC]** Create OpenAPI/Swagger specification

### 7.3 User Documentation

- [ ] **[WRITE]** CLI Runner README
- [ ] **[WRITE]** CLI Builder README
- [ ] **[WRITE]** Platform user guide
- [ ] **[WRITE]** Tester quick-start guide
- [ ] **[WRITE]** Moderator guide
- [ ] **[WRITE]** Version builder guide

### 7.4 Developer Documentation

- [ ] **[SPEC]** Document local development setup
- [ ] **[SPEC]** Document contribution guidelines
- [ ] **[SPEC]** Document testing strategies
- [ ] **[SPEC]** Document deployment procedures

---

## 8. Testing & Validation

### 8.1 Pre-Launch Validation

- [ ] **[BUILD]** Run Phase 1 validation (calibrate judge prompt with 2-3 models)
- [ ] **[BUILD]** Run full benchmark on 3-5 initial models
- [ ] **[BUILD]** Verify weighted scoring produces meaningful differentiation
- [ ] **[BUILD]** Validate human review process works
- [ ] **[BUILD]** Test payment flow end-to-end
- [ ] **[BUILD]** Test refund process
- [ ] **[BUILD]** Test user registration and authentication

### 8.2 Automated Testing

- [ ] **[BUILD]** Write unit tests for CLI Builder
- [ ] **[BUILD]** Write unit tests for CLI Runner
- [ ] **[BUILD]** Write integration tests for platform
- [ ] **[BUILD]** Set up CI testing pipeline

---

## 9. Launch Preparation

### 9.1 Pre-Launch Checklist

- [ ] All legal documents completed and reviewed
- [ ] WCAG Level A compliance verified
- [ ] Initial question set created and validated
- [ ] Platform deployed and tested
- [ ] Payment processing tested
- [ ] Initial 3-5 models on leaderboard
- [ ] Moderators trained and ready
- [ ] Email notifications working
- [ ] Analytics configured
- [ ] Backup strategy implemented

### 9.2 Launch Activities

- [ ] **[WRITE]** Prepare launch announcement
- [ ] **[DECISION]** Define launch communication channels
- [ ] **[DECISION]** Identify launch partners/early adopters
- [ ] **[BUILD]** Set up monitoring and alerting
- [ ] **[DECISION]** Define launch date criteria (when we're "ready")

---

## 10. Post-Launch & Ongoing

### 10.1 Monitoring & Maintenance

- [ ] **[SPEC]** Define monitoring checklist
- [ ] **[SPEC]** Define incident response procedures
- [ ] **[DECISION]** On-call/support rotation

### 10.2 Version 2 Planning

- [ ] **[DECISION]** Triggers for V2 question set (timeline: ~yearly)
- [ ] **[SPEC]** Document question set refresh process
- [ ] **[DECISION]** Community question contribution process

### 10.3 Future Considerations

- [x] **[DECISION]** Multilingual support priority and timeline: **Built and expected to quickly follow the MVP in English**
- [x] **[DECISION]** Additional language support (Spanish, Portuguese, etc.): **Spanish, Portuguese, and Korean will be the first languages to auto-translate**
- [x] **[DECISION]** WCAG Level AA upgrade timeline: **No expectation for Level AA upgrade. It will be next year or the year after.**
- [x] **[DECISION]** Volume discount pricing thresholds: **No volume discounting price thresholds. Simple app and math of the pricing.**

---

## Summary Statistics

| Category | Total Items | Decisions | Specs | Build | Write |
|----------|-------------|-----------|-------|-------|-------|
| CLI Builder | 31 | 3 | 2 | 23 | 13 |
| CLI Runner | 30 | 4 | 4 | 23 | 0 |
| Platform | 38 | 4 | 3 | 31 | 0 |
| Process | 33 | 5 | 4 | 15 | 7 |
| Benchmark Content | 16 | 3 | 2 | 2 | 10 |
| Integration | 9 | 3 | 6 | 2 | 0 |
| Documentation | 16 | 0 | 13 | 0 | 6 |
| Testing | 10 | 0 | 0 | 10 | 0 |
| Launch | 11 | 4 | 0 | 2 | 2 |
| Post-Launch | 7 | 6 | 2 | 0 | 0 |
| **TOTAL** | **~200** | **~33** | **~36** | **~108** | **~38** |

---

## Priority Recommendations

### Highest Priority (Do First)

1. **Governance Decisions** — Select stewarding ministry, form committee, designate chair
2. **Question Creation** — Can't launch without questions
3. **Judge Prompt Finalization** — Core to benchmark validity
4. **Legal Documents** — Required for launch

### High Priority (Critical Path)

1. CLI Builder foundation (enables question creation)
2. Calibration set creation
3. Platform backend (results API, execution)
4. Payment integration
5. Multi-turn testing framework (included in V1)

### Medium Priority (Important but Parallel)

1. CLI Runner implementation
2. Platform frontend
3. Moderator setup
4. User documentation

### Lower Priority (Can Follow Launch)

1. Multilingual support
2. Advanced analytics
3. Feature enhancements

---

## Judge Model Recommendation

**Decision:** Default judge model is **OpenAI gpt-oss-20b**

### Comparison: GPT-OSS-20B vs Qwen3 Coder 30B

| Capability | GPT-OSS-20B | Qwen3 Coder 30B | Winner |
|------------|-------------|-----------------|--------|
| **Reasoning** | 89.8% | 78% | ✅ GPT-OSS-20B |
| **Instruction Following** | 66% | 51.5% | ✅ GPT-OSS-20B |
| **General Knowledge** | 99% | 32.2% | ✅ GPT-OSS-20B |
| **Ethics Understanding** | 99% | Not specified | ✅ GPT-OSS-20B |
| **Coding** | 92% | 89% | ✅ GPT-OSS-20B |
| **Mathematics** | 66.7% | 89% | ✅ Qwen3 (not relevant for judging) |
| **Efficiency** | MoE architecture (faster) | Dense model | ✅ GPT-OSS-20B |
| **Availability** | Both LM Studio & OpenRouter | Both LM Studio & OpenRouter | ✅ Tie |

### Rationale

**GPT-OSS-20B is the clear choice for judging because:**

1. **Superior Reasoning (89.8% vs 78%)** — Critical for evaluating whether responses meet criteria
2. **Better Instruction Following (66% vs 51.5%)** — Essential for following judge prompts correctly
3. **Strong General Knowledge (99% vs 32.2%)** — Needed to understand context and theological content
4. **High Ethics Understanding (99%)** — Important for evaluating religious content appropriately
5. **More Efficient** — MoE architecture means faster inference and lower resource usage
6. **Consistent Availability** — Available on both LM Studio (local) and OpenRouter (cloud)

**Qwen3 Coder 30B's only advantage is mathematics (89% vs 66.7%), which is not relevant for evaluating Great Commission benchmark responses.**

### Implementation Notes

- Model ID on OpenRouter: `openai/gpt-oss-20b`
- Model ID on LM Studio: Same model name (verify exact identifier)
- Cost: Very low (~$0.17 per test run based on infrastructure costs doc)
- Hardware: Runs efficiently on 16GB+ systems (suitable for local use)

---

## Minimum Hardware Requirements for Local Testing

**Decision:** Minimum hardware requirements for local testing are defined below.

### Recommended Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 16 GB | 32 GB | Required for running judge model (gpt-oss-20b) + test model simultaneously |
| **Storage** | 50 GB free | 100 GB free | For models, results database, and question bundles |
| **CPU** | 4 cores | 8+ cores | Multi-core helps with parallel inference and database operations |
| **GPU** | Optional | NVIDIA GPU (8GB+ VRAM) | Significantly speeds up inference; CPU-only is viable but slower |
| **Python** | 3.9+ | 3.11+ | Required for CLI runner |
| **Internet** | 5 Mbps | 25+ Mbps | For initial model downloads and updates; offline operation possible after setup |

### Detailed Breakdown

#### 1. Python Runtime Requirements

**Minimum:**
- **Python 3.9+** (required for modern type hints and features)
- **SQLite 3.8+** (included with Python standard library)
- **Package dependencies:** ~50-100 MB (typer, rich, requests, sqlalchemy, etc.)

**Storage:** ~200 MB for Python installation + dependencies

#### 2. SQLite Database Storage

**Per test run:**
- **Question data:** ~500 KB (300 questions with metadata)
- **Results storage:** ~5-10 MB per test run (includes full responses, verdicts, metadata)
- **Database overhead:** ~1-2 MB per database file

**Total:** ~10-15 MB per test run. With 10 test runs stored locally: ~100-150 MB

#### 3. Local Model Storage

**Judge Model (gpt-oss-20b):**
- **Model size:** ~40 GB (quantized) to ~80 GB (full precision)
- **Recommended:** Use quantized version (Q4_K_M or Q5_K_M) for ~40-50 GB
- **Required:** Must be loaded into RAM during inference

**Test Models (varies by model):**
- **Small models (7B-13B):** 4-8 GB (quantized)
- **Medium models (20B-30B):** 12-20 GB (quantized)
- **Large models (70B+):** 40-80 GB (quantized)

**Storage recommendation:** Reserve 100+ GB for model storage to accommodate multiple models and judge model.

#### 4. Memory (RAM) Requirements

**Critical constraint:** Both the test model and judge model must run simultaneously.

**Minimum (16 GB RAM):**
- **Judge model (gpt-oss-20b):** ~12-14 GB (quantized, loaded in RAM)
- **Test model (small, 7B-13B):** ~4-6 GB (quantized)
- **System overhead:** ~2 GB
- **Total:** ~18-22 GB (may require swap/offloading)

**Recommended (32 GB RAM):**
- **Judge model:** ~12-14 GB
- **Test model (medium, 20B-30B):** ~12-18 GB
- **System overhead:** ~4 GB
- **Buffer:** ~2-4 GB for smooth operation
- **Total:** ~30-36 GB (comfortable margin)

**With GPU (8GB+ VRAM):**
- Models can run on GPU, reducing RAM requirements
- **RAM:** 16 GB sufficient if models run on GPU
- **VRAM:** 8 GB minimum for single model, 16 GB+ for running both models simultaneously

#### 5. Internet Connection Requirements

**Initial Setup:**
- **Model downloads:** 40-80 GB per model (one-time)
- **Speed:** 5 Mbps minimum (downloads will take hours), 25+ Mbps recommended
- **Time estimate:** 
  - At 5 Mbps: ~18-36 hours per model
  - At 25 Mbps: ~3.5-7 hours per model

**Ongoing Usage:**
- **CLI updates:** ~10-50 MB per update (infrequent)
- **Benchmark version updates:** ~1-5 MB per version (infrequent)
- **Results upload (optional):** ~1-5 MB per test run
- **Minimal bandwidth:** 1 Mbps sufficient for updates and uploads

**Offline Operation:**
- Once models are downloaded, **fully offline operation is possible**
- No internet required for:
  - Running tests
  - Viewing results locally
  - Generating reports
- Internet only needed for:
  - Initial model downloads
  - CLI/benchmark updates
  - Uploading results to platform (optional)

#### 6. CPU Requirements

**Minimum (4 cores):**
- Sufficient for basic inference
- May experience slowdowns with larger models
- Single-threaded performance matters for some operations

**Recommended (8+ cores):**
- Better parallelization for inference
- Faster database operations
- More responsive during concurrent operations

**Note:** GPU acceleration (if available) significantly reduces CPU load.

### Use Case Scenarios

#### Scenario 1: Budget Setup (Minimum Requirements)
- **Hardware:** 16 GB RAM, 50 GB storage, 4-core CPU, no GPU
- **Models:** Small test models (7B-13B) + quantized judge model
- **Performance:** Slow but functional (~2-4 hours per test run)
- **Cost:** ~$500-800 (refurbished workstation or entry-level laptop)

#### Scenario 2: Recommended Setup
- **Hardware:** 32 GB RAM, 100 GB storage, 8-core CPU, optional GPU
- **Models:** Medium test models (20B-30B) + quantized judge model
- **Performance:** Moderate speed (~1-2 hours per test run)
- **Cost:** ~$1,000-1,500 (mid-range workstation or gaming laptop)

#### Scenario 3: Optimal Setup
- **Hardware:** 64 GB RAM, 200+ GB storage, 12+ core CPU, NVIDIA GPU (16GB+ VRAM)
- **Models:** Large test models (70B+) + full precision judge model
- **Performance:** Fast (~30-60 minutes per test run)
- **Cost:** ~$2,500-4,000 (high-end workstation or gaming PC)

### Software Package Requirements

**Python Packages (Minimum):**
- Python 3.9+ (stdlib includes SQLite)
- `typer` - CLI framework
- `rich` - Terminal UI
- `requests` - HTTP client
- `sqlalchemy>=2.0` - Database ORM
- `pydantic` - Data validation

**Total package size:** ~50-100 MB

**Local Model Runtime:**
- **LM Studio** or **Ollama** (separate installation, ~500 MB - 2 GB)
- Model files stored separately (40-80 GB per model)

### Storage Breakdown Example

For a typical local testing setup:

| Item | Size | Notes |
|------|------|-------|
| Python + packages | 200 MB | Runtime environment |
| CLI runner | 10 MB | Application code |
| Question bundles | 5 MB | Embedded benchmark versions |
| Judge model (quantized) | 40 GB | gpt-oss-20b Q4_K_M |
| Test model (small, quantized) | 8 GB | Example: Llama 3.2 13B |
| Test model (medium, quantized) | 20 GB | Example: Mistral Small 24B |
| Results database (10 runs) | 150 MB | Local test history |
| **Total** | **~68 GB** | Minimum viable setup |

**Recommendation:** Reserve 100 GB to allow for multiple models and growth.

### Decision Summary

**Minimum Viable Configuration:**
- **RAM:** 16 GB (with swap/offloading strategies)
- **Storage:** 50 GB free space
- **CPU:** 4 cores
- **Python:** 3.9+
- **Internet:** 5 Mbps (for initial setup)
- **GPU:** Optional but recommended

**Recommended Configuration:**
- **RAM:** 32 GB
- **Storage:** 100 GB free space
- **CPU:** 8+ cores
- **Python:** 3.11+
- **Internet:** 25+ Mbps
- **GPU:** NVIDIA GPU with 8GB+ VRAM (optional but highly recommended)

**Key Constraints:**
1. **RAM is the primary bottleneck** — Must accommodate both test model and judge model simultaneously
2. **Storage for models** — Largest component, plan for 40-80 GB per model
3. **Internet for setup only** — Fully offline operation possible after initial downloads
4. **GPU optional but beneficial** — Significantly improves inference speed and reduces RAM pressure

**Permanent Documentation:** This decision is permanently recorded in [`../documents/Technical-Decisions.md`](../documents/Technical-Decisions.md) for long-term reference.

---

## CLI Version Check System

**Decision:** CLI runner will check the platform API for version updates and display non-blocking alerts when newer versions are available.

### Overview

The CLI runner will periodically check the platform website via a public API endpoint to determine:
1. **Latest CLI version** — Whether a newer CLI release is available
2. **Latest benchmark version** — Whether newer benchmark question sets are available

If the local version is outdated, a non-blocking alert is displayed, but users can continue using their current version.

### Platform API Endpoint

**Endpoint:** `GET /api/cli/versions` (public, no authentication required)

**Response Format:**
```json
{
  "cli": {
    "latest_version": "1.4.0",
    "release_date": "2025-12-20",
    "release_notes_url": "https://gcb.example.com/releases/1.4.0"
  },
  "benchmark": {
    "latest_semantic_version": "2.1",
    "latest_marketing_version": "Version 2",
    "release_date": "2025-12-15",
    "changelog_url": "https://gcb.example.com/versions/2.1"
  },
  "api_version": "1.0"
}
```

**Implementation (FastAPI):**
```python
# FastAPI endpoint (platform backend)
@router.get("/api/cli/versions", tags=["public"])
async def get_cli_versions():
    """Public endpoint for CLI version checking."""
    return {
        "cli": {
            "latest_version": get_latest_cli_version(),  # From config/env
            "release_date": get_cli_release_date(),
            "release_notes_url": f"{settings.BASE_URL}/releases/{get_latest_cli_version()}"
        },
        "benchmark": {
            "latest_semantic_version": get_current_benchmark_version(),
            "latest_marketing_version": get_current_marketing_version(),
            "release_date": get_benchmark_release_date(),
            "changelog_url": f"{settings.BASE_URL}/versions/{get_current_benchmark_version()}"
        },
        "api_version": "1.0"
    }
```

### CLI Version Checker Implementation

**Location:** `gcb_runner/version_check.py`

**Features:**
- Checks platform API on startup and before test runs
- Caches results locally (24-hour TTL) to avoid excessive API calls
- Graceful degradation if API is unavailable (no blocking)
- Non-blocking alerts using `rich` console formatting
- Compares both CLI version and benchmark version

**Implementation Structure:**
```python
# gcb_runner/version_check.py

import json
import time
from pathlib import Path
from typing import Optional
from packaging import version
import httpx
from rich.console import Console
from rich.panel import Panel

class VersionChecker:
    """Check for CLI and benchmark version updates."""
    
    def __init__(
        self,
        api_url: str = "https://gcb.example.com",
        cache_file: Optional[Path] = None,
        cache_ttl: int = 86400  # 24 hours
    ):
        self.api_url = api_url.rstrip("/")
        self.cache_file = cache_file or Path.home() / ".gcb-runner" / "version_cache.json"
        self.cache_ttl = cache_ttl
        self.console = Console()
    
    def check_versions(
        self,
        current_cli_version: str,
        current_benchmark_version: str,
        show_alert: bool = True
    ) -> dict:
        """Check for version updates and optionally display alert."""
        cached = self._load_cache()
        
        # Use cache if still valid
        if cached and self._is_cache_valid(cached):
            version_info = cached["data"]
        else:
            # Fetch from API
            try:
                version_info = self._fetch_from_api()
                self._save_cache(version_info)
            except Exception as e:
                # If API fails, use cache even if expired, or skip check
                if cached:
                    version_info = cached["data"]
                    if show_alert:
                        self.console.print(
                            "[yellow]⚠ Could not check for updates (using cached data)[/yellow]"
                        )
                else:
                    # No cache and API failed - skip version check
                    return {"cli": None, "benchmark": None, "error": str(e)}
        
        # Compare versions
        cli_outdated = self._is_outdated(
            current_cli_version,
            version_info.get("cli", {}).get("latest_version")
        )
        benchmark_outdated = self._is_outdated(
            current_benchmark_version,
            version_info.get("benchmark", {}).get("latest_semantic_version")
        )
        
        if show_alert and (cli_outdated or benchmark_outdated):
            self._show_alert(cli_outdated, benchmark_outdated, version_info)
        
        return {
            "cli": {
                "current": current_cli_version,
                "latest": version_info.get("cli", {}).get("latest_version"),
                "outdated": cli_outdated
            },
            "benchmark": {
                "current": current_benchmark_version,
                "latest": version_info.get("benchmark", {}).get("latest_semantic_version"),
                "outdated": benchmark_outdated
            }
        }
    
    def _fetch_from_api(self) -> dict:
        """Fetch version information from platform API."""
        url = f"{self.api_url}/api/cli/versions"
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    
    def _is_outdated(self, current: str, latest: Optional[str]) -> bool:
        """Check if current version is outdated."""
        if not latest:
            return False
        try:
            return version.parse(current) < version.parse(latest)
        except Exception:
            # If version parsing fails, assume not outdated
            return False
    
    def _show_alert(
        self,
        cli_outdated: bool,
        benchmark_outdated: bool,
        version_info: dict
    ):
        """Display non-blocking version update alert."""
        messages = []
        
        if cli_outdated:
            cli_latest = version_info.get("cli", {}).get("latest_version")
            cli_url = version_info.get("cli", {}).get("release_notes_url", "")
            messages.append(
                f"[bold]CLI Update Available:[/bold] {cli_latest}\n"
                f"  Run: [cyan]pip install --upgrade gcb-runner[/cyan]"
            )
            if cli_url:
                messages.append(f"  Release notes: {cli_url}")
        
        if benchmark_outdated:
            bench_latest = version_info.get("benchmark", {}).get("latest_semantic_version")
            bench_marketing = version_info.get("benchmark", {}).get("latest_marketing_version")
            bench_url = version_info.get("benchmark", {}).get("changelog_url", "")
            messages.append(
                f"\n[bold]New Benchmark Version:[/bold] {bench_marketing} ({bench_latest})\n"
                f"  Update CLI to access the latest question set"
            )
            if bench_url:
                messages.append(f"  Changelog: {bench_url}")
        
        if messages:
            alert_text = "\n".join(messages)
            self.console.print(
                Panel(
                    alert_text,
                    title="[yellow]📦 Version Update Available[/yellow]",
                    border_style="yellow",
                    padding=(1, 2)
                )
            )
            self.console.print(
                "[dim]You can continue using your current version.[/dim]\n"
            )
    
    def _load_cache(self) -> Optional[dict]:
        """Load cached version information."""
        if not self.cache_file.exists():
            return None
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_cache(self, data: dict):
        """Save version information to cache."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "data": data
            }, f)
    
    def _is_cache_valid(self, cached: dict) -> bool:
        """Check if cache is still valid."""
        timestamp = cached.get("timestamp", 0)
        return (time.time() - timestamp) < self.cache_ttl
```

### Integration into CLI

**Usage in CLI commands:**
```python
# gcb_runner/cli.py

from gcb_runner.version_check import VersionChecker
from gcb_runner import __version__ as CLI_VERSION
from gcb_runner.versions.loader import VersionLoader

@app.command()
def test(...):
    """Run benchmark test."""
    # Check versions (non-blocking)
    checker = VersionChecker(api_url=config.get("platform", {}).get("url"))
    current_benchmark = VersionLoader.CURRENT_VERSION
    checker.check_versions(CLI_VERSION, current_benchmark, show_alert=True)
    
    # Continue with test execution...
```

### Configuration

**CLI Config (`~/.gcb-runner/config.json`):**
```json
{
  "platform": {
    "url": "https://gcb.example.com",
    "check_updates": true
  }
}
```

**Environment Variable Override:**
- `GCB_API_URL` — Override platform API URL
- `GCB_DISABLE_VERSION_CHECK` — Disable version checking entirely

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **HTTP Client** | `httpx` | Already in dependencies; async-capable |
| **Version Comparison** | `packaging` | Standard Python library for semantic versioning |
| **Caching** | JSON file | Simple, no external dependencies |
| **UI** | `rich` | Already used for CLI output |
| **API Endpoint** | FastAPI | Matches existing platform stack |

### User Experience

**Example Alert Display:**
```
╔═══════════════════════════════════════════════════════════════╗
║              📦 Version Update Available                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ CLI Update Available: 1.4.0                                  ║
║   Run: pip install --upgrade gcb-runner                       ║
║   Release notes: https://gcb.example.com/releases/1.4.0     ║
║                                                               ║
║ New Benchmark Version: Version 2 (2.1)                        ║
║   Update CLI to access the latest question set               ║
║   Changelog: https://gcb.example.com/versions/2.1            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

You can continue using your current version.
```

**Behavior:**
- Alert appears once per session (cached for 24 hours)
- Non-blocking — user can dismiss or ignore
- Works offline (uses cached data if API unavailable)
- Configurable — can be disabled via config or environment variable

### Implementation Tasks

1. **[BUILD]** Create FastAPI endpoint `/api/cli/versions` in platform backend
2. **[BUILD]** Implement `VersionChecker` class in CLI runner
3. **[BUILD]** Integrate version check into CLI commands (test, versions, etc.)
4. **[BUILD]** Add version check configuration to CLI config system
5. **[BUILD]** Add `packaging` dependency to CLI runner `pyproject.toml`

### Security Considerations

- **Public endpoint** — No authentication required (version info is public)
- **Rate limiting** — Platform should rate limit to prevent abuse
- **HTTPS only** — All API calls use HTTPS
- **Timeout** — Short timeout (5 seconds) to avoid blocking
- **Cache validation** — Cache includes timestamp to prevent stale data

### Error Handling

- **API unavailable** — Use cached data if available, otherwise skip check silently
- **Invalid response** — Log error, skip check, don't block user
- **Network timeout** — Use cached data or skip check
- **Version parsing errors** — Assume versions are current (fail-safe)

**Permanent Documentation:** This decision is permanently recorded in [`../documents/Technical-Decisions.md`](../documents/Technical-Decisions.md) for long-term reference.

---

## Refund Approval Process

**Decision:** Refund approval process is defined below, with automatic refund eligibility for test failures and a retest mechanism with a maximum of three attempts.

### Overview

The refund process is triggered when a test run fails due to technical issues (purchase/processing failures, model unavailability) rather than model performance. Users are provided with both refund and retest options, with retesting limited to three attempts per purchase.

### Refund Eligibility Criteria

**Automatic Refund Eligibility:**
1. **Purchase/Processing Failure** — Payment processed but test execution failed to start
2. **Model Unavailability** — Selected model is no longer available or accessible during test execution
3. **Technical Infrastructure Failure** — Platform/system errors that prevent test completion
4. **Invalid Test Configuration** — Test cannot proceed due to configuration errors (system fault, not user error)

**Not Eligible for Refund:**
- Test completed successfully but model performed poorly
- User selected wrong model or configuration
- Test completed but user is dissatisfied with results
- User-initiated cancellation after test has started

### Refund Workflow

#### 1. Failure Detection

When a test run fails due to eligible reasons, the system automatically:
- Detects the failure type and reason
- Records the failure in the test run record
- Determines if the failure qualifies for refund eligibility
- Updates the test run status to `FAILED_ELIGIBLE_FOR_REFUND` or `FAILED_NOT_ELIGIBLE`

#### 2. User Notification

Upon eligible failure, the user receives:
- **Email notification** with failure details
- **In-app notification** on the user dashboard
- **Test run status page** showing:
  - Failure reason and details
  - Refund button (if eligible)
  - Retest button (if retest attempts remaining)

#### 3. User Action Options

**Option A: Request Refund**
- User clicks "Request Refund" button
- System processes automatic refund via Stripe
- Refund is processed immediately (no manual approval needed for eligible failures)
- User receives confirmation email
- Test run status updated to `REFUNDED`

**Option B: Retest**
- User clicks "Retest" button
- System checks retest attempt count (must be < 3)
- If eligible, creates new test run with same configuration
- User is not charged again (uses original purchase)
- Retest attempt counter incremented
- Test run status updated to `RETESTING`

**Option C: No Action**
- User can choose to do nothing
- Test run remains in `FAILED_ELIGIBLE_FOR_REFUND` status
- Refund option remains available indefinitely
- Retest option remains available until 3 attempts reached

### Retest Limitations

**Maximum Retest Attempts:** 3 attempts per purchase

**Retest Attempt Tracking:**
- Each purchase has a `retest_count` field (starts at 0)
- Incremented each time user clicks "Retest"
- When `retest_count >= 3`, retest button is disabled
- Retest button shows remaining attempts: "Retest (2 attempts remaining)"

**Retest Behavior:**
- Uses same model and configuration as original test
- No additional charge to user
- Each retest creates a new test run record (linked to original purchase)
- If retest succeeds, original purchase is considered fulfilled
- If all 3 retests fail, user can still request refund

### User Interface Flow

#### Test Run Status Page (After Failure)

```
┌─────────────────────────────────────────────────────────┐
│ Test Run Failed                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ❌ Test execution failed                                 │
│                                                          │
│ Reason: Model unavailable (gpt-4-turbo)                 │
│ Status: Eligible for refund                              │
│                                                          │
│ [Request Refund]  [Retest (2 attempts remaining)]       │
│                                                          │
│ Note: You can retest up to 3 times at no additional     │
│ cost. If all retests fail, you can still request a      │
│ refund.                                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### After 3 Retest Attempts

```
┌─────────────────────────────────────────────────────────┐
│ Test Run Failed                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ❌ Test execution failed                                 │
│                                                          │
│ Reason: Model unavailable (gpt-4-turbo)                 │
│ Status: Eligible for refund                              │
│ Retest attempts: 3/3 (maximum reached)                   │
│                                                          │
│ [Request Refund]                                         │
│                                                          │
│ Note: Maximum retest attempts reached. You can still     │
│ request a refund.                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Database Schema

**TestRun Table Additions:**
```sql
ALTER TABLE test_runs ADD COLUMN failure_reason TEXT;
ALTER TABLE test_runs ADD COLUMN refund_eligible BOOLEAN DEFAULT FALSE;
ALTER TABLE test_runs ADD COLUMN refund_status VARCHAR(50); -- NULL, 'PENDING', 'PROCESSED', 'REFUNDED'
ALTER TABLE test_runs ADD COLUMN retest_count INTEGER DEFAULT 0;
ALTER TABLE test_runs ADD COLUMN original_purchase_id INTEGER REFERENCES purchases(id);
ALTER TABLE test_runs ADD COLUMN is_retest BOOLEAN DEFAULT FALSE;
```

**Purchase Table Additions:**
```sql
ALTER TABLE purchases ADD COLUMN total_retest_count INTEGER DEFAULT 0;
ALTER TABLE purchases ADD COLUMN refund_status VARCHAR(50); -- NULL, 'PENDING', 'PROCESSED', 'REFUNDED'
```

### Implementation Details

#### 1. Failure Detection Logic

```python
def determine_refund_eligibility(test_run: TestRun) -> bool:
    """Determine if test run failure qualifies for automatic refund."""
    failure_reasons_eligible = [
        "MODEL_UNAVAILABLE",
        "PROCESSING_FAILURE",
        "INFRASTRUCTURE_ERROR",
        "CONFIGURATION_ERROR"  # System fault, not user error
    ]
    
    if test_run.status == "FAILED":
        return test_run.failure_reason in failure_reasons_eligible
    return False
```

#### 2. Retest Attempt Check

```python
def can_retest(purchase: Purchase) -> bool:
    """Check if user can retest (hasn't exceeded 3 attempts)."""
    return purchase.total_retest_count < 3
```

#### 3. Refund Processing

```python
def process_refund(test_run: TestRun, purchase: Purchase):
    """Process automatic refund via Stripe."""
    if not test_run.refund_eligible:
        raise ValueError("Test run not eligible for refund")
    
    # Process refund via Stripe API
    refund = stripe.Refund.create(
        payment_intent=purchase.stripe_payment_intent_id,
        amount=purchase.amount_cents,
        reason="requested_by_customer"
    )
    
    # Update database
    test_run.refund_status = "PROCESSED"
    purchase.refund_status = "PROCESSED"
    # ... save to database
```

#### 4. Retest Creation

```python
def create_retest(purchase: Purchase, original_test_run: TestRun) -> TestRun:
    """Create a new test run as a retest attempt."""
    if purchase.total_retest_count >= 3:
        raise ValueError("Maximum retest attempts reached")
    
    # Create new test run with same configuration
    retest = TestRun(
        user_id=purchase.user_id,
        model_id=original_test_run.model_id,
        benchmark_version=original_test_run.benchmark_version,
        is_retest=True,
        original_purchase_id=purchase.id,
        status="PENDING"
    )
    
    # Increment retest count
    purchase.total_retest_count += 1
    retest.retest_count = purchase.total_retest_count
    
    # Save and return
    # ... save to database
    return retest
```

### Stripe Integration

**Refund Processing:**
- Use Stripe Refund API (`stripe.Refund.create`)
- Refund full amount of original purchase
- Reason: "requested_by_customer"
- Automatic processing (no manual approval for eligible failures)

**Webhook Handling:**
- Listen for `charge.refunded` webhook event
- Update database when refund is confirmed
- Send confirmation email to user

### User Experience Considerations

1. **Clear Communication** — Failure reasons are clearly explained
2. **Immediate Options** — Both refund and retest buttons visible immediately
3. **Transparency** — Retest attempt counter always visible
4. **No Surprises** — User knows exactly how many retests remain
5. **Flexibility** — User can choose refund or retest, or wait
6. **Automatic Processing** — No manual approval delays for eligible refunds

### Edge Cases

1. **Partial Test Completion** — If test runs partially (e.g., 50% complete) then fails, still eligible for refund
2. **Model Becomes Available During Retest** — Retest proceeds normally; if successful, purchase fulfilled
3. **Multiple Failures** — Each retest failure is tracked separately; user can refund at any point
4. **Refund After Successful Retest** — Not allowed; successful retest fulfills purchase
5. **Concurrent Retests** — System prevents multiple concurrent retests from same purchase

### Testing Requirements

1. **[BUILD]** Test refund flow for eligible failures
2. **[BUILD]** Test retest attempt counting and blocking
3. **[BUILD]** Test Stripe refund webhook handling
4. **[BUILD]** Test UI display of refund/retest options
5. **[BUILD]** Test edge cases (partial completion, concurrent retests, etc.)

### Implementation Tasks

1. **[BUILD]** Add database fields for refund and retest tracking
2. **[BUILD]** Implement failure detection and eligibility determination
3. **[BUILD]** Build refund processing endpoint (Stripe integration)
4. **[BUILD]** Build retest creation endpoint
5. **[BUILD]** Create UI components for refund/retest buttons
6. **[BUILD]** Implement retest attempt counter and blocking logic
7. **[BUILD]** Add email notifications for failures and refunds
8. **[BUILD]** Set up Stripe webhook handler for refund confirmations

**Permanent Documentation:** This decision is permanently recorded in [`../documents/Technical-Decisions.md`](../documents/Technical-Decisions.md) for long-term reference.

---

*This document should be reviewed and updated as items are completed or new gaps are identified.*
