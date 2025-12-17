# Retesting Feature Specification

## Purpose

The retesting feature enables users to rerun benchmark tests on models that have already been tested. This supports use cases like verifying results, testing model updates, comparing performance over time, and validating improvements.

---

## Overview

The retesting feature provides:

- **Quick retest flow** — Retest a model with minimal steps
- **Version selection** — Choose which benchmark version to use
- **Comparison tracking** — Link retests to original tests for comparison
- **Cost estimation** — Show estimated cost before retesting
- **Payment handling** — Process payment for retest (same as new test)
- **Result comparison** — Automatically compare new results with previous results

---

## User Stories

### Primary Users

1. **Volunteers** — "I want to retest a model to verify the results are consistent"
2. **Organizations** — "We need to retest after the model provider released an update"
3. **Researchers** — "I want to track how model performance changes over time"
4. **Model Developers** — "I need to validate that my model improvements increased the benchmark score"

### Key Scenarios

- **Scenario 1:** A user retests Claude 3.5 Sonnet to verify their original test results
- **Scenario 2:** An organization retests GPT-4 after OpenAI released an update
- **Scenario 3:** A researcher retests multiple models monthly to track performance trends
- **Scenario 4:** A developer retests their model after fine-tuning to measure improvement

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│         Retest Flow (Multi-Page)                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Retest       │  │ Payment      │  │ Test         │  │
│  │ Selection    │  │ Confirmation │  │ Execution    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Results       │  │ Comparison   │  │ History      │  │
│  │ Display       │  │ View         │  │ Tracking     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI Backend (Retest API)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │ POST /api/tests/:id/retest                      │  │
│  │ GET  /api/tests/:id/retest/history              │  │
│  │ GET  /api/tests/:id/compare                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
        (test_runs, retest_relationships, results)
