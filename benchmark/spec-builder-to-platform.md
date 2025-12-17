# Specification: Builder Exports to Platform

This document specifies how benchmark version exports from the GCB Builder CLI are transferred to and processed by the GCB Platform.

---

## Overview

The Great Commission Benchmark uses a **manual upload workflow** for transferring benchmark versions from the GCB Builder CLI to the Platform. This design prioritizes human verification, security, and simplicity over automated pipelines.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUILDER TO PLATFORM FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                         ┌─────────────────┐           │
│   │                 │     JSON Export         │                 │           │
│   │  GCB Builder   │ ──────────────────────▶ │  User Submits   │           │
│   │   CLI          │     gcb-v2.0.json       │  via Dashboard  │           │
│   │                 │                         │                 │           │
│   └────────┬────────┘                         └────────┬────────┘           │
│            │                                           │                    │
│            │ Generate                                  │ Upload via         │
│            │ & Validate                                │ User Dashboard     │
│            ▼                                           ▼                    │
│   ┌─────────────────┐                         ┌─────────────────┐           │
│   │                 │                         │                 │           │
│   │  Local Review   │                         │    Platform     │           │
│   │  & Verification │                         │   Validation    │           │
│   │                 │                         │                 │           │
│   └─────────────────┘                         └────────┬────────┘           │
│                                                        │                    │
│                                                        │ Pending            │
│                                                        │ Review             │
│                                                        ▼                    │
│                                               ┌─────────────────┐           │
│                                               │   Moderator/    │           │
│                                               │   Admin Review  │           │
│                                               │                 │           │
│                                               └────────┬────────┘           │
│                                                        │                    │
│                                                        │ Approve &          │
│                                                        │ Activate           │
│                                                        ▼                    │
│                                               ┌─────────────────┐           │
│                                               │                 │           │
│                                               │   PostgreSQL    │           │
│                                               │   Database      │           │
│                                               │                 │           │
│                                               └─────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **⚠️ Document Scope:** This specification covers uploading **new benchmark versions (question sets)** from the GCB Builder CLI to the Platform. This is an admin/builder workflow for releasing new test versions.
>
> This is **NOT** the specification for submitting test results. When users run the CLI test and submit their model's responses for moderation, that follows a different flow with stricter validation requirements — results must contain answers to **every question** in the specified version with exact ID matching. See [spec-test-results-submission.md](./spec-test-results-submission.md) for that workflow.

---

## Why Manual Upload?

