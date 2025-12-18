# Great Commission Benchmark - Platform Build Tasks

> **Last Updated:** December 18, 2025
> **Target:** Full platform build following phased approach
> **Reference Documents:** See `/benchmark/` folder for detailed specifications

---

## How to Use This Document

1. Work through each phase in order (A → B → C → D → E)
2. Complete all tasks in a phase before moving to the next
3. For each task:
   - Read the linked specification documents
   - Implement the feature
   - Verify against the **Success Criteria**
   - Check the box when complete
4. Run phase-end validation before proceeding

---

## Build Progress Summary

| Phase | Name | Status | Tasks | Complete |
|-------|------|--------|-------|----------|
| A | Foundation | ✅ Complete | 23 | 23/23 |
| B | Core Backend | ✅ Complete | 28 | 28/28 |
| C | Frontend | ✅ Complete | 35 | 35/35 |
| D | Payments & Moderation | 🔲 Not Started | 24 | 0/24 |
| E | Launch Preparation | 🔲 Not Started | 18 | 0/18 |
| **Total** | | | **128** | **86/128** |

---

# Phase A: Foundation

**Goal:** Establish the core infrastructure, database, and authentication layer.

**Estimated Duration:** 1-2 weeks

**Prerequisites:** 
- Railway account
- Auth0 account
- PostgreSQL access
- Development environment (Node.js 18+, Python 3.11+)

---

## A.1 Project Setup

### A.1.1 Repository Structure
- [x] **Create monorepo structure**
  
  ```
  gcb-platform/
  ├── backend/          # FastAPI application
  ├── frontend/         # Next.js application
  ├── shared/           # Shared types/utilities
  └── docker-compose.yml
  ```

  **Success Criteria:**
  - [x] Directory structure exists
  - [x] Git initialized with `.gitignore` for Python and Node.js
  - [x] README.md with setup instructions

### A.1.2 Backend Project Initialization
- [x] **Initialize FastAPI project**
  
  **Reference:** `platform-technical-architecture.md` §Backend Responsibilities
  
  ```bash
  cd backend
  python -m venv venv
  pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic python-dotenv
  ```

  **Success Criteria:**
  - [x] `backend/` has `pyproject.toml` or `requirements.txt`
  - [x] FastAPI app runs with `uvicorn main:app --reload`
  - [x] Health endpoint `GET /health` returns `{"status": "ok"}`

### A.1.3 Frontend Project Initialization
- [x] **Initialize Next.js project with shadcn/ui**
  
  **Reference:** `platform-tech-specification.md` §3.2 Frontend Component Library
  
  ```bash
  npx create-next-app@latest frontend --typescript --tailwind --eslint --app
  cd frontend
  npx shadcn-ui@latest init
  ```

  **Success Criteria:**
  - [x] Next.js app runs with `npm run dev`
  - [x] Tailwind CSS working (test with colored div)
  - [x] shadcn/ui Button component added and rendering

### A.1.4 Environment Configuration
- [x] **Create environment files**
  
  **Reference:** `platform-tech-specification.md` Appendix C
  
  Create `.env.example` files for both frontend and backend with all required variables.

  **Success Criteria:**
  - [x] `backend/.env.example` exists with all variables documented
  - [x] `frontend/.env.example` exists with all variables documented
  - [x] `.env` files added to `.gitignore`
  - [x] Local `.env` files created from examples

---

## A.2 Database Setup