```

---

## Data Model

### Retest Request

```typescript
interface RetestRequest {
  original_test_run_id: string;
  model_id: string;                  // Same model or updated version
  question_set_version: string;      // Default: same version, or "current"
  methodology_version: string;       // Default: current methodology
  reason?: string;                    // Optional: why retesting
  compare_with_original: boolean;   // Default: true
}
```

### Retest Relationship

```typescript
interface RetestRelationship {
  id: string;
  original_test_run_id: string;
  retest_run_id: string;
  relationship_type: 'verification' | 'update' | 'improvement' | 'research';
  reason: string | null;
  created_at: string;
}
```

### Retest Comparison

```typescript
interface RetestComparison {
  original: {
    test_run_id: string;
    completed_at: string;
    scores: {
      overall: number;
      tier1: number;
      tier2: number;
      tier3: number;
    };
    verdict_distribution: VerdictDistribution;
  };
  retest: {
    test_run_id: string;
    completed_at: string;
    scores: {
      overall: number;
      tier1: number;
      tier2: number;
      tier3: number;
    };
    verdict_distribution: VerdictDistribution;
  };
  changes: {
    overall_delta: number;          // Positive = improvement
    tier1_delta: number;
    tier2_delta: number;
    tier3_delta: number;
    verdict_changes: {
      ACCEPTED: number;               // Net change in count
      COMPROMISED: number;
      REFUSED: number;
    };
    improved_categories: string[];    // Categories with higher scores
    declined_categories: string[];    // Categories with lower scores
  };
  significance: {
    overall_change_percent: number;
    is_significant: boolean;          // >5% change considered significant
  };
}
```

---

## Retest Workflow

### Step 1: Initiate Retest

**User Actions:**
1. Navigate to test detail page
2. Click "Retest Model" button
3. System shows retest options

**System Actions:**
1. Load original test run details
2. Check if model is still available
3. Calculate estimated cost
4. Show retest configuration options

### Step 2: Configure Retest

**Options:**
- **Benchmark Version:**
  - Same version (default)
  - Current version
  - Specific version (if available)
  
- **Methodology Version:**
  - Current methodology (default)
  - Same methodology as original
  
- **Reason for Retest:**
  - Verification (default)
  - Model update
  - Improvement validation
  - Research/tracking

**Display:**
- Original test summary
- Estimated cost
- Expected duration
- Comparison will be available

### Step 3: Payment

**Same as new test:**
- Show cost estimate
- Process payment via Stripe
- Create payment intent
- Confirm payment

### Step 4: Test Execution

**Same as new test:**
- Queue test run
- Execute benchmark
- Track progress
- Store results

### Step 5: Results & Comparison

**After completion:**
- Display new test results
- Automatically generate comparison
- Show side-by-side view
- Highlight changes

---

## API Endpoints

### POST /api/tests/:id/retest

Initiate a retest of a completed test run.

**Path Parameters:**
- `id`: Original test run UUID

**Request Body:**

```json
{
  "question_set_version": "current",
  "methodology_version": "current",
  "reason": "verification",
  "compare_with_original": true
}
```

**Response:**

```json
{
  "retest_request": {
    "id": "uuid",
    "original_test_run_id": "uuid",
    "model_id": "uuid",
    "question_set_version": "V1",
    "methodology_version": "V1.0",
    "reason": "verification",
    "status": "pending_payment"
  },
  "cost_estimate": {
    "amount": 20.00,
    "currency": "USD",
    "breakdown": {
      "api_costs": 18.50,
      "platform_fee": 1.50
    }
  },
  "payment_intent": {
    "id": "stripe_pi_xxx",
    "client_secret": "pi_xxx_secret_xxx"
  }
}
```

### GET /api/tests/:id/retest/history

Get retest history for a test run.

**Path Parameters:**
- `id`: Original test run UUID

**Response:**

```json
{
  "original_test": {
    "id": "uuid",
    "completed_at": "2025-11-01T10:00:00Z",
    "scores": {
      "overall": 85
    }
  },
  "retests": [
    {
      "id": "uuid",
      "completed_at": "2025-12-01T10:00:00Z",
      "scores": {
        "overall": 87
      },
      "relationship": {
        "type": "verification",
        "reason": "Verifying original results"
      },
      "changes": {
        "overall_delta": 2,
        "overall_change_percent": 2.35
      }
    }
  ],
  "total_retests": 1
}
```

### GET /api/tests/:id/compare

Compare original test with retest.

**Path Parameters:**
- `id`: Original test run UUID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `retest_id` | string | - | Specific retest to compare (if multiple) |
| `category` | string | - | Filter to specific category |

**Response:**

```json
{
  "comparison": {
    "original": {
      "test_run_id": "uuid",
      "completed_at": "2025-11-01T10:00:00Z",
      "scores": {
        "overall": 85,
        "tier1": 88,
        "tier2": 78,
        "tier3": 70
      },
      "verdict_distribution": {
        "ACCEPTED": 240,
        "COMPROMISED": 15,
        "REFUSED": 10
      }
    },
    "retest": {
      "test_run_id": "uuid",
      "completed_at": "2025-12-01T10:00:00Z",
      "scores": {
        "overall": 87,
        "tier1": 90,
        "tier2": 79,
        "tier3": 71
      },
      "verdict_distribution": {
        "ACCEPTED": 245,
        "COMPROMISED": 12,
        "REFUSED": 8
      }
    },
    "changes": {
      "overall_delta": 2,
      "tier1_delta": 2,
      "tier2_delta": 1,
      "tier3_delta": 1,
      "verdict_changes": {
        "ACCEPTED": 5,
        "COMPROMISED": -3,
        "REFUSED": -2
      },
      "improved_categories": ["3.2", "3.5"],
      "declined_categories": []
    },
    "significance": {
      "overall_change_percent": 2.35,
      "is_significant": false
    }
  }
}
```

---

## UI/UX Design

### Retest Initiation

**From Test Detail Page:**

```
┌─────────────────────────────────────────────────────────────┐
│  Test Results: Claude 3.5 Sonnet                            │
│  Overall Score: 85 | Completed: Nov 1, 2025                │
│                                                               │
│  [View Full Results] [Retest Model] [Download Report]       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Retest Modal/Page:**