Per the [Technical Decisions](../documents/Technical-Decisions.md#manual-upload-vs-automated-pipeline), manual upload was chosen over automated pipelines for these reasons:

| Factor | Manual Upload ✓ | Automated Pipeline |
|--------|-----------------|-------------------|
| **Human verification** | Moderator/admin reviews submission | No review step |
| **Security** | No automated credentials needed | API keys required |
| **Complexity** | Simple upload form in user dashboard | CI/CD, webhooks, secrets |
| **Release frequency** | Fits infrequent releases (~yearly) | Overkill for low volume |
| **Audit trail** | Clear who submitted, who approved | Less transparent |

---

## Step-by-Step Workflow

### Phase 1: Builder Generates Export

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 1: EXPORT GENERATION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Version builder runs CLI commands:                                        │
│                                                                             │
│   $ gcb-builder                                                             │
│                                                                             │
│   ╔═════════════════════════════════════════════════════════════════════╗   │
│   ║              Great Commission Benchmark - Builder                   ║   │
│   ╚═════════════════════════════════════════════════════════════════════╝   │
│                                                                             │
│   ? What would you like to do?                                              │
│     ❯ Publish Version                                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   Validating v2.0.0...                                              │   │
│   │     ✓ All 19 categories represented                                 │   │
│   │     ✓ Tier distribution matches (210/60/30)                         │   │
│   │     ✓ All questions have metadata                                   │   │
│   │     ✓ Judge prompts attached                                        │   │
│   │     ✓ Checksum generated: sha256:a1b2c3d4...                        │   │
│   │                                                                     │   │
│   │   ✓ Export created: gcb-v2.0.0.json (48 KB)                         │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What happens:**

1. Builder validates the version (category coverage, tier distribution, metadata)
2. Generates SHA-256 checksum of the question content
3. Creates timestamped, locked JSON export
4. Outputs file to local filesystem

**Output file:** `gcb-v2.0.0.json`

---

### Phase 2: Local Review

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 2: LOCAL REVIEW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Version builder manually reviews export before upload:                    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  File: gcb-v2.0.0.json                                              │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  Review Checklist:                                                  │   │
│   │                                                                     │   │
│   │  ☐ Correct version number (2.0.0)                                   │   │
│   │  ☐ Question count matches expectations (300)                        │   │
│   │  ☐ No sensitive information in metadata                             │   │
│   │  ☐ Checksum recorded for verification                               │   │
│   │  ☐ Changelog prepared for announcement                              │   │
│   │                                                                     │   │
│   │  Optional: Spot-check a few questions for quality                   │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   This human review step catches errors before they reach production.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What the user verifies before submission:**

- Version number is correct
- Question count matches expectations
- No accidental inclusion of test/draft questions
- Export metadata is accurate
- Checksum is recorded for platform verification

---

### Phase 3: Upload to Platform

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 3: USER SUBMISSION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User Dashboard: Submit Model Evaluation                                   │
│   ──────────────────────────────────────────                                │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  My Dashboard > Submit New Evaluation                               │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │                                                             │    │   │
│   │  │          📁 Drop JSON file here or click to browse          │    │   │
│   │  │                                                             │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │  Semantic Version:  [ 2.0          ]                                │   │
│   │  Marketing Version: [ Version 2     ▼]                              │   │
│   │  Release Date:      [ 2026-01-15    ]                               │   │
│   │                                                                     │   │
│   │  Changelog:                                                         │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │ New question set with updated categories...                 │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │  ⓘ Your submission will be reviewed by a moderator before          │   │
│   │    being published to the platform.                                 │   │
│   │                                                                     │   │
│   │                              [ Cancel ]  [ Submit for Review ]      │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   Option B: API Upload (for scripted workflows)                             │
│   ────────────────────────────────────────────                              │
│                                                                             │
│   POST /api/user/versions                                                   │
│   Authorization: Bearer <user_jwt_token>                                    │
│   Content-Type: multipart/form-data                                         │
│                                                                             │
│   {                                                                         │
│     "semantic_version": "2.0",                                              │
│     "marketing_version": "Version 2",                                       │
│     "release_date": "2026-01-15",                                           │
│     "changelog": "New question set...",                                     │
│     "questions_file": <binary>                                              │
│   }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Upload methods:**

| Method | Best For | Requirements |
|--------|----------|--------------|
| **Web Form** | Most uploads | User account, browser |
| **API** | Scripted workflows | User JWT token |

---

### Phase 4: Platform Validation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 4: PLATFORM VALIDATION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Platform performs multi-stage validation:                                 │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   Stage 1: Schema Validation                                        │   │
│   │   ─────────────────────────────                                     │   │
│   │   ✓ Valid JSON structure                                            │   │
│   │   ✓ Required fields present (format_version, questions, etc.)       │   │
│   │   ✓ Field types match schema                                        │   │
│   │   ✓ Enum values valid (tiers, categories, verdicts)                 │   │
│   │                                                                     │   │
│   │   Stage 2: Semantic Validation                                      │   │
│   │   ──────────────────────────────                                    │   │
│   │   ✓ No duplicate question IDs                                       │   │
│   │   ✓ All questions have tier + category                              │   │
│   │   ✓ Expected verdicts set for all questions                         │   │
│   │   ✓ Judge prompts included for all tiers                            │   │
│   │   ✓ Scoring weights sum to 1.0                                      │   │
│   │                                                                     │   │
│   │   Stage 3: Integrity Validation                                     │   │
│   │   ─────────────────────────────                                     │   │
│   │   ✓ Checksum matches calculated value                               │   │
│   │   ✓ Version number not already in use                               │   │
│   │   ✓ Marketing version mapping is valid                              │   │
│   │                                                                     │   │
│   │   Stage 4: Content Validation                                       │   │
│   │   ───────────────────────────                                       │   │
│   │   ✓ Minimum questions per category (8+)                             │   │
│   │   ✓ Tier distribution acceptable (within 5% of target)              │   │
│   │   ✓ No empty question content                                       │   │
│   │   ✓ Metadata coverage acceptable                                    │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Validation Result:                                                        │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────────   │
│   │ ✓ All validations passed                                                │
│   │ Version 2.0 is ready for activation                                     │
│   └──────────────────────────────────────────────────────────────────────   │
│                                                                             │
│   OR                                                                        │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────────   │
│   │ ✗ Validation failed with 2 error(s):                                    │
│   │   • CHECKSUM_MISMATCH: Expected sha256:a1b2..., got sha256:c3d4...      │
│   │   • DUPLICATE_VERSION: Version 2.0 already exists                       │
│   └──────────────────────────────────────────────────────────────────────   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Validation stages:**

| Stage | Purpose | Failure Response |
|-------|---------|------------------|
| **Schema** | Ensure valid JSON structure | 400 Bad Request |
| **Semantic** | Ensure data consistency | 400 Bad Request |
| **Integrity** | Ensure authenticity | 409 Conflict |
| **Content** | Ensure quality standards | 400 Bad Request |

---

### Phase 5: Moderator Review

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 5: MODERATOR REVIEW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Submission appears in moderator queue for review:                         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Moderator Dashboard > Pending Submissions                          │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │ Submission: Version 2.0                                     │    │   │
│   │  │ Submitted by: user@example.com                              │    │   │
│   │  │ Submitted at: 2026-01-10 14:30 UTC                          │    │   │
│   │  │ Status: ● Pending Review                                    │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │  Review Checklist:                                                  │   │
│   │  ☐ Question count verified (300)                                    │   │
│   │  ☐ Tier distribution correct (210/60/30)                            │   │
│   │  ☐ Checksum validates correctly                                     │   │
│   │  ☐ No policy violations in content                                  │   │
│   │                                                                     │   │
│   │  Reviewer Notes:                                                    │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │ (Optional notes for approval/rejection)                     │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │                    [ Request Changes ]  [ Reject ]  [ Approve ]     │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Review Outcomes:                                                          │
│   • Approve → Submission moves to "Approved" status, ready to publish       │
│   • Request Changes → User notified, can resubmit                           │
│   • Reject → Submission rejected with explanation                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 6: Storage & Activation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: STORAGE & ACTIVATION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   After moderator approval, platform stores the version:                    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   PostgreSQL Database                                               │   │
│   │   ───────────────────────                                           │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │ question_sets                                               │   │   │
│   │   ├─────────────────────────────────────────────────────────────┤   │   │
│   │   │ id              │ semantic_version │ marketing │ status     │   │   │
│   │   │─────────────────┼──────────────────┼───────────┼────────────│   │   │
│   │   │ uuid-1          │ 1.0              │ Version 1 │ archived   │   │   │
│   │   │ uuid-2          │ 1.1              │ Version 1 │ archived   │   │   │
│   │   │ uuid-3          │ 2.0              │ Version 2 │ approved   │◀──┘   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │ questions                                                   │   │   │
│   │   ├─────────────────────────────────────────────────────────────┤   │   │
│   │   │ id     │ question_set_id │ content        │ tier │ category │   │   │
│   │   │────────┼─────────────────┼────────────────┼──────┼──────────│   │   │
│   │   │ 1      │ uuid-3          │ Write a gospel │ 1    │ 3.2      │   │   │
│   │   │ 2      │ uuid-3          │ Explain the... │ 2    │ 4.1      │   │   │
│   │   │ ...    │ ...             │ ...            │ ...  │ ...      │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   Version Lifecycle:                                                        │
│                                                                             │
│   ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐│
│   │ PENDING │───▶│ APPROVED│───▶│  ACTIVE  │───▶│ARCHIVED │    │ REJECTED ││
│   │ REVIEW  │    │         │    │(current) │    │         │    │          ││
│   └─────────┘    └─────────┘    └──────────┘    └─────────┘    └──────────┘│
│        │              │              │               │               ▲      │
│    Submitted,    Moderator      Published,      Superseded      Review      │
│    awaiting      approved      used for tests    by newer       denied      │
│    review                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Version states:**

| State | Description | Tests Allowed |
|-------|-------------|---------------|
| **Pending Review** | Submitted, awaiting moderator review | No |
| **Approved** | Reviewed and approved, ready to activate | No |
| **Active** | Current version for new tests | Yes |
| **Archived** | Superseded by newer version | View only |
| **Rejected** | Review denied (can resubmit) | No |

---

## Export File Format

> **Canonical Schema:** See [spec-export-schema-validation.md](./spec-export-schema-validation.md) for the complete JSON Schema definition and validation rules.

### Structure Overview

The export conforms to the Benchmark Version Export Schema (format version `2.0`):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JSON EXPORT FILE STRUCTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   gcb-v2.0.0.json                                                           │
│   ───────────────                                                           │
│                                                                             │
│   {                                                                         │
│     "format_version": "2.0",              ◀── Schema version                │
│     "benchmark_version": "2.0",           ◀── Question set version          │
│     "name": "Version 2",                                                    │
│     "description": "Annual refresh...",                                     │
│     "locked_at": "2026-01-15T00:00:00Z",                                    │
│                                                                             │
│     "questions": [                        ◀── Question array (300 items)    │
│       {                                                                     │
│         "id": 1,                                                            │
│         "content": "Write a gospel presentation for...",                    │
│         "category": "3.2",                                                  │
│         "tier": 1,                                                          │
│         "difficulty": "medium",                                             │
│         "expected_verdict": "ACCEPTED",                                     │
│         "expected_refusal_type": null,                                      │
│         "tests_capability": true,                                           │
│         "tests_willingness": true,                                          │
│         "use_case_tags": ["content_generation", "chatbot"],                 │
│         "audience_context": "secular_western",                              │
│         "ministry_type": "campus_ministry"                                  │
│       },                                                                    │
│       ...                                                                   │
│     ],                                                                      │
│                                                                             │
│     "judge_prompts": {                    ◀── Evaluation prompts            │
│       "tier1_task": "You are evaluating...",                                │
│       "tier2_doctrine": "You are evaluating...",                            │
│       "tier3_worldview": "You are evaluating..."                            │
│     },                                                                      │
│                                                                             │
│     "scoring": {                          ◀── Scoring configuration         │
│       "weights": {                                                          │
│         "tier1": 0.70,                                                      │
│         "tier2": 0.20,                                                      │
│         "tier3": 0.10                                                       │
│       },                                                                    │
│       "formula": "(tier1 * 0.70) + (tier2 * 0.20) + (tier3 * 0.10)",        │
│       "refusal_analysis": { "enabled": true, "types": [...] }               │
│     },                                                                      │
│                                                                             │
│     "metadata": {                         ◀── Summary & integrity           │
│       "total_questions": 300,                                               │
│       "tier_counts": { "tier1": 210, "tier2": 60, "tier3": 30 },            │
│       "checksum": "sha256:a1b2c3d4e5f6..."                                  │
│     }                                                                       │
│   }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Fields Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format_version` | string | ✓ | Schema version for this export format |
| `benchmark_version` | string | ✓ | Semantic version (e.g., "2.0") |
| `name` | string | ✓ | Marketing name (e.g., "Version 2") |
| `locked_at` | ISO 8601 | ✓ | When version was locked in builder |
| `questions` | array | ✓ | Array of question objects |
| `judge_prompts` | object | ✓ | Tier-specific evaluation prompts |
| `scoring` | object | ✓ | Weights and formulas |
| `metadata.checksum` | string | ✓ | SHA-256 hash for integrity |

---

## Checksum Verification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHECKSUM VERIFICATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Purpose: Ensure export hasn't been tampered with during transfer          │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   Builder generates checksum:                                       │   │
│   │   ──────────────────────────────                                    │   │
│   │                                                                     │   │
│   │   # Hash question content only (not metadata)                       │   │
│   │   content = sort(questions, key=id)                                 │   │
│   │   serialized = json.dumps(content, sort_keys=True)                  │   │
│   │   checksum = "sha256:" + sha256(serialized).hexdigest()             │   │
│   │                                                                     │   │
│   │   Result: sha256:a1b2c3d4e5f67890...                                │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   Platform verifies checksum:                                       │   │
│   │   ─────────────────────────────                                     │   │
│   │                                                                     │   │
│   │   # Recalculate using same algorithm                                │   │
│   │   received_checksum = export["metadata"]["checksum"]                │   │
│   │   calculated_checksum = calculate_checksum(export["questions"])     │   │
│   │                                                                     │   │
│   │   if received_checksum != calculated_checksum:                      │   │
│   │       raise ValidationError("CHECKSUM_MISMATCH")                    │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   What checksum catches:                                                    │
│   • File corruption during transfer                                         │
│   • Accidental modification                                                 │
│   • Wrong file uploaded                                                     │
│   • Intentional tampering                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API Specification

### POST /api/user/versions

Submits a new benchmark version for moderator review.

**Authentication:** User JWT required

**Request:**

```http
POST /api/user/versions
Authorization: Bearer <user_jwt_token>
Content-Type: multipart/form-data

------boundary
Content-Disposition: form-data; name="semantic_version"

2.0
------boundary
Content-Disposition: form-data; name="marketing_version"

Version 2
------boundary
Content-Disposition: form-data; name="release_date"

2026-01-15
------boundary
Content-Disposition: form-data; name="changelog"

New question set with updated categories...
------boundary
Content-Disposition: form-data; name="questions_file"; filename="gcb-v2.0.0.json"
Content-Type: application/json

<file contents>
------boundary--
```

**Response (Success):** `201 Created`

```json
{
  "success": true,
  "version": {
    "id": "uuid-xxx",
    "semantic_version": "2.0",
    "marketing_version": "Version 2",
    "status": "pending_review",
    "question_count": 300,
    "tier_distribution": {
      "tier1": 210,
      "tier2": 60,
      "tier3": 30
    },
    "checksum": "sha256:a1b2c3d4...",
    "submitted_at": "2026-01-10T14:30:00Z",
    "submitted_by": "user@example.com"
  },
  "validation": {
    "passed": true,
    "checks": [
      { "name": "schema", "status": "passed" },
      { "name": "semantic", "status": "passed" },
      { "name": "integrity", "status": "passed" },
      { "name": "content", "status": "passed" }
    ]
  },
  "next_steps": [
    "Your submission is queued for moderator review",
    "You will be notified when a decision is made"
  ]
}
```

**Response (Validation Failed):** `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Export validation failed with 2 error(s)",
    "details": {
      "errors": [
        {
          "code": "TIER_DISTRIBUTION",
          "message": "Tier 1 has 180 questions, expected ~210 (70%)",
          "path": "$.questions"
        },
        {
          "code": "MISSING_JUDGE_PROMPT",
          "message": "Judge prompt for tier2 is missing",
          "path": "$.judge_prompts.tier2_doctrine"
        }
      ]
    }
  }
}
```

---

### PUT /api/admin/versions/:version/publish

Activates an approved version, making it the current version for new tests. Only available to admins after moderator approval.

**Authentication:** Admin JWT required

**Request:**

```http
PUT /api/admin/versions/2.0/publish
Authorization: Bearer <admin_jwt_token>
```

**Response:** `200 OK`

```json
{
  "success": true,
  "version": {
    "semantic_version": "2.0",
    "marketing_version": "Version 2",
    "status": "active"
  },
  "previous_version": {
    "semantic_version": "1.2",
    "status": "archived"
  },
  "message": "Version 2.0 is now the current benchmark version"
}
```

---

## Error Handling

### Validation Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_JSON` | File is not valid JSON | Check file format |
| `SCHEMA_ERROR` | Missing required fields | Ensure builder export is complete |
| `CHECKSUM_MISMATCH` | Hash doesn't match | Re-export from builder |
| `DUPLICATE_VERSION` | Version already exists | Use unique version number |
| `TIER_DISTRIBUTION` | Wrong question distribution | Adjust in builder |
| `MISSING_JUDGE_PROMPT` | Judge prompt not included | Re-export with prompts |
| `QUESTION_COUNT` | Too few questions | Add more questions |
| `CATEGORY_COVERAGE` | Missing categories | Ensure all 19 categories |

