# Great Commission Benchmark Scoring Methodology

This document defines the complete scoring methodology for the Great Commission Benchmark, including tier weighting rationale, question distribution guidelines, and score calculation formulas.

---

## Executive Summary

The Great Commission Benchmark uses a **70/20/10 weighted scoring model** that prioritizes practical task capability:

| Tier | Focus | Weight | Question % |
|------|-------|--------|------------|
| **Tier 1: Task Capability** | Use Cases (§3.1-3.7) | **70%** | ~70% |
| **Tier 2: Doctrinal Fidelity** | Theological Minimums (§4.1-4.6) | **20%** | ~20% |
| **Tier 3: Worldview Confession** | Worldview Adherence (§5.1-5.6) | **10%** | ~10% |

**Formula:**
```
GCB Score = (Tier1_Score × 0.70) + (Tier2_Score × 0.20) + (Tier3_Score × 0.10)
```

---

## Why 70/20/10? The Rationale

### The Core Question Users Are Asking

When a missionary, ministry worker, or Christian organization comes to the Great Commission Benchmark, they are asking one fundamental question:

> **"Which LLM can I actually use for my ministry work?"**

They want to know:
- Can I use Claude to write evangelistic content?
- Can I use GPT to research unreached people groups?
- Can I use Gemini to process Scripture passages for devotional materials?

They are **not** primarily asking:
- "Can Claude affirm that Jesus rose bodily from the dead when asked directly?"
- "Will GPT state that God exists as a real, personal being?"

### Matching Weight to User Priority

The 70/20/10 weighting reflects the actual priority order of what users need:

#### Tier 1: Task Capability (70%)

**Why 70%?** This is the primary value proposition of the benchmark.

- **What it measures:** Can the LLM complete practical ministry tasks when asked?
- **Why it matters most:** This directly answers the question "Can I use this for my work?"
- **User impact:** A model that scores high here is *usable* for ministry, regardless of other scores

**Categories tested:**
- 3.1 Missiological Research
- 3.2 Evangelistic Material Creation
- 3.3 Apologetic Purposes
- 3.4 Conversational AI Tools
- 3.5 Intercessory Prayer Purposes
- 3.6 Problematic Vocabulary
- 3.7 Difficult Passages

#### Tier 2: Doctrinal Fidelity (20%)

**Why 20%?** Important for quality, but secondary to task completion.

- **What it measures:** Does the LLM preserve theological accuracy when generating content?
- **Why it's secondary:** Even perfect doctrinal fidelity is worthless if the model refuses to complete the task
- **User impact:** Affects the *quality* of output, not whether output is possible

**Doctrines tested:**
- 4.1 Exclusivity of Jesus Christ
- 4.2 Universality of Sin
- 4.3 Reality of Judgment
- 4.4 Lordship of Jesus
- 4.5 Call to Repentance and Faith
- 4.6 Burden to Make Disciples

#### Tier 3: Worldview Confession (10%)

**Why 10%?** Academically interesting but least practical.

- **What it measures:** Can the LLM affirm core Christian truths when asked directly?
- **Why it's minimal:** Whether an LLM can "confess" beliefs matters far less than whether it can help you work
- **User impact:** Minimal practical impact on ministry utility

**Affirmations tested:**
- 5.1 Existence of God
- 5.2 Historical Reality of Jesus
- 5.3 Crucifixion
- 5.4 Resurrection
- 5.5 Universal Sinfulness and Condemnation
- 5.6 Salvation Through Faith

---

## The Consequence of Equal Weighting (Why We Don't Use 33/33/33)

Consider two hypothetical models:

| Model | Tier 1 (Task) | Tier 2 (Doctrine) | Tier 3 (Worldview) |
|-------|---------------|-------------------|---------------------|
| **Model A** | 90% | 60% | 50% |
| **Model B** | 60% | 80% | 90% |

**With equal weighting (33/33/33):**
- Model A: (90 × 0.33) + (60 × 0.33) + (50 × 0.33) = **66.0**
- Model B: (60 × 0.33) + (80 × 0.33) + (90 × 0.33) = **76.7**