```
┌─────────────────────────────────────────────────────────────┐
│  Retest Model: Claude 3.5 Sonnet                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Original Test Summary                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Completed: November 1, 2025                           │   │
│  │ Overall Score: 85                                     │   │
│  │ Tier 1: 88 | Tier 2: 78 | Tier 3: 70                 │   │
│  │ Version: V1                                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Retest Configuration                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Benchmark Version:                                    │   │
│  │ ○ Same version (V1)                                  │   │
│  │ ○ Current version (V1)                                │   │
│  │                                                       │   │
│  │ Methodology Version:                                  │   │
│  │ ○ Current methodology (V1.0)                         │   │
│  │ ○ Same as original (V1.0)                           │   │
│  │                                                       │   │
│  │ Reason for Retest:                                    │   │
│  │ [Verification ▼]                                     │   │
│  │   Options: Verification, Model Update, Improvement,   │   │
│  │            Research/Tracking                         │   │
│  │                                                       │   │
│  │ ✓ Compare results with original test                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Cost Estimate                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Estimated Cost: $20.00                                │   │
│  │   API Costs: $18.50                                  │   │
│  │   Platform Fee: $1.50                                │   │
│  │                                                       │   │
│  │ Estimated Duration: ~1.5 hours                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [Cancel] [Continue to Payment]                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Comparison View

**After Retest Completes:**

```
┌─────────────────────────────────────────────────────────────┐
│  Retest Comparison: Claude 3.5 Sonnet                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Score Comparison                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Metric      │ Original │ Retest │ Change │ Status   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Overall     │   85     │   87   │  +2    │ ↑ Improved│   │
│  │ Tier 1      │   88     │   90   │  +2    │ ↑ Improved│   │
│  │ Tier 2      │   78     │   79   │  +1    │ ↑ Improved│   │
│  │ Tier 3      │   70     │   71   │  +1    │ ↑ Improved│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Verdict Changes                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Verdict      │ Original │ Retest │ Change            │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ ACCEPTED     │   240    │   245  │  +5    ↑         │   │
│  │ COMPROMISED  │   15     │   12   │  -3    ↓         │   │
│  │ REFUSED      │   10     │    8   │  -2    ↓         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Category Changes                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Category          │ Original │ Retest │ Change       │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 3.1 Missiological │   86     │   87   │  +1    ↑    │   │
│  │ 3.2 Evangelistic  │   90     │   92   │  +2    ↑    │   │
│  │ 3.3 Apologetic    │   88     │   88   │   0    —    │   │
│  │ 3.4 Conversational│   85     │   85   │   0    —    │   │
│  │ 3.5 Intercessory  │   89     │   91   │  +2    ↑    │   │
│  │ 3.6 Scripture     │   87     │   87   │   0    —    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Summary                                                      │
│  • Overall score improved by 2.35% (not statistically       │
│    significant)                                               │
│  • 2 categories showed improvement                            │
│  • 5 more questions accepted, 5 fewer refusals                │
│                                                               │
│  [View Full Comparison] [Download Comparison Report]         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Retest History

**On Test Detail Page:**