### A.2.1 PostgreSQL Database
- [x] **Provision PostgreSQL database**
  
  **Reference:** `platform-tech-specification.md` §4 Database Schema
  
  **Options:**
  - Railway PostgreSQL (recommended)
  - Local Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15`

  **Success Criteria:**
  - [x] Database accessible via connection string
  - [x] Can connect from backend application
  - [x] `DATABASE_URL` environment variable configured

### A.2.2 Database Migrations Setup
- [x] **Configure Alembic for migrations**
  
  ```bash
  cd backend
  alembic init alembic
  ```
  
  Configure `alembic.ini` and `env.py` to use `DATABASE_URL`.

  **Success Criteria:**
  - [x] `alembic/` directory exists
  - [x] `alembic revision --autogenerate` works
  - [x] `alembic upgrade head` runs without error

### A.2.3 Core Tables - Users & Auth
- [x] **Create users table migration**
  
  **Reference:** `platform-tech-specification.md` §4.1 Core Tables
  
  ```sql
  CREATE TABLE users (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      auth0_id VARCHAR(255) UNIQUE NOT NULL,
      email VARCHAR(255) NOT NULL,
      name VARCHAR(255),
      role VARCHAR(50) DEFAULT 'user',
      credentials TEXT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

  **Success Criteria:**
  - [x] Migration file created
  - [x] Migration applies successfully
  - [x] Can INSERT and SELECT from `users` table

### A.2.4 Core Tables - Models
- [x] **Create models table migration**
  
  ```sql
  CREATE TABLE models (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      model_id VARCHAR(255) UNIQUE NOT NULL,
      name VARCHAR(255) NOT NULL,
      provider VARCHAR(255) NOT NULL,
      is_active BOOLEAN DEFAULT true,
      estimated_cost_per_test DECIMAL(10,2),
      created_at TIMESTAMP DEFAULT NOW()
  );
  ```

  **Success Criteria:**
  - [x] Migration applies successfully
  - [x] Can query `models` table

### A.2.5 Core Tables - Question Sets & Questions
- [x] **Create question_sets and questions tables**
  
  **Reference:** `platform-tech-specification.md` §4.1
  
  **Success Criteria:**
  - [x] `question_sets` table created with versioning fields
  - [x] `questions` table created with category, tier, content
  - [x] `methodology_versions` table created
  - [x] Foreign key relationships working

### A.2.6 Core Tables - Test Runs & Results
- [x] **Create test_runs and results tables**
  
  **Reference:** `platform-tech-specification.md` §4.1
  
  **Success Criteria:**
  - [x] `test_runs` table with all status fields
  - [x] `results` table with verdict and reasoning
  - [x] Foreign keys to users, models, question_sets

### A.2.7 Core Tables - Moderation
- [x] **Create moderation_logs table**
  
  **Success Criteria:**
  - [x] `moderation_logs` table created
  - [x] Links to test_runs and users (moderators)

### A.2.8 Core Tables - Community & Notifications
- [x] **Create remaining tables**
  
  - `sponsorship_requests`
  - `newsletter_subscribers`
  - `community_submissions`
  - `notification_preferences`

  **Success Criteria:**
  - [x] All tables from schema created
  - [x] All foreign key constraints working
  - [x] Can run basic CRUD operations

### A.2.9 Database Indexes
- [x] **Create performance indexes**
  
  **Reference:** `platform-tech-specification.md` §4.2 Indexes
  
  **Success Criteria:**
  - [x] All indexes from spec created
  - [x] EXPLAIN shows indexes being used

---

## A.3 Authentication (Auth0)

### A.3.1 Auth0 Tenant Setup
- [x] **Create Auth0 application**
  
  **Reference:** `platform-tech-specification.md` §6 Authentication
  
  1. Create Auth0 tenant
  2. Create "Regular Web Application"
  3. Configure allowed callback URLs
  4. Configure allowed logout URLs
  5. Configure allowed web origins

  **Success Criteria:**
  - [x] Auth0 tenant created
  - [x] Application created with Client ID and Secret
  - [x] Environment variables configured:
    - `AUTH0_DOMAIN`
    - `AUTH0_CLIENT_ID`
    - `AUTH0_CLIENT_SECRET`
    - `AUTH0_AUDIENCE`

### A.3.2 Auth0 Social Connections
- [x] **Enable social login providers**
  
  - Enable Google OAuth
  - Enable GitHub OAuth (optional)

  **Success Criteria:**
  - [x] Google login working in Auth0 Universal Login
  - [x] Test user can sign up via Google

### A.3.3 Auth0 Roles & Permissions
- [x] **Configure RBAC in Auth0**
  
  Create roles:
  - `user` (default)
  - `moderator`
  - `admin`

  **Success Criteria:**
  - [x] Roles created in Auth0 dashboard
  - [x] Test user assigned a role
  - [x] Role appears in JWT token

### A.3.4 Backend JWT Validation
- [x] **Implement JWT validation middleware**
  
  **Reference:** `spec-api-endpoints.md` §Authentication
  
  ```python
  # Use python-jose or authlib for JWT validation
  pip install python-jose[cryptography]
  ```

  **Success Criteria:**
  - [x] Middleware extracts and validates JWT from Authorization header
  - [x] Invalid tokens return 401 Unauthorized
  - [x] Valid tokens pass through with user info
  - [x] Protected endpoint test passes

### A.3.5 Backend Role Authorization
- [x] **Implement role-based authorization**
  
  Create decorators/dependencies:
  - `@require_auth` - Any authenticated user
  - `@require_role("moderator")` - Moderator or admin
  - `@require_role("admin")` - Admin only

  **Success Criteria:**
  - [x] User without required role gets 403 Forbidden
  - [x] User with required role gets access
  - [x] Tests for all three roles pass

### A.3.6 Frontend Auth Integration
- [x] **Integrate Auth0 with Next.js**
  
  ```bash
  npm install @auth0/nextjs-auth0
  ```

  **Success Criteria:**
  - [x] Login button redirects to Auth0
  - [x] Callback handles auth response
  - [x] User session persists
  - [x] Logout clears session
  - [x] Protected pages redirect to login

---

## A.4 Railway Infrastructure

### A.4.1 Railway Project Setup
- [x] **Create Railway project**
  
  **Reference:** `platform-technical-architecture.md` §Infrastructure
  
  1. Create new Railway project
  2. Add PostgreSQL service
  3. Configure environment variables

  **Success Criteria:**
  - [x] Railway project created
  - [x] PostgreSQL provisioned and accessible
  - [x] Connection string available

### A.4.2 Backend Deployment Configuration
- [x] **Configure FastAPI for Railway**
  
  Create `Dockerfile` or `railway.json` for backend.
  
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

  **Success Criteria:**
  - [x] Backend deploys to Railway
  - [x] Health endpoint accessible via Railway URL
  - [x] Environment variables configured in Railway

### A.4.3 Frontend Deployment Configuration
- [x] **Configure Next.js for Railway**
  
  **Success Criteria:**
  - [x] Frontend deploys to Railway
  - [x] Site accessible via Railway URL
  - [x] Environment variables configured

### A.4.4 CI/CD Pipeline
- [x] **Configure automatic deployments**
  
  Connect Railway to GitHub repository.

  **Success Criteria:**
  - [x] Push to `main` triggers deployment
  - [x] Deployment completes without manual intervention
  - [x] Can view deployment logs

---

## Phase A Completion Checklist

Before proceeding to Phase B, verify:

- [x] **Database:** All tables created, migrations working
- [x] **Auth:** Users can sign up, sign in, sign out
- [x] **Backend:** FastAPI running, JWT validation working
- [x] **Frontend:** Next.js running, Auth0 integrated
- [x] **Infrastructure:** Both apps deployed to Railway
- [x] **Integration:** Frontend can call authenticated backend endpoint

**Phase A Sign-off Date:** December 18, 2025

---

# Phase B: Core Backend

**Goal:** Build the benchmark execution engine, results API, and core business logic.

**Estimated Duration:** 2-3 weeks

**Prerequisites:** Phase A complete

---

## B.1 Results API

### B.1.1 SQLAlchemy Models
- [x] **Create SQLAlchemy ORM models**
  
  **Reference:** `platform-tech-specification.md` §4 Database Schema
  
  Create models for all database tables with relationships.

  **Success Criteria:**
  - [x] All tables have corresponding SQLAlchemy models
  - [x] Relationships (ForeignKey, relationship()) defined
  - [x] Models can be used to query database

### B.1.2 Pydantic Schemas
- [x] **Create Pydantic request/response schemas**
  
  **Reference:** `spec-api-endpoints.md` for response formats
  
  **Success Criteria:**
  - [x] Request schemas for all POST/PUT endpoints
  - [x] Response schemas matching API spec
  - [x] Validation working on request bodies

### B.1.3 Public Leaderboard Endpoint
- [x] **Implement `GET /api/public/leaderboard`**
  
  **Reference:** `spec-api-endpoints.md` §1 Public API
  
  Query parameters: version, category, tier, provider, trust_tier, limit, offset, sort, order

  **Success Criteria:**
  - [x] Returns leaderboard data matching spec format
  - [x] Filtering works for all parameters
  - [x] Sorting works (score, date, tier scores)
  - [x] Pagination working with correct total count
  - [x] Response time < 500ms

### B.1.4 Public Models Endpoints
- [x] **Implement model listing and detail endpoints**
  
  - `GET /api/public/models` - List all tested models
  - `GET /api/public/models/:id` - Model details with results

  **Success Criteria:**
  - [x] Model list returns with pagination
  - [x] Model detail includes test history
  - [x] Category breakdown included
  - [x] Search/filter by provider working

### B.1.5 Public Versions Endpoint
- [x] **Implement `GET /api/public/versions`**
  
  **Success Criteria:**
  - [x] Returns all benchmark versions
  - [x] Current version marked
  - [x] Question counts and tier distribution included

### B.1.6 Public Stats Endpoint
- [x] **Implement `GET /api/public/stats`**
  
  **Success Criteria:**
  - [x] Returns total models tested
  - [x] Returns average score
  - [x] Returns last updated timestamp

### B.1.7 Model Comparison Endpoint
- [x] **Implement `GET /api/public/leaderboard/compare`**
  
  **Reference:** `feature-model-comparison.md`
  
  **Success Criteria:**
  - [x] Accepts array of model IDs (max 5)
  - [x] Returns side-by-side scores
  - [x] Returns category deltas
  - [x] Returns best per category

---

## B.2 User API

### B.2.1 User Profile Endpoints
- [x] **Implement user profile CRUD**
  
  - `GET /api/user/profile`
  - `PUT /api/user/profile`

  **Success Criteria:**
  - [x] Returns authenticated user's profile
  - [x] Can update name and organization
  - [x] Returns user stats (test counts, contributions)

### B.2.2 User Tests Endpoints
- [x] **Implement user test history**
  
  - `GET /api/user/tests` - List user's tests
  - `GET /api/user/tests/:id` - Test detail
  - `GET /api/user/tests/:id/results` - Individual responses

  **Success Criteria:**
  - [x] Only returns authenticated user's tests
  - [x] Filtering by status, model, version works
  - [x] Pagination works
  - [x] Detail view includes all test info

### B.2.3 User Submissions Endpoints
- [x] **Implement CLI submission endpoints**
  
  - `GET /api/user/submissions` - List user's submissions
  - `GET /api/user/submissions/:id` - Submission detail

  **Success Criteria:**
  - [x] Returns user's community submissions
  - [x] Shows submission status and reviewer notes

### B.2.4 User Activity Endpoint
- [x] **Implement `GET /api/user/activity`**
  
  **Success Criteria:**
  - [x] Returns activity feed with types
  - [x] Includes links to related resources
  - [x] Respects limit parameter

### B.2.5 Notification Preferences
- [x] **Implement notification preference endpoints**
  
  - `GET /api/user/notifications`
  - `PUT /api/user/notifications`

  **Success Criteria:**
  - [x] Returns current preferences
  - [x] Can update each preference type
  - [x] Defaults created for new users

---

## B.3 Benchmark Executor

### B.3.1 OpenRouter Integration
- [x] **Create OpenRouter API client**
  
  **Reference:** `platform-technical-architecture.md` §OpenRouter
  
  ```python
  class OpenRouterClient:
      async def complete(self, model: str, messages: list, ...) -> str
      async def list_models(self) -> list
      async def get_model_pricing(self, model: str) -> dict
  ```

  **Success Criteria:**
  - [x] Can send completion request to any model
  - [x] Handles rate limiting gracefully
  - [x] Returns response text and token counts
  - [x] Error handling for API failures

### B.3.2 LLM-as-Judge Implementation
- [x] **Create judge evaluation system**
  
  **Reference:** `benchmark/judge_prompts/` for prompts
  
  Load judge prompts for each tier:
  - `tier1_task.md`
  - `tier2_doctrine.md`
  - `tier3_worldview.md`

  **Success Criteria:**
  - [x] Judge prompts loaded from database/files
  - [x] Evaluation returns verdict and reasoning
  - [x] Handles all verdict types per tier
  - [x] Parses structured judge output

### B.3.3 Question Delivery System
- [x] **Implement question loading and delivery**
  
  Questions must be server-side only (never sent to client).

  **Success Criteria:**
  - [x] Can load questions for a question set version
  - [x] Questions grouped by tier and category
  - [x] Distribution matches 70/20/10 weighting

### B.3.4 Test Execution Pipeline
- [x] **Implement test runner**
  
  **Reference:** `platform-tech-specification.md` §8 Benchmark Execution
  
  ```python
  class BenchmarkExecutor:
      async def execute(self, test_run_id: str) -> TestRun
      async def evaluate_response(self, question, response) -> Verdict
      async def save_checkpoint(self, test_run_id, progress)
  ```

  **Success Criteria:**
  - [x] Executes all questions sequentially
  - [x] Saves each response and verdict
  - [x] Updates progress in database
  - [x] Handles errors gracefully
  - [x] Checkpointing works (can resume)

### B.3.5 Checkpoint & Recovery System
- [x] **Implement test checkpoint and resume**
  
  **Reference:** `platform-tech-specification.md` §9.4 Test Recovery
  
  **Success Criteria:**
  - [x] Progress saved after each question
  - [x] Can resume from checkpoint
  - [x] Never re-runs completed questions
  - [x] Handles 3 retry attempts automatically

### B.3.6 Score Calculation
- [x] **Implement weighted scoring**
  
  **Reference:** `benchmark-scoring.md`
  
  Formula: `(Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)`

  **Success Criteria:**
  - [x] Per-tier scores calculated correctly
  - [x] Weighted overall score calculated
  - [x] Handles partial responses (COMPROMISED/HEDGED)
  - [x] Category scores calculated

### B.3.7 Automated Validation
- [x] **Implement validation checks**
  
  **Reference:** `platform-tech-specification.md` §8.5
  
  - Inter-rater reliability (≥80%)
  - Reproducibility (≥95%)
  - Differentiation (meaningful variance)

  **Success Criteria:**
  - [x] Validation runs after test completion
  - [x] Results include validation metrics
  - [x] Failed validation flags test for review

---

## B.4 Tests API

### B.4.1 Create Test Endpoint
- [x] **Implement `POST /api/tests`**
  
  **Reference:** `spec-api-endpoints.md` §3 Tests API
  
  **Success Criteria:**
  - [x] Creates test run record
  - [x] Returns cost estimate
  - [x] Creates Stripe payment intent (stub for now)
  - [x] Status set to `pending_payment`

### B.4.2 Start Test Endpoint
- [x] **Implement `POST /api/tests/:id/start`**
  
  **Success Criteria:**
  - [x] Verifies payment completed (stub - deferred to Phase D)
  - [x] Updates status to `running`
  - [x] Triggers benchmark execution (async)
  - [x] Returns started_at timestamp

### B.4.3 Test Progress Endpoint
- [x] **Implement `GET /api/tests/:id/progress`**
  
  **Success Criteria:**
  - [x] Returns current progress
  - [x] Includes completed/total questions
  - [x] Shows current tier and category
  - [x] Estimated completion time

### B.4.4 Cancel Test Endpoint
- [x] **Implement `POST /api/tests/:id/cancel`**
  
  **Success Criteria:**
  - [x] Updates status to `cancelled`
  - [x] Returns refund eligibility
  - [x] Stops execution if running

### B.4.5 Retest Endpoints
- [x] **Implement retest functionality**
  
  **Reference:** `feature-retesting.md`
  
  - `POST /api/tests/:id/retest`
  - `GET /api/tests/:id/retest/history`
  - `GET /api/tests/:id/compare`

  **Success Criteria:**
  - [x] Can initiate retest of completed test
  - [x] History shows all retests
  - [x] Comparison calculates deltas

---

## B.5 Submissions API

### B.5.1 CLI Submission Upload
- [x] **Implement `POST /api/submissions`**
  
  **Reference:** `spec-export-schema-validation.md`
  
  **Success Criteria:**
  - [x] Accepts JSON export from CLI
  - [x] Validates against export schema
  - [x] Creates community_submission record
  - [x] Returns submission ID and status
  - [x] Returns validation errors if invalid

### B.5.2 Submission Validation
- [x] **Implement export validation logic**
  
  **Reference:** `spec-export-schema-validation.md` §Validation Rules
  
  Implement all semantic validation:
  - Version consistency
  - Question count consistency
  - Verdict count consistency
  - Score calculation verification
  - Weight sum validation

  **Success Criteria:**
  - [x] All validation rules implemented
  - [x] Returns detailed error messages
  - [x] Valid submissions pass
  - [x] Invalid submissions rejected with reasons

---

## B.6 Questions API (Runner)

### B.6.1 Runner Versions Endpoint
- [x] **Implement `GET /api/runner/versions`**
  
  **Reference:** `spec-questions-api.md`
  
  Requires API key authentication.

  **Success Criteria:**
  - [x] Returns all available versions
  - [x] Indicates current version
  - [x] Includes question counts

### B.6.2 Runner Questions Endpoint
- [x] **Implement `GET /api/runner/questions`**
  
  **Success Criteria:**
  - [x] Returns full question set
  - [x] Includes judge prompts
  - [x] Includes scoring configuration
  - [x] Rate limited appropriately
  - [x] Only accessible with valid API key

### B.6.3 Runner Judge Prompts Endpoint
- [x] **Implement `GET /api/runner/judge-prompts`**
  
  **Success Criteria:**
  - [x] Returns all three tier prompts
  - [x] Version-specific prompts

---

## B.7 Newsletter Endpoint

### B.7.1 Newsletter Signup
- [x] **Implement `POST /api/newsletter/subscribe`**
  
  **Success Criteria:**
  - [x] No auth required
  - [x] Validates email format
  - [x] Creates newsletter_subscriber record
  - [x] Handles duplicate emails gracefully
  - [x] Returns success message

---

## Phase B Completion Checklist

Before proceeding to Phase C, verify:

- [x] **Public API:** Leaderboard, models, versions, stats all working
- [x] **User API:** Profile, tests, submissions, notifications all working
- [x] **Benchmark Executor:** Full test pipeline working end-to-end
- [x] **Scoring:** Weighted scores calculated correctly
- [x] **Submissions:** CLI export validation working
- [x] **Runner API:** Questions and prompts accessible
- [x] **Integration Test:** Can run a complete benchmark test via API

**Phase B Sign-off Date:** December 18, 2025

---

# Phase C: Frontend

**Goal:** Build the complete user interface for public, user, and admin pages.

**Estimated Duration:** 3-4 weeks

**Prerequisites:** Phase B complete

---

## C.1 Design System Setup

### C.1.1 Tailwind Configuration
- [x] **Configure Tailwind with design system**
  
  **Reference:** `wireframes-design-system.md`
  
  ```javascript
  // tailwind.config.js
  module.exports = {
    theme: {
      extend: {
        colors: {
          'ga-red': '#a11824',
          'ga-dark-red': '#7a1219',
          'ga-light-red': '#e84545',
          'ga-accent-red': '#fee9e8',
          // ... rest from design system
        }
      }
    }
  }
  ```

  **Success Criteria:**
  - [x] All brand colors available as Tailwind classes
  - [x] Typography scale configured
  - [x] Spacing scale configured

### C.1.2 shadcn/ui Components
- [x] **Install required shadcn/ui components**
  
  ```bash
  npx shadcn-ui@latest add button card table badge tabs dialog sheet form input select checkbox radio-group progress alert toast dropdown-menu navigation-menu avatar skeleton separator
  ```

  **Success Criteria:**
  - [x] All listed components installed
  - [x] Components render with correct styling
  - [x] Components accessible (keyboard, screen reader)

### C.1.3 Font Configuration
- [x] **Configure Inter font**
  
  **Reference:** `wireframes-design-system.md` §Font Loading
  
  **Success Criteria:**
  - [x] Inter font loading via `next/font`
  - [x] Fallback fonts configured
  - [x] Font applied to entire app

### C.1.4 Layout Components
- [x] **Create global layout components**
  
  - Header with navigation
  - Footer
  - Page container
  - Mobile navigation (hamburger menu)

  **Success Criteria:**
  - [x] Header matches wireframe design
  - [x] Footer matches wireframe design
  - [x] Mobile navigation works
  - [x] Auth state reflected in header

---

## C.2 Public Pages

### C.2.1 Homepage
- [x] **Build homepage**
  
  **Reference:** `wireframes-public-pages.md` §1 Homepage
  
  Sections:
  - Hero with mission statement
  - Top Performers cards (top 3)
  - Quick Rankings table (top 10)
  - Task Capability Leaders
  - The Challenge section
  - CTA to run test

  **Success Criteria:**
  - [x] Hero section with clear value proposition
  - [x] Top 3 models displayed with scores
  - [x] Quick rankings table loads from API
  - [x] Responsive design (mobile/tablet/desktop)
  - [x] Links work (Research, Run Test, etc.)

### C.2.2 Research - Leaderboard Page
- [x] **Build full leaderboard page**
  
  **Reference:** `wireframes-public-pages.md` §2a Research Landing
  **Reference:** `feature-leaderboard.md`
  
  Features:
  - Filter panel (version, category, tier, provider, trust)
  - Data table with sorting
  - Multi-select for comparison
  - Pagination

  **Success Criteria:**
  - [x] Filters work and update results
  - [x] Sorting by clicking column headers
  - [x] Can select models for comparison
  - [x] Pagination shows correct counts
  - [x] Performance: loads in < 2s

### C.2.3 Research - Model Detail Page
- [x] **Build model detail page**
  
  **Reference:** `wireframes-public-pages.md` §2c Model Detail
  
  Features:
  - Score overview
  - Category breakdown with charts
  - Version history chart
  - Recent test runs table

  **Success Criteria:**
  - [x] Displays model info and scores
  - [x] Category bar chart working (Chart.js)
  - [x] Version history line chart working
  - [x] Recent tests listed
  - [x] Compare and Run Test buttons work

### C.2.4 Research - Model Comparison Page
- [x] **Build comparison page**
  
  **Reference:** `wireframes-public-pages.md` §2b Model Comparison
  
  Features:
  - Model selector dropdowns
  - Side-by-side scores
  - Radar chart comparison
  - Category breakdown table

  **Success Criteria:**
  - [x] Can select 2-3 models
  - [x] Scores display side-by-side
  - [x] Radar chart renders (Chart.js)
  - [x] Difference indicators shown
  - [x] Share link works

### C.2.5 Research - Category Page
- [x] **Build category results page**
  
  **Reference:** `wireframes-public-pages.md` §2d Category Results
  
  **Success Criteria:**
  - [x] Category description displayed
  - [x] Top performers for category
  - [x] All models ranked for category
  - [x] Subcategory breakdown (if applicable)

### C.2.6 Contribute Page
- [x] **Build contribute/community page**
  
  **Reference:** `wireframes-public-pages.md` §3 Contribute Page
  
  Sections:
  - Run Benchmark Tests
  - Submit Fine-Tuned Model
  - Contribute to Development
  - Support the Project
  - Join the Community

  **Success Criteria:**
  - [x] All sections rendered
  - [x] CTAs link to appropriate pages/flows
  - [x] GitHub and Discord links work

### C.2.7 About/Methodology Page
- [x] **Build about page**
  
  **Reference:** `wireframes-public-pages.md` §4 About/Methodology
  
  Features:
  - Sticky table of contents
  - FAQ accordions
  - Contact information

  **Success Criteria:**
  - [x] TOC navigation works
  - [x] FAQ accordions expand/collapse
  - [x] Contact email displayed

### C.2.8 Public Profile Page
- [x] **Build public user profile page**
  
  **Reference:** `wireframes-public-pages.md` §5 Public Profile
  
  **Success Criteria:**
  - [x] Shows username and member since
  - [x] Test contributions table
  - [x] Models tested list
  - [x] Activity heatmap (optional)

---

## C.3 Chart.js Integration

### C.3.1 Chart.js Setup
- [x] **Install and configure Chart.js**
  
  ```bash
  npm install chart.js react-chartjs-2
  ```

  **Success Criteria:**
  - [x] Chart.js installed
  - [x] Basic chart renders in test component

### C.3.2 Leaderboard Charts
- [x] **Build leaderboard visualization components**
  
  **Reference:** `feature-leaderboard.md` §UI/UX Design
  
  - Top Performers horizontal bar chart
  - Tier Breakdown grouped bar chart
  - Category Performance heatmap
  - Verdict Distribution stacked bar chart

  **Success Criteria:**
  - [x] All four chart types render
  - [x] Charts responsive
  - [x] Tooltips show on hover
  - [x] Click interactions work

### C.3.3 Model Detail Charts
- [x] **Build model detail charts**
  
  - Category scores bar chart
  - Radar chart for category distribution
  - Version history line chart

  **Success Criteria:**
  - [x] Charts render with real data
  - [x] Charts update when data changes

---

## C.4 User Dashboard

### C.4.1 Dashboard Overview
- [x] **Build user dashboard**
  
  **Reference:** `wireframes-user-pages.md`
  **Reference:** `feature-user-dashboard.md`
  
  Features:
  - Summary stat cards
  - Test history table
  - Community submissions table
  - Activity feed

  **Success Criteria:**
  - [x] Stats cards show correct counts
  - [x] Test history loads from API
  - [x] Submissions section works
  - [x] Activity feed displays events

### C.4.2 Test Detail Page
- [x] **Build test run detail page**
  
  Features:
  - Score breakdown
  - Category scores
  - Verdict distribution chart
  - Progress timeline (for running tests)
  - Actions (retest, download, share)

  **Success Criteria:**
  - [x] All test info displayed
  - [x] Charts render correctly
  - [x] Actions work
  - [x] Running tests show progress

### C.4.3 Test Results Browser
- [x] **Build individual results browser**
  
  Features:
  - Paginated list of question/response pairs
  - Filter by verdict
  - Filter by tier/category
  - Expand to see full response and reasoning

  **Success Criteria:**
  - [x] Results load with pagination
  - [x] Filters work
  - [x] Expand/collapse works
  - [x] Large responses handled well

### C.4.4 Account Settings Page
- [x] **Build account settings page**
  
  Features:
  - Profile editing
  - Notification preferences
  - Connected accounts (Auth0)

  **Success Criteria:**
  - [x] Can update profile
  - [x] Can update notification preferences
  - [x] Changes persist

---

## C.5 Test Execution Flow

### C.5.1 Model Selection Page
- [x] **Build model selection step**
  
  **Reference:** `wireframes-test-flow.md`
  
  Features:
  - Model search/browse
  - Model info display
  - Cost estimate
  - System prompt option

  **Success Criteria:**
  - [x] Can search models
  - [x] Model details displayed
  - [x] Cost estimate shown
  - [x] Can proceed to payment

### C.5.2 Payment Page
- [x] **Build payment step (stub)**
  
  Stripe integration comes in Phase D. For now, create the UI with a stub.

  **Success Criteria:**
  - [x] Price breakdown displayed
  - [x] Optional tip selector
  - [x] Payment button (stub for now)
  - [x] Progress indicator shows step 2

### C.5.3 Processing Page
- [x] **Build test processing page**
  
  Features:
  - Progress bar
  - Current question indicator
  - Estimated time remaining
  - Real-time updates

  **Success Criteria:**
  - [x] Progress updates in real-time
  - [x] Shows current tier/category
  - [x] Estimated completion shown
  - [x] Can navigate away and return

### C.5.4 Results Page
- [x] **Build results ready page**
  
  Features:
  - Score announcement
  - Tier breakdown
  - Quick stats
  - Links to detailed view

  **Success Criteria:**
  - [x] Score prominently displayed
  - [x] Tier scores shown
  - [x] Links to full results work
  - [x] Share functionality works

---

## C.6 Moderator Pages

### C.6.1 Moderator Dashboard
- [x] **Build moderator dashboard**
  
  **Reference:** `wireframes-moderator-pages.md`
  **Reference:** `feature-moderator-dashboard.md`
  
  Features:
  - Queue summary cards
  - Moderation queue table
  - Personal activity stats

  **Success Criteria:**
  - [x] Summary shows pending counts
  - [x] Queue loads with correct items
  - [x] Activity stats display

### C.6.2 Review Interface
- [x] **Build verdict review interface**
  
  Features:
  - Question display
  - Model response display
  - Judge verdict and reasoning
  - Agree/Disagree/Unsure buttons
  - Navigation (prev/next)
  - Overall assessment form

  **Success Criteria:**
  - [x] 20 verdicts load for review
  - [x] Can mark each verdict
  - [x] Navigation works
  - [x] Can submit assessment
  - [x] Progress saves automatically

### C.6.3 Review History Page
- [x] **Build moderator activity history**
  
  **Success Criteria:**
  - [x] Shows past reviews
  - [x] Includes outcome and duration
  - [x] Filterable by date

---

## C.7 Admin Pages

### C.7.1 Admin Dashboard
- [x] **Build admin system stats dashboard**
  
  **Reference:** `wireframes-admin-pages.md`
  
  Features:
  - User stats
  - Test stats
  - Revenue stats
  - Moderation stats

  **Success Criteria:**
  - [x] All stat cards display
  - [x] Data loads from API
  - [x] Charts render if included

### C.7.2 User Management Page
- [x] **Build user management page**
  
  Features:
  - User list with search
  - Role assignment
  - User details modal

  **Success Criteria:**
  - [x] Users list loads
  - [x] Can search users
  - [x] Can change user role
  - [x] Changes persist

### C.7.3 Question Management Page
- [x] **Build question CMS**
  
  **Reference:** `feature-question-management.md`
  
  Features:
  - Question browser with filters
  - Question editor
  - Import (JSON/CSV)
  - Approval workflow

  **Success Criteria:**
  - [x] Questions list with filtering
  - [x] Can edit question
  - [x] Can import questions
  - [x] Approval flow works

### C.7.4 Version Management Page
- [x] **Build version assembly interface**
  
  Features:
  - Version list
  - Question selection for new version
  - Validation feedback
  - Lock/publish actions

  **Success Criteria:**
  - [x] Versions list displays
  - [x] Can create new version draft
  - [x] Can select questions
  - [x] Validation shows tier distribution
  - [x] Can lock and publish

---

## C.8 Analytics Integration

### C.8.1 Umami Analytics
- [x] **Integrate Umami analytics**
  
  **Reference:** `platform-tech-specification.md` Appendix D
  
  Create `UmamiAnalytics` component and add to root layout.

  **Success Criteria:**
  - [x] Component created
  - [x] Environment variables configured
  - [x] Page views tracked in Umami dashboard
  - [x] Component doesn't render if env vars missing

---

## Phase C Completion Checklist

Before proceeding to Phase D, verify:

- [x] **Public Pages:** All public pages rendering correctly
- [x] **Charts:** All Chart.js visualizations working
- [x] **User Dashboard:** Full dashboard functionality
- [x] **Test Flow:** Can navigate through test flow (without payment)
- [x] **Moderator:** Review interface fully functional
- [x] **Admin:** All admin pages working
- [x] **Responsive:** All pages work on mobile/tablet/desktop
- [x] **Accessibility:** Keyboard navigation working throughout

**Phase C Sign-off Date:** December 18, 2025

---

# Phase D: Payments & Moderation

**Goal:** Integrate Stripe payments, complete moderation workflows, and add email notifications.

**Estimated Duration:** 2 weeks

**Prerequisites:** Phase C complete

---

## D.1 Stripe Integration

### D.1.1 Stripe Account Setup
- [ ] **Configure Stripe account**
  
  1. Create Stripe account (or use existing)
  2. Get API keys (test mode first)
  3. Configure webhook endpoint

  **Success Criteria:**
  - [ ] Stripe account active
  - [ ] Test API keys available
  - [ ] Environment variables set:
    - `STRIPE_SECRET_KEY`
    - `STRIPE_PUBLISHABLE_KEY`
    - `STRIPE_WEBHOOK_SECRET`

### D.1.2 Backend Stripe Integration
- [ ] **Install Stripe SDK and create payment service**
  
  ```bash
  pip install stripe
  ```
  
  Create payment service:
  - `create_payment_intent(amount, metadata)`
  - `handle_webhook(payload, signature)`
  - `create_refund(payment_id, amount)`

  **Success Criteria:**
  - [ ] Can create payment intent
  - [ ] Returns client_secret for frontend
  - [ ] Webhook signature verification works

### D.1.3 Payment Intent Endpoint
- [ ] **Implement `POST /api/payments/create-intent`**
  
  **Reference:** `spec-api-endpoints.md` §7 Payments API
  
  **Success Criteria:**
  - [ ] Creates Stripe PaymentIntent
  - [ ] Returns client_secret
  - [ ] Amount calculated correctly

### D.1.4 Stripe Webhook Handler
- [ ] **Implement `POST /api/webhooks/stripe`**
  
  Handle events:
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `charge.refunded`

  **Success Criteria:**
  - [ ] Webhook signature validated
  - [ ] `payment_intent.succeeded` starts test
  - [ ] `payment_intent.payment_failed` updates status
  - [ ] `charge.refunded` updates test status

### D.1.5 Frontend Stripe Integration
- [ ] **Add Stripe Elements to payment page**
  
  ```bash
  npm install @stripe/stripe-js @stripe/react-stripe-js
  ```

  **Success Criteria:**
  - [ ] Card element renders
  - [ ] Payment submission works
  - [ ] Success redirects to processing page
  - [ ] Errors displayed to user

### D.1.6 Refund Endpoint
- [ ] **Implement `POST /api/payments/refund`**
  
  **Success Criteria:**
  - [ ] Creates Stripe refund
  - [ ] Updates test_run status
  - [ ] Returns refund status

### D.1.7 Price Calculation
- [ ] **Implement dynamic pricing**
  
  **Reference:** `platform-tech-specification.md` §9 Payment System
  
  Components:
  - API cost estimate (from OpenRouter)
  - Processing fee (fixed)
  - Optional tip

  **Success Criteria:**
  - [ ] Price varies by model
  - [ ] Breakdown shown to user
  - [ ] Tip options available

---

## D.2 Moderation System

### D.2.1 Moderation Queue Endpoints
- [ ] **Implement `GET /api/moderator/queue`**
  
  **Reference:** `spec-api-endpoints.md` §5 Moderator API
  
  **Success Criteria:**
  - [ ] Returns queue items
  - [ ] Priority sorting works
  - [ ] Status filtering works
  - [ ] Only accessible to moderators

### D.2.2 Queue Item Detail Endpoint
- [ ] **Implement `GET /api/moderator/queue/:id`**
  
  **Success Criteria:**
  - [ ] Returns test run details
  - [ ] Includes 20 random sample verdicts
  - [ ] Shows existing reviews
  - [ ] Creates review session

### D.2.3 Review Submission Endpoint
- [ ] **Implement `POST /api/moderator/reviews`**
  
  **Success Criteria:**
  - [ ] Accepts verdict reviews array
  - [ ] Accepts overall assessment
  - [ ] Updates trust tier
  - [ ] Triggers second opinion if concerns

### D.2.4 Trust Tier System
- [ ] **Implement trust tier progression**
  
  **Reference:** `platform-tech-specification.md` §10 Moderation System
  
  Logic:
  - 0 reviews → `automated`
  - 1-2 reviews → `reviewed`
  - 3+ reviews → `validated`

  **Success Criteria:**
  - [ ] Trust tier updates after review
  - [ ] Concerns trigger second reviewer
  - [ ] Escalation triggers committee notification

### D.2.5 Moderator Activity Endpoint
- [ ] **Implement `GET /api/moderator/activity`**
  
  **Success Criteria:**
  - [ ] Returns review history
  - [ ] Includes duration and outcomes
  - [ ] Filterable by date range

### D.2.6 Moderator Stats Endpoint
- [ ] **Implement `GET /api/moderator/stats`**
  
  **Success Criteria:**
  - [ ] Returns personal stats
  - [ ] Returns system-wide stats
  - [ ] Agreement rate calculated

### D.2.7 Community Submission Review
- [ ] **Implement community submission moderation**
  
  - `GET /api/moderator/community`
  - `POST /api/moderator/community/:id/review`

  **Success Criteria:**
  - [ ] Community submissions in queue
  - [ ] Can approve or reject
  - [ ] Approved submissions appear on leaderboard

---

## D.3 Email Notifications

### D.3.1 Email Service Setup
- [ ] **Configure email service (SendGrid or Resend)**
  
  ```bash
  pip install sendgrid  # or resend
  ```

  **Success Criteria:**
  - [ ] API key configured
  - [ ] Can send test email
  - [ ] From address verified

### D.3.2 Email Templates
- [ ] **Create email templates**
  
  Templates needed:
  - Test completed
  - Test failed (needs attention)
  - Submission approved
  - Submission rejected
  - Payment confirmation
  - Welcome email

  **Success Criteria:**
  - [ ] All templates created
  - [ ] Templates have consistent branding
  - [ ] Dynamic content placeholders work

### D.3.3 Notification Triggers
- [ ] **Implement notification sending**
  
  Trigger points:
  - Test completion → send email
  - Test failure → send email
  - Submission status change → send email

  **Success Criteria:**
  - [ ] Emails sent at correct triggers
  - [ ] Respects user notification preferences
  - [ ] Errors logged but don't break flow

### D.3.4 Newsletter Integration
- [ ] **Implement newsletter subscription**
  
  **Success Criteria:**
  - [ ] Subscribers stored in database
  - [ ] Can export subscriber list
  - [ ] Unsubscribe link works

---

## D.4 Admin Endpoints

### D.4.1 User Management Endpoints
- [ ] **Implement admin user endpoints**
  
  - `GET /api/admin/users`
  - `PUT /api/admin/users/:id/role`

  **Success Criteria:**
  - [ ] Can list all users
  - [ ] Can search users
  - [ ] Can change user role
  - [ ] Only admins can access

### D.4.2 Question Import Endpoint
- [ ] **Implement `POST /api/admin/questions/import`**
  
  **Reference:** `feature-question-management.md`
  
  **Success Criteria:**
  - [ ] Accepts JSON or CSV
  - [ ] Validates format
  - [ ] Reports errors
  - [ ] Dry run option works

### D.4.3 Question CRUD Endpoints
- [ ] **Implement question management endpoints**
  
  - `GET /api/admin/questions`
  - `GET /api/admin/questions/:id`
  - `PUT /api/admin/questions/:id`
  - `DELETE /api/admin/questions/:id`
  - `POST /api/admin/questions/:id/approve`

  **Success Criteria:**
  - [ ] CRUD operations work
  - [ ] Cannot delete locked questions
  - [ ] Approval flow works

### D.4.4 Version Management Endpoints
- [ ] **Implement version management**
  
  - `POST /api/admin/versions`
  - `PUT /api/admin/versions/:version/publish`

  **Success Criteria:**
  - [ ] Can create version draft
  - [ ] Validation checks tier distribution
  - [ ] Lock prevents further edits
  - [ ] Publish makes version active

### D.4.5 Admin Stats Endpoint
- [ ] **Implement `GET /api/admin/stats`**
  
  **Success Criteria:**
  - [ ] Returns user stats
  - [ ] Returns test stats
  - [ ] Returns revenue stats
  - [ ] Returns moderation stats

---

## Phase D Completion Checklist

Before proceeding to Phase E, verify:

- [ ] **Payments:** Full Stripe flow working (test mode)
- [ ] **Moderation:** Complete review workflow functional
- [ ] **Trust Tiers:** Progression working correctly
- [ ] **Email:** Notifications sending
- [ ] **Admin:** All admin endpoints working
- [ ] **Integration:** Full test flow with payment works end-to-end

**Phase D Sign-off Date:** _______________

---

# Phase E: Launch Preparation

**Goal:** Complete legal documents, accessibility audit, security review, and final polish for launch.

**Estimated Duration:** 1-2 weeks

**Prerequisites:** Phase D complete

---

## E.1 Legal Documents

### E.1.1 Terms of Service
- [ ] **Create Terms of Service document**
  
  **Reference:** `process-legal-requirements.md`
  
  Must include:
  - Service description
  - User responsibilities
  - Disclaimers
  - Limitation of liability
  - Governing law

  **Success Criteria:**
  - [ ] Document drafted
  - [ ] Legal review (if applicable)
  - [ ] Published on website at `/terms`

### E.1.2 Privacy Policy
- [ ] **Create Privacy Policy**
  
  Must include:
  - What data we collect
  - How we use data
  - Third-party services (Auth0, Stripe, OpenRouter)
  - Data retention
  - User rights

  **Success Criteria:**
  - [ ] Document drafted
  - [ ] GDPR-compliant language
  - [ ] Published at `/privacy`

### E.1.3 Tester Agreement
- [ ] **Create Tester Agreement**
  
  Presented during first test:
  - Agreement to methodology
  - Result publication consent
  - Question confidentiality

  **Success Criteria:**
  - [ ] Agreement displays before first test
  - [ ] User must accept to proceed
  - [ ] Acceptance recorded in database

### E.1.4 Liability Disclaimers
- [ ] **Add disclaimers throughout site**
  
  Key disclaimer:
  > "This benchmark is for informational purposes only and does not constitute an endorsement or recommendation of any AI model or service."

  **Success Criteria:**
  - [ ] Disclaimer on leaderboard page
  - [ ] Disclaimer in footer
  - [ ] Disclaimer in results display

---

## E.2 Accessibility Audit

### E.2.1 Automated Accessibility Testing
- [ ] **Run automated accessibility tests**
  
  Tools:
  - Lighthouse (Chrome DevTools)
  - axe DevTools
  - WAVE

  **Success Criteria:**
  - [ ] All pages score ≥90 on Lighthouse accessibility
  - [ ] No critical axe violations
  - [ ] Fix all WCAG Level A issues

### E.2.2 Keyboard Navigation
- [ ] **Test and fix keyboard navigation**
  
  **Success Criteria:**
  - [ ] All interactive elements focusable
  - [ ] Tab order logical
  - [ ] Focus indicators visible
  - [ ] Skip links work
  - [ ] No keyboard traps

### E.2.3 Screen Reader Testing
- [ ] **Test with screen reader**
  
  Test with VoiceOver (Mac) or NVDA (Windows).

  **Success Criteria:**
  - [ ] Pages announce correctly
  - [ ] Forms have labels
  - [ ] Images have alt text
  - [ ] Buttons and links descriptive
  - [ ] Status updates announced

### E.2.4 Color Contrast
- [ ] **Verify color contrast ratios**
  
  **Success Criteria:**
  - [ ] All text meets 4.5:1 contrast ratio
  - [ ] Large text meets 3:1 ratio
  - [ ] Interactive elements distinguishable

---

## E.3 Security Review

### E.3.1 Security Headers
- [ ] **Configure security headers**
  
  Headers to add:
  - `Content-Security-Policy`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security`

  **Success Criteria:**
  - [ ] Headers configured in Next.js
  - [ ] Headers configured in FastAPI
  - [ ] SecurityHeaders.com grades A or higher

### E.3.2 Input Validation Audit
- [ ] **Review all input validation**
  
  Check:
  - All API endpoints validate input
  - SQL injection prevented (ORM usage)
  - XSS prevented (React's default escaping)
  - File upload validation (if applicable)

  **Success Criteria:**
  - [ ] All endpoints validated
  - [ ] No obvious injection vulnerabilities
  - [ ] Error messages don't leak info

### E.3.3 Authentication Security
- [ ] **Review auth implementation**
  
  Check:
  - JWT validation on all protected endpoints
  - Role checks enforced
  - Session timeout appropriate
  - CSRF protection (if applicable)

  **Success Criteria:**
  - [ ] Cannot access protected routes without auth
  - [ ] Cannot access admin routes as user
  - [ ] JWT expiration working

### E.3.4 Rate Limiting
- [ ] **Implement rate limiting**
  
  **Reference:** `spec-api-endpoints.md` §Rate Limiting
  
  Limits:
  - Public API: 100 req/min
  - Authenticated: 300 req/min
  - Questions API: 50 req/hour

  **Success Criteria:**
  - [ ] Rate limiting middleware added
  - [ ] Headers returned (X-RateLimit-*)
  - [ ] 429 returned when exceeded

### E.3.5 Secrets Audit
- [ ] **Verify no secrets in code**
  
  **Success Criteria:**
  - [ ] No API keys in codebase
  - [ ] `.env` files in `.gitignore`
  - [ ] No secrets in client-side code

---

## E.4 Performance Optimization

### E.4.1 Frontend Performance
- [ ] **Optimize frontend performance**
  
  Checks:
  - Images optimized (next/image)
  - Code splitting working
  - Bundle size reasonable
  - Lighthouse performance score

  **Success Criteria:**
  - [ ] Lighthouse performance ≥80
  - [ ] First Contentful Paint < 2s
  - [ ] Time to Interactive < 4s

### E.4.2 Backend Performance
- [ ] **Optimize backend performance**
  
  Checks:
  - Database queries optimized
  - N+1 queries eliminated
  - Response times acceptable

  **Success Criteria:**
  - [ ] API responses < 500ms (typical)
  - [ ] Leaderboard loads < 1s
  - [ ] No obvious N+1 queries

### E.4.3 Caching Strategy
- [ ] **Implement caching**
  
  Cache:
  - Leaderboard data (5 min)
  - Model details (5 min)
  - Public stats (5 min)

  **Success Criteria:**
  - [ ] Cache headers set appropriately
  - [ ] Cache invalidation on updates
  - [ ] Performance improved with caching

---

## E.5 Documentation & Polish

### E.5.1 API Documentation
- [ ] **Generate API documentation**
  
  FastAPI auto-generates OpenAPI spec.

  **Success Criteria:**
  - [ ] `/docs` (Swagger UI) accessible
  - [ ] `/redoc` accessible
  - [ ] All endpoints documented
  - [ ] Examples included

### E.5.2 README Updates
- [ ] **Update repository README**
  
  Include:
  - Project overview
  - Setup instructions
  - Development workflow
  - Deployment instructions

  **Success Criteria:**
  - [ ] New developer can set up from README
  - [ ] All commands documented
  - [ ] Links to detailed docs

### E.5.3 Error Pages
- [ ] **Create custom error pages**
  
  - 404 Not Found
  - 500 Server Error
  - Maintenance page

  **Success Criteria:**
  - [ ] Error pages match design system
  - [ ] Helpful messages displayed
  - [ ] Links back to home

### E.5.4 Final UI Polish
- [ ] **Review and polish UI**
  
  Check:
  - Consistent spacing
  - Loading states everywhere
  - Empty states handled
  - Edge cases covered

  **Success Criteria:**
  - [ ] No broken layouts
  - [ ] All loading states in place
  - [ ] Empty states have helpful messages

---

## E.6 Production Deployment

### E.6.1 Production Environment
- [ ] **Configure production environment**
  
  - Set all production environment variables
  - Configure production database
  - Configure production domains

  **Success Criteria:**
  - [ ] Production env vars set in Railway
  - [ ] Production database provisioned
  - [ ] Domain configured and SSL working

### E.6.2 Stripe Live Mode
- [ ] **Switch Stripe to live mode**
  
  **Success Criteria:**
  - [ ] Live API keys configured
  - [ ] Webhook endpoint updated
  - [ ] Test payment works in production

### E.6.3 Monitoring Setup
- [ ] **Configure monitoring**
  
  Options:
  - Railway built-in logs
  - Sentry for error tracking (optional)
  - Umami for analytics

  **Success Criteria:**
  - [ ] Can view application logs
  - [ ] Errors reported (if Sentry configured)
  - [ ] Analytics tracking (if Umami configured)

### E.6.4 Backup Verification
- [ ] **Verify backup strategy**
  
  **Success Criteria:**
  - [ ] Railway automatic backups enabled
  - [ ] Can restore from backup (test)
  - [ ] Secondary backup location configured (optional)

---

## E.7 Launch Checklist

### E.7.1 Pre-Launch Testing
- [ ] **Complete end-to-end testing**
  
  Test flows:
  - [ ] User signup → run test → view results
  - [ ] User submits CLI results → moderation → publish
  - [ ] Moderator reviews test → trust tier updates
  - [ ] Admin manages users and questions

### E.7.2 Soft Launch
- [ ] **Soft launch to limited users**
  
  **Success Criteria:**
  - [ ] 5-10 users complete full flow
  - [ ] No critical bugs found
  - [ ] Performance acceptable under real use

### E.7.3 Public Launch
- [ ] **Public launch**
  
  **Success Criteria:**
  - [ ] Site publicly accessible
  - [ ] Payments working
  - [ ] All features functional
  - [ ] Monitoring in place

---

## Phase E Completion Checklist

Before declaring launch complete, verify:

- [ ] **Legal:** All legal documents published
- [ ] **Accessibility:** WCAG Level A compliant
- [ ] **Security:** No critical vulnerabilities
- [ ] **Performance:** Acceptable load times
- [ ] **Documentation:** README and API docs complete
- [ ] **Production:** All systems running in production
- [ ] **Testing:** End-to-end flows verified
- [ ] **Launch:** Site publicly accessible and functional

**Phase E Sign-off Date:** _______________

**🎉 LAUNCH DATE:** _______________

---

# Post-Launch Tasks

## Ongoing Maintenance

- [ ] Monitor error logs daily for first week
- [ ] Review user feedback
- [ ] Address critical bugs immediately
- [ ] Plan Phase 2 features based on feedback

## First Week Checks

- [ ] Day 1: Monitor for critical issues
- [ ] Day 2: Check payment flows working
- [ ] Day 3: Verify moderation queue processing
- [ ] Day 7: Review analytics and performance

---

# Appendix: Quick Reference

## Key Specification Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Tech Specification | `benchmark/platform-tech-specification.md` | Master technical spec |
| API Endpoints | `benchmark/spec-api-endpoints.md` | Full API reference |
| Design System | `benchmark/wireframes-design-system.md` | UI/UX standards |
| Feature Specs | `benchmark/feature-*.md` | Individual feature details |

## Environment Variables Checklist

### Backend
```
DATABASE_URL=
AUTH0_DOMAIN=
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
AUTH0_AUDIENCE=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
OPENROUTER_API_KEY=
SENDGRID_API_KEY=
```

### Frontend
```
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_AUTH0_DOMAIN=
NEXT_PUBLIC_AUTH0_CLIENT_ID=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_UMAMI_SCRIPT_URL=
NEXT_PUBLIC_UMAMI_WEBSITE_ID=
```

## Command Reference

```bash
# Backend
cd backend
uvicorn main:app --reload  # Development
alembic upgrade head       # Run migrations
pytest                     # Run tests

# Frontend  
cd frontend
npm run dev               # Development
npm run build             # Production build
npm run lint              # Linting
```

---

*This document is a living checklist. Update progress as you complete each task.*
