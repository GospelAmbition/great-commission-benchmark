# Core: Publication Model

This document defines the criteria and process for publishing benchmark results. It implements a **Progressive Trust Model** where results publish immediately after automated validation, with human review adding credibility over time.

---

## Design Principles

1. **Self-service first** — Users can run and publish tests without waiting for human approval
2. **Transparency over gatekeeping** — Show what's been verified, don't hide limitations
3. **Progressive credibility** — Results gain trust as more validation accumulates
4. **No artificial bottlenecks** — Human reviewer scarcity shouldn't block publication
5. **Instant publication** — Automated validation success means immediate visibility

---

## Publication Criteria

### Automated Criteria (Required for Publication)

These must pass before any result appears on the leaderboard:

| Criterion | Threshold | How It's Measured |
|-----------|-----------|-------------------|
| **Inter-rater reliability** | ≥80% | LLM-judge verdicts compared against calibration set with known human verdicts |
| **Reproducibility** | ≥95% | Same model + same questions re-run produces identical verdicts |
| **Differentiation** | Meaningful variance | Results must not cluster (e.g., all models scoring 88-92%) |

### Human Review Criteria (Additive)

These don't block publication but increase trust level when completed:

| Criterion | Description |
|-----------|-------------|
| **Spot-check** | Trusted reviewer examines random sample of verdicts and confirms accuracy |
| **Methodology review** | Reviewer confirms test execution followed documented procedures |

---

## Trust Tiers

Each published result displays its current trust level:

| Tier | Label | Requirements |
|------|-------|--------------|
| **Tier 1** | `Automated` | Passed all automated criteria |
| **Tier 2** | `Reviewed` | 1-2 human spot-checks completed |
| **Tier 3** | `Fully Validated` | 3+ human reviewers have confirmed |

### Display Example

```
┌─────────────────────────────────────────────────────────────────┐
│  Claude 3.5 Sonnet — Benchmark v1.0                             │
│  Overall Score: 78/100                                          │
│                                                                 │
│  Validation Status: Reviewed ✓✓                                 │
│  ├─ Inter-rater reliability: 84% ✓                              │
│  ├─ Reproducibility: 97% ✓                                      │
│  ├─ Differentiation: Passed ✓                                   │
│  └─ Human spot-checks: 2 of 3 ✓✓⬜                              │
│                                                                 │
│  Tested: Dec 14, 2024 | Last reviewed: Dec 15, 2024             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Publication Flow

### 1. Test Execution

User initiates test via hosted platform:
- Benchmark runs against selected model
- Raw responses and verdicts captured
- Execution metadata recorded (timestamps, model version, question set version)

### 2. Automated Validation

System performs validation checks:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Inter-rater     │────▶│ Reproducibility │────▶│ Differentiation │
│ Reliability     │     │ Check           │     │ Check           │
│ (vs calibration)│     │ (re-run sample) │     │ (vs other       │
│                 │     │                 │     │  models)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Pass/Fail              Pass/Fail               Pass/Fail
```

**If all pass:** Result publishes immediately with "Automated" trust tier

**If any fail:** Result held; user notified of specific failure with guidance

### 3. Immediate Publication

Results appear on leaderboard with:
- Full scores and category breakdowns
- Clear "Automated" badge
- Visible validation metrics
- "Awaiting human review" indicator

**Publication timing:** Instant upon automated validation success. There is no queue or delay.

### 4. Asynchronous Human Review

Moderators review published results on their own schedule:

1. **Claim a review** — Moderator selects result from queue
2. **Spot-check verdicts** — Examine random sample (e.g., 20 questions)
3. **Confirm or flag** — Mark as verified or raise concerns
4. **Trust tier updates** — Result's validation status reflects new review

See [decision-moderation-process.md](./decision-moderation-process.md) for complete moderator workflows.

### 5. Progressive Trust Accumulation

Over time, results accumulate reviews:

