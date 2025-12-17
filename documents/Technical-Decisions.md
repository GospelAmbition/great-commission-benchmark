# Great Commission Benchmark — Technical Decisions

This document serves as a permanent record of all technical decisions made during the development of the Great Commission Benchmark platform, CLI tools, and related systems.

**Purpose:** To maintain a complete historical record of technical choices, rationale, and implementation details that will persist beyond working documents like REVIEW-GAPS-AND-DECISIONS.md.

**Last Updated:** December 16, 2025

---

## Table of Contents

1. [Judge Model Selection](#judge-model-selection)
2. [Question Generation Model Selection](#question-generation-model-selection)
3. [Minimum Hardware Requirements for Local Testing](#minimum-hardware-requirements-for-local-testing)
4. [UI Design System/Component Library Selection](#ui-design-systemcomponent-library-selection)
5. [Secondary Backup Location Strategy](#secondary-backup-location-strategy)
6. [Analytics Service Selection](#analytics-service-selection)
7. [Email Service Provider Selection](#email-service-provider-selection)
8. [Newsletter Service Selection](#newsletter-service-selection)
9. [Discussion Platform Selection](#discussion-platform-selection)
10. [Minimum Question Count for V1](#minimum-question-count-for-v1)
11. [Judge Prompt Accuracy Threshold](#judge-prompt-accuracy-threshold)
12. [CLI Version Check System](#cli-version-check-system)
13. [Manual Upload vs Automated Pipeline](#manual-upload-vs-automated-pipeline)
14. [Benchmark Hosting Contribution Amount](#benchmark-hosting-contribution-amount)
15. [Refund Approval Process](#refund-approval-process)
16. [Initial Human Reviewers for Calibration](#initial-human-reviewers-for-calibration)
17. [Multi-Turn Testing Inclusion](#multi-turn-testing-inclusion)
18. [Sample Questions Publication Strategy](#sample-questions-publication-strategy)
19. [Launch Communication Channels](#launch-communication-channels)
20. [Launch Partners and Early Adopters](#launch-partners-and-early-adopters)
21. [Launch Date Criteria](#launch-date-criteria)
22. [On-Call/Support Rotation](#on-callsupport-rotation)
23. [Multilingual Support Priority](#multilingual-support-priority)
24. [Additional Language Support](#additional-language-support)
25. [WCAG Level AA Upgrade Timeline](#wcag-level-aa-upgrade-timeline)
26. [Volume Discount Pricing Thresholds](#volume-discount-pricing-thresholds)

---

## Judge Model Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized

### Decision

**Default judge model:** **OpenAI gpt-oss-20b**

### Rationale

After comparing GPT-OSS-20B and Qwen3 Coder 30B, GPT-OSS-20B was selected as the default judge model based on superior performance in all relevant evaluation categories:

| Capability | GPT-OSS-20B | Qwen3 Coder 30B | Winner |
|------------|-------------|-----------------|--------|
| **Reasoning** | 89.8% | 78% | ✅ GPT-OSS-20B |
| **Instruction Following** | 66% | 51.5% | ✅ GPT-OSS-20B |
| **General Knowledge** | 99% | 32.2% | ✅ GPT-OSS-20B |
| **Ethics Understanding** | 99% | Not specified | ✅ GPT-OSS-20B |
| **Coding** | 92% | 89% | ✅ GPT-OSS-20B |
| **Mathematics** | 66.7% | 89% | Qwen3 (not relevant for judging) |
| **Efficiency** | MoE architecture (faster) | Dense model | ✅ GPT-OSS-20B |
| **Availability** | Both LM Studio & OpenRouter | Both LM Studio & OpenRouter | ✅ Tie |

### Key Advantages

1. **Superior Reasoning (89.8% vs 78%)** — Critical for evaluating whether responses meet criteria
2. **Better Instruction Following (66% vs 51.5%)** — Essential for following judge prompts correctly
3. **Strong General Knowledge (99% vs 32.2%)** — Needed to understand context and theological content
4. **High Ethics Understanding (99%)** — Important for evaluating religious content appropriately
5. **More Efficient** — MoE architecture means faster inference and lower resource usage
6. **Consistent Availability** — Available on both LM Studio (local) and OpenRouter (cloud)

### Implementation Details

- **Model ID on OpenRouter:** `openai/gpt-oss-20b`
- **Model ID on LM Studio:** Same model name (verify exact identifier)
- **Cost:** Very low (~$0.17 per test run based on infrastructure costs doc)
- **Hardware:** Runs efficiently on 16GB+ systems (suitable for local use)

### Notes

Qwen3 Coder 30B's only advantage is mathematics (89% vs 66.7%), which is not relevant for evaluating Great Commission benchmark responses.

---

## Question Generation Model Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 1.3 LLM Backend Adapters - CLI Builder

### Decision

**Default/recommended models for question generation:** **OpenRouter** with the following models:
- **GPT 5.2** (OpenAI)
- **Gemini 3** (Google)
- **Claude Opus** (Anthropic)

### Rationale

Question generation requires high-quality models capable of:
- Understanding complex theological and missiological concepts
- Following detailed prompt instructions for category-specific question generation
- Producing diverse, well-structured questions across 19 categories
- Generating questions that test both capability and willingness appropriately

### Recommended Models

| Model | Provider | Use Case | Rationale |
|-------|----------|----------|-----------|
| **GPT 5.2** | OpenAI | Primary generation model | Latest GPT model with strong instruction following and reasoning capabilities |
| **Gemini 3** | Google | Alternative/backup generation | Provides diversity in generation style and approach |
| **Claude Opus** | Anthropic | High-quality refinement | Excellent for generating nuanced questions requiring deep understanding |

### Backend Selection: OpenRouter

**Why OpenRouter:**
- **Single API interface** — Simplifies implementation with one adapter for multiple models
- **Access to 100+ models** — Flexibility to experiment with different models
- **Pay-per-use pricing** — Cost-effective for question generation workloads
- **Consistent interface** — OpenAI-compatible API format (de facto standard)
- **Model availability** — All three recommended models available through OpenRouter

### Implementation Details

- **Backend:** OpenRouter (`openrouter` adapter)
- **Model IDs (verify exact identifiers on OpenRouter):**
  - GPT 5.2: `openai/gpt-5.2` (or latest identifier)
  - Gemini 3: `google/gemini-3` (or latest identifier)
  - Claude Opus: `anthropic/claude-opus` (or latest identifier)
- **Usage pattern:** CLI Builder will support selecting between these models for question generation
- **Fallback:** Architecture supports direct API backends (OpenAI, Anthropic) if needed

### Notes

- These models represent the current state-of-the-art for question generation as of December 2025
- Model identifiers may need verification/updates as OpenRouter's model catalog evolves
- The CLI Builder architecture supports adding additional models or switching backends as needed
- Local models (via LM Studio/Ollama) remain available for question generation but are not the default recommendation

---

## Minimum Hardware Requirements for Local Testing

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 2.9 Local Model Support - CLI Runner

### Decision

Minimum hardware requirements for local testing are defined below to support running the Great Commission Benchmark CLI runner with local models via LM Studio or Ollama.

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

### Key Constraints

1. **RAM is the primary bottleneck** — Must accommodate both test model and judge model simultaneously
2. **Storage for models** — Largest component, plan for 40-80 GB per model
3. **Internet for setup only** — Fully offline operation possible after initial downloads
4. **GPU optional but beneficial** — Significantly improves inference speed and reduces RAM pressure

### Rationale

These requirements were determined based on:
- The need to run both a test model and judge model (gpt-oss-20b) simultaneously
- Typical model sizes for quantized versions suitable for local inference
- SQLite database storage needs for test results (minimal)
- Python runtime and dependency sizes (minimal)
- Practical use cases from budget to optimal setups

The minimum requirements enable basic functionality, while recommended requirements provide a smooth user experience suitable for regular testing.

---

## UI Design System/Component Library Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 3.2 Frontend (Next.js) - Platform

### Decision

**UI component library:** **shadcn/ui**

### Rationale

After evaluating multiple component library options for Next.js + Tailwind CSS, shadcn/ui was selected as the best fit for the Great Commission Benchmark platform.

### Options Evaluated

| Library | Tailwind Fit | Accessibility | Bundle Size | Customization | Decision |
|---------|--------------|---------------|-------------|---------------|----------|
| **shadcn/ui** | ✅ Perfect | ✅ Excellent (Radix UI) | ✅ Zero runtime | ✅ Full control | ✅ **Selected** |
| Headless UI | ✅ Perfect | ✅ Excellent | ✅ Small | ⚠️ More work | ❌ Limited components |
| Radix UI | ✅ Good | ✅ Excellent | ✅ Small | ⚠️ Low-level | ❌ Too low-level |
| Mantine | ⚠️ Conflicts | ✅ Good | ⚠️ Large | ⚠️ Opinionated | ❌ Tailwind conflicts |
| Chakra UI | ⚠️ Conflicts | ✅ Good | ⚠️ Medium | ⚠️ Opinionated | ❌ Tailwind conflicts |

### Key Advantages

1. **Perfect Tailwind Integration** — Built specifically for Tailwind CSS workflows, no conflicts
2. **Excellent Accessibility** — Built on Radix UI primitives, WCAG Level A compatible
3. **Full Customization** — Components live in your codebase, fully customizable
4. **No Runtime Overhead** — Copy-paste components, zero bundle size impact
5. **Ideal Component Set** — Perfect for leaderboards, forms, dashboards, moderation interfaces
6. **Growing Ecosystem** — Active community and expanding component library

### Component Categories Available

**Layout:**
- Card, Separator, Sheet, Dialog, Drawer

**Forms:**
- Input, Select, Checkbox, Radio Group, Form (with react-hook-form integration)

**Data Display:**
- Table, Badge, Avatar, Progress, Skeleton

**Navigation:**
- Tabs, Dropdown Menu, Navigation Menu, Breadcrumb

**Feedback:**
- Alert, Toast, Dialog, Popover, Tooltip

**Overlay:**
- Sheet, Dialog, Popover, Tooltip, Hover Card

### Implementation Details

**Setup:**
- Components installed via CLI (`npx shadcn-ui@latest init`)
- Components copied into project (`components/ui/` directory)
- Full TypeScript support
- Fully customizable with Tailwind CSS

**Key Features:**
- **Copy-paste architecture** — Components live in your codebase
- **Radix UI primitives** — Accessible by default
- **Tailwind CSS styling** — No CSS-in-JS conflicts
- **Zero runtime dependencies** — No external component library bundle
- **Full control** — Modify components as needed for project requirements

### Use Cases in Platform

**Leaderboard:**
- Table component for model rankings
- Badge components for trust tiers and scores
- Select/Dropdown Menu for filtering
- Card components for model details

**Test Execution Flow:**
- Form components (Input, Select, Checkbox)
- Button components
- Dialog/Sheet for payment modals
- Progress indicators for test status

**User Dashboard:**
- Table for test history
- Card components for test summaries
- Badge components for status indicators

**Moderation Interface:**
- Table for review queue
- Dialog for review interface
- Radio Group for verdict selection
- Alert components for feedback

**Admin Pages:**
- Table component for user management
- Dropdown Menu for actions
- Dialog for user details
- Card components for system metrics

### Accessibility

shadcn/ui components are built on Radix UI primitives, which provide:
- **Keyboard navigation** — Full keyboard support
- **Screen reader support** — ARIA attributes and semantic HTML
- **Focus management** — Proper focus trapping and restoration
- **WCAG Level A compliance** — Meets accessibility requirements

### Notes

- Components are installed and customized per project needs
- No subscription or licensing fees
- Active development and community support
- Can be combined with other libraries as needed (e.g., Chart.js for visualizations)
- Components can be extended or modified for project-specific requirements

---

## Secondary Backup Location Strategy

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 3.3 Infrastructure - Platform

### Decision

**Secondary backup location:** In the beginning, we will simply download a copy to a local machine for offline storage.

### Rationale

For the initial launch and early stages of the platform:
- **Simplicity** — No need to set up and maintain cloud storage infrastructure initially
- **Cost-effective** — Avoids cloud storage costs during early stages
- **Offline access** — Provides offline backup that doesn't depend on cloud services
- **Sufficient for MVP** — Railway's built-in backup plus local download provides adequate redundancy for initial launch

### Implementation Details

**Initial Approach:**
- Railway provides primary database backups (automated)
- Manual download process for secondary backup:
  - Export database dump from Railway
  - Download to designated local machine
  - Store offline for disaster recovery

**Process:**
1. Regular database exports from Railway (weekly or monthly)
2. Download to local machine with sufficient storage
3. Store in secure, offline location
4. Document backup location and access procedures

### Future Considerations

As the platform grows, we may consider:
- Automated cloud backup (e.g., Google Cloud Storage bucket)
- Automated backup scheduling
- Multiple backup locations
- Backup retention policies

However, for the initial launch and early operations, the local machine download approach is sufficient and keeps infrastructure complexity minimal.

### Notes

- This decision focuses on the **secondary** backup location
- Railway's built-in backup serves as the **primary** backup mechanism
- The local download provides an additional layer of redundancy
- This approach can be upgraded to automated cloud backups as the platform scales

---

## Analytics Service Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 3.4 Third-Party Integrations - Platform

### Decision

**Analytics service:** **Umami** (self-hosted on off-site server)

### Rationale

Umami was selected as the analytics solution for the Great Commission Benchmark platform:
- **Privacy-focused** — GDPR compliant, no cookies required, respects user privacy
- **Open source** — Self-hosted option provides full control over data
- **Lightweight** — Minimal performance impact on the platform
- **Simple integration** — Easy to integrate via script tag in HTML header
- **Cost-effective** — Self-hosted eliminates ongoing subscription costs

### Implementation Details

**Deployment:**
- Umami will be hosted on an **off-site server** (separate from the main platform)
- URL and integration information will be provided when ready for deployment
- Integration will be done via script tag in the HTML header of the Next.js application

**Integration Approach:**
- Script tag will be added to the main layout/header component
- Configuration will be provided at deployment time
- No additional build-time configuration required

### Notes

- The off-site server hosting Umami is separate from the Railway deployment
- Integration details (URL, site ID, etc.) will be provided at deployment time
- This allows for flexibility in server setup and configuration
- Umami's privacy-first approach aligns with the platform's values

---

## Email Service Provider Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 3.4 Third-Party Integrations - Platform

### Decision

**Email service provider:** **SendGrid**

### Rationale

SendGrid was selected for handling transactional emails and user notifications:
- **Reliability** — Proven track record for deliverability
- **API Integration** — Well-documented API for programmatic email sending
- **Scalability** — Handles high-volume email sending
- **Template Support** — Supports email templates for consistent messaging
- **Analytics** — Provides email delivery and engagement metrics

### Implementation Details

- **Service:** SendGrid
- **Use Cases:**
  - User registration confirmations
  - Test completion notifications
  - Test submission status updates
  - Refund confirmations
  - Failure notifications
- **Integration:** API-based integration with FastAPI backend

### Notes

- SendGrid will handle all transactional emails for the platform
- Email templates will be created for each notification type
- Analytics and delivery tracking will be monitored

---

## Newsletter Service Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 4.6 Communications - Process & Operations

### Decision

**Newsletter service:** **Brevo** (formerly Sendinblue)

**Note:** Implementation should be modular to allow switching services based on moderation/maintenance team's final decision.

### Rationale

Brevo was selected for newsletter management:
- **Cost-effective** — Competitive pricing for email marketing
- **Feature-rich** — Includes automation, segmentation, and analytics
- **User-friendly** — Intuitive interface for managing newsletters
- **Modular Design** — Architecture allows for easy service switching if needed

### Implementation Details

- **Service:** Brevo
- **Modularity:** Implementation will be abstracted to allow service switching
- **Use Cases:**
  - Regular platform updates
  - New benchmark version announcements
  - Community news and highlights
  - Feature announcements

### Notes

- The implementation architecture will support switching to alternative services if the moderation/maintenance team decides to change providers
- Newsletter content and scheduling will be managed by the moderation team

---

## Discussion Platform Selection

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 4.6 Communications - Process & Operations

### Decision

**Discussion platform:** **Discord**

### Rationale

Discord was selected for community discussions:
- **Wide Adoption** — Popular platform with familiar interface
- **Real-time Communication** — Supports both synchronous and asynchronous discussions
- **Channel Organization** — Easy to organize discussions by topic
- **Integration Capabilities** — Can integrate with platform for notifications
- **Free Tier** — Cost-effective for community building

### Implementation Details

- **Platform:** Discord
- **Use Cases:**
  - Community discussions about benchmark results
  - Technical support and questions
  - Feature requests and feedback
  - General community engagement

### Notes

- Discord server will be set up and managed by the moderation team
- Integration with platform may be added for automated notifications

---

## Minimum Question Count for V1

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 1.2 Question Generation System - CLI Builder

### Decision

**Minimum question count per category for V1:** **Full expected build (210 Tier 1, 60 Tier 2, 30 Tier 3) — no subset for V1**

### Rationale

The full question set is required for V1 to ensure:
- **Comprehensive Coverage** — All categories and tiers are adequately represented
- **Statistical Validity** — Sufficient questions for meaningful scoring and differentiation
- **Benchmark Integrity** — Complete question set provides accurate assessment of model capabilities
- **No Subset Approach** — Avoids the complexity of maintaining a subset version

### Implementation Details

- **Tier 1 (Task Questions):** 210 questions total
- **Tier 2 (Doctrine Questions):** 60 questions total
- **Tier 3 (Worldview Questions):** 30 questions total
- **Total:** 300 questions for V1

### Notes

- All questions must be generated, reviewed, and validated before V1 launch
- No reduced subset will be created for initial launch

---

## Judge Prompt Accuracy Threshold

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 1.4 Judge Prompt Development - CLI Builder

### Decision

**Minimum accuracy threshold for judge prompts before locking:** **≥90%**

### Rationale

A 90% accuracy threshold ensures:
- **High Reliability** — Judge prompts produce consistent and accurate verdicts
- **Benchmark Validity** — Results are trustworthy and reproducible
- **Quality Standard** — Meets the minimum standard for production use
- **Calibration Requirement** — Must be validated against human reviewers before locking

### Implementation Details

- **Threshold:** ≥90% accuracy required
- **Validation Process:**
  - Judge prompts tested against calibration set
  - Compared with human reviewer verdicts
  - Accuracy calculated and verified
  - Prompts locked only after meeting threshold
- **Applies to:** All three judge prompts (Tier 1, Tier 2, Tier 3)

### Notes

- Judge prompts must achieve ≥90% accuracy before being locked for production use
- Inter-rater reliability with human reviewers should also be ≥80% (per methodology specifications)

---

## CLI Version Check System

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 6.3 Platform → CLI Runner - Integration & End-to-End

### Decision

**CLI version checking:** ✅ **YES** — CLI will automatically check for updates. This follows the standard pattern used by popular CLI tools (npm's `update-notifier`, pip packages, cargo tools).

### Overview

The CLI runner will periodically check the platform website via a public API endpoint to determine:
1. **Latest CLI version** — Whether a newer CLI release is available
2. **Latest benchmark version** — Whether newer benchmark question sets are available

If the local version is outdated, a non-blocking alert is displayed, but users can continue using their current version.

### Implementation Features

- Automatic version checking on startup and before test runs
- Non-blocking alerts (users can continue using current version)
- 24-hour cache to minimize API calls
- Graceful degradation if API is unavailable
- Configurable via `check_updates` setting and `GCB_DISABLE_VERSION_CHECK` env var

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

### CLI Implementation

**Location:** `gcb_runner/version_check.py`

**Features:**
- Checks platform API on startup and before test runs
- Caches results locally (24-hour TTL) to avoid excessive API calls
- Graceful degradation if API is unavailable (no blocking)
- Non-blocking alerts using `rich` console formatting
- Compares both CLI version and benchmark version

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

**Behavior:**
- Alert appears once per session (cached for 24 hours)
- Non-blocking — user can dismiss or ignore
- Works offline (uses cached data if API unavailable)
- Configurable — can be disabled via config or environment variable

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

### Implementation Tasks

1. **[BUILD]** Create FastAPI endpoint `/api/cli/versions` in platform backend
2. **[BUILD]** Implement `VersionChecker` class in CLI runner
3. **[BUILD]** Integrate version check into CLI commands (test, versions, etc.)
4. **[BUILD]** Add version check configuration to CLI config system
5. **[BUILD]** Add `packaging` dependency to CLI runner `pyproject.toml`

---

## Manual Upload vs Automated Pipeline

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 6.1 CLI Builder → Platform - Integration & End-to-End

### Decision

**CLI Builder → Platform upload workflow:** **Manual upload workflow selected**

### Decision Analysis

**Manual Upload (Preferred Approach):**
- CLI Builder generates JSON file (e.g., `gcb-v1.0.0.json`)
- User manually uploads via web form or API endpoint
- Platform verifies checksum, format, and content before accepting

**Pros:**
- ✅ **Human verification step** — Builder can review JSON before upload (catch errors early)
- ✅ **Security control** — No automated credentials needed; reduces attack surface
- ✅ **Audit trail** — Clear record of who uploaded what and when
- ✅ **Simple implementation** — Just need upload form/endpoint with validation
- ✅ **Flexibility** — Builder can review, edit, or regenerate before upload
- ✅ **No infrastructure dependencies** — No CI/CD, webhooks, or API keys to manage
- ✅ **Version control friendly** — JSON files can be committed to git for history
- ✅ **Offline workflow** — Builder can work completely offline, upload later

**Cons:**
- ❌ **Extra step** — Requires manual action (but this is intentional for verification)
- ❌ **Potential for delay** — Human step means not instant (but acceptable for version releases)
- ❌ **Possible human error** — Could upload wrong file (mitigated by checksum verification)

**Automated Pipeline Approach:**
- CLI Builder publishes to git repo or triggers webhook
- CI/CD pipeline or webhook handler automatically uploads to platform
- Platform validates and processes automatically

**Pros:**
- ✅ **Instant deployment** — No manual step, immediate availability
- ✅ **Consistency** — Eliminates possibility of forgetting to upload
- ✅ **Integration** — Fits into modern DevOps workflows

**Cons:**
- ❌ **Complexity** — Requires CI/CD setup, webhook infrastructure, API authentication
- ❌ **Security concerns** — Need secure API keys, webhook secrets, access controls
- ❌ **Less control** — No human review step before platform receives data
- ❌ **Infrastructure overhead** — Additional services to maintain (GitHub Actions, webhook handlers, etc.)
- ❌ **Debugging difficulty** — Automated failures harder to diagnose
- ❌ **Overkill for use case** — Version releases are infrequent (not daily deployments)
- ❌ **Dependency risk** — Platform must be available when pipeline runs

### Rationale

1. Version releases are infrequent (not daily)
2. Human verification is valuable for quality control
3. Simplicity reduces security and maintenance burden
4. The workflow already includes a manual review step (publishing locks the version)

### Implementation Plan

- CLI Builder generates JSON with checksum
- Web form or authenticated API endpoint accepts upload
- Platform validates: checksum match, format version, required fields
- Moderator/admin reviews before making version live (if needed)

---

## Benchmark Hosting Contribution Amount

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 4.5 Financial Setup - Process & Operations

### Decision

**Benchmark hosting contribution amount:** **$20 will be the beginning cost for the hosting contribution. This amount may adjust later based on operational needs, but $20 is confirmed as the starting cost.**

### Rationale

- **Starting Point** — $20 provides a reasonable starting cost for benchmark hosting
- **Flexibility** — Amount may be adjusted based on operational needs and costs
- **Transparency** — Clear communication that this is the initial cost, subject to change

### Implementation Details

- **Initial Cost:** $20 per benchmark test run
- **Future Adjustments:** May be adjusted based on:
  - Operational costs
  - Infrastructure expenses
  - Market conditions
  - Platform sustainability needs

### Notes

- This is the confirmed starting cost for benchmark hosting contributions
- Users will be informed of any future cost adjustments
- Pricing structure will remain simple and transparent

---

## Refund Approval Process

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 4.5 Financial Setup - Process & Operations

### Decision

Refund approval process is defined below, with automatic refund eligibility for test failures and a retest mechanism with a maximum of three attempts.

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

### Implementation Tasks

1. **[BUILD]** Add database fields for refund and retest tracking
2. **[BUILD]** Implement failure detection and eligibility determination
3. **[BUILD]** Build refund processing endpoint (Stripe integration)
4. **[BUILD]** Build retest creation endpoint
5. **[BUILD]** Create UI components for refund/retest buttons
6. **[BUILD]** Implement retest attempt counter and blocking logic
7. **[BUILD]** Add email notifications for failures and refunds
8. **[BUILD]** Set up Stripe webhook handler for refund confirmations

---

## Initial Human Reviewers for Calibration

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 5.2 Calibration Set - Benchmark Content

### Decision

**Initial human reviewers for calibration:** **Chris Wynn will be the initial reviewer for the calibration.**

### Rationale

- **Single Initial Reviewer** — Provides consistent baseline for calibration set
- **Expertise** — Initial reviewer has domain knowledge and understanding of benchmark requirements
- **Scalability** — Additional reviewers can be added as needed for validation

### Implementation Details

- **Initial Reviewer:** Chris Wynn
- **Future Expansion:** Additional reviewers (3+ total) will be added for inter-rater reliability validation
- **Calibration Set:** Minimum 50 questions per specifications

### Notes

- This decision identifies the initial reviewer for calibration set creation
- Additional reviewers will be added to achieve 3+ human reviewers for inter-rater reliability measurement

---

## Multi-Turn Testing Inclusion

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 5.3 Multi-Turn Testing - Benchmark Content

### Decision

**Multi-turn testing:** **Included in V1** (essential for chatbot and AI counseling categories)

### Rationale

- **Essential for V1** — Multi-turn testing is critical for evaluating conversational AI capabilities
- **Category Requirements** — Chatbot and AI counseling categories require multi-turn conversation evaluation
- **Comprehensive Assessment** — Provides assessment of model behavior across conversation turns
- **Methodology Alignment** — Aligns with Phase 5 in the testing methodology

### Implementation Details

- **Included in V1** — Multi-turn testing framework will be built and included in initial release
- **Conversation Scripts** — 5-10 multi-turn conversation scripts will be designed
- **Measurement** — "Turn-to-break" measurement methodology will be defined
- **Misalignment Markers** — Misalignment markers will be defined for evaluation

### Notes

- Multi-turn testing is not optional for V1; it is essential for comprehensive benchmark coverage
- Framework will support evaluation of conversational AI models across multiple interaction turns

---

## Sample Questions Publication Strategy

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 5.4 Sample Questions - Benchmark Content

### Decision

**Sample questions publication strategy:**
- **How many:** Do not publish exact questions. Publish similar questions (20 or under) to give a sample of the different kinds of questions.
- **Which categories:** Mostly task questions, with one or two worldview and theological questions.

### Rationale

- **Transparency** — Provides transparency about question types without exposing exact questions
- **Security** — Protects the integrity of the benchmark by not publishing exact questions
- **Representation** — Similar questions demonstrate the variety and nature of questions across categories
- **Balance** — Focus on task questions with limited worldview/theological examples

### Implementation Details

- **Number of Samples:** 20 or under similar questions
- **Category Distribution:**
  - Mostly task questions (Tier 1)
  - One or two worldview questions (Tier 3)
  - One or two theological questions (Tier 2)
- **Format:** Similar but not identical questions to actual benchmark questions

### Notes

- Exact benchmark questions will not be published
- Similar questions will be created to demonstrate question types and categories
- This approach balances transparency with benchmark security

---

## Launch Communication Channels

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 9.2 Launch Activities - Launch Preparation

### Decision

Launch communication will be distributed through multiple strategies coordinated across supporting organizations, separate from ongoing platform communications.

### Overview

The launch announcement is a separate, coordinated effort from the ongoing communication infrastructure (newsletter, Discord, email notifications). It will leverage the networks and communication channels of the supporting organizations to reach the target audience effectively.

### Supporting Organizations

The launch will be coordinated through:

1. **Digital Disciple Makers Network** — Stewarding ministry; will distribute through their network channels
2. **Gospel Ambition** — Technical infrastructure provider; will leverage their communication channels
3. **Visual Story Network** — Media-focused ministry; will support media and content distribution
4. **Other partner organizations** — Additional networks and ministries as identified

### Multi-Strategy Approach

Launch communication will utilize multiple strategies simultaneously:

1. **Organization Networks** — Each supporting organization will distribute the launch announcement through their existing communication channels (newsletters, member networks, social media)
2. **Coordinated Messaging** — Core launch announcement content will be provided, with each organization adapting messaging to their audience while maintaining consistency
3. **Multi-Channel Distribution** — Launch will be announced through:
   - Email newsletters (via supporting organizations' lists)
   - Social media (coordinated posts across organizations)
   - Partner organization websites and blogs
   - Direct outreach to early adopters and launch partners
   - Press releases (if applicable)
   - Community platforms (Discord, etc.)

### Coordination Process

1. **Central Launch Announcement** — Core announcement content prepared by the founding committee
2. **Organization Adaptation** — Each supporting organization adapts messaging for their audience
3. **Coordinated Timing** — Launch announcements synchronized across all channels
4. **Amplification** — Each organization amplifies through their networks

### Relationship to Ongoing Communications

**Launch Communications (One-Time Event):**
- Coordinated multi-organization distribution
- Focused on initial launch announcement
- Leverages partner networks for maximum reach
- Time-bound (launch week/month)

**Ongoing Communications (Section 4.6):**
- Platform-managed (Brevo newsletter, Discord, email notifications)
- Regular updates and community engagement
- User-focused (test completions, submissions, etc.)
- Continuous operation

### Implementation Tasks

1. **[WRITE]** Prepare core launch announcement content
2. **[WRITE]** Create organization-specific messaging templates
3. **[SPEC]** Document coordination process and timeline
4. **[BUILD]** Coordinate launch day communication across organizations

---

## Launch Partners and Early Adopters

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 9.2 Launch Activities - Launch Preparation

### Decision

Launch partners and early adopters have been identified and are managed separately from this project folder.

### Overview

The identification and management of launch partners and early adopters is handled outside of this project repository. A list of identified partners and early adopters has been established and will be involved in the launch process.

### Management Approach

- **Separate Process** — Partner identification and management is handled independently from this project folder
- **List Established** — Partners and early adopters have been identified and documented elsewhere
- **Launch Involvement** — Identified partners and early adopters will be involved in the launch activities
- **Coordination** — Partner engagement will be coordinated as part of the launch communication strategy (see Launch Communication Channels above)

### Relationship to Launch Activities

Launch partners and early adopters will:
- Receive early notification of launch
- Be included in coordinated launch communication
- Potentially provide testimonials or endorsements
- Help amplify launch messaging through their networks
- Serve as initial users/testers of the platform

---

## Launch Date Criteria

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 9.2 Launch Activities - Launch Preparation

### Decision

Launch readiness is determined by meeting all criteria across five categories: Legal & Compliance, Technical Infrastructure, Content & Validation, Operations & Support, and Launch Preparation.

### Overview

The platform is considered "ready" for launch when all criteria in the following categories are met. These criteria ensure the platform is legally compliant, technically functional, validated with real data, operationally supported, and prepared for public launch.

### Category 1: Legal & Compliance ✅

**All items must be complete:**

- [ ] **Legal Documents** — All legal documents completed and reviewed:
  - Terms of Service finalized and published
  - Privacy Policy finalized and published
  - Liability Disclaimers finalized and published
  - Tester Agreement finalized and published
  - Governing law/jurisdiction decision finalized

- [ ] **Accessibility** — WCAG Level A compliance verified:
  - Automated testing completed (WAVE, Lighthouse)
  - Basic screen reader testing completed
  - Keyboard navigation verified
  - Alt text added to all images
  - Form labels properly implemented

### Category 2: Technical Infrastructure ✅

**All items must be complete:**

- [ ] **Platform Deployment** — Platform deployed and tested:
  - Production environment deployed on Railway (or equivalent)
  - Database configured and backed up
  - HTTPS/SSL certificates configured
  - Environment variables configured
  - CI/CD pipeline operational

- [ ] **Core Functionality** — Essential features working:
  - User registration and authentication (Auth0) tested
  - Test execution flow end-to-end tested
  - Results storage and retrieval working
  - Leaderboard display functional
  - User dashboard functional

- [ ] **Payment Processing** — Payment system fully tested:
  - Stripe integration tested end-to-end
  - Payment flow tested (select → pay → run)
  - Refund process tested and verified
  - Webhook handling tested
  - Test failure refund eligibility verified

- [ ] **Monitoring & Alerting** — Observability in place:
  - Monitoring and alerting configured
  - Error tracking operational
  - Performance monitoring active
  - Backup strategy implemented and tested

### Category 3: Content & Validation ✅

**All items must be complete:**

- [ ] **Question Set** — Initial question set created and validated:
  - Full question set created (210 Tier 1, 60 Tier 2, 30 Tier 3)
  - All questions assigned expected verdicts
  - All questions assigned expected refusal types (where applicable)
  - All questions assigned capability/willingness flags
  - All questions assigned metadata (use_case_tags, audience_context, ministry_type)

- [ ] **Judge Prompt Validation** — Judge prompts calibrated and validated:
  - Phase 1 validation completed (calibrate judge prompt with 2-3 models)
  - Inter-rater reliability ≥80% with human review
  - Judge prompt accuracy ≥90% (minimum threshold)
  - All three judge prompts finalized (Tier 1, Tier 2, Tier 3)

- [ ] **Benchmark Validation** — Full benchmark validated:
  - Full benchmark run on 3-5 initial models completed
  - Weighted scoring produces meaningful differentiation
  - Results are reproducible and consistent
  - Scoring formulas verified across all systems

- [ ] **Initial Leaderboard** — Initial models tested:
  - Minimum 3-5 models tested and on leaderboard
  - Results have been human-reviewed (spot-checked)
  - Results demonstrate meaningful differentiation between models

### Category 4: Operations & Support ✅

**All items must be complete:**

- [ ] **Moderation System** — Moderation workflow operational:
  - Moderators trained and ready
  - Moderation interface functional
  - Human review process validated and working
  - Spot-check workflow tested

- [ ] **Communication Systems** — All communication channels working:
  - Email notifications working (SendGrid configured and tested)
  - Newsletter system set up (Brevo configured)
  - Discord community platform set up
  - User notification system tested (test completion, submission status, etc.)

- [ ] **Analytics** — Analytics configured:
  - Umami analytics configured and tracking
  - Key metrics dashboard accessible
  - Event tracking implemented

### Category 5: Launch Preparation ✅

**All items must be complete:**

- [ ] **Launch Communication** — Launch materials prepared:
  - Launch announcement drafted
  - Launch communication channels defined
  - Launch partners/early adopters identified
  - FAQ content created
  - Organization-specific messaging templates prepared (if applicable)

- [ ] **Documentation** — User-facing documentation ready:
  - Platform user guide available
  - Tester quick-start guide available
  - Moderator guide available
  - Methodology documentation published

- [ ] **Pre-Launch Testing** — Final validation completed:
  - End-to-end user journey tested (registration → payment → test → results)
  - Refund process tested with real payment
  - User authentication tested
  - All critical user flows verified

### Launch Readiness Decision Process

1. **Review All Categories** — Founding committee reviews completion status of all criteria
2. **Gap Assessment** — Identify any incomplete items and assess impact
3. **Go/No-Go Decision** — Make launch decision based on:
   - **GO:** All criteria met, or remaining items are non-blocking and can be addressed post-launch
   - **NO-GO:** Critical items incomplete (legal, payment, core functionality, validation)

### Post-Launch Items (Non-Blocking)

The following items can be completed post-launch without blocking launch:
- Advanced analytics features
- Additional documentation
- Enhanced moderation features
- Performance optimizations
- Additional language support

### Launch Readiness Checklist

**Quick Reference — All must be ✅:**

- [ ] Legal documents complete
- [ ] WCAG Level A compliance verified
- [ ] Platform deployed and tested
- [ ] Payment processing tested
- [ ] Initial 3-5 models on leaderboard
- [ ] Moderators trained and ready
- [ ] Email notifications working
- [ ] Analytics configured
- [ ] Backup strategy implemented
- [ ] Judge prompts validated (≥90% accuracy, ≥80% inter-rater reliability)
- [ ] Full benchmark validation completed
- [ ] Launch announcement prepared
- [ ] Launch communication channels defined
- [ ] Launch partners identified

**Decision Authority:** Founding committee makes final launch readiness determination.

---

## On-Call/Support Rotation

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 10.1 Monitoring & Maintenance - Post-Launch & Ongoing

### Decision

**On-call/support rotation:** Project lead will monitor inboxes and error notifications. Sentry is identified as an error monitoring system. Alerts should be programmatically organized for failed attempts to run a module and get a refund. These alerts should notify the same inboxes monitored by the project lead.

### Rationale

- **Centralized Monitoring** — Project lead monitors all critical notifications
- **Error Tracking** — Sentry provides comprehensive error monitoring
- **Automated Alerts** — Programmatic organization of alerts ensures critical issues are not missed
- **Refund Monitoring** — Special attention to failed test runs and refund requests

### Implementation Details

- **Primary Monitor:** Project lead
- **Error Monitoring System:** Sentry
- **Alert Organization:**
  - Failed test run attempts
  - Refund requests
  - System errors
  - Critical infrastructure issues
- **Notification Channels:** Inboxes monitored by project lead

### Notes

- This approach provides centralized monitoring for the initial launch period
- As the platform grows, a more formal on-call rotation may be established
- Sentry will be configured to send alerts to designated inboxes

---

## Multilingual Support Priority

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 10.3 Future Considerations - Post-Launch & Ongoing

### Decision

**Multilingual support priority and timeline:** Built and expected to quickly follow the MVP in English

### Rationale

- **High Priority** — Multilingual support is important for global reach
- **Quick Follow-up** — Will be implemented shortly after English MVP launch
- **Strategic Priority** — Enables broader adoption and accessibility

### Implementation Details

- **Timeline:** Quickly following MVP in English
- **Approach:** Auto-translation for initial implementation
- **Languages:** Spanish, Portuguese, and Korean will be the first languages (see Additional Language Support decision)

### Notes

- Multilingual support is a high priority but follows the English MVP
- Implementation will begin shortly after initial launch

---

## Additional Language Support

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 10.3 Future Considerations - Post-Launch & Ongoing

### Decision

**Additional language support (Spanish, Portuguese, etc.):** **Spanish, Portuguese, and Korean will be the first languages to auto-translate**

### Rationale

- **Strategic Selection** — These languages represent significant user bases
- **Auto-Translation** — Initial implementation will use auto-translation
- **Priority Order** — Spanish, Portuguese, and Korean are the first priority languages

### Implementation Details

- **First Languages:**
  1. Spanish
  2. Portuguese
  3. Korean
- **Method:** Auto-translation (initial implementation)
- **Timeline:** Following English MVP launch

### Notes

- Additional languages may be added based on user demand and resources
- Auto-translation provides initial support; human translation may be added later

---

## WCAG Level AA Upgrade Timeline

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 10.3 Future Considerations - Post-Launch & Ongoing

### Decision

**WCAG Level AA upgrade timeline:** **No expectation for Level AA upgrade. It will be next year or the year after.**

### Rationale

- **Level A First** — Initial launch focuses on WCAG Level A compliance
- **Future Enhancement** — Level AA upgrade is planned but not immediate
- **Timeline Flexibility** — Upgrade expected within 1-2 years after launch

### Implementation Details

- **Current Target:** WCAG Level A (required for launch)
- **Future Target:** WCAG Level AA
- **Timeline:** Next year or the year after (1-2 years post-launch)

### Notes

- Level A compliance is required for launch
- Level AA upgrade is a future enhancement, not a launch requirement
- Timeline provides flexibility for implementation

---

## Volume Discount Pricing Thresholds

**Decision Date:** December 16, 2025  
**Status:** ✅ Finalized  
**Context:** Section 10.3 Future Considerations - Post-Launch & Ongoing

### Decision

**Volume discount pricing thresholds:** **No volume discounting price thresholds. Simple app and math of the pricing.**

### Rationale

- **Simplicity** — Keeps pricing structure straightforward and transparent
- **Consistency** — All users pay the same rate regardless of volume
- **Ease of Implementation** — Simple pricing model reduces complexity
- **Fairness** — Equal pricing for all users

### Implementation Details

- **Pricing Model:** Flat rate per test run ($20 initial cost)
- **No Volume Discounts:** All users pay the same rate
- **Simple Calculation:** Straightforward pricing math

### Notes

- This decision maintains a simple, transparent pricing structure
- No volume-based discounts will be implemented
- Pricing remains consistent for all users

---

*This document will be updated as additional technical decisions are made and finalized.*