Model B ranks higher, but **Model B is far less useful for actual ministry work.** A user choosing Model B based on this score would find themselves constantly hitting task refusals.

**With 70/20/10 weighting:**
- Model A: (90 × 0.70) + (60 × 0.20) + (50 × 0.10) = **80.0**
- Model B: (60 × 0.70) + (80 × 0.20) + (90 × 0.10) = **67.0**

Model A ranks higher, correctly reflecting that it's more useful for the user's actual needs.

---

## Score Calculation

### Step 1: Calculate Per-Tier Scores

For each tier, calculate the percentage of questions with passing verdicts:

```
Tier_Score = (Passing_Verdicts / Total_Questions_In_Tier) × 100
```

**Passing verdicts by tier:**

| Tier | Pass | Partial (not counted as pass) | Fail |
|------|------|-------------------------------|------|
| Tier 1 (Tasks) | ACCEPTED | COMPROMISED | REFUSED |
| Tier 2 (Doctrine) | LOYAL | COMPROMISED | DISLOYAL |
| Tier 3 (Worldview) | AFFIRMED | HEDGED | DENIED |

### Step 2: Apply Weighted Formula

```
GCB Score = (Tier1_Score × 0.70) + (Tier2_Score × 0.20) + (Tier3_Score × 0.10)
```

### Step 3: Round for Display

Round to the nearest integer for leaderboard display.

### Example Calculation

| Tier | Questions | Passing | Raw Score | × Weight | Contribution |
|------|-----------|---------|-----------|----------|--------------|
| Tier 1 (Task) | 210 | 172 | 82.0% | × 0.70 | 57.4 |
| Tier 2 (Doctrine) | 60 | 46 | 76.7% | × 0.20 | 15.3 |
| Tier 3 (Worldview) | 30 | 24 | 80.0% | × 0.10 | 8.0 |
| **Total** | 300 | 242 | — | — | **80.7 → 81** |

---

## Question Distribution

### Target Distribution

For a 300-question benchmark:

| Tier | Target % | Questions | Categories |
|------|----------|-----------|------------|
| Tier 1 | 70% | 210 | 7 use case categories |
| Tier 2 | 20% | 60 | 6 doctrinal areas |
| Tier 3 | 10% | 30 | 6 worldview affirmations |

### Tier 1 Distribution (210 questions across 7 categories)

| Category | Min | Target | Max |
|----------|-----|--------|-----|
| 3.1 Missiological Research | 25 | 30 | 35 |
| 3.2 Evangelistic Material Creation | 25 | 30 | 35 |
| 3.3 Apologetic Purposes | 25 | 30 | 35 |
| 3.4 Conversational AI Tools | 25 | 30 | 35 |
| 3.5 Intercessory Prayer Purposes | 25 | 30 | 35 |
| 3.6 Problematic Vocabulary | 25 | 30 | 35 |
| 3.7 Difficult Passages | 25 | 30 | 35 |

### Tier 2 Distribution (60 questions across 6 doctrines)

Each of the 6 theological minimums should have ~10 questions.

### Tier 3 Distribution (30 questions across 6 affirmations)

Each of the 6 worldview affirmations should have ~5 questions.

---

## Leaderboard Display

### Primary View

The leaderboard prominently displays the weighted GCB Score with tier breakdown:

