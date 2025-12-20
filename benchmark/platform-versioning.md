# Core: Versioning

This document defines how benchmark versions are managed, including question set versioning, release cycles, and migration strategies.

---

## Overview

The Great Commission Benchmark uses a **strict versioning system** to ensure:
- All results are comparable within a version
- Changes are tracked and documented
- Older results remain valid and accessible
- Transitions between versions are orderly

---

## Version Components

### What Gets Versioned

| Component | Versioning | Example |
|-----------|------------|---------|
| **Question Sets** | Semantic versioning | 1.0, 1.1, 1.2, 2.0 |
| **Marketing Milestones** | Milestone names | Version 1, Version 2 |
| **Scoring Methodology** | Tied to question set | Changes with question set version |
| **Judge Prompts** | Tied to methodology | Changes with scoring |
| **Platform Code** | Semantic versioning | 1.0.0, 1.1.0, 2.0.0 |

### Version Format

The benchmark uses **two complementary versioning systems**:

1. **Semantic Versioning (Question Set Evolution)**: `1.0`, `1.1`, `1.2`, `2.0`
   - Tracks incremental changes to the question set
   - Used internally for tracking evolution and technical references
   - Format: `{major}.{minor}`
   - Examples:
     - `1.0` — Initial question set release
     - `1.1` — Minor question set updates (additions, refinements)
     - `1.2` — More question set updates
     - `2.0` — Major question set overhaul (new questions)

2. **Milestone Versioning (Marketing)**: `Version 1`, `Version 2`
   - Used for marketing, public communication, and milestone identification
   - Maps to major semantic versions (1.x → Version 1, 2.x → Version 2)
   - Examples:
     - `Version 1` — Maps to question set versions 1.0, 1.1, 1.2, etc.
     - `Version 2` — Maps to question set versions 2.0, 2.1, 2.2, etc.

### Version Mapping

```
Semantic Version → Marketing Version
─────────────────────────────────────
1.0, 1.1, 1.2  → Version 1
2.0, 2.1, 2.2  → Version 2
3.0, 3.1, 3.2  → Version 3
```

---

## Question Set Versioning

### Version Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Draft      │────▶│   Active     │────▶│   Archived   │
│  (editable)  │     │ (immutable)  │     │  (readonly)  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
    Internal            Production           Historical
    review only         testing              reference
```

| State | Description | Duration |
|-------|-------------|----------|
| **Draft** | Under development, can be edited freely | Weeks to months |
| **Active** | Locked, immutable, used for all new tests | ~1 year (typical) |
| **Archived** | Superseded by newer version, results retained | Indefinite |

### Locking Process

1. **Question import** — Questions generated externally are uploaded to Platform via admin UI
2. **Review and approval** — Committee reviews questions in Platform, approves them
3. **Version assembly** — Admin selects approved questions and assembles version in Platform
4. **Final validation** — Platform validates:
   - Tier distribution (70/20/10)
   - Category coverage (minimum per category)
   - **Difficulty distribution (25-40% each level)**
   - **Difficulty-verdict alignment (easy→PASSING, etc.)**
5. **Lock executed** — Version is locked in Platform (questions become immutable)
6. **Publish** — Version is published and becomes available via API
7. **Activation** — New version becomes default ("current") for testing

### What Triggers Version Changes

| Change Type | Version Bump | Marketing Version | Example |
|-------------|--------------|------------------|---------|
| **Question leak** | Major (1.x → 2.0) | Changes (Version 1 → Version 2) | Questions appear in training data |
| **Major category changes** | Major (1.x → 2.0) | Changes (Version 1 → Version 2) | New use cases or doctrines added |
| **Annual refresh** | Major (1.x → 2.0) | Changes (Version 1 → Version 2) | Proactive contamination prevention |
| **Question additions** | Minor (1.0 → 1.1) | Stays same (Version 1) | Adding 10-20 new questions |
| **Question refinements** | Minor (1.0 → 1.1) | Stays same (Version 1) | Improving existing questions |
| **Methodology refinements** | Patch (1.1 → 1.1.1) | Stays same (Version 1) | Judge prompt improvements |
| **Bug fixes** | Patch (1.1 → 1.1.1) | Stays same (Version 1) | Correcting evaluation errors |

---

## Question Management

Questions are managed through the Platform's CMS (Content Management System). The workflow supports external question generation with Platform-based curation and version assembly.

### Question Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Draft     │────▶│    Review    │────▶│   Approved   │────▶│  In Version  │
│  (imported)  │     │  (pending)   │     │  (ready)     │     │  (locked)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
   Upload to         Committee           Available for      Part of locked
   Platform          review              version assembly   version
```

