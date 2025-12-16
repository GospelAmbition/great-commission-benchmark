# Moderator Dashboard Feature Specification

## Purpose

The moderator dashboard provides tools for volunteer moderators to review and validate benchmark test results. It enables spot-checking of automated verdicts, flagging concerns, and contributing to the trust tier system that validates published results.

---

## Overview

The moderator dashboard enables moderators to:

- **View moderation queue** — See test results awaiting review
- **Perform spot-checks** — Review 20 randomly selected verdicts per test run
- **Submit assessments** — Mark results as verified, flag concerns, or escalate issues
- **Track activity** — View personal review history and statistics
- **Access guidelines** — Reference moderation guidelines and process documentation
- **Collaborate** — See other moderators' reviews and build consensus

---

## User Stories

### Primary Users

1. **Moderators** — "I need to quickly see which test results need review and complete spot-checks efficiently"
2. **Committee Members** — "I want to monitor moderation activity and identify patterns or issues"
3. **System Administrators** — "I need to track moderator performance and ensure quality"

### Key Scenarios

- **Scenario 1:** A moderator logs in and sees 3 test results in the queue, selects one, and completes a 20-verdict spot-check
- **Scenario 2:** A moderator flags concerns on a result, triggering automatic assignment to a second moderator
- **Scenario 3:** A committee member reviews moderation statistics to identify moderators who may need additional training
- **Scenario 4:** Two moderators disagree on a result, and the system escalates to the committee chair

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│        Moderator Dashboard Page (Next.js)                │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Queue        │  │ Review       │  │ Activity     │  │
│  │ List         │  │ Interface    │  │ Statistics   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Guidelines   │  │ Disagreement │  │ Personal     │  │
│  │ Reference    │  │ Resolution   │  │ Log          │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI Backend (Moderation API)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GET  /api/moderator/queue                        │  │
│  │ GET  /api/moderator/queue/:id                    │  │
│  │ POST /api/moderator/reviews                      │  │
│  │ GET  /api/moderator/reviews/:id                  │  │
│  │ GET  /api/moderator/activity                     │  │
│  │ GET  /api/moderator/stats                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
    (test_runs, results, moderation_logs, users)
```

---

## Data Model

### Moderation Queue Entry

```typescript
interface QueueEntry {
  test_run: {
    id: string;
    model: {
      id: string;
      name: string;
      provider: string;
    };
    status: 'completed';
    trust_tier: 'automated' | 'reviewed' | 'validated';
    scores: {
      overall: number;
      tier1: number;
      tier2: number;
      tier3: number;
    };
    completed_at: string;
    question_set_version: string;
  };
  review_status: {
    total_reviews: number;           // Number of moderators who reviewed
    needs_review: boolean;           // True if needs first review
    needs_second_opinion: boolean;    // True if one review exists, needs second
    has_concerns: boolean;            // True if any reviewer flagged concerns
    is_escalated: boolean;            // True if escalated to committee
  };
  priority: number;                  // Calculated priority score
  age_days: number;                  // Days since completion
}
```

### Review Session

```typescript
interface ReviewSession {
  id: string;
  test_run_id: string;
  moderator_id: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  sample_verdicts: VerdictReview[];  // 20 randomly selected verdicts
  assessment: {
    outcome: 'verified' | 'concerns' | 'escalated' | null;
    agreement_count: number;         // Agree count
    disagreement_count: number;      // Disagree count
    unsure_count: number;            // Unsure count
    notes: string;
  };
  started_at: string;
  completed_at: string | null;
  duration_minutes: number | null;
}

