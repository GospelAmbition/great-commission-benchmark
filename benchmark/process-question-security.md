# Question Security

This document defines how benchmark questions are protected from contamination, how versions are managed, and how leaks are handled.

---

## The Contamination Problem

If benchmark questions are publicly accessible, LLM providers could:
- Discover the questions through web scraping
- Fine-tune models specifically to perform well on these exact questions
- Game the benchmark without genuinely improving Great Commission support

This would undermine the benchmark's validity and usefulness.

---

## Solution: Controlled Distribution

### What IS Public

| Item | Status | Rationale |
|------|--------|-----------|
| Benchmark methodology | ✅ Public | Transparency in evaluation approach |
| Scoring framework | ✅ Public | How scores are calculated |
| Leaderboard results | ✅ Public | The primary output |
| Aggregate statistics | ✅ Public | Category scores, trends |
| Use case categories | ✅ Public | What's being tested |
| Testing tiers | ✅ Public | Task, Doctrinal, Worldview |
| Sample questions | ✅ Public | Small subset for transparency |
| Platform code | ✅ Public | Open source infrastructure |

### What is NOT Public

| Item | Status | Rationale |
|------|--------|-----------|
| Full question sets | ❌ Private | Prevent contamination |
| Specific test prompts | ❌ Private | Prevent gaming |
| Expected responses | ❌ Private | Prevent training |
| Detailed scoring rubrics | ❌ Private | Prevent optimization |

---

## Question Set Design

### Fixed Question Sets

**Decision:** The benchmark uses an **exact, fixed set of questions** for each version.

- No variations between testers
- No watermarking or per-tester customization
- Every tester receives identical questions

**Rationale:** Reproducibility takes priority over leak tracing. All scores must be:
- Fully reproducible
- Directly comparable across testers
- Verifiable through re-runs

### No Watermarking

The concept of "subtle variations per tester to trace leaks" has been **removed** from the design:
- Different questions would produce different scores
- Complicates result comparison
- Reproducibility is more valuable than leak attribution

---

## Version Management

### Version Numbering

Each question set uses semantic versioning:
- **Semantic versions**: 1.0, 1.1, 1.2, 2.0, etc. (tracks question set evolution)
- **Marketing versions**: Version 1, Version 2, etc. (for public communication)
- Refreshed periodically (likely yearly or as needed)
- Major version changes (1.x → 2.0) trigger new marketing version (Version 1 → Version 2)

### Version Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Draft      │────▶│   Locked     │────▶│  Superseded  │
│  (editable)  │     │ (immutable)  │     │  (archived)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

| State | Description |
|-------|-------------|
| **Draft** | Under development, can be edited |
| **Locked** | Finalized, immutable, active for testing |
| **Superseded** | Replaced by newer version, results retained |

### Results Tagging

All benchmark results are tagged with both semantic and marketing versions:
- Results from 1.0, 1.1, 1.2 are labeled as "Version 1" (with semantic version details)
- Results from 2.0, 2.1, 2.2 are labeled as "Version 2" (with semantic version details)
- No mixing of major versions in comparisons (1.x vs 2.x are not directly comparable)

---

## Leaderboard Versioning

### Default View

Users see **current version results first** (e.g., Version 2):
- Default filter shows latest marketing version
- Prominent display of current leaderboard
- Semantic version details available (e.g., "Version 2 (2.0)")

### Older Versions

Older version results are:
- **Accessible** — Users can view them
- **Deprioritized** — Not shown by default
- **Labeled** — Clearly marked with version number

### Version Filtering

The leaderboard supports:
- Filter by version
- View all versions for a model
- Compare model performance across versions

---

## Leak Response

### Detection

Monitor for questions appearing in:
- Training data
- Online forums
- Social media
- Model outputs that reference questions

### Response Plan

**If questions leak publicly:**

1. **Version invalidation** — The leaked version is marked superseded
2. **New version release** — Release V(n+1) with new questions
3. **Communication** — Notify testers that results should use new version
4. **No emergency rotation** — Orderly transition to new version

### Why This Approach

- Simple and predictable process
- No panic or rushed response needed
- Old results remain valid (just for old version)
- New version restores benchmark integrity

---

## Question Set Discussion

### External Platform

Discussions about question sets happen on a **separate external platform** (e.g., Discord):
- Not on the benchmark platform itself
- Keeps governance separate from execution

### Access Control

Only **approved insiders** with access to question sets can participate:
- Moderators
- Committee members
- Approved reviewers

### Discussion Scope

What can be discussed:
- Debating whether verdicts are fair
- Refining question wording
- Proposing additions or removals
- Evaluating if questions test what they intend

### Pre-Lock Governance

All discussion and refinement happens **before** a version number is locked:
- Open discussion during Draft phase
- Consensus-building on changes
- Final review before locking

### Version Finalization

Once consensus is reached:
- Version is locked
- Question set becomes immutable
- No further edits for that version
- Changes go into next version

---

## Tester Registration

### Registration Process

1. **Application** — User registers interest on website
2. **Information Collection** — Contact and identity information
3. **Agreement** — Tester signs terms (see below)
4. **Verification** — Manual review (prevent bots/spam)
5. **Approval** — Access granted
6. **Distribution** — Questions delivered via authenticated API

### Tester Agreement

Testers agree to:
- ❌ Not publish questions publicly (web, social media, forums)
- ❌ Not share questions with LLM providers
- ❌ Not use questions for model training
- ❌ Not share API keys or allow unauthorized access
- ✅ Report any suspected leaks
- ✅ Follow benchmark usage guidelines
- ✅ Keep API keys secure

### Enforcement

| Violation | Response |
|-----------|----------|
| Minor (accidental partial disclosure) | Warning, re-confirmation of agreement |
| Major (deliberate sharing) | Access revocation |
| Severe (providing to LLM providers) | Permanent ban, public disclosure if appropriate |

---

## Cross-Version Analysis

The versioning system enables valuable analysis:

| Analysis Type | What It Shows |
|---------------|---------------|
| **Model improvement** | How a model performs on V2 vs. V1 |
| **Question quality** | Whether new questions better differentiate models |
| **Trend tracking** | Industry-wide changes over benchmark versions |
| **Regression detection** | Models that got worse on newer versions |

---

## Technical Implementation

### Database Design

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ QuestionSet    │     │ Question       │     │ TestResult     │
├────────────────┤     ├────────────────┤     ├────────────────┤
│ id             │────▶│ question_set_id│     │ question_set_id│
│ version        │     │ content        │     │ model_id       │
│ status         │     │ category       │     │ verdicts       │
│ created_at     │     │ expected_tier  │     │ created_at     │
│ locked_at      │     └────────────────┘     └────────────────┘
└────────────────┘
```

### API Security

Questions are delivered via authenticated API:

**Platform Tests (Server-side execution):**
- Questions never sent to client
- Execution happens on Platform servers
- Maximum security for question protection

**Runner CLI (API-based distribution):**
- Questions fetched via authenticated API (API key required)
- Questions cached locally for offline operation
- Rate limiting prevents bulk extraction (50 requests/hour)
- All access logged for audit
- API keys can be revoked at any time
- Checksums verify question integrity

**Security Measures:**
- API key authentication required for Runner access
- Rate limiting on question fetch endpoints
- Audit logging of all API access
- Key management and rotation support
- Questions only served to authenticated users

---

## Related Documents

- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment strategy
- [Core Publication Model](./process-publication-model.md) — Publication criteria
- [Moderation Process](./process-moderation-process.md) — Moderator workflows