### Question Workflow

1. **External Generation**
   - Questions generated using any tool (manual writing, ChatGPT, Claude, spreadsheets, etc.)
   - Questions prepared in JSON or CSV format

2. **Import to Platform**
   - Admin uploads questions via Platform admin UI
   - Questions enter "draft" status
   - Platform validates format and required fields

3. **Review and Approval**
   - Committee reviews questions in Platform browser/editor
   - Questions can be edited directly in Platform
   - Approved questions move to "approved" status

4. **Version Assembly**
   - Admin selects approved questions for new version
   - Platform validates tier distribution and category coverage
   - Version created in "draft" status

5. **Version Locking**
   - When version is locked, all questions in that version become immutable
   - Questions cannot be deleted if part of a locked version
   - Version moves to "active" or "archived" status

### Question States

| State | Description | Can Edit | Can Delete |
|-------|-------------|----------|------------|
| **Draft** | Newly imported, pending review | Yes | Yes |
| **Review** | Under committee review | Yes | Yes |
| **Approved** | Approved for use in versions | Yes | Yes (if not in locked version) |
| **In Version** | Part of a locked version | No | No |

---

## Methodology Versioning

### Version Changes

Question set versions use semantic versioning:
- **Major version changes** (1.0 → 2.0): New question set, results NOT directly comparable
- **Minor version changes** (1.0 → 1.1): Question set updates, results comparable with noted changes
- **Patch version changes** (1.1 → 1.1.1): Bug fixes, methodology refinements, fully comparable

| Change Type | Version Bump | Impact |
|-------------|--------------|--------|
| New question set | Major (1.0 → 2.0) | Results NOT directly comparable |
| Question additions/refinements | Minor (1.0 → 1.1) | Results comparable with noted changes |
| Judge prompt wording | Patch (1.1 → 1.1.1) | Fully comparable |
| Scoring thresholds | Patch (1.1 → 1.1.1) | Fully comparable |
| Calibration set updates | Patch (1.1 → 1.1.1) | Fully comparable |
| Bug fixes | Patch (1.1 → 1.1.1) | Fully comparable |

### Compatibility Rules

- **Same major version** (1.x) — Results are comparable
- **Different minor versions** (1.0 vs 1.1) — Results are comparable with noted question set changes
- **Different major versions** (1.x vs 2.x) — Results are NOT directly comparable

### Deprecation Policy

When methodology changes:

1. **Announce** — Notify users of upcoming change
2. **Grace period** — 2 weeks for in-progress tests to complete
3. **Activate** — New methodology becomes default
4. **Document** — Changelog records all changes

---

## Version Display

### On Leaderboard

```
┌─────────────────────────────────────────────────────────────────┐
│  🏆 Great Commission Benchmark Leaderboard                      │
│                                                                 │
│  Version: Version 2 (2.0) ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ● Version 2 (2.0) - Current                             │   │
│  │ ○ Version 1 (1.2) - Archived (156 results)              │   │
│  │ ○ Version 1 (1.1) - Archived (89 results)               │   │
│  │ ○ Version 1 (1.0) - Archived (45 results)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Rank │ Model              │ Score │ Tested      │ Trust       │
│  ─────┼────────────────────┼───────┼─────────────┼─────────────│
│    1  │ Claude 3.5 Sonnet  │ 78/100│ Dec 14, 2025│ Validated ✓ │
│    2  │ GPT-4o             │ 72/100│ Dec 13, 2025│ Reviewed ✓  │
└─────────────────────────────────────────────────────────────────┘
```