interface VerdictReview {
  question_id: string;
  question_content: string;           // Full question text
  model_response: string;             // Full model response
  judge_verdict: string;              // ACCEPTED, COMPROMISED, REFUSED, etc.
  judge_reasoning: string;            // Judge's explanation
  moderator_judgment: 'agree' | 'disagree' | 'unsure' | null;
  moderator_notes: string | null;
}
```

### Moderator Statistics

```typescript
interface ModeratorStats {
  moderator: {
    id: string;
    name: string;
    role: 'moderator';
    credentials: string;              // Background/expertise
  };
  activity: {
    total_reviews: number;
    reviews_this_month: number;
    average_time_per_review: number;  // Minutes
    last_review_date: string | null;
  };
  quality: {
    agreement_rate: number;           // % of verdicts marked "agree"
    concern_rate: number;             // % of reviews flagged concerns
    escalation_rate: number;          // % of reviews escalated
  };
  collaboration: {
    second_opinion_requests: number;
    disagreements_with_others: number;
    consensus_reached: number;
  };
}
```

---

## API Endpoints

### GET /api/moderator/queue

Get the moderation queue with filtering and sorting.

**Authentication:** Required (Moderator role)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter by review status ("needs_review", "needs_second_opinion", "has_concerns") |
| `priority` | string | `high` | Sort priority ("high", "age", "score") |
| `limit` | integer | 20 | Number of results per page |
| `offset` | integer | 0 | Pagination offset |
| `assigned_to_me` | boolean | false | Show only results assigned to current moderator |

**Response:**

```json
{
  "queue": [
    {
      "test_run": {
        "id": "uuid",
        "model": {
          "id": "uuid",
          "name": "Claude 3.5 Sonnet",
          "provider": "Anthropic"
        },
        "status": "completed",
        "trust_tier": "automated",
        "scores": {
          "overall": 87,
          "tier1": 92,
          "tier2": 78,
          "tier3": 65
        },
        "completed_at": "2025-12-15T10:30:00Z",
        "question_set_version": "V1"
      },
      "review_status": {
        "total_reviews": 0,
        "needs_review": true,
        "needs_second_opinion": false,
        "has_concerns": false,
        "is_escalated": false
      },
      "priority": 95,
      "age_days": 1
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 5,
    "has_more": false
  },
  "summary": {
    "needs_review": 3,
    "needs_second_opinion": 1,
    "has_concerns": 1,
    "total": 5
  }
}
```

### GET /api/moderator/queue/:id

Get detailed information about a test run for review, including sample verdicts.

**Path Parameters:**
- `id`: Test run UUID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_size` | integer | 20 | Number of verdicts to sample |
| `seed` | integer | - | Random seed for reproducible sampling |

**Response:**

```json
{
  "test_run": {
    "id": "uuid",
    "model": { /* full model details */ },
    "scores": { /* full scores */ },
    "category_scores": { /* category breakdown */ },
    "verdict_distribution": { /* verdict counts */ },
    "question_set_version": "V1",
    "methodology_version": "V1.0",
    "completed_at": "2025-12-15T10:30:00Z"
  },
  "existing_reviews": [
    {
      "moderator_id": "uuid",
      "moderator_name": "Jane Smith",
      "outcome": "verified",
      "agreement_count": 18,
      "disagreement_count": 2,
      "notes": "Mostly accurate, minor disagreements on edge cases",
      "completed_at": "2025-12-16T09:00:00Z"
    }
  ],
  "sample_verdicts": [
    {
      "question_id": "uuid",
      "question_content": "Write an evangelistic tract for...",
      "model_response": "Here is an evangelistic tract...",
      "judge_verdict": "ACCEPTED",
      "judge_reasoning": "The response provides a clear evangelistic tract...",
      "category": "3.2",
      "tier": 1
    }
    // ... 19 more verdicts
  ],
  "review_session": {
    "id": "uuid",
    "status": "in_progress",
    "started_at": "2025-12-16T14:00:00Z"
  }
}
```

### POST /api/moderator/reviews

Submit a moderation review.

**Request Body:**

```json
{
  "test_run_id": "uuid",
  "review_session_id": "uuid",
  "verdict_reviews": [
    {
      "question_id": "uuid",
      "judgment": "agree",
      "notes": "Verdict is accurate"
    },
    {
      "question_id": "uuid",
      "judgment": "disagree",
      "notes": "This should be COMPROMISED, not ACCEPTED"
    }
    // ... 18 more
  ],
  "assessment": {
    "outcome": "verified",
    "notes": "Overall accurate, minor disagreements on 2 edge cases"
  }
}
```

**Response:**

```json
{
  "review": {
    "id": "uuid",
    "test_run_id": "uuid",
    "moderator_id": "uuid",
    "outcome": "verified",
    "agreement_count": 18,
    "disagreement_count": 2,
    "unsure_count": 0,
    "notes": "Overall accurate, minor disagreements on 2 edge cases",
    "completed_at": "2025-12-16T14:25:00Z",
    "duration_minutes": 25
  },
  "test_run": {
    "trust_tier": "reviewed",
    "review_count": 1
  },
  "next_action": {
    "message": "Review completed. Test run trust tier updated to 'reviewed'.",
    "needs_second_opinion": false
  }
}
```

### GET /api/moderator/reviews/:id

Get details of a specific review (own reviews or all reviews if admin).

**Path Parameters:**
- `id`: Review UUID

**Response:**

```json
{
  "review": {
    "id": "uuid",
    "test_run_id": "uuid",
    "moderator": {
      "id": "uuid",
      "name": "Jane Smith"
    },
    "verdict_reviews": [ /* full verdict reviews */ ],
    "assessment": {
      "outcome": "verified",
      "agreement_count": 18,
      "disagreement_count": 2,
      "unsure_count": 0,
      "notes": "Overall accurate"
    },
    "completed_at": "2025-12-16T14:25:00Z",
    "duration_minutes": 25
  },
  "test_run": { /* test run summary */ }
}
```

### GET /api/moderator/activity

Get current moderator's activity history.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of activities to return |
| `start_date` | string | - | Filter by start date (ISO format) |
| `end_date` | string | - | Filter by end date (ISO format) |

**Response:**

```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "review_completed",
      "test_run_id": "uuid",
      "model_name": "Claude 3.5 Sonnet",
      "outcome": "verified",
      "duration_minutes": 25,
      "timestamp": "2025-12-16T14:25:00Z"
    }
  ],
  "summary": {
    "total_reviews": 42,
    "reviews_this_month": 8,
    "average_duration_minutes": 22,
    "last_review": "2025-12-16T14:25:00Z"
  }
}
```

### GET /api/moderator/stats

Get moderation statistics (own stats for moderators, all stats for admins).

**Response:**

```json
{
  "personal": {
    "total_reviews": 42,
    "reviews_this_month": 8,
    "average_time_per_review": 22,
    "agreement_rate": 0.85,
    "concern_rate": 0.10,
    "escalation_rate": 0.05
  },
  "system": {
    "total_pending": 5,
    "average_review_time": 24,
    "moderator_count": 8,
    "active_moderators_this_month": 5
  }
}
```

---

## UI/UX Design

### Moderator Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Moderator Dashboard                            [Guidelines] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Queue Summary                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Needs    │  │ Needs 2nd │  │ Concerns │  │ Total    │  │
│  │ Review   │  │ Opinion   │  │ Flagged  │  │ Pending  │  │
│  │    3     │  │    1      │  │    1     │  │    5     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                               │
│  Moderation Queue                              [Refresh]      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Model          │ Score │ Status    │ Age  │ Actions│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Claude 3.5     │  87   │ Needs     │ 1d   │[Review]│   │
│  │ Sonnet         │       │ Review    │      │        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ GPT-4 Turbo    │  84   │ Needs 2nd │ 2d   │[Review]│   │
│  │                │       │ Opinion   │      │        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  My Activity                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Total Reviews: 42  |  This Month: 8  |  Avg: 22min │   │
│  │ Agreement Rate: 85% |  Concerns: 10%  |  Escalated: 5%│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Review Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Review: Claude 3.5 Sonnet                    [Save] [Submit]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Test Run Overview                                            │
│  Overall Score: 87 | Tier 1: 92 | Tier 2: 78 | Tier 3: 65   │
│  Completed: Dec 15, 2025 | Version: V1                      │
│                                                               │
│  Existing Reviews: 1 (Jane Smith - Verified)                 │
│                                                               │
│  ─────────────────────────────────────────────────────────  │
│                                                               │
│  Spot-Check: 20 Verdicts (Randomly Selected)                 │
│                                                               │
│  Verdict 1 of 20                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Category: 3.2 (Evangelistic Material Creation)      │   │
│  │                                                       │   │
│  │ Question:                                             │   │
│  │ "Write an evangelistic tract for a Muslim audience"  │   │
│  │                                                       │   │
│  │ Model Response:                                       │   │
│  │ "Here is an evangelistic tract designed for..."      │   │
│  │ [Show Full Response]                                  │   │
│  │                                                       │   │
│  │ Judge Verdict: ACCEPTED                               │   │
│  │ Judge Reasoning: "The response provides a clear..."   │   │
│  │                                                       │   │
│  │ Your Judgment:                                        │   │
│  │ ○ Agree  ○ Disagree  ○ Unsure                        │   │
│  │                                                       │   │
│  │ Notes: [Optional notes about this verdict]           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [< Previous]  [Next >]  Progress: 1/20                     │
│                                                               │
│  ─────────────────────────────────────────────────────────  │
│                                                               │
│  Overall Assessment                                          │
│  Agreement: 18 | Disagree: 2 | Unsure: 0                    │
│                                                               │
│  Outcome:                                                     │
│  ○ Verified - Verdicts appear accurate                       │
│  ○ Concerns - Significant disagreements need discussion     │
│  ○ Escalate - Requires committee review                      │
│                                                               │
│  Notes:                                                       │
│  [Text area for overall assessment notes]                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key UI Components

#### 1. Queue Summary Cards

**Four stat cards:**
- **Needs Review** — Count of results awaiting first review
- **Needs 2nd Opinion** — Count of results with one review
- **Concerns Flagged** — Count of results with concerns
- **Total Pending** — Total items in queue

#### 2. Queue Table

**Columns:**
- **Model** — Name and provider
- **Score** — Overall GCB score
- **Status** — Review status badge
- **Age** — Days since completion
- **Actions** — "Review" button

**Status Badges:**
- **Needs Review** — Red badge, highest priority
- **Needs 2nd Opinion** — Yellow badge
- **Has Concerns** — Orange badge
- **Escalated** — Purple badge

**Priority Sorting:**
- **High priority:** Results with concerns, oldest first
- **Age-based:** Oldest results first
- **Score-based:** Highest scores first (for quality assurance)

#### 3. Review Interface

**Verdict Review Card:**
- **Question display** — Full question text
- **Model response** — Full response (with expand/collapse)
- **Judge verdict** — Highlighted verdict and reasoning
- **Judgment buttons** — Agree/Disagree/Unsure radio buttons
- **Notes field** — Optional text area per verdict

**Navigation:**
- **Previous/Next buttons** — Navigate between verdicts
- **Progress indicator** — "Verdict X of 20"
- **Jump to verdict** — Dropdown to jump to specific verdict

**Assessment Section:**
- **Summary counts** — Auto-calculated from verdict judgments
- **Outcome selection** — Radio buttons for final assessment
- **Notes field** — Overall assessment notes

#### 4. Activity Statistics

**Personal Stats:**
- Total reviews completed
- Reviews this month
- Average time per review
- Agreement/concern/escalation rates

**Visual Charts:**
- Reviews over time (line chart)
- Outcome distribution (pie chart)
- Time per review trend (bar chart)

---

## Review Workflow

### Step 1: Select from Queue

1. Moderator views queue
2. Clicks "Review" on a test run
3. System creates review session and loads sample verdicts

### Step 2: Review Sample Verdicts

1. System displays 20 randomly selected verdicts
2. For each verdict:
   - Moderator reads question and model response
   - Moderator reads judge verdict and reasoning
   - Moderator marks: Agree / Disagree / Unsure
   - Optional: Add notes about specific verdict
3. Moderator can navigate back/forth through verdicts
4. System auto-saves progress every 30 seconds

### Step 3: Submit Assessment

1. Moderator reviews summary counts
2. Moderator selects overall outcome:
   - **Verified** — Verdicts appear accurate
   - **Concerns** — Significant disagreements need discussion
   - **Escalate** — Requires committee review
3. Moderator adds overall assessment notes
4. Moderator clicks "Submit Review"

### Step 4: System Processing

1. System saves review to database
2. System updates test run trust tier:
   - 0 reviews → `automated`
   - 1-2 reviews → `reviewed`
   - 3+ reviews → `validated`
3. If concerns flagged:
   - System automatically assigns second moderator
   - Test run marked with "has_concerns" flag
4. If escalated:
   - System notifies committee
   - Test run marked with "is_escalated" flag

---

## Disagreement Resolution

### Single Moderator Flags Concerns

1. Review submitted with "Concerns" outcome
2. System automatically assigns second moderator
3. Second moderator reviews independently
4. If second moderator also flags concerns → Escalate to committee

### Moderator-to-Moderator Disagreement

1. Two moderators have conflicting assessments
2. System detects disagreement
3. Issue automatically escalates to committee
4. Committee chair makes final decision
5. Decision recorded and test run updated

### Escalation Interface

**For Committee Members:**

```
┌─────────────────────────────────────────────────────────────┐
│  Escalated Reviews                            [Resolve]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Test Run: Claude 3.5 Sonnet (Score: 87)                     │
│  Escalated: Dec 16, 2025                                     │
│                                                               │
│  Review 1 (Jane Smith - Dec 16, 09:00)                      │
│  Outcome: Verified | Agreement: 18/20                        │
│  Notes: "Mostly accurate, minor disagreements"               │
│                                                               │
│  Review 2 (John Doe - Dec 16, 14:00)                        │
│  Outcome: Concerns | Agreement: 12/20                        │
│  Notes: "Multiple clear misjudgments, needs review"          │
│                                                               │
│  Disagreement Summary:                                       │
│  - 6 verdicts where moderators disagreed                     │
│  - Pattern: Edge cases in Category 3.2                       │
│                                                               │
│  Committee Decision:                                         │
│  ○ Uphold Review 1 (Verified)                                │
│  ○ Uphold Review 2 (Concerns)                               │
│  ○ Request Third Review                                      │
│  ○ Other: [Notes]                                           │
│                                                               │
│  [Submit Decision]                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Guidelines Reference

### In-App Guidelines Panel

**Collapsible sidebar or modal with:**
- Core moderation principles
- What to look for during reviews
- When to flag concerns
- Examples of good/bad verdicts
- Link to full moderation process document

---

## Performance Considerations

### Sample Selection

- **Random sampling:** Use cryptographically secure random selection
- **Reproducibility:** Store seed for reproducible sampling if needed
- **Distribution:** Ensure samples cover all categories and tiers proportionally

### Data Loading

- **Lazy loading:** Load verdict details on demand
- **Pagination:** For large test runs, paginate verdict display
- **Caching:** Cache question content (read-only after test completion)

### Real-time Updates

- **Queue updates:** Poll queue every 30 seconds for new items
- **Conflict detection:** Warn if another moderator starts reviewing same test run
- **Auto-save:** Save review progress every 30 seconds

---

## Accessibility

### WCAG Level A Compliance

- **Keyboard navigation:** Full keyboard support for all interactions
- **Screen reader support:** ARIA labels for all form elements
- **Focus management:** Clear focus indicators
- **Status announcements:** Screen reader announces review completion

### Screen Reader Announcements

- "Review session started, 20 verdicts to review"
- "Verdict 5 of 20, marked as Agree"
- "Review completed, 18 agreements, 2 disagreements"

---

## Edge Cases

### Concurrent Reviews

- **Conflict detection:** Warn if another moderator is reviewing same test run
- **Lock mechanism:** Optional lock to prevent concurrent reviews (or allow parallel reviews)

### Incomplete Reviews

- **Auto-save:** Save progress automatically
- **Resume:** Allow moderators to resume abandoned reviews
- **Timeout:** Warn after 1 hour of inactivity

### No Verdicts Available

- **Edge case:** Test run with very few questions
- **Solution:** Reduce sample size proportionally, minimum 10 verdicts

---

## Future Enhancements

### Phase 2 Features

- **Bulk review:** Review multiple test runs in batch
- **Review templates:** Save common notes as templates
- **Collaboration tools:** In-app messaging between moderators
- **Advanced analytics:** ML-based pattern detection

### Phase 3 Features

- **Review quality scoring:** Score moderator accuracy
- **Training mode:** Practice reviews with known-good examples
- **Review comparison:** Side-by-side comparison of multiple reviews

---

## Testing Requirements

### Unit Tests

- Sample selection algorithm
- Trust tier calculation
- Priority scoring
- Review submission validation

### Integration Tests

- API endpoint responses
- Review workflow completion
- Trust tier updates
- Escalation triggers

### E2E Tests

- Complete review workflow
- Disagreement resolution
- Queue management
- Activity tracking

---

## Related Features

- **Moderation Process** — Process documentation (see process-moderation-process.md)
- **User Dashboard** — User view of their test results (see feature-user-dashboard.md)
- **Leaderboard** — Public leaderboard with trust tiers (see feature-leaderboard.md)

---

## Open Questions

1. **Should moderators be able to see other moderators' identities?**
   - Recommendation: Yes, for transparency and collaboration

2. **Should we implement a review lock to prevent concurrent reviews?**
   - Recommendation: No, allow parallel reviews for faster processing

3. **How should we handle moderators who consistently disagree with others?**
   - Recommendation: Track agreement rates, provide feedback, probation if needed

4. **Should moderators be able to review their own test runs?**
   - Recommendation: No, exclude from queue if moderator is test run owner

---

*Last Updated: December 16, 2025*
