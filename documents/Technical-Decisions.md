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

*This document will be updated as additional technical decisions are made and finalized.*