### On Individual Results

```
┌─────────────────────────────────────────────────────────────────┐
│  Claude 3.5 Sonnet — Benchmark Version 2                        │
│  ────────────────────────────────────────────────────────────   │
│  Question Set: 1.2 (locked Dec 1, 2025)                        │
│  Marketing: Version 2                                           │
│  Tested: Dec 14, 2025                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cross-Version Analysis

### Model Tracking

The system supports tracking a model's performance across versions:

```
Model: Claude 3.5 Sonnet

┌──────────────────────────────────────────────────────────┐
│  Performance History                                      │
│  ─────────────────────────────────────────────────────   │
│  Version 1 (1.0): 71/100 (Mar 2025)                       │
│  Version 1 (1.1): 73/100 (Jun 2025) — question updates    │
│  Version 1 (1.2): 74/100 (Sep 2025) — question updates    │
│  Version 2 (2.0): 78/100 (Dec 2025) — new question set    │
│                                                          │
│  ⚠️ Version 1 (1.x) and Version 2 (2.x) scores are not  │
│     directly comparable                                   │
└──────────────────────────────────────────────────────────┘
```

### Version Comparison Warnings

When comparing across major versions:

> ⚠️ **Different question sets** — Version 1 and Version 2 use different questions. Score changes may reflect question difficulty differences, not model improvements.

---

## Version Migration

### When New Version Launches

1. **Announcement** — 2 weeks before activation
2. **Grace period** — Existing tests complete on current version
3. **Cutover** — New version becomes default
4. **Archive** — Old version moves to archived state

### User Experience

| User Action | During Transition |
|-------------|-------------------|
| Start new test | Uses new version |
| Complete in-progress test | Uses version started with |
| View leaderboard | Defaults to new version |
| View old results | Still accessible via filter |

### No Automatic Retesting

- Results are **not** automatically migrated between versions
- Models must be retested on new versions to appear on current leaderboard
- Old results remain valid for their version

---

## Changelog

### Requirements

Every version change must document:

| Field | Description |
|-------|-------------|
| **Version** | From → To |
| **Date** | When change occurred |
| **Type** | Major (questions) or Minor (methodology) |
| **Summary** | Brief description |
| **Details** | Specific changes made |
| **Impact** | How this affects existing results |

### Example Entry

```markdown
## 1.1 (June 15, 2025) - Version 1

**Type:** Minor (question set updates)

**Summary:** Added 15 new questions and refined judge prompt for Problematic Vocabulary and Difficult Passages categories

**Details:**
- Added 5 new questions to categories 3.6 and 3.7 (Problematic Vocabulary, Difficult Passages)
- Added 10 new questions to category 3.4 (AI Counseling)
- Clarified distinction between COMPROMISED and REFUSED verdicts in judge prompt
- Added explicit handling for passages in different Bible translations
- Updated calibration set with 10 additional edge cases

**Impact:**
- Existing 1.0 results remain valid and comparable
- New tests will use updated question set (1.1)
- Score differences expected to be <2% for most models
- Marketing version remains "Version 1" (no milestone change)
```

---

## Technical Implementation

### Database Schema

```sql
-- Questions (individual question management)
CREATE TABLE questions (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(10) NOT NULL,  -- e.g., '3.2'
    tier INTEGER NOT NULL,           -- 1, 2, or 3
    difficulty VARCHAR(20) NOT NULL, -- 'easy', 'medium', 'hard' (REQUIRED)
    expected_verdict VARCHAR(20),   -- 'ACCEPTED', 'REFUSED', etc.
    expected_refusal_type VARCHAR(50),
    tests_capability BOOLEAN,
    tests_willingness BOOLEAN,
    use_case_tags TEXT[],
    audience_context VARCHAR(50),
    ministry_type VARCHAR(50),
    status VARCHAR(20) NOT NULL,     -- 'draft', 'review', 'approved'
    created_at TIMESTAMP NOT NULL,
    approved_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    notes TEXT,
    
    -- Constraint: difficulty-verdict alignment for easy questions
    CONSTRAINT easy_must_pass CHECK (
        difficulty != 'easy' OR 
        expected_verdict = 'ACCEPTED'
    )
);

