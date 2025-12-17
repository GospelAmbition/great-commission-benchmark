# Great Commission Benchmark - Technical Specification

This is the master technical specification for the Great Commission Benchmark platform. It consolidates requirements from all platform and process documents into a single implementation guide.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Schema](#4-database-schema)
5. [API Specification](#5-api-specification)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Features](#7-features)
8. [Benchmark Execution](#8-benchmark-execution)
9. [Payment System](#9-payment-system)
10. [Moderation System](#10-moderation-system)
11. [Versioning System](#11-versioning-system)
12. [Security](#12-security)
13. [Infrastructure](#13-infrastructure)
14. [Legal & Compliance](#14-legal--compliance)
15. [Success Metrics](#15-success-metrics)
16. [Build Phases](#16-build-phases)

---

## 1. Overview

### 1.1 Purpose

The Great Commission Benchmark platform is a public-facing website that:

- Evaluates LLMs on their ability to support Great Commission Christians
- Publishes benchmark results to interactive leaderboards
- Enables volunteers to run tests against their preferred LLMs
- Creates a self-sustaining, community-funded testing ecosystem
- Provides actionable insights for Christian organizations choosing AI tools

### 1.2 Core Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Christian Organizations** | Quickly identify which LLMs best support their work |
| **Volunteers** | Easily contribute by testing models they care about |
| **Model Developers** | Clear feedback on how to better serve this user segment |
| **Broader Community** | Evidence-based conversation about religious freedom in AI |

### 1.3 Traffic Expectations

| Metric | Expectation |
|--------|-------------|
| **Total submissions** | ~600 anticipated overall |
| **Monthly submissions** | ~2 at typical rate |
| **Concurrent tests** | 1-2 typical, 5-10 peak |
| **Monthly visitors** | 100-2,500+ (growth over time) |

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Public Website (Next.js)                     │
│                    SSR / SSG / React SPA                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Leaderboard│  │Model     │  │Category  │  │Community        │ │
│  │Dashboard │  │Comparison│  │Deep-Dive │  │(Newsletter, etc)│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Next.js API Routes (light tasks)               │ │
│  │      Auth callbacks · Simple queries · Newsletter signup    │ │
│  └─────────────────────────────────────────────────────────────┘ │
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
                              │
                              ▼
                       ┌──────────┐
                       │ Stripe   │
                       │(Payments)│
                       └──────────┘
```

### 2.2 Responsibility Split

#### Next.js (Frontend + Light Backend)

| Responsibility | Description |
|----------------|-------------|
| Page rendering | SSR/SSG for leaderboards, model pages, SEO |
| Auth callbacks | Handle Auth0 redirects |
| Light queries | Simple data fetches for UI |
| Static assets | Serve images, CSS, JS |
| Newsletter signup | Simple form submissions |
| Simple CRUD | Basic data operations |

#### FastAPI (Heavy Backend)

| Responsibility | Description |
|----------------|-------------|
| Benchmark execution | Run the full testing pipeline |
| LLM API calls | Communicate with OpenRouter |
| Heavy computation | Evaluation logic, result processing |
| Database writes | Store results, verdicts, responses |
| Moderation workflows | Handle review queues and escalations |
| Payment processing | Stripe integration for charges |

---

## 3. Technology Stack

### 3.1 Stack Overview

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | React + Next.js + Tailwind CSS | SSR/SSG for SEO; modern DX; popular ecosystem |
| **UI Components** | shadcn/ui | Copy-paste components built on Radix UI + Tailwind; excellent accessibility; full customization; no runtime overhead |
| **API Backend** | Python + FastAPI | Matches existing pipeline code; handles benchmark execution |
| **Hosting** | Railway | Familiar stack, cost bundling with other projects |
| **Authentication** | Auth0 | Industry-standard OAuth, free tier available |
| **Database** | PostgreSQL | Robust and reliable; already in use |
| **LLM Access** | OpenRouter | Single API for 100+ models; pay-per-use |
| **Payments** | Stripe | Industry standard; handles cards and compliance |
| **Email** | SendGrid | User notifications |
| **Analytics** | Umami (self-hosted, off-site) | Privacy-respecting analytics; shared instance on separate server |

### 3.2 Frontend Component Library (shadcn/ui)

**Why shadcn/ui:**
- **Perfect Tailwind integration** — Built specifically for Tailwind CSS workflows
- **Excellent accessibility** — Built on Radix UI primitives (WCAG Level A compatible)
- **Full customization** — Components live in your codebase, fully customizable
- **No runtime overhead** — Copy-paste components, no external dependencies at runtime
- **Ideal for project needs** — Perfect for leaderboards, forms, dashboards, moderation interfaces
- **Growing ecosystem** — Active community and expanding component library

**Component Categories:**
- **Layout:** Card, Separator, Sheet, Dialog, Drawer
- **Forms:** Input, Select, Checkbox, Radio Group, Form (with react-hook-form)
- **Data Display:** Table, Badge, Avatar, Progress, Skeleton
- **Navigation:** Tabs, Dropdown Menu, Navigation Menu, Breadcrumb
- **Feedback:** Alert, Toast, Dialog, Popover, Tooltip
- **Overlay:** Sheet, Dialog, Popover, Tooltip, Hover Card

**Implementation:**
- Components are installed via CLI and copied into your project
- Full TypeScript support
- Fully customizable with Tailwind CSS
- Built on accessible Radix UI primitives
- Zero runtime bundle size impact

**Typography:**
- **Primary Font:** Inter (with fallbacks: "Segoe UI", Roboto, sans-serif)
- Load via `@next/font` for automatic optimization:

```typescript
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

// Apply to <html> or <body> in root layout
<html className={inter.className}>
```

- Configure in `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
}
```

### 3.3 OpenRouter Integration

**Why OpenRouter:**
- Single API for 100+ models
- Pay-per-use pricing (no subscriptions)
- Consistent interface simplifies testing pipeline
- Community can sponsor tests of any available model

**API Format:**
- Built following the **OpenAI API format** (de facto standard)
- Portable to other providers if needed
- Supports direct API integrations as fallback

### 3.3 Umami Analytics Integration

**Configuration:**
- Umami instance hosted on separate server (shared across multiple projects)
- Privacy-respecting analytics (no cookies, GDPR compliant)
- Lightweight tracking script (~2KB)
- No cookie consent banners required

**Setup Requirements:**
1. Add website to Umami dashboard on external server
2. Obtain website ID from Umami dashboard
3. Configure environment variables (see Appendix C)
4. Add Umami script component to Next.js app

**Environment Variables:**
- `NEXT_PUBLIC_UMAMI_SCRIPT_URL` — Full URL to Umami tracking script (e.g., `https://analytics.example.com/script.js`)
- `NEXT_PUBLIC_UMAMI_WEBSITE_ID` — Website ID from Umami dashboard

**Implementation:**
- Add `<UmamiAnalytics />` component to Next.js root layout
- Component conditionally renders based on environment variables
- Works with SSR/SSG without issues

### 3.4 Migration Path

If Railway becomes unsuitable:
- Standard containerized deployment
- Migrate to Render, Fly.io, or other container platforms
- No vendor lock-in on core architecture

---

## 4. Database Schema

### 4.1 Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',  -- 'user', 'moderator', 'admin'
    credentials TEXT,                  -- For moderators: background, expertise
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Models (LLMs available for testing)
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(255) UNIQUE NOT NULL,  -- OpenRouter model ID
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    estimated_cost_per_test DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Question Sets (versioned)
CREATE TABLE question_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semantic_version VARCHAR(10) NOT NULL,  -- '1.0', '1.1', '1.2', '2.0', etc.
    marketing_version VARCHAR(20) NOT NULL, -- 'Version 1', 'Version 2', etc.
    status VARCHAR(20) NOT NULL,            -- 'draft', 'active', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    locked_at TIMESTAMP,
    archived_at TIMESTAMP,
    notes TEXT
);

-- Methodology Versions (tied to question set)
CREATE TABLE methodology_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_set_id UUID REFERENCES question_sets(id),
    judge_prompt TEXT NOT NULL,
    scoring_config JSONB NOT NULL,
    active_from TIMESTAMP NOT NULL,
    active_until TIMESTAMP,
    changelog TEXT
);

-- Questions (linked to question sets)
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_set_id UUID REFERENCES question_sets(id),
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,         -- Use case category (3.1-3.6)
    tier INTEGER NOT NULL,                  -- 1=Task, 2=Doctrinal, 3=Worldview
    subcategory VARCHAR(100),
    expected_verdict VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test Runs
CREATE TABLE test_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    model_id UUID REFERENCES models(id),
    question_set_id UUID REFERENCES question_sets(id),
    methodology_version_id UUID REFERENCES methodology_versions(id),
    status VARCHAR(50) NOT NULL,            -- 'pending', 'running', 'retrying', 'awaiting_admin', 
                                            -- 'admin_completing', 'completed', 'refunded', 'rejected'
    retry_count INTEGER DEFAULT 0,          -- Number of automatic retry attempts (max 3)
    last_error TEXT,                        -- Most recent error message
    checkpoint_question_index INTEGER,      -- Last completed question index for resume
    payment_id VARCHAR(255),                -- Stripe payment ID
    payment_status VARCHAR(50),
    total_cost DECIMAL(10,2),
    trust_tier VARCHAR(50) DEFAULT 'automated',  -- 'automated', 'reviewed', 'validated'
    validation_metrics JSONB,               -- Inter-rater, reproducibility, etc.
    admin_assigned_id UUID REFERENCES users(id),  -- Admin handling completion (if escalated)
    admin_notes TEXT,                       -- Admin notes on manual completion
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Results (individual question responses)
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_run_id UUID REFERENCES test_runs(id),
    question_id UUID REFERENCES questions(id),
    response TEXT NOT NULL,
    verdict VARCHAR(50) NOT NULL,           -- 'ACCEPTED', 'COMPROMISED', 'REFUSED', etc.
    reasoning TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Moderation Logs
CREATE TABLE moderation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_run_id UUID REFERENCES test_runs(id),
    moderator_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,            -- 'verified', 'concerns', 'escalated'
    sample_size INTEGER,
    agreements INTEGER,
    disagreements INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sponsorship Requests
CREATE TABLE sponsorship_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    model_id UUID REFERENCES models(id),
    justification TEXT NOT NULL,
    context TEXT,
    status VARCHAR(50) DEFAULT 'pending',   -- 'pending', 'approved', 'funded', 'completed', 'rejected'
    funded_by UUID REFERENCES users(id),
    funded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Newsletter Subscribers
CREATE TABLE newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP
);

-- Community Submissions (CLI-generated results)
CREATE TABLE community_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    model_name VARCHAR(255) NOT NULL,         -- User-provided model name
    model_url VARCHAR(500),                   -- Optional: Link to publicly hosted model (e.g., Hugging Face)
                                                -- Enables open-source validation: others can download and verify results
    organization VARCHAR(255),                -- Submitting organization
    cli_version VARCHAR(50) NOT NULL,         -- CLI version used
    question_set_version VARCHAR(10) NOT NULL,
    results_package JSONB NOT NULL,           -- Full results from CLI
    overall_score INTEGER,
    tier1_score INTEGER,
    tier2_score INTEGER,
    tier3_score INTEGER,
    status VARCHAR(50) DEFAULT 'pending',     -- 'pending', 'reviewing', 'approved', 'rejected'
    reviewer_id UUID REFERENCES users(id),
    reviewer_notes TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

-- User Notification Preferences
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    test_completion BOOLEAN DEFAULT true,
    publication BOOLEAN DEFAULT true,
    moderation_updates BOOLEAN DEFAULT true,
    newsletter BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 Indexes

```sql
-- Performance indexes
CREATE INDEX idx_test_runs_user ON test_runs(user_id);
CREATE INDEX idx_test_runs_model ON test_runs(model_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_question_set ON test_runs(question_set_id);
CREATE INDEX idx_results_test_run ON results(test_run_id);
CREATE INDEX idx_results_verdict ON results(verdict);
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_tier ON questions(tier);
CREATE INDEX idx_moderation_logs_test_run ON moderation_logs(test_run_id);
CREATE INDEX idx_moderation_logs_moderator ON moderation_logs(moderator_id);
CREATE INDEX idx_community_submissions_user ON community_submissions(user_id);
CREATE INDEX idx_community_submissions_status ON community_submissions(status);
```

---

## 5. API Specification

### 5.1 Public Endpoints (No Auth Required)

```
GET  /api/leaderboard                    # Overall leaderboard
GET  /api/leaderboard/:version           # Leaderboard by version
GET  /api/models                         # List all tested models
GET  /api/models/:id                     # Model details and results
GET  /api/models/:id/history             # Model performance across versions
GET  /api/categories                     # List use case categories
GET  /api/categories/:slug               # Category deep-dive
GET  /api/versions                       # List all benchmark versions
GET  /api/versions/current               # Get current active version
GET  /api/cli/versions                   # CLI version check endpoint (for gcb-runner)
GET  /api/compare                        # Compare multiple models (query params)
POST /api/newsletter/subscribe           # Newsletter signup
```

### 5.2 Authenticated Endpoints (User)

```
GET  /api/user/profile                   # Get user profile
PUT  /api/user/profile                   # Update profile
GET  /api/user/tests                     # User's test history
GET  /api/user/tests/:id                 # Specific test details
GET  /api/user/notifications             # Notification preferences
PUT  /api/user/notifications             # Update preferences

POST /api/tests/estimate                 # Get price estimate for model
POST /api/tests/create                   # Initiate test (creates payment intent)
POST /api/tests/:id/start                # Start test after payment
GET  /api/tests/:id/status               # Check test status

POST /api/sponsorship/request            # Submit sponsorship request
GET  /api/sponsorship/available          # List available requests to fund
POST /api/sponsorship/:id/fund           # Fund a sponsorship request

POST /api/community/submit               # Submit CLI-generated benchmark results
GET  /api/community/submissions          # User's submitted results history
GET  /api/community/submissions/:id      # Specific submission status
```

### 5.3 Moderator Endpoints

```
GET  /api/moderation/queue               # Get review queue
GET  /api/moderation/queue/:id           # Get specific item for review
POST /api/moderation/queue/:id/claim     # Claim a review
POST /api/moderation/queue/:id/submit    # Submit review
GET  /api/moderation/activity            # View own activity log
GET  /api/moderation/stats               # Moderation statistics

GET  /api/moderation/community           # Community submission review queue
POST /api/moderation/community/:id/review # Review community submission
```

### 5.4 Admin Endpoints

```
GET  /api/admin/users                    # List users
PUT  /api/admin/users/:id/role           # Update user role
GET  /api/admin/moderators               # List moderators with activity
GET  /api/admin/tests                    # All tests with filtering
GET  /api/admin/metrics                  # System metrics
POST /api/admin/question-sets            # Create new question set
PUT  /api/admin/question-sets/:id        # Update question set (if draft)
POST /api/admin/question-sets/:id/lock   # Lock question set
```

### 5.5 Webhook Endpoints

```
POST /api/webhooks/stripe                # Stripe payment webhooks
POST /api/webhooks/auth0                 # Auth0 event webhooks
```

---

## 6. Authentication & Authorization

### 6.1 Auth0 Configuration

**Authentication Methods:**
- Email/password
- Google OAuth
- GitHub OAuth (optional)

**User Metadata:**
- `role`: user | moderator | admin
- `tester_agreement_signed`: boolean
- `tester_agreement_date`: timestamp

### 6.2 Role Permissions

| Permission | User | Moderator | Admin |
|------------|------|-----------|-------|
| View leaderboard | ✅ | ✅ | ✅ |
| Run tests | ✅ | ✅ | ✅ |
| View own results | ✅ | ✅ | ✅ |
| Access moderation queue | ❌ | ✅ | ✅ |
| Submit reviews | ❌ | ✅ | ✅ |
| View all activity logs | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Manage question sets | ❌ | ❌ | ✅ |

### 6.3 Tester Registration Flow

1. User signs up via Auth0
2. Presented with Tester Agreement
3. Must accept agreement to access testing features
4. Agreement acceptance recorded in user metadata
5. Questions delivered only via authenticated API (server-side only)

---

## 7. Features

### 7.1 Public Features

#### 7.1.1 Leaderboard

**Display:**
- Overall benchmark scores across all models
- Category-specific leaderboards
- Tier-specific rankings (Task, Doctrinal, Worldview)
- Trust tier badges (Automated, Reviewed, Validated)
- Historical tracking (model changes over time)

**Filtering:**
- By benchmark version (default: current)
- By model type (commercial, open-source)
- By category
- By tier

**Example Display:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏆 Great Commission Benchmark Leaderboard                                   │
│                                                                              │
│  Version: Version 2 (2.0) ▼                Scoring: 70% Task / 20% Doctrine │
│                                                      / 10% Worldview        │
│                                                                              │
│  Rank │ Model              │ Score │ Task │ Doct │ World │ Tested      │Trust│
│  ─────┼────────────────────┼───────┼──────┼──────┼───────┼─────────────┼─────│
│    1  │ Claude 3.5 Sonnet  │ 81/100│  82  │  75  │  77   │ Dec 14, 2025│ ✓✓✓ │
│    2  │ GPT-4o             │ 76/100│  78  │  70  │  72   │ Dec 13, 2025│ ✓✓  │
│    3  │ My Christian LLM*  │ 74/100│  75  │  72  │  70   │ Dec 12, 2025│ ✓   │
│       │ 🔗 huggingface.co/...│      │      │      │       │             │     │
│    4  │ Gemini 1.5 Pro     │ 71/100│  72  │  68  │  65   │ Dec 12, 2025│ ✓   │
└─────────────────────────────────────────────────────────────────────────────┘

* Community Submitted — Model available for download and independent verification
Score calculation: (Task × 0.70) + (Doctrine × 0.20) + (Worldview × 0.10)
Example: Claude = (82 × 0.70) + (75 × 0.20) + (77 × 0.10) = 57.4 + 15.0 + 7.7 = 80.1 ≈ 81
```

**Community Submission Display:**
- Models submitted via CLI show a "Community Submitted" badge
- When a Hugging Face link is provided, it appears as a clickable link below the model name
- The link enables open-source validation: visitors can download the model and independently verify results

#### 7.1.2 Model Comparison

- Side-by-side comparison of 2-4 models
- Breakdown by category and tier
- Response examples (selected excerpts)
- Performance visualization (charts)

#### 7.1.3 Category Deep-Dive

- Detailed results by use case category
- Identify which models excel at specific tasks
- Example responses for each category
- Failure pattern analysis

#### 7.1.4 Documentation Pages

- Methodology explanation
- Scoring framework
- FAQ
- About the benchmark

#### 7.1.5 Developer Resources Page

A dedicated public page supporting Christian organizations developing or fine-tuning their own LLMs.

**Page Content:**

| Section | Description |
|---------|-------------|
| **Overview** | Explanation of how the CLI tool serves LLM developers working on Kingdom projects |
| **CLI Download** | Direct download links for the CLI tool (macOS, Linux, Windows) |
| **Getting Started** | Quick-start guide for running the benchmark locally |
| **Usage Documentation** | Detailed instructions for testing custom/fine-tuned models |
| **Submitting Results** | How to submit benchmark scores for publication on the leaderboard |
| **Best Practices** | Guidance on testing during development, before release, and for publication |

**Key Messaging:**

> "Are you developing or fine-tuning an LLM for Christian ministry work? Use our CLI tool to test your model against the Great Commission Benchmark and ensure it will truly serve the needs of Great Commission Christians."

**Call to Action:**
- Download the CLI
- Test your model locally
- Submit your results to the benchmark
- Publish your model on Hugging Face with your GCB score

**Submission Flow:**
1. User downloads CLI and runs benchmark locally
2. CLI generates a results package (scores + metadata)
3. User creates account on platform (if not existing)
4. User uploads results package via authenticated submission form
   - **Optional: Hugging Face Model Link** — Users can provide a link to their publicly hosted model on Hugging Face
   - This enables open-source validation: community members can download the model and independently verify the submitted results
   - The link is displayed on the leaderboard entry for transparency
5. Results enter moderation queue for validation
6. Upon approval, model appears on leaderboard with "Community Submitted" badge

### 7.2 User Features

#### 7.2.1 Test Execution Flow

```
1. Select Model
   ├── Browse available models (via OpenRouter)
   ├── View estimated cost
   └── See last test date (if retesting)

2. Review Price
   ├── API costs (model-dependent)
   ├── Processing fee
   ├── Optional tip
   └── Total displayed upfront

3. Payment
   ├── Stripe Checkout
   ├── Card payment
   └── Payment confirmation

4. Execution
   ├── Test queued
   ├── Progress updates (WebSocket or polling)
   ├── Automated validation runs
   └── Results published (if validation passes)

5. Notification
   ├── Email: test completed
   ├── Link to results
   └── Thank you message
```

#### 7.2.2 User Dashboard

- Test history with status
- Results access
- Notification preferences
- Account settings

#### 7.2.3 Community Submission Form

**Purpose:** Allow users to submit CLI-generated benchmark results for their own fine-tuned or custom LLMs.

| Field | Required | Description |
|-------|----------|-------------|
| Model name | Yes | User-provided name for the model being tested |
| **Hugging Face Model Link** | No | Optional link to publicly hosted model on Hugging Face. When provided, enables open-source validation: community members can download the model and independently verify the submitted results. The link is displayed on the leaderboard entry for transparency. |
| Organization | No | Submitting organization or ministry name |
| Results package | Yes | JSON file containing complete benchmark results from CLI |
| CLI version | Auto-detected | Version of CLI tool used (extracted from results package) |
| Question set version | Auto-detected | Benchmark version (extracted from results package) |

**Open-Source Validation Benefits:**
- Community members can download the model and run their own tests
- Independent verification increases trust in submitted results
- Promotes transparency and reproducibility
- Encourages open-source model development

#### 7.2.4 Sponsorship Request Form

| Field | Description |
|-------|-------------|
| Model requested | Which model to test |
| Justification | Why it should be tested |
| Context | Ministry/organization/situation |

### 7.3 Moderator Features

#### 7.3.1 Review Queue

**Queue Priority:**
1. Results awaiting first review (oldest first)
2. Results with one review (seeking second opinion)
3. Results flagged with concerns

**Review Interface:**
- View 20 randomly selected verdicts
- For each: question, response, verdict, reasoning
- Mark: Agree / Disagree / Unsure
- Submit: Verified / Concerns
- Add notes

#### 7.3.2 Activity Log

- Reviews completed
- Verdicts given
- Agreement rate with other moderators
- Concerns raised

### 7.4 Admin Features

#### 7.4.1 User Management

- View all users
- Assign/revoke moderator role
- View moderator activity

#### 7.4.2 Question Set Management

- Create new question sets (draft)
- Edit draft question sets
- Lock question sets (make immutable)
- Archive old versions

#### 7.4.3 System Metrics Dashboard

- Test completion rate
- Moderation queue depth
- Financial summary
- Technical health

---

## 8. Benchmark Execution

### 8.1 Testing Tiers

| Tier | Focus | What's Measured | Weight |
|------|-------|-----------------|--------|
| **Tier 1: Task Capability** | Use Cases (§3.1-3.6) | Can the LLM *do the task* when asked? | **70%** |
| **Tier 2: Doctrinal Fidelity** | Theological Minimums (§4.1-4.6) | Does it preserve *theological accuracy*? | **20%** |
| **Tier 3: Worldview Confession** | Worldview Adherence (§5.1-5.6) | Can it *affirm* core Christian truths? | **10%** |

**Why 70/20/10 Weighting:**

The benchmark prioritizes **practical task capability** (Tier 1) because this directly answers the core question users are asking: *"Can I use this LLM for my ministry work?"*

- **Tier 1 (70%)** — The primary value proposition. Users want to know if an LLM can help with missiological research, evangelistic content creation, apologetics, and other practical Great Commission tasks.
- **Tier 2 (20%)** — Important for ensuring theological accuracy in generated content, but secondary to whether the model will complete the task at all.
- **Tier 3 (10%)** — Interesting for completeness but the least practical. Whether an LLM can "affirm" beliefs when asked directly matters less than whether it can help accomplish ministry work.

See [benchmark-scoring.md](./benchmark-scoring.md) for detailed scoring methodology.

### 8.2 Use Case Categories

See [benchmark-categories.md](./benchmark-categories.md) for full definitions of all categories:

| Category | Brief Description |
|----------|-------------------|
| **3.1** | Missiological Research |
| **3.2** | Evangelistic Material Creation |
| **3.3** | Apologetic Purposes |
| **3.4** | Conversational AI Tools |
| **3.5** | Intercessory Prayer Purposes |
| **3.6** | Scripture Processing |

### 8.3 Response Classification

See [benchmark-categories.md](./benchmark-categories.md) for the complete response classification framework.

| Tier | Pass | Partial | Fail |
|------|------|---------|------|
| **Tier 1** (Tasks) | ACCEPTED | COMPROMISED | REFUSED |
| **Tier 2** (Doctrine) | LOYAL | COMPROMISED | DISLOYAL |
| **Tier 3** (Worldview) | AFFIRMED | HEDGED | DENIED |

### 8.4 Execution Pipeline

```
1. Load question set (current active version)
   - Question distribution: 70% Tier 1, 20% Tier 2, 10% Tier 3
   - Example: 300 questions = 210 Tier 1 + 60 Tier 2 + 30 Tier 3
2. For each question:
   a. Send prompt to model via OpenRouter
   b. Capture response and metadata
   c. Run LLM-as-judge evaluation
   d. Record verdict and reasoning
3. Calculate aggregate scores:
   a. Calculate per-tier scores (% passing verdicts)
   b. Apply weighted formula: (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)
   c. Round to nearest integer for display
4. Run automated validation:
   - Inter-rater reliability (≥80%)
   - Reproducibility (≥95%)
   - Differentiation (meaningful variance)
5. If validation passes: publish immediately
6. If validation fails: notify user, hold for review
```

### 8.5 Automated Validation Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Inter-rater reliability** | ≥80% | LLM-judge vs. calibration set with known human verdicts |
| **Reproducibility** | ≥95% | Same model + same questions re-run produces identical verdicts |
| **Differentiation** | Meaningful variance | Results must not cluster (all models 88-92%) |

---

## 9. Payment System

### 9.1 Pricing Structure

**Fixed price commitment** — Users see and pay a set price before execution.

| Component | Description | Variability |
|-----------|-------------|-------------|
| **API Costs** | OpenRouter/LLM token charges | Variable by model |
| **Processing Fee** | Server compute + operations | Fixed per test |
| **Tip (optional)** | Voluntary contribution | User's choice |

### 9.2 Price Display

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  API Cost (OpenRouter)         $12.40
  Processing Fee                 [TBD]
  ─────────────────────────────────────
  Subtotal                      [TBD]
  
  💡 Help with server & hosting (optional)
     ○ $5   ○ $10   ○ $20   ○ $100
  ─────────────────────────────────────
  Total                         $14.90
─────────────────────────────────────────
```

### 9.3 Stripe Integration

**Payment Flow:**
1. User selects model → API calculates price
2. Create Stripe PaymentIntent
3. User completes payment via Stripe Checkout
4. Webhook confirms payment
5. Test execution begins

**Webhook Events:**
- `payment_intent.succeeded` → Start test
- `payment_intent.payment_failed` → Notify user
- `charge.refunded` → Update test status

### 9.4 Test Recovery System

The platform includes robust checkpoint and automatic recovery:

**Checkpoint Mechanism:**
- Progress saved after each question (response, verdict, metadata)
- On failure, system resumes from checkpoint—never re-runs completed questions
- Checkpoints include: question index, responses collected, partial scores

**Automatic Retry (Transparent to User):**
```
Error occurs during test
    ↓
Save checkpoint (current progress)
    ↓
Wait with exponential backoff (30s → 60s → 120s)
    ↓
Resume from checkpoint (attempt 1, 2, or 3)
    ↓
Success? → Continue test
    ↓
Failure after 3 attempts? → Escalate to admin
```

**Admin Escalation Process:**
1. After 3 failed retry attempts, system alerts administrator(s)
2. User is presented with two choices:
   - **Wait for admin completion**: Admin manually runs remaining questions
   - **Request refund now**: Full refund processed immediately
3. If user waits, admin investigates and completes test manually
4. Completed results merge with checkpoint data
5. Test proceeds to normal moderation queue

### 9.5 Refund Policy

| Situation | Refund | Notes |
|-----------|--------|-------|
| Test failed after 3 auto-retries | User choice | Can wait for admin OR request refund |
| Admin unable to complete | Yes | After admin investigation |
| Test stuck in error state | Yes | — |
| User reports issue before completion | Yes | Case-by-case |
| Test completed successfully | No | — |
| User unhappy with results | No | — |

### 9.6 Financial Steward

Payments flow to a stewarding ministry (TBD) that:
- Receives Stripe payments
- Pays infrastructure costs
- Manages accounting
- Provides tax-deductible receipts where applicable

---

## 10. Moderation System

### 10.1 Trust Tiers

| Tier | Label | Requirements |
|------|-------|--------------|
| **Tier 1** | `Automated` | Passed all automated criteria |
| **Tier 2** | `Reviewed` | 1-2 human spot-checks completed |
| **Tier 3** | `Fully Validated` | 3+ human reviewers confirmed |

### 10.2 Review Process

1. **Claim review** — Moderator selects from queue
2. **Examine sample** — Review 20 randomly selected verdicts
3. **Evaluate each:**
   - Read question, response, verdict, reasoning
   - Mark: `Agree` / `Disagree` / `Unsure`
4. **Submit assessment:**
   - `Verified` — Verdicts appear accurate
   - `Concerns` — Significant disagreements
5. **Add notes** — Document patterns or issues

### 10.3 Disagreement Escalation

```
Single moderator flags "Concerns"
    ↓
Second moderator assigned
    ↓
Second also flags "Concerns"?
    ├── No → Result stays with concerns noted
    └── Yes → Escalate to committee
                ↓
         Committee chair makes final decision
```

### 10.4 Activity Logging

| Data Captured | Purpose |
|---------------|---------|
| Reviews completed | Track workload |
| Time to complete | Identify bottlenecks |
| Agreement rate | Calibration between moderators |
| Concerns raised | Pattern detection |

---

## 11. Versioning System

### 11.1 Version Format

```
Benchmark V{major}.{minor}

Semantic versioning: {major}.{minor}
- Major version (1.0 → 2.0): New question set, triggers new marketing version
- Minor version (1.0 → 1.1): Question set updates, same marketing version

Examples:
- 1.0 — Initial release (Version 1)
- 1.1 — Question set updates (Version 1)
- 1.2 — More question set updates (Version 1)
- 2.0 — New question set (Version 2)
```

### 11.2 Question Set Lifecycle

```
Draft → Active → Archived
  │        │          │
Internal  Production  Historical
review    testing     reference
```

### 11.3 Version Triggers

| Trigger | Version Bump | Marketing Version |
|---------|--------------|-------------------|
| Question leak | Major (1.x → 2.0) | Changes (Version 1 → Version 2) |
| Major category changes | Major (1.x → 2.0) | Changes (Version 1 → Version 2) |
| Annual refresh | Major (1.x → 2.0) | Changes (Version 1 → Version 2) |
| Question additions | Minor (1.0 → 1.1) | Stays same (Version 1) |
| Question refinements | Minor (1.0 → 1.1) | Stays same (Version 1) |
| Methodology refinement | Patch (1.1 → 1.1.1) | Stays same (Version 1) |

### 11.4 Leaderboard Display

- **Default view:** Current version results
- **Older versions:** Accessible via filter, not prominent
- **Cross-version warning:** "Version 1 (1.x) and Version 2 (2.x) scores are not directly comparable"

---

## 12. Security

### 12.1 Question Security

**Questions are NOT public:**
- Full question sets are private
- Specific test prompts are private
- Expected responses are private
- Detailed scoring rubrics are private

**Server-side only:**
- Questions never sent to client browser
- Delivered via authenticated API
- Rate limiting prevents bulk extraction
- Audit logging of all access

### 12.2 API Security

| Measure | Implementation |
|---------|----------------|
| **HTTPS only** | All traffic encrypted |
| **Rate limiting** | Prevent abuse |
| **Input validation** | FastAPI automatic validation |
| **SQL injection** | ORM parameterized queries |
| **CORS** | Restrict to known origins |

### 12.3 Payment Security

- **Stripe handles PCI compliance** — No card data on servers
- **Webhook verification** — Validate Stripe signatures
- **Idempotency** — Prevent double charges

### 12.4 Authentication Security

- **Auth0 handles identity** — No password storage
- **JWT tokens** — Short-lived, validated per request
- **Role-based access** — Enforced at API level

---

## 13. Infrastructure

### 13.1 Railway Configuration

**Services:**
1. **next-frontend** — Next.js application
2. **fastapi-backend** — FastAPI application
3. **postgres** — PostgreSQL database

**Environment Configuration:**
- Separate staging and production projects
- Environment variables for secrets
- Automatic deployments from Git

### 13.2 Cost Estimates

| Service | Monthly Cost |
|---------|--------------|
| Railway (hobby plan) | ~$5-20 |
| Database | Included |
| Auth0 | Free tier |
| Domain | ~$1 (amortized) |
| **Total Infrastructure** | **< $20/month** |

| Per-Test Variable | Cost |
|-------------------|------|
| OpenRouter API | $5-50 (model dependent) |
| Compute time | ~$0.10-0.50 |

### 13.3 Backup Strategy

| Tier | Provider | Frequency |
|------|----------|-----------|
| **Primary** | Railway | Automated/daily |
| **Secondary** | Google Cloud Bucket | Occasional/weekly |

**Recovery Objectives:**
- **RPO:** < 24 hours data loss acceptable
- **RTO:** < 4 hours to restore service

### 13.4 Monitoring

| What | Where |
|------|-------|
| Application logs | Railway built-in |
| Error tracking | Sentry (optional) |
| API request logs | FastAPI middleware |
| Moderation activity | Database |

**Alerting:**
- Test failure spikes → Email to admins
- Payment failures → Immediate notification
- Infrastructure issues → Railway notifications

---

## 14. Legal & Compliance

### 14.1 Required Documents (Pre-Launch)

| Document | Status | Priority |
|----------|--------|----------|
| Terms of Service | Not started | Required |
| Privacy Policy | Not started | Required |
| Liability Disclaimers | Not started | Required |
| Tester Agreement | Not started | Required |

### 14.2 Key Disclaimers

> "This benchmark is for **informational purposes only** and does not constitute an endorsement or recommendation of any AI model or service."

> "Results reflect performance on specific test questions at a point in time and may not predict performance on other tasks or future model versions."

### 14.3 Accessibility

**Target:** WCAG Level A compliance

| Requirement | Implementation |
|-------------|----------------|
| Text alternatives | Alt text for images |
| Keyboard navigation | All functions accessible |
| No seizure triggers | No flashing content |
| Page titles | Descriptive titles |
| Link purpose | Clear link text |
| Language | Page language specified |

### 14.4 Internationalization

**Launch:** English only

**Future:** Add major languages based on demand
- Build with i18n framework from start
- Extract strings for translation
- Priority languages: Spanish, Portuguese, French, Chinese

---

## 15. Success Metrics

### 15.1 Quantitative KPIs

| Metric | Description | Target |
|--------|-------------|--------|
| **Models tested** | Unique models on leaderboard | Comprehensive coverage |
| **Monthly visitors** | Unique website visitors | Steady growth |
| **Benchmark runs** | Total completed tests | ~600 lifetime |
| **Review completion** | % results with human review | > 80% |
| **Refund rate** | % tests resulting in refunds | < 5% |

### 15.2 Success Milestones

**Launch (Month 1):**
- [ ] Platform live and functional
- [ ] 5+ models tested
- [ ] First external user completes test

**Early Traction (Month 3):**
- [ ] 15+ models tested
- [ ] 100+ monthly visitors
- [ ] First organization cites benchmark

**Established (Month 6):**
- [ ] 30+ models tested
- [ ] 500+ monthly visitors
- [ ] 10+ organizations aware

**Mature (Year 1):**
- [ ] 50+ models tested
- [ ] 1,000+ monthly visitors
- [ ] Financially sustainable

---

## 16. Build Phases

### Phase A: Foundation

| Task | Description |
|------|-------------|
| A.1 | Database schema — Full PostgreSQL schema |
| A.2 | Auth0 setup — Authentication and role configuration |
| A.3 | Basic FastAPI — Core API structure, database connections |
| A.4 | Railway infrastructure — Services, environment config |

**Deliverables:**
- Working database with migrations
- Auth0 tenant configured
- FastAPI skeleton deployed
- CI/CD pipeline working

### Phase B: Core Backend

| Task | Description |
|------|-------------|
| B.1 | Results API — Leaderboard data endpoints |
| B.2 | Benchmark executor — OpenRouter integration, response collection |
| B.3 | Evaluation pipeline — LLM-as-judge, verdict generation |
| B.4 | Automated validation — Inter-rater, reproducibility, differentiation |

**Deliverables:**
- Can execute benchmark against model
- Results stored in database
- Validation runs automatically
- API returns leaderboard data

### Phase C: Frontend

| Task | Description |
|------|-------------|
| C.1 | Next.js app — Project setup, routing, layouts |
| C.2 | Public pages — Landing, leaderboard, model comparison, categories |
| C.3 | Auth integration — Login, registration, protected routes |
| C.4 | User flows — Test execution, dashboard, settings |
| C.5 | Analytics integration — Umami component setup and configuration |

**Deliverables:**
- Public leaderboard visible
- Users can register and login
- Test execution flow works
- User dashboard functional
- Umami analytics tracking active

### Phase D: Payments & Moderation

| Task | Description |
|------|-------------|
| D.1 | Stripe integration — Payment flow, webhooks |
| D.2 | Price calculation — Estimate based on model |
| D.3 | Moderation UI — Review queue, submission interface |
| D.4 | Email notifications — SendGrid/Resend integration |

**Deliverables:**
- Users can pay for tests
- Moderators can review results
- Email notifications sent
- Refund flow works

### Phase E: Launch Preparation

| Task | Description |
|------|-------------|
| E.1 | Legal documents — ToS, Privacy Policy, Tester Agreement |
| E.2 | WCAG Level A — Accessibility audit and fixes |
| E.3 | Security review — Penetration testing, vulnerability scan |
| E.4 | Performance — Load testing, optimization |
| E.5 | Documentation — User guides, API docs |

**Deliverables:**
- Legal documents published
- Accessibility compliant
- Security validated
- Ready for public launch

---

## Appendix A: Data Flow Diagram

```
User initiates test
        │
        ▼
┌───────────────────┐
│ Price Calculation │──► Display to user
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Stripe Payment    │──► Payment confirmation
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Test Execution    │──► OpenRouter API calls
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ LLM-as-Judge      │──► Verdict generation
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Automated         │──► Inter-rater, reproducibility
│ Validation        │
└───────────────────┘
        │
    Pass/Fail
    ┌───┴───┐
    ▼       ▼
  Pass    Fail
    │       │
    ▼       ▼
Publish  Hold for
to       manual
leaderboard review
    │
    ▼
┌───────────────────┐
│ Email Notification│──► User notified
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ Async Moderation  │──► Trust tier progression
└───────────────────┘
```

---

## Appendix B: API Response Examples

### Leaderboard Response

```json
{
  "semantic_version": "2.0",
  "marketing_version": "Version 2",
  "version_status": "active",
  "results": [
    {
      "rank": 1,
      "model": {
        "id": "claude-3-5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic"
      },
      "score": 81,
      "trust_tier": "validated",
      "tested_at": "2025-12-14T10:30:00Z",
      "breakdown": {
        "task_capability": {
          "score": 82,
          "weight": 70,
          "weighted_contribution": 57.4
        },
        "doctrinal_fidelity": {
          "score": 75,
          "weight": 20,
          "weighted_contribution": 15.0
        },
        "worldview_confession": {
          "score": 77,
          "weight": 10,
          "weighted_contribution": 7.7
        }
      },
      "questions_by_tier": {
        "tier1": 105,
        "tier2": 30,
        "tier3": 15
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45
  }
}
```

### Test Status Response

```json
{
  "test_run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "total_questions": 300,
    "completed": 174,
    "percentage": 58,
    "by_tier": {
      "tier1": { "total": 210, "completed": 124 },
      "tier2": { "total": 60, "completed": 34 },
      "tier3": { "total": 30, "completed": 16 }
    }
  },
  "started_at": "2025-12-14T10:30:00Z",
  "estimated_completion": "2025-12-14T10:45:00Z"
}
```

### CLI Versions Response

**Endpoint:** `GET /api/cli/versions`

**Response:**
```json
{
  "cli": {
    "latest_version": "1.4.0",
    "release_date": "2025-12-20",
    "release_notes_url": "https://greatcommissionbenchmark.ai/releases/1.4.0"
  },
  "benchmark": {
    "latest_semantic_version": "2.1",
    "latest_marketing_version": "Version 2",
    "release_date": "2025-12-15",
    "changelog_url": "https://greatcommissionbenchmark.ai/versions/2.1"
  },
  "api_version": "1.0"
}
```

**Purpose:** Allows CLI runner (`gcb-runner`) to check for updates to both the CLI tool itself and available benchmark versions. Used for non-blocking update notifications.

### Community Submission Request

**Endpoint:** `POST /api/community/submit`

**Request Body:**

```json
{
  "model_name": "My Fine-Tuned Christian LLM",
  "model_url": "https://huggingface.co/username/my-christian-llm",
  "organization": "Example Ministry",
  "cli_version": "1.2.0",
  "question_set_version": "2.0",
  "results_package": {
    "overall_score": 85,
    "tier1_score": 88,
    "tier2_score": 82,
    "tier3_score": 80,
    "responses": [...],
    "metadata": {...}
  }
}
```

**Field Descriptions:**

| Field | Required | Description |
|-------|----------|-------------|
| `model_name` | Yes | User-provided name for the model |
| `model_url` | No | Link to publicly hosted model (typically Hugging Face). Enables open-source validation by allowing others to download and independently verify results |
| `organization` | No | Submitting organization or ministry name |
| `cli_version` | Yes | Version of CLI tool used to generate results |
| `question_set_version` | Yes | Semantic version (e.g., "2.0") |
| `results_package` | Yes | Complete JSON results package from CLI |

**Response:**

```json
{
  "submission_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "message": "Submission received and queued for review",
  "submitted_at": "2025-12-14T10:30:00Z"
}
```

---

## Appendix C: Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/gcb

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=xxx
AUTH0_CLIENT_SECRET=xxx
AUTH0_AUDIENCE=https://api.greatcommissionbenchmark.ai

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# OpenRouter
OPENROUTER_API_KEY=sk-or-xxx

# Email
SENDGRID_API_KEY=SG.xxx
EMAIL_FROM=noreply@greatcommissionbenchmark.ai

# Analytics (Umami - self-hosted, off-site)
NEXT_PUBLIC_UMAMI_SCRIPT_URL=https://analytics.example.com/script.js
NEXT_PUBLIC_UMAMI_WEBSITE_ID=your-website-id-from-umami

# Application
NEXT_PUBLIC_API_URL=https://api.greatcommissionbenchmark.ai
FASTAPI_SECRET_KEY=xxx
ENVIRONMENT=production
```

---

## Appendix D: Umami Analytics Integration

### Component Implementation

Create `components/UmamiAnalytics.tsx`:

```tsx
'use client'

import Script from 'next/script'

export default function UmamiAnalytics() {
  const scriptUrl = process.env.NEXT_PUBLIC_UMAMI_SCRIPT_URL
  const websiteId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID

  // Only render if both environment variables are set
  if (!scriptUrl || !websiteId) {
    return null
  }

  return (
    <Script
      async
      defer
      data-website-id={websiteId}
      src={scriptUrl}
      strategy="afterInteractive"
    />
  )
}
```

### Integration in Next.js App

Add to your root layout (`app/layout.tsx` or `pages/_app.tsx`):

```tsx
import UmamiAnalytics from '@/components/UmamiAnalytics'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <UmamiAnalytics />
      </body>
    </html>
  )
}
```

### Setup Steps

1. **In Umami Dashboard (external server):**
   - Log into your Umami instance
   - Navigate to Settings → Websites
   - Click "Add Website"
   - Enter website domain (e.g., `greatcommissionbenchmark.ai`)
   - Copy the generated Website ID

2. **In Railway/Environment:**
   - Add `NEXT_PUBLIC_UMAMI_SCRIPT_URL` with full script URL
   - Add `NEXT_PUBLIC_UMAMI_WEBSITE_ID` with website ID from step 1

3. **In Next.js App:**
   - Create the `UmamiAnalytics` component (see above)
   - Import and add to root layout
   - Deploy

### Verification

After deployment:
- Visit your website
- Check Umami dashboard for real-time visitor
- Verify page views are being tracked

### Notes

- Component uses `'use client'` directive for Next.js 13+ App Router
- Script loads with `strategy="afterInteractive"` to avoid blocking page load
- Component gracefully handles missing environment variables (returns null)
- No cookie consent required (Umami is privacy-respecting)

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [benchmark-vision.md](./benchmark-vision.md) | What the benchmark tests and why |
| [benchmark-categories.md](./benchmark-categories.md) | Canonical category, doctrine, and verdict definitions |
| [benchmark-scoring.md](./benchmark-scoring.md) | Scoring methodology and tier weighting rationale |
| [platform-deployment-vision.md](./platform-deployment-vision.md) | Product architecture and deployment |
| [platform-technical-architecture.md](./platform-technical-architecture.md) | Stack decisions and infrastructure |
| [platform-testing-methodology.md](./platform-testing-methodology.md) | How tests are executed and scored |
| [platform-versioning.md](./platform-versioning.md) | Benchmark version management |
| [process-publication-model.md](./process-publication-model.md) | Trust tiers and publication criteria |
| [process-moderation-process.md](./process-moderation-process.md) | Moderator selection and workflows |
| [process-pricing-model.md](./process-pricing-model.md) | Payment structure and sustainability |
| [process-question-security.md](./process-question-security.md) | Question protection and versioning |
| [process-success-metrics.md](./process-success-metrics.md) | KPIs and tracking plan |
| [process-legal-requirements.md](./process-legal-requirements.md) | ToS, Privacy, Accessibility |

---

*"Go therefore and make disciples of all nations..."* — Matthew 28:19
