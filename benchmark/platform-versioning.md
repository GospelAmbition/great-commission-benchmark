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
| **Question Sets** | Major versions | V1, V2, V3 |
| **Scoring Methodology** | Minor versions | V1.0, V1.1, V1.2 |
| **Judge Prompts** | Tied to methodology | Changes with scoring |
| **Platform Code** | Semantic versioning | 1.0.0, 1.1.0, 2.0.0 |

### Version Format

```
Benchmark V{major}.{minor}

Major: Question set version (1, 2, 3...)
Minor: Methodology refinements (0, 1, 2...)

Examples:
- V1.0 — Initial release
- V1.1 — Scoring refinement, same questions
- V2.0 — New question set
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

1. **Final review** — Committee reviews complete question set
2. **Calibration** — Human reviewers validate expected verdicts
3. **Lock date set** — Announcement of transition timeline
4. **Lock executed** — Questions become immutable
5. **Activation** — New version becomes default for testing

### What Triggers a New Major Version

| Trigger | Example |
|---------|---------|
| **Question leak** | Questions appear in training data |
| **Methodology overhaul** | Fundamental scoring changes |
| **Category changes** | New use cases or doctrines added |
| **Annual refresh** | Proactive contamination prevention |
| **Community request** | Significant concerns about question quality |

---

## Methodology Versioning

### Minor Version Changes

Minor versions (V1.0 → V1.1) indicate refinements that don't affect question content:

| Change Type | Impact |
|-------------|--------|
| Judge prompt wording | Improved clarity, same intent |
| Scoring thresholds | Adjusted cutoffs for verdicts |
| Calibration set updates | More accurate baseline |
| Bug fixes | Correcting evaluation errors |

### Compatibility Rules

- **Same major version** — Results are comparable
- **Different minor versions** — Results are comparable with noted methodology
- **Different major versions** — Results are NOT directly comparable

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
│  Version: V2.0 ▼                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ● V2.0 (Current)                                         │   │
│  │ ○ V1.1 (Archived - 47 results)                          │   │
│  │ ○ V1.0 (Archived - 23 results)                          │   │
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
│  Claude 3.5 Sonnet — Benchmark V2.0                             │
│  ────────────────────────────────────────────────────────────   │
│  Question Set: V2 (locked Dec 1, 2025)                          │
│  Methodology: V2.0                                              │
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
│  V1.0: 71/100 (Mar 2025)                                 │
│  V1.1: 73/100 (Jun 2025) — methodology refinement        │
│  V2.0: 78/100 (Dec 2025) — new question set              │
│                                                          │
│  ⚠️ V1.x and V2.0 scores are not directly comparable     │
└──────────────────────────────────────────────────────────┘
```

### Version Comparison Warnings

When comparing across major versions:

> ⚠️ **Different question sets** — V1 and V2 use different questions. Score changes may reflect question difficulty differences, not model improvements.

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
## V1.1 (June 15, 2025)

**Type:** Minor (methodology)

**Summary:** Refined judge prompt for Scripture Processing category

**Details:**
- Clarified distinction between COMPROMISED and REFUSED verdicts
- Added explicit handling for passages in different Bible translations
- Updated calibration set with 10 additional edge cases

**Impact:**
- Existing V1.0 results remain valid
- New tests will use refined scoring
- Score differences expected to be <2% for most models
```

---

## Technical Implementation

### Database Schema

```sql
-- Question set versioning
CREATE TABLE question_sets (
    id UUID PRIMARY KEY,
    version VARCHAR(10) NOT NULL,  -- 'V1', 'V2', etc.
    status VARCHAR(20) NOT NULL,   -- 'draft', 'active', 'archived'
    created_at TIMESTAMP NOT NULL,
    locked_at TIMESTAMP,
    archived_at TIMESTAMP,
    notes TEXT
);

-- Methodology versioning
CREATE TABLE methodology_versions (
    id UUID PRIMARY KEY,
    version VARCHAR(10) NOT NULL,  -- 'V1.0', 'V1.1', etc.
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
| `GET /api/results?version=V2` | Filter results by version |
| `GET /api/model/{id}/history` | Model performance across versions |

---

## Related Documents

- [Question Security](./process-question-security.md) — Question protection and versioning
- [Core Publication Model](./process-publication-model.md) — How results are published
- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment strategy

