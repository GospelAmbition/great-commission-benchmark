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

- [x] **[BUILD]** Create project structure (`pyproject.toml`, directory layout)
- [x] **[BUILD]** Define all 19 categories from benchmark-vision.md as code constants
- [x] **[BUILD]** Implement SQLAlchemy database models (Question, BenchmarkVersion, VersionQuestion, JudgeTestCase)
- [x] **[BUILD]** Create database migrations strategy with Alembic
- [x] **[BUILD]** Build CLI entry point with rich menus and navigation

### 1.2 Question Generation System

- [x] **[WRITE]** Create generation prompt template for Category 3.1 (Missiological Research)
- [x] **[WRITE]** Create generation prompt template for Category 3.2 (Evangelistic Material Creation)
- [x] **[WRITE]** Create generation prompt template for Category 3.3 (Apologetic Purposes)
- [x] **[WRITE]** Create generation prompt template for Category 3.4 (Conversational AI Tools)
- [x] **[WRITE]** Create generation prompt template for Category 3.5 (Intercessory Prayer Purposes)
- [x] **[WRITE]** Create generation prompt template for Category 3.6 (Problematic Vocabulary)
- [x] **[WRITE]** Create generation prompt template for Category 3.7 (Difficult Passages)
- [x] **[WRITE]** Create generation prompt templates for Tier 2 doctrines (4.1-4.6)
- [x] **[WRITE]** Create generation prompt templates for Tier 3 worldview affirmations (5.1-5.6)
- [x] **[BUILD]** Implement LLM-based question generator
- [x] **[DECISION]** Define minimum question count per category for V1: **Full expected build (210 Tier 1, 60 Tier 2, 30 Tier 3) — no subset for V1** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#minimum-question-count-for-v1))

### 1.3 LLM Backend Adapters

- [x] **[BUILD]** Implement OpenRouter backend adapter
- [x] **[BUILD]** Implement LM Studio backend adapter
- [x] **[BUILD]** Implement Ollama backend adapter
- [x] **[BUILD]** Implement direct API backends (OpenAI, Anthropic)
- [x] **[DECISION]** Determine default/recommended models for question generation: **OpenRouter: GPT 5.2, Gemini 3, Claude Opus** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#question-generation-model-selection))

### 1.4 Judge Prompt Development

- [x] **[WRITE]** Finalize Tier 1 Task Judge prompt (draft exists in specs)
- [x] **[WRITE]** Finalize Tier 2 Doctrine Judge prompt (draft exists in specs)
- [x] **[WRITE]** Finalize Tier 3 Worldview Judge prompt (draft exists in specs)
- [x] **[BUILD]** Implement judge prompt testing framework
- [x] **[BUILD]** Create judge test case management system
- [x] **[SPEC]** Define inter-rater reliability measurement methodology (See [spec-inter-rater-reliability.md](./spec-inter-rater-reliability.md))
- [x] **[DECISION]** Minimum accuracy threshold for judge prompts before locking: **≥90%** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#judge-prompt-accuracy-threshold))

### 1.5 Curation Workflow

- [x] **[BUILD]** Build question review/approval workflow
- [x] **[BUILD]** Implement question locking mechanism
- [x] **[BUILD]** Build Datasette integration for database exploration
- [x] **[BUILD]** Create bulk operations (delete drafts, regenerate category)
- [x] **[SPEC]** Define curation guidelines for reviewers (See [spec-curation-guidelines.md](./spec-curation-guidelines.md))

### 1.6 Version Building & Publishing