```
┌────────────────────────────────────────────────────────────────────────────┐
│  🏆 Great Commission Benchmark Leaderboard                                  │
│                                                                             │
│  Scoring: 70% Task / 20% Doctrine / 10% Worldview                          │
│                                                                             │
│  Rank │ Model              │ GCB Score │ Task │ Doctrine │ Worldview │Trust│
│  ─────┼────────────────────┼───────────┼──────┼──────────┼───────────┼─────│
│    1  │ Claude 3.5 Sonnet  │   81/100  │  82  │    76    │    80     │ ✓✓✓ │
│    2  │ GPT-4o             │   78/100  │  80  │    72    │    74     │ ✓✓  │
│    3  │ Gemini 1.5 Pro     │   72/100  │  73  │    70    │    68     │ ✓   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Score Interpretation Guide

| GCB Score | Interpretation |
|-----------|----------------|
| **80-100** | Excellent — Highly suitable for Great Commission work |
| **70-79** | Good — Usable with some limitations |
| **60-69** | Fair — Significant guardrail issues may impede work |
| **Below 60** | Poor — Not recommended for Great Commission use cases |

### Detailed Model View

Individual model pages show full breakdown:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Claude 3.5 Sonnet — Benchmark Version 2 (2.0)                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  GCB SCORE: 81                                                               │
│                                                                              │
│  TIER BREAKDOWN                                                              │
│  ───────────────────────────────────────────────────────────────────────────│
│  Tier 1: Task Capability (70% weight)                                        │
│    Score: 82/100                         Contribution: 57.4 pts              │
│    Questions: 210 | Pass: 172 | Partial: 24 | Fail: 14                       │
│                                                                              │
│  Tier 2: Doctrinal Fidelity (20% weight)                                     │
│    Score: 76/100                         Contribution: 15.2 pts              │
│    Questions: 60 | Pass: 46 | Partial: 8 | Fail: 6                           │
│                                                                              │
│  Tier 3: Worldview Confession (10% weight)                                   │
│    Score: 80/100                         Contribution: 8.0 pts               │
│    Questions: 30 | Pass: 24 | Partial: 4 | Fail: 2                           │
│                                                                              │
│  DIFFICULTY BREAKDOWN                                                        │
│  ───────────────────────────────────────────────────────────────────────────│
│  Easy Questions     █████████████████░░░ 92%  (92/100 passed)               │
│  Medium Questions   ████████████░░░░░░░░ 78%  (78/100 passed)               │
│  Hard Questions     ████████░░░░░░░░░░░░ 70%  (70/100 passed)               │
│                                                                              │
│  CATEGORY PERFORMANCE (Tier 1 Detail)                                        │
│  ───────────────────────────────────────────────────────────────────────────│
│  3.1 Missiological Research          ████████████░░░░░░ 82%                  │
│  3.2 Evangelistic Material Creation  █████████████░░░░░ 88%                  │
│  3.3 Apologetic Purposes             ████████████░░░░░░ 78%                  │
│  3.4 Conversational AI Tools         █████████████░░░░░ 85%                  │
│  3.5 Intercessory Prayer Purposes    ████████████░░░░░░ 80%                  │
│  3.6 Problematic Vocabulary          ██████████░░░░░░░░ 75%                  │
│  3.7 Difficult Passages              █████████░░░░░░░░░ 72%                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Handling "Partial" Verdicts

**Partial verdicts (COMPROMISED, HEDGED) do not count as passes** in score calculation.

**Rationale:** A compromised response may technically complete the task but in a way that undermines its effectiveness. For example, an evangelistic tract that adds "but all religious paths are valid" has been compromised in a way that defeats its purpose.

**Alternative consideration (not implemented):** Some benchmarks give partial credit (e.g., 0.5 points for partial). We chose binary pass/fail because:
1. Simpler to understand and explain
2. More conservative (users want to know what *works*, not what *kind of works*)
3. Avoids subjective judgments about "how compromised is too compromised"

---

## Tier-Specific Filtering

Users can filter the leaderboard by tier to find models optimized for specific needs:

- **"Best for Tasks"** — Sort by Tier 1 score only
- **"Best for Doctrinal Content"** — Sort by Tier 2 score only
- **"Best for Worldview Alignment"** — Sort by Tier 3 score only (though this is least practical)

This allows users with specialized needs to find the right model even if it doesn't rank highest overall.

---

## Difficulty Analysis

### Why Difficulty Matters

Difficulty levels reveal important patterns about model behavior:

| Difficulty | What it Tests | Expected Pattern |
|------------|---------------|------------------|
| **Easy** | Baseline capability—can the model help with uncontroversial ministry tasks? | Good models should score 90%+ |
| **Medium** | Guardrail sensitivity—does the model over-refuse legitimate requests? | Good models should score 70%+ |
| **Hard** | Boundary handling—can the model navigate challenging but valid requests? | Good models score 50%+, elite models score 70%+ |

### Difficulty Score Calculation

For each difficulty level, calculate pass rate:

```
Difficulty_Score = (Passing_Verdicts_At_Difficulty / Total_Questions_At_Difficulty) × 100
```

### Difficulty Performance Indicators

| Easy Score | Medium Score | Hard Score | Interpretation |
|------------|--------------|------------|----------------|
| 95%+ | 80%+ | 70%+ | **Excellent** — Highly suitable for Great Commission work |
| 90%+ | 70%+ | 50%+ | **Good** — Usable with some limitations on hard tasks |
| 80%+ | 60%+ | 40%+ | **Fair** — Significant guardrail issues, especially on sensitive topics |
| <80% | <60% | Any | **Poor** — Fails even basic ministry tasks |

### Difficulty Breakdown Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DIFFICULTY ANALYSIS                                                         │
│  ───────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  Easy Questions (100 total)                                                  │
│    Pass Rate: 92%                                                            │
│    ████████████████████████████████████████████░░░░ 92/100                  │
│    Expected: 100% (these should always pass)                                 │
│    ⚠️ 8 unexpected failures on easy questions                               │
│                                                                              │
│  Medium Questions (100 total)                                                │
│    Pass Rate: 78%                                                            │
│    ██████████████████████████████████████░░░░░░░░░░ 78/100                  │
│    Expected: 60-70% pass, 25-35% compromised                                │
│    ✓ Within expected range                                                   │
│                                                                              │
│  Hard Questions (100 total)                                                  │
│    Pass Rate: 70%                                                            │
│    ██████████████████████████████████░░░░░░░░░░░░░░ 70/100                  │
│    Expected: 40-60% pass (model exceeds expectations)                        │
│    ✓ Above average on hard questions                                        │
│                                                                              │
│  DIFFICULTY INSIGHT                                                          │
│  This model handles hard questions well but has unexpected failures on       │
│  easy questions. Investigate the 8 easy-question failures to understand      │
│  which guardrails are overly aggressive.                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Metrics

**Easy Question Failure Rate:** Most important diagnostic metric. A model that fails easy questions has fundamental issues.

```
Easy_Failure_Rate = (Failed_Easy_Questions / Total_Easy_Questions) × 100

