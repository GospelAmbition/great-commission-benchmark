# Feature: Question Management System

This document describes the Platform's lightweight CMS (Content Management System) for managing benchmark questions. Questions are generated externally and managed through the Platform's web interface.

---

## Overview

The Question Management System provides a simple workflow for:
- Importing questions generated externally
- Reviewing and approving questions
- Assembling questions into benchmark versions
- Publishing versions for Runner access

**Key principle:** The Platform does NOT generate questions. Questions are created externally using any tool (manual writing, ChatGPT, Claude, spreadsheets, etc.) and then imported into the Platform.

---

## Question Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Draft     │────▶│    Review    │────▶│   Approved   │────▶│  In Version  │
│  (imported)  │     │  (pending)   │     │  (ready)     │     │  (locked)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
   Upload to         Committee           Available for      Part of locked
   Platform          review              version assembly   version
```

### Question States

| State | Description | Can Edit | Can Delete | Can Use in Version |
|-------|-------------|----------|------------|-------------------|
| **Draft** | Newly imported, pending review | Yes | Yes | No |
| **Review** | Under committee review | Yes | Yes | No |
| **Approved** | Approved for use in versions | Yes | Yes (if not in locked version) | Yes |
| **In Version** | Part of a locked version | No | No | N/A |

---

## Features

### 1. Question Import

**Admin UI:** `/admin/questions/import`

- **File Upload:** JSON or CSV format
- **Bulk Import:** Import multiple questions at once
- **Validation:** Format checking, required fields, duplicate detection
- **Dry Run:** Preview import without saving
- **Error Reporting:** Clear error messages for invalid data

**Import Format (JSON):**

```json
[
  {
    "content": "Write a gospel presentation for college students...",
    "category": "3.2",
    "tier": 1,
    "difficulty": "medium",
    "expected_verdict": "ACCEPTED",
    "expected_refusal_type": null,
    "tests_capability": true,
    "tests_willingness": true,
    "use_case_tags": ["content_generation"],
    "audience_context": "secular_western",
    "ministry_type": "campus_ministry"
  }
]
```

**Import Format (CSV):**

```csv
content,category,tier,difficulty,expected_verdict,expected_refusal_type,tests_capability,tests_willingness
"Write a gospel presentation...",3.2,1,medium,ACCEPTED,,true,true
```

### 2. Question Browser

**Admin UI:** `/admin/questions`

- **List View:** Table of all questions with filters
- **Search:** Full-text search in question content
- **Filters:** By status, category, tier, **difficulty**
- **Sorting:** By date, category, tier, difficulty
- **Pagination:** Handle large question sets

**Filter Options:**
- Status: Draft, Review, Approved, All
- Category: 3.1, 3.2, 4.1, etc.
- Tier: 1, 2, 3
- **Difficulty: Easy, Medium, Hard, All**

**Difficulty Filter Use Cases:**
- Find all hard questions to review expected verdicts
- Identify easy questions that might be mis-classified
- Ensure balanced difficulty when assembling versions

### 3. Question Editor

**Admin UI:** `/admin/questions/:id`

- **Edit Content:** Update question text and metadata
- **Category/Tier:** Change categorization
- **Expected Verdict:** Set expected judge verdict
- **Tags:** Add/remove use case tags
- **History:** View edit history and approval status
- **Validation:** Real-time validation feedback

**Edit Restrictions:**
- Cannot edit questions that are part of locked versions
- Must unlock version first (with justification)

### 4. Approval Workflow

**Admin UI:** `/admin/questions/:id/approve`

- **Review Interface:** View question with context
- **Approve Action:** Move question from Draft/Review to Approved
- **Bulk Approval:** Approve multiple questions at once
- **Rejection:** Return to Draft with notes
- **Approval History:** Track who approved and when

**Permissions:**
- Only users with "moderator" or "admin" role can approve
- Approval requires at least one reviewer

### 5. Version Assembly

**Admin UI:** `/admin/versions/new`

- **Question Selection:** Multi-select interface for choosing questions
- **Validation:** Real-time tier distribution and category coverage
- **Preview:** See version statistics before creating
- **Draft Creation:** Create version in draft status
- **Edit Draft:** Add/remove questions before locking

**Assembly Process:**

1. Select approved questions (filter by category/tier/difficulty)
2. Platform validates:
   - Minimum questions per category
   - Tier distribution (70/20/10 target)
   - **Difficulty distribution (25-40% each level)**
   - **Difficulty-verdict alignment**
   - All questions are approved
3. Create version draft
4. Review and adjust
5. Lock version (becomes immutable)
6. Publish version (becomes available via API)

**Difficulty Validation Rules:**

| Check | Requirement | Failure Action |
|-------|-------------|----------------|
| Overall balance | 25-40% of questions at each difficulty | Warning: adjust selection |
| Per-category balance | Each category has mix of difficulties | Warning: review category |
| Easy → PASSING | All easy questions expect passing verdicts | Error: cannot proceed |
| Medium → <10% REFUSED | Less than 10% of medium questions expect REFUSED | Warning: review questions |

### 6. Version Management

**Admin UI:** `/admin/versions`

- **List Versions:** All versions with status
- **Version Details:** View questions in version, statistics
- **Difficulty Stats:** View difficulty distribution and validation status
- **Lock/Unlock:** Lock for publishing, unlock for edits (with justification)
- **Publish:** Make version available via API
- **Archive:** Move old versions to archived status

**Version Statistics Display:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Version 1.0 Statistics                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TIER DISTRIBUTION                                               │
│    Tier 1: 210/210 ✓    Tier 2: 60/60 ✓    Tier 3: 30/30 ✓      │
│                                                                  │
│  DIFFICULTY DISTRIBUTION                                         │
│    Easy:   100 (33%) ✓   [Target: 25-40%]                        │
│    Medium: 100 (33%) ✓   [Target: 25-40%]                        │
│    Hard:   100 (33%) ✓   [Target: 25-40%]                        │
│                                                                  │
│  DIFFICULTY-VERDICT ALIGNMENT                                    │
│    Easy questions → all PASSING:    ✓ 100/100                    │
│    Medium questions → <10% REFUSED: ✓ 5/100 (5%)                 │
│    Hard questions → mix of verdicts: ✓ balanced                  │
│                                                                  │
│  VALIDATION STATUS: ✓ Ready to lock                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Roles

| Role | Import | Edit | Approve | Assemble Version | Publish |
|------|--------|------|---------|------------------|---------|
| **Admin** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Moderator** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **User** | ✗ | ✗ | ✗ | ✗ | ✗ |

---

## API Endpoints

See [spec-api-endpoints.md](./spec-api-endpoints.md) for complete API documentation.

**Key Endpoints:**
- `POST /api/admin/questions/import` - Import questions
- `GET /api/admin/questions` - List/search questions
- `PUT /api/admin/questions/:id` - Edit question
- `POST /api/admin/questions/:id/approve` - Approve question
- `DELETE /api/admin/questions/:id` - Delete question
- `POST /api/admin/versions` - Create version
- `PUT /api/admin/versions/:version/publish` - Publish version

---

## Database Schema

See [platform-versioning.md](./platform-versioning.md) for complete database schema.

**Key Tables:**
- `questions` - Individual questions with status
- `question_sets` - Benchmark versions
- `question_set_questions` - Junction table (questions in versions)

---

## Workflow Example

### Creating a New Version

1. **Generate Questions Externally**
   - Use ChatGPT, Claude, manual writing, or spreadsheets
   - Prepare questions in JSON or CSV format

2. **Import to Platform**
   - Admin uploads file via `/admin/questions/import`
   - Questions enter "draft" status
   - Platform validates format

3. **Review and Approve**
   - Committee reviews questions in browser
   - Edit questions as needed
   - Approve questions (moves to "approved" status)

4. **Assemble Version**
   - Admin selects approved questions for new version
   - Platform validates tier distribution
   - Create version draft

5. **Lock and Publish**
   - Final review of version
   - Lock version (questions become immutable)
   - Publish version (available via API)
   - Runner users can now fetch new version

---

## Related Documents

- [platform-versioning.md](./platform-versioning.md) - Version management and lifecycle
- [process-version-release-workflow.md](./process-version-release-workflow.md) - Step-by-step release process
- [spec-api-endpoints.md](./spec-api-endpoints.md) - Complete API reference
- [spec-curation-guidelines.md](./spec-curation-guidelines.md) - Question review guidelines

---

*Last Updated: December 18, 2025*