-- Index for difficulty-based queries
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_tier_difficulty ON questions(tier, difficulty);

-- Question set versioning
CREATE TABLE question_sets (
    id UUID PRIMARY KEY,
    semantic_version VARCHAR(10) NOT NULL,  -- '1.0', '1.1', '1.2', '2.0', etc.
    marketing_version VARCHAR(20) NOT NULL, -- 'Version 1', 'Version 2', etc.
    status VARCHAR(20) NOT NULL,            -- 'draft', 'active', 'archived'
    created_at TIMESTAMP NOT NULL,
    locked_at TIMESTAMP,
    archived_at TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Junction table: questions in versions
CREATE TABLE question_set_questions (
    question_set_id UUID REFERENCES question_sets(id),
    question_id UUID REFERENCES questions(id),
    PRIMARY KEY (question_set_id, question_id)
);

-- Methodology versioning (tied to question set)
CREATE TABLE methodology_versions (
    id UUID PRIMARY KEY,
    question_set_id UUID REFERENCES question_sets(id),
    judge_prompt TEXT NOT NULL,
    scoring_config JSONB NOT NULL,
    active_from TIMESTAMP NOT NULL,
    active_until TIMESTAMP,
    changelog TEXT
);

-- Results tagged with versions
CREATE TABLE test_runs (
    id UUID PRIMARY KEY,
    question_set_id UUID REFERENCES question_sets(id),
    methodology_version_id UUID REFERENCES methodology_versions(id),
    -- ... other fields
);
```

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/versions` | List all versions with status |
| `GET /api/versions/current` | Get current active version |
| `GET /api/versions/:version/difficulty-stats` | Get difficulty distribution for version |
| `GET /api/results?version=1.2` | Filter results by semantic version |
| `GET /api/results?version=1.2&difficulty=hard` | Filter results by version and difficulty |
| `GET /api/results?marketing_version=Version+2` | Filter results by marketing version |
| `GET /api/model/{id}/history` | Model performance across versions |
| `GET /api/model/{id}/difficulty-breakdown` | Model performance by difficulty |
| `POST /api/admin/questions/import` | Import questions (JSON/CSV) |
| `GET /api/admin/questions` | List/search questions |
| `GET /api/admin/questions?difficulty=hard` | Filter questions by difficulty |
| `PUT /api/admin/questions/:id` | Edit question |
| `POST /api/admin/questions/:id/approve` | Approve question |
| `POST /api/admin/versions` | Create version (select questions) |
| `POST /api/admin/versions/:version/validate-difficulty` | Validate difficulty distribution |
| `PUT /api/admin/versions/:version/publish` | Lock and publish version |

### Difficulty Stats Response Format

```json
GET /api/versions/1.0/difficulty-stats

{
  "version": "1.0",
  "total_questions": 300,
  "difficulty_distribution": {
    "easy": {
      "count": 100,
      "percentage": 33.3,
      "in_range": true,
      "expected_verdict_alignment": {
        "all_passing": true,
        "violations": 0
      }
    },
    "medium": {
      "count": 100,
      "percentage": 33.3,
      "in_range": true,
      "expected_verdict_alignment": {
        "refused_count": 5,
        "refused_percentage": 5.0,
        "under_threshold": true
      }
    },
    "hard": {
      "count": 100,
      "percentage": 33.3,
      "in_range": true,
      "expected_verdict_distribution": {
        "passing": 60,
        "compromised": 15,
        "refused": 25
      }
    }
  },
  "validation_passed": true,
  "validation_errors": []
}
```

---

## Related Documents

- [Question Security](./process-question-security.md) — Question protection and versioning
- [Core Publication Model](./process-publication-model.md) — How results are published
- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment strategy
- [Question Management Feature](./feature-question-management.md) — Platform CMS features
- [Version Release Workflow](./process-version-release-workflow.md) — Step-by-step release process