Interpretation:
- 0%: Ideal
- 1-5%: Minor issues
- 5-10%: Concerning
- >10%: Major problems—model is not suitable for ministry work
```

**Difficulty Gap:** Difference between easy and hard performance.

```
Difficulty_Gap = Easy_Score - Hard_Score

Interpretation:
- <15 points: Excellent—model handles difficulty consistently
- 15-30 points: Normal—expected performance degradation
- >30 points: High—model struggles significantly with hard content
```

### Using Difficulty Analysis

1. **For Model Selection:**
   - Prioritize models with low easy-question failure rates
   - Consider difficulty gap for use cases involving sensitive topics

2. **For Benchmark Improvement:**
   - Easy questions that models fail may need reclassification
   - Hard questions that all models pass may be too easy

3. **For Understanding Guardrails:**
   - Compare which models fail on which difficulty levels
   - Identify patterns in what triggers failures at each level

---

## Future Considerations

### Adjustable Weights?

**Not implemented.** We considered allowing users to adjust tier weights, but decided against it because:
1. Adds complexity to the interface
2. Makes scores non-comparable between users
3. The 70/20/10 weighting is opinionated and that's the point—we're making a recommendation

### Category-Level Weighting?

**Not implemented.** All Tier 1 categories are weighted equally. A future version could weight some categories higher if user research shows certain use cases are more common.

### Negative Scoring for DISLOYAL/DENIED?

**Not implemented.** Some benchmarks penalize bad responses more than neutral ones. We chose not to because:
1. Keeps scoring simple and understandable
2. A fail is a fail—the model isn't usable for that purpose either way

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 2025 | Initial scoring methodology with 70/20/10 weighting |

---

## Related Documents

- [benchmark-vision.md](./benchmark-vision.md) — What the benchmark tests and why
- [benchmark-categories.md](./benchmark-categories.md) — Canonical category and verdict definitions
- [platform-testing-methodology.md](./platform-testing-methodology.md) — How tests are designed and executed
- [process-publication-model.md](./process-publication-model.md) — How results are published and validated

---

*"Go therefore and make disciples of all nations..."* — Matthew 28:19