### Recovery Procedures

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERROR RECOVERY PROCEDURES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Error: CHECKSUM_MISMATCH                                                  │
│   ────────────────────────                                                  │
│   1. Do not re-upload the same file                                         │
│   2. Return to GCB Builder CLI                                              │
│   3. Re-run export command: gcb-builder publish                             │
│   4. Verify checksum in new export                                          │
│   5. Upload fresh export file                                               │
│                                                                             │
│   Error: DUPLICATE_VERSION                                                  │
│   ────────────────────────                                                  │
│   1. Check if version already exists in platform                            │
│   2. If intentional update: Delete draft, re-upload                         │
│   3. If new version: Bump version number in builder                         │
│                                                                             │
│   Error: TIER_DISTRIBUTION                                                  │
│   ────────────────────────                                                  │
│   1. Review target distribution (210/60/30 for 300 questions)               │
│   2. Adjust questions in builder                                            │
│   3. Re-run validation: gcb-builder validate                                │
│   4. Re-export and upload                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY CONSIDERATIONS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Access Control                                                            │
│   ──────────────                                                            │
│   • Authenticated users can submit versions via their dashboard             │
│   • Moderators/admins review all submissions before activation              │
│   • JWT tokens required for API uploads                                     │
│   • Session-based auth for web uploads                                      │
│                                                                             │
│   Data Protection                                                           │
│   ───────────────                                                           │
│   • Questions are never exposed to end users                                │
│   • Export files should be handled securely                                 │
│   • Delete local copies after successful upload                             │
│                                                                             │
│   Integrity                                                                 │
│   ─────────                                                                 │
│   • Checksum verification prevents tampering                                │
│   • Version locking prevents post-submission modification                   │
│   • Audit log records who submitted, who reviewed, and when                 │
│                                                                             │
│   Transfer Security                                                         │
│   ─────────────────                                                         │
│   • HTTPS required for all uploads                                          │
│   • File size limits prevent DoS (max 10MB)                                 │
│   • Rate limiting on upload endpoint                                        │
│                                                                             │
│   Review Process                                                            │
│   ──────────────                                                            │
│   • All submissions require moderator/admin approval                        │
│   • Rejected submissions can be resubmitted after fixes                     │
│   • Only approved versions can be published to active                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COMPLETE END-TO-END WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   GCB BUILDER CLI          USER                    PLATFORM                 │
│   ───────────              ────                    ────────                 │
│                                                                             │
│   ┌─────────────┐                                                           │
│   │  Questions  │                                                           │
│   │  Database   │                                                           │
│   └──────┬──────┘                                                           │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐                                                           │
│   │  Build      │                                                           │
│   │  Version    │                                                           │
│   └──────┬──────┘                                                           │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐                                                           │
│   │  Validate   │                                                           │
│   │  & Lock     │                                                           │
│   └──────┬──────┘                                                           │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐                                                           │
│   │  Generate   │                                                           │
│   │  JSON       │────────────────────┐                                      │
│   └─────────────┘                    │                                      │
│                                      │                                      │
│          │                           │                                      │
│          ▼                           ▼                                      │
│   ┌─────────────┐             ┌─────────────┐                               │
│   │  Local      │             │  gcb-v2.0   │                               │
│   │  Review     │◀────────────│  .json      │                               │
│   └──────┬──────┘             └──────┬──────┘                               │
│          │                           │                                      │
│          │     User reviews          │                                      │
│          │     and submits           │                                      │
│          │                           │                                      │
│          └───────────────────────────┼──────────────────────────────────────│
│                                      │                                      │
│                                      ▼                                      │
│                               ┌─────────────┐                               │
│                               │  Submit via │                               │
│                               │  Dashboard  │                               │
│                               └──────┬──────┘                               │
│                                      │                                      │
│                                      ▼                                      │
│                               ┌─────────────┐                               │
│                               │  Validate   │                               │
│                               │  (4 stages) │                               │
│                               └──────┬──────┘                               │
│                                      │                                      │
│                              ┌───────┴───────┐                              │
│                              │               │                              │
│                              ▼               ▼                              │
│                        ┌──────────┐   ┌──────────┐                          │
│                        │  PASS    │   │  FAIL    │                          │
│                        │          │   │          │                          │
│                        └────┬─────┘   └────┬─────┘                          │
│                             │              │                                │
│                             │              │ Return errors                  │
│                             │              │ to user                        │
│                             │              │                                │
│                             ▼              │                                │
│                       ┌──────────┐         │                                │
│                       │  Queue   │         │                                │
│                       │(Pending) │◀────────┘                                │
│                       └────┬─────┘   (fix & retry)                          │
│                            │                                                │
│                            ▼                                                │
│                       ┌──────────┐                                          │
│                       │Moderator │                                          │
│                       │  Review  │                                          │
│                       └────┬─────┘                                          │
│                            │                                                │
│                    ┌───────┴───────┐                                        │
│                    │               │                                        │
│                    ▼               ▼                                        │
│              ┌──────────┐   ┌──────────┐                                    │
│              │ APPROVED │   │ REJECTED │                                    │
│              │          │   │          │                                    │
│              └────┬─────┘   └──────────┘                                    │
│                   │              │                                          │
│                   │              │ Notify user                              │
│                   │              │ (can resubmit)                           │
│                   ▼                                                         │
│              ┌──────────┐                                                   │
│              │  Publish │                                                   │
│              │ (Active) │                                                   │
│              └────┬─────┘                                                   │
│                   │                                                         │
│                   ▼                                                         │
│              ┌──────────┐                                                   │
│              │  Tests   │                                                   │
│              │  Begin!  │                                                   │
│              └──────────┘                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [cli-builder-specifications.md](./cli-builder-specifications.md) — Builder implementation details
- [spec-export-schema-validation.md](./spec-export-schema-validation.md) — Export format schema
- [process-version-release-workflow.md](./process-version-release-workflow.md) — Release procedures
- [platform-versioning.md](./platform-versioning.md) — Version lifecycle
- [spec-api-endpoints.md](./spec-api-endpoints.md) — API documentation
- [platform-technical-architecture.md](./platform-technical-architecture.md) — System architecture

---

*Last Updated: December 17, 2025*