```
Day 1:  Automated ⬜⬜⬜
Day 3:  Reviewed  ✓⬜⬜  (first spot-check)
Day 7:  Reviewed  ✓✓⬜  (second spot-check)
Day 14: Fully Validated ✓✓✓
```

---

## Validation Failure Handling

### Inter-rater Reliability Failure (<80%)

**Possible causes:**
- Judge prompt needs recalibration
- Question set has ambiguous items
- Model produces unusual response patterns

**Resolution path:**
1. Flag result for methodology review
2. Examine specific disagreements
3. Either: recalibrate judge, or exclude problematic questions from this run

### Reproducibility Failure (<95%)

**Possible causes:**
- Model has high temperature/randomness
- API returned different model version
- Network/timeout issues corrupted responses

**Resolution path:**
1. Check model configuration (temperature should be 0 or low)
2. Verify API is returning consistent model
3. Re-run with stricter parameters

### Differentiation Failure

**Possible causes:**
- Question set is too easy (all models ace it)
- Question set is too hard (all models fail)
- Scoring is too coarse-grained

**Resolution path:**
1. Review score distribution across models
2. Adjust question difficulty or add discriminating questions
3. Refine scoring granularity

---

## Calibration Set

A **calibration set** is a curated subset of questions with human-verified "correct" verdicts. This serves as ground truth for inter-rater reliability checks.

### Calibration Set Requirements

- Minimum 50 questions across all categories
- Each question has 3+ human reviewers agree on verdict
- Covers edge cases and clear-cut cases
- Updated when benchmark version changes

### Calibration Process

1. Select diverse questions from full set
2. Collect human verdicts (multiple reviewers per question)
3. Retain questions with ≥80% human agreement
4. Document disagreements for methodology refinement

---

## Reviewer Guidelines

### Who Can Review

Moderators are users with a special role granting elevated permissions:

- Moderator status is tied to their user account
- Accounts include credentials/qualifications on record
- Selected by the founding committee based on:
  - Background and expertise
  - Special interest in the benchmark's mission
  - Community involvement and standing

See [decision-moderation-process.md](./decision-moderation-process.md) for selection criteria.

### Review Process

1. **Select result** from review queue (prioritize oldest unreviewed)
2. **Examine sample** of 20 randomly selected verdicts
3. **For each verdict:**
   - Read the question and model response
   - Read the LLM-judge's verdict and reasoning
   - Mark as: `Agree` / `Disagree` / `Unsure`
4. **Submit review** with overall assessment:
   - `Verified` — Verdicts appear accurate
   - `Concerns` — Significant disagreements, flag for discussion
5. **Optional notes** — Document any patterns or issues observed

### Disagreement Handling

If a reviewer marks `Concerns`:
1. Result remains published but flagged
2. Second reviewer assigned
3. If second reviewer also flags: escalate to methodology review
4. Resolution documented; result updated or withdrawn

### Moderator Disagreement Escalation

If moderators cannot reach consensus on whether to approve a submission:
1. Issue escalates to a designated **committee**
2. The **chair of the committee** makes the final decision
3. Decision is documented and binding

---

## Activity Logging

The system maintains an **activity log** tracking each moderator's review history and actions:

- Reviews completed
- Verdicts given
- Concerns raised
- Time to review
- Patterns in agreement/disagreement with other moderators

This supports:
- Quality assurance
- Moderator accountability
- Identifying training needs
- Detecting systematic biases

---

## Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| What's the minimum sample size for spot-checks? | 20 questions |
| Should there be a time limit for "Automated" tier before auto-escalation? | No—low traffic means async review is sufficient |
| How do we handle borderline reproducibility (e.g., 93%)? | Fail and re-run with stricter parameters |
| Should users see which specific reviewers validated a result? | Just count, not names (privacy) |

---

## Related Documents

- [Deployment Vision](./core-deployment-vision.md) — Overall deployment strategy
- [Testing Methodology](./core-testing-methodology.md) — How tests are executed
- [Moderation Process](./decision-moderation-process.md) — Moderator selection and workflows
- [Question Security](./decision-question-security.md) — Question protection and versioning