```
┌─────────────────────────────────────────────────────────────┐
│  Retest History                                               │
│                                                               │
│  Original Test (Nov 1, 2025)                                  │
│  Overall Score: 85                                            │
│                                                               │
│  Retest 1 (Dec 1, 2025) - Verification                       │
│  Overall Score: 87 (+2, +2.35%)                               │
│  [View Comparison]                                            │
│                                                               │
│  Retest 2 (Jan 1, 2026) - Model Update                       │
│  Overall Score: 89 (+4, +4.71%)                               │
│  [View Comparison]                                            │
│                                                               │
│  [+ Retest Again]                                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Retest Scenarios

### Scenario 1: Verification Retest

**Use Case:** User wants to verify original results are consistent

**Configuration:**
- Same benchmark version
- Same methodology
- Reason: "Verification"

**Expected Outcome:**
- Similar scores (within 2-3 points)
- Comparison shows consistency
- Builds confidence in results

### Scenario 2: Model Update Retest

**Use Case:** Model provider released an update, user wants to test new version

**Configuration:**
- Same benchmark version (if available)
- Current methodology
- Reason: "Model Update"

**Expected Outcome:**
- May show improvement or regression
- Comparison highlights changes
- Helps track model evolution

### Scenario 3: Improvement Validation

**Use Case:** Developer retests after fine-tuning to measure improvement

**Configuration:**
- Same benchmark version
- Current methodology
- Reason: "Improvement Validation"

**Expected Outcome:**
- Should show score improvement
- Comparison validates improvements
- Documents model development progress

### Scenario 4: Research/Tracking

**Use Case:** Researcher tracks model performance over time

**Configuration:**
- Current benchmark version (may change)
- Current methodology (may change)
- Reason: "Research/Tracking"

**Expected Outcome:**
- Historical tracking data
- May show trends across versions
- Research dataset for analysis

---

## Comparison Logic

### Score Comparison

**Calculate deltas:**
- `delta = retest_score - original_score`
- `percent_change = (delta / original_score) * 100`

**Significance threshold:**
- Changes >5% considered significant
- Changes <5% considered minor variation

### Verdict Comparison

**Compare verdict distributions:**
- Count changes per verdict type
- Calculate percentage changes
- Identify patterns (more acceptances, fewer refusals, etc.)

### Category Comparison

**Compare category scores:**
- Identify improved categories (higher score)
- Identify declined categories (lower score)
- Calculate category-level deltas

---

## Edge Cases

### Model No Longer Available

**Scenario:** Original model is discontinued or unavailable

**Handling:**
- Show warning: "Model no longer available"
- Suggest similar models if available
- Allow retest with different model (document as different test)

### Version Mismatch

**Scenario:** User retests with different benchmark version

**Handling:**
- Show clear warning about version difference
- Comparison may be less meaningful
- Document version difference in comparison

### Multiple Retests

**Scenario:** User has multiple retests of same original test

**Handling:**
- Show retest history
- Allow comparing any retest with original
- Allow comparing retests with each other
- Show timeline of retests

### Incomplete Retest

**Scenario:** Retest encounters errors during execution

**Automatic Recovery (Transparent to User):**
- System saves checkpoint after each question
- On error, system automatically retries from checkpoint (not from beginning)
- Up to 3 retry attempts with exponential backoff (30s → 60s → 120s)
- User may see brief "reconnecting" message but test continues

**After 3 Failed Retry Attempts:**
- System alerts administrator(s)
- User is presented with two options:
  1. **Wait for admin completion**: Admin manually completes remaining questions, then comparison is generated
  2. **Request refund now**: Full refund processed, no comparison created

**Admin Completion Path:**
- Admin investigates failure cause
- Admin manually runs remaining questions (possibly with different configuration)
- Results merged with checkpoint data
- Comparison generated once retest is complete
- User notified via email

**Handling:**
- Checkpoint preserved even if user requests refund (for debugging)
- Comparison only created when retest fully completes
- Partial retests do not affect original test results

---

## Performance Considerations

### Cost Optimization

- **Same version retest:** May use cached question set
- **Cost estimation:** Accurate estimate before payment
- **Refund policy:** Same as new tests

### Data Storage

- **Retest relationships:** Store links between tests
- **Comparison caching:** Cache comparison results
- **History tracking:** Maintain retest history

---

## Accessibility

### WCAG Level A Compliance

- **Keyboard navigation:** Full keyboard support
- **Screen reader support:** Announce comparison results
- **Color contrast:** Minimum 4.5:1 for all text
- **Status indicators:** Text labels for up/down arrows

### Screen Reader Announcements

- "Retest initiated, estimated cost $20.00"
- "Retest completed, overall score improved by 2 points"
- "Comparison available, 2 categories improved"

---

## Future Enhancements

### Phase 2 Features

- **Bulk retest:** Retest multiple models at once
- **Scheduled retests:** Automatically retest on schedule
- **Retest alerts:** Notify when model updates available
- **Statistical analysis:** Advanced comparison analytics

### Phase 3 Features

- **Retest recommendations:** Suggest when to retest
- **Trend analysis:** Multi-retest trend visualization
- **Automated retesting:** Auto-retest on model updates
- **Retest API:** Programmatic retest initiation

---

## Testing Requirements

### Unit Tests

- Retest request validation
- Comparison calculation
- Delta calculations
- Significance determination

### Integration Tests

- Retest workflow
- Payment processing
- Comparison generation
- History tracking

### E2E Tests

- Complete retest flow
- Comparison display
- Retest history
- Multiple retests

---

## Related Features

- **User Dashboard** — Retest initiation and history (see feature-user-dashboard.md)
- **Model Comparison** — Compare retest with original (see feature-model-comparison.md)
- **Test Execution** — Same execution flow as new tests

---

## Open Questions

1. **Should retests be free for users who already paid for original test?**
   - Recommendation: No, retests are separate tests requiring payment

2. **Should we limit number of retests per original test?**
   - Recommendation: No limit, but track for abuse prevention

3. **How should we handle retests when benchmark version changes significantly?**
   - Recommendation: Warn user, allow but document version difference

4. **Should retests appear on leaderboard separately or replace original?**
   - Recommendation: Show best result (highest score) as primary, with retest history

---

*Last Updated: December 16, 2025*