- [x] **[BUILD]** Implement version creation and assembly
- [x] **[BUILD]** Build pre-publish validation (category coverage, tier distribution, etc.)
- [x] **[BUILD]** Implement version locking mechanism
- [x] **[BUILD]** Create JSON export for platform publication
- [x] **[BUILD]** Build bundle compiler for CLI distribution (compress + base64 encode)
- [x] **[SPEC]** Document version release workflow

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
- [x] **[DECISION]** How to communicate CLI updates when new benchmark versions release: **Automatic version checking enabled** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#cli-version-check-system))

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
- [x] **[DECISION]** Default judge model: **OpenAI gpt-oss-20b** (available on both LM Studio and OpenRouter) (See [Technical-Decisions.md](../documents/Technical-Decisions.md#judge-model-selection))

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
- [x] **[SPEC]** Design dashboard wireframes/mockups (See [wireframes-cli-results-viewer.md](./wireframes-cli-results-viewer.md))

### 2.7 Static Report Generator

- [ ] **[BUILD]** Implement `gcb-runner report` command
- [ ] **[BUILD]** Create self-contained HTML report template
- [ ] **[BUILD]** Build comparison report for two runs

### 2.8 Export & Upload

- [ ] **[BUILD]** Implement JSON export format
- [ ] **[BUILD]** Create platform upload functionality
- [ ] **[BUILD]** Build account linking flow
- [x] **[SPEC]** Define export format schema validation (See [spec-export-schema-validation.md](./spec-export-schema-validation.md))

### 2.9 Local Model Support

- [ ] **[BUILD]** Implement LM Studio backend
- [ ] **[BUILD]** Implement Ollama backend
- [x] **[SPEC]** Document local model setup instructions (See [spec-local-model-setup.md](./spec-local-model-setup.md))
- [x] **[DECISION]** Minimum hardware requirements for local testing: **16 GB RAM minimum, 32 GB recommended** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#minimum-hardware-requirements-for-local-testing))

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
- [x] **[SPEC]** Document API endpoints (OpenAPI spec) (See [spec-api-endpoints.md](./spec-api-endpoints.md))

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
- [x] **[SPEC]** Design UI wireframes/mockups
- [x] **[DECISION]** UI design system/component library choice: **shadcn/ui** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#ui-design-systemcomponent-library-selection))

### 3.3 Infrastructure

- [ ] **[BUILD]** Set up Railway project
- [ ] **[BUILD]** Configure PostgreSQL database
- [ ] **[BUILD]** Set up CI/CD deployment pipeline
- [ ] **[BUILD]** Configure environment variables
- [ ] **[BUILD]** Set up backup strategy (Railway + local machine download)
- [x] **[DECISION]** Secondary backup location: **In the beginning, we will simply download a copy to a local machine for offline storage** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#secondary-backup-location-strategy))

### 3.4 Third-Party Integrations

- [ ] **[BUILD]** Configure Auth0 application
- [ ] **[BUILD]** Set up Stripe account and webhooks
- [ ] **[BUILD]** Configure OpenRouter API access
- [ ] **[BUILD]** Set up email service for notifications (SendGrid)
- [ ] **[BUILD]** Configure Umami analytics (off-site server - URL and integration info to be provided at deployment)
- [x] **[DECISION]** Select email service provider: **SendGrid** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#email-service-provider-selection))
- [x] **[DECISION]** Analytics choice: **Umami** (on off-site server; URL and integration information will be provided when ready for deployment) (See [Technical-Decisions.md](../documents/Technical-Decisions.md#analytics-service-selection))

### 3.5 Security

- [ ] **[BUILD]** Implement rate limiting
- [ ] **[BUILD]** Set up HTTPS/SSL
- [ ] **[BUILD]** Implement audit logging for question access
- [ ] **[BUILD]** Configure API authentication
- [x] **[SPEC]** Document security practices (See [Security-Practices.md](../documents/Security-Practices.md))

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
- [x] **[SPEC]** Document moderator onboarding process (See [Moderator-Onboarding.md](../documents/Moderator-Onboarding.md))
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
- [x] **[DECISION]** Confirm $20 benchmark hosting contribution amount: **$20 will be the beginning cost for the hosting contribution. This amount may adjust later based on operational needs, but $20 is confirmed as the starting cost.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#benchmark-hosting-contribution-amount))
- [x] **[DECISION]** Define refund approval process (See [Technical-Decisions.md](../documents/Technical-Decisions.md#refund-approval-process))

### 4.6 Communications

- [ ] **[BUILD]** Set up newsletter system
- [ ] **[BUILD]** Create email notification templates
- [ ] **[BUILD]** Set up external discussion platform (Discord)
- [x] **[DECISION]** Select newsletter service: **Brevo** (Note: Implementation should be modular to allow switching services based on moderation/maintenance team's final decision) (See [Technical-Decisions.md](../documents/Technical-Decisions.md#newsletter-service-selection))
- [x] **[DECISION]** Discussion platform: **Discord** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#discussion-platform-selection))
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
- [x] **[SPEC]** Document calibration set creation process (See [spec-calibration-process.md](./spec-calibration-process.md))
- [x] **[DECISION]** Who are the initial human reviewers for calibration? **Chris will be the initial reviewer for the calibration.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#initial-human-reviewers-for-calibration))

### 5.3 Multi-Turn Testing (Phase 5 in methodology)

- [ ] **[WRITE]** Design 5-10 multi-turn conversation scripts
- [x] **[SPEC]** Define misalignment markers (See [spec-misalignment-markers.md](./spec-misalignment-markers.md))
- [x] **[SPEC]** Define "turn-to-break" measurement methodology (See [spec-multi-turn-testing.md](./spec-multi-turn-testing.md))
- [x] **[DECISION]** Multi-turn testing: **Included in V1** (essential for chatbot and AI counseling categories) (See [Technical-Decisions.md](../documents/Technical-Decisions.md#multi-turn-testing-inclusion))

### 5.4 Sample Questions

- [ ] **[WRITE]** Select sample questions to publish publicly (for transparency)
- [x] **[DECISION]** How many sample questions to publish (small subset): **Do not publish exact questions. Publish similar questions (20 or under) to give a sample of the different kinds of questions.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#sample-questions-publication-strategy))
- [x] **[DECISION]** Which categories to include in samples: **Mostly task questions, with one or two worldview and theological questions.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#sample-questions-publication-strategy))

---

## 6. Integration & End-to-End

### 6.1 CLI Builder → Platform

- [x] **[SPEC]** Document how builder exports get to platform (See [spec-builder-to-platform.md](./spec-builder-to-platform.md))
- [ ] **[BUILD]** Create upload mechanism for JSON exports
- [x] **[DECISION]** Manual upload vs. automated pipeline: **Manual upload workflow selected** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#manual-upload-vs-automated-pipeline))

### 6.2 CLI Builder → CLI Runner

- [x] **[SPEC]** Document bundle compilation and distribution process (See [spec-builder-to-runner.md](./spec-builder-to-runner.md))
- [ ] **[BUILD]** Create workflow for adding new versions to gcb-runner
- [x] **[SPEC]** Document CLI release process (version bump, PyPI publish) (See [spec-builder-to-runner.md](./spec-builder-to-runner.md))

### 6.3 Platform → CLI Runner

- [x] **[SPEC]** Document how CLI users know about new versions
- [x] **[DECISION]** Whether CLI should check for updates automatically: **YES — Automatic version checking enabled** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#cli-version-check-system))

### 6.4 Cross-System Consistency

- [x] **[SPEC]** Ensure export format matches between builder and platform (See [spec-cross-system-consistency.md](./spec-cross-system-consistency.md))
- [x] **[SPEC]** Ensure bundle format matches between builder and runner (See [spec-cross-system-consistency.md](./spec-cross-system-consistency.md))
- [x] **[SPEC]** Ensure scoring formulas match across all systems (See [spec-cross-system-consistency.md](./spec-cross-system-consistency.md))

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

- [x] **[SPEC]** Document public API endpoints (See [spec-api-endpoints.md](./spec-api-endpoints.md) Section 1)
- [x] **[SPEC]** Document internal API endpoints (See [spec-api-endpoints.md](./spec-api-endpoints.md) Sections 2-8)
- [x] **[SPEC]** Create OpenAPI/Swagger specification (FastAPI auto-generates at `/openapi.json`, `/docs`, `/redoc`)

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
- [x] **[DECISION]** Define launch communication channels (See [Technical-Decisions.md](../documents/Technical-Decisions.md#launch-communication-channels))
- [x] **[DECISION]** Identify launch partners/early adopters (See [Technical-Decisions.md](../documents/Technical-Decisions.md#launch-partners-and-early-adopters))
- [ ] **[BUILD]** Set up monitoring and alerting
- [x] **[DECISION]** Define launch date criteria (when we're "ready") (See [Technical-Decisions.md](../documents/Technical-Decisions.md#launch-date-criteria))

---

## 10. Post-Launch & Ongoing

### 10.1 Monitoring & Maintenance

- [ ] **[SPEC]** Define monitoring checklist
- [ ] **[SPEC]** Define incident response procedures
- [x] **[DECISION]** On-call/support rotation: **Project lead will monitor inboxes and error notifications. Sentry is identified as an error monitoring system. Alerts should be programmatically organized for failed attempts to run a module and get a refund. These alerts should notify the same inboxes monitored by the project lead.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#on-callsupport-rotation))

### 10.2 Version 2 Planning

- [ ] **[DECISION]** Triggers for V2 question set (timeline: ~yearly)
- [ ] **[SPEC]** Document question set refresh process
- [ ] **[DECISION]** Community question contribution process

### 10.3 Future Considerations

- [x] **[DECISION]** Multilingual support priority and timeline: **Built and expected to quickly follow the MVP in English** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#multilingual-support-priority))
- [x] **[DECISION]** Additional language support (Spanish, Portuguese, etc.): **Spanish, Portuguese, and Korean will be the first languages to auto-translate** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#additional-language-support))
- [x] **[DECISION]** WCAG Level AA upgrade timeline: **No expectation for Level AA upgrade. It will be next year or the year after.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#wcag-level-aa-upgrade-timeline))
- [x] **[DECISION]** Volume discount pricing thresholds: **No volume discounting price thresholds. Simple app and math of the pricing.** (See [Technical-Decisions.md](../documents/Technical-Decisions.md#volume-discount-pricing-thresholds))

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


---

*This document should be reviewed and updated as items are completed or new gaps are identified.*
