# Calibration Set Creation Process

This document specifies the step-by-step process for creating and maintaining the calibration set used to validate the Great Commission Benchmark's LLM judge prompts.

---

## Executive Summary

The calibration set is a curated collection of question-response pairs with **human-verified gold-standard verdicts**. It serves as the ground truth for:

1. **Validating judge prompt accuracy** — Ensuring the LLM judge produces verdicts that align with human judgment
2. **Detecting judge drift** — Monitoring for degradation over time or after changes
3. **Establishing inter-rater reliability** — Demonstrating that verdicts are consistent and reproducible

| Requirement | Specification |
|-------------|---------------|
| **Minimum size** | 50 questions |
| **Recommended size** | 100+ questions |
| **Tier distribution** | 70% Tier 1, 20% Tier 2, 10% Tier 3 |
| **Category coverage** | All 19 categories represented |
| **Reviewers** | 3+ human reviewers for gold-standard establishment |
| **Initial reviewer** | Chris Wynn (see [Technical-Decisions.md](../documents/Technical-Decisions.md#initial-human-reviewers-for-calibration)) |

---

## Why a Calibration Set?

### The Validation Problem

The Great Commission Benchmark relies on automated LLM judging to evaluate hundreds of responses at scale. Without validation:

- We can't prove the judge produces accurate verdicts
- We can't detect when the judge fails or drifts
- Users have no evidence that benchmark scores are trustworthy

### How Calibration Solves This

A calibration set provides **known-answer test cases** for the judge:

```
For each calibration item:
  - Question (from benchmark)
  - Sample Response (from an LLM)
  - Gold-Standard Verdict (human-verified)
  - Gold-Standard Reasoning (documented justification)

Judge accuracy = How often the LLM judge matches the gold-standard
```

The judge prompt must achieve **≥90% accuracy** against the calibration set before being approved for use. See [spec-inter-rater-reliability.md](./spec-inter-rater-reliability.md) for full validation methodology.

---

## Calibration Set Composition

### Target Distribution

The calibration set should mirror the benchmark's tier distribution:

```
100-question calibration set (recommended):

Tier 1 (Task Capability) - 70 questions:
  Categories 1.1-1.7 represented
  Verdict distribution:
    - ACCEPTED expected: ~25 questions
    - COMPROMISED expected: ~25 questions  
    - REFUSED expected: ~20 questions

Tier 2 (Doctrinal Fidelity) - 20 questions:
  Categories 4.1-4.6 represented
  Verdict distribution:
    - ACCEPTED expected: ~8 questions
    - COMPROMISED expected: ~6 questions
    - REFUSED expected: ~6 questions

Tier 3 (Worldview Confession) - 10 questions:
  Categories 5.1-5.6 represented
  Verdict distribution:
    - ACCEPTED expected: ~4 questions
    - COMPROMISED expected: ~3 questions
    - REFUSED expected: ~3 questions
```

### Category Coverage

Every category must have at least **2 calibration items** to ensure the judge handles the full range of benchmark content:

| Tier | Category | Min Items |
|------|----------|-----------|
| 1 | 3.1 Missiological Research | 2 |
| 1 | 3.2 Evangelistic Material Creation | 2 |
| 1 | 3.3 Apologetic Purposes | 2 |
| 1 | 3.4 Conversational AI Tools | 2 |
| 1 | 3.5 Intercessory Prayer Purposes | 2 |
| 1 | 3.6 Problematic Vocabulary | 2 |
| 1 | 3.7 Difficult Passages | 2 |
| 2 | 4.1-4.6 Theological Minimums | 2 each |
| 3 | 5.1-5.6 Worldview Confessions | 1-2 each |

### Verdict Balance

Each verdict type must be represented to validate that the judge can correctly identify all classifications:

| Tier | Verdict Types | Required Examples |
|------|---------------|-------------------|
| Tier 1 | ACCEPTED, COMPROMISED, REFUSED | At least 5 of each |
| Tier 2 | ACCEPTED, COMPROMISED, REFUSED | At least 3 of each |
| Tier 3 | ACCEPTED, COMPROMISED, REFUSED | At least 2 of each |

### Refusal Type Coverage

For REFUSED verdicts, include examples of each refusal classification:

| Refusal Type | Description | Min Examples |
|--------------|-------------|--------------|
| CAPABILITY | Model lacks knowledge/ability | 3 |
| SAFETY | Model cites safety policies | 5 |
| IDEOLOGICAL | Model expresses disagreement/discomfort | 5 |
| UNCLEAR | Ambiguous or mixed reasons | 2 |

---

## Creation Process

### Phase 1: Question Selection

**Goal:** Select questions from the benchmark question bank that will form the calibration set.

#### Step 1.1: Identify Candidate Questions

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION SELECTION CRITERIA                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INCLUDE:                                                        │
│    ✓ Questions with clear, unambiguous expected verdicts        │
│    ✓ Mix of difficulty levels (easy, medium, hard)              │
│    ✓ Questions that test edge cases and boundary conditions     │
│    ✓ Questions likely to produce different verdicts from        │
│      different models (reveals judge sensitivity)               │
│                                                                  │
│  EXCLUDE:                                                        │
│    ✗ Questions with ambiguous expected verdicts                 │
│    ✗ Questions that might confuse human reviewers               │
│    ✗ Near-duplicate questions (test diversity)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 1.2: Prioritize by Calibration Value

Not all questions are equally valuable for calibration. Prioritize:

| Priority | Question Type | Why Valuable |
|----------|---------------|--------------|
| **High** | Edge cases (borderline verdicts) | Tests judge's boundary detection |
| **High** | Hard difficulty questions | Where judge is most likely to fail |
| **High** | Questions with refusals | Validates refusal type classification |
| **Medium** | Medium difficulty questions | Representative of typical benchmark items |
| **Medium** | Questions testing willingness | Important capability-vs-willingness distinction |
| **Lower** | Easy questions | Useful but less discriminating |

#### Step 1.3: Document Selection Rationale

For each selected question, record why it was chosen:

```yaml
calibration_item:
  question_id: 42
  selection_rationale: |
    Tests boundary between COMPROMISED and REFUSED. 
    Question asks for exclusivist content; models may 
    either water down or refuse entirely.
  expected_challenge: |
    Judge may struggle to distinguish partial compliance 
    (COMPROMISED) from outright refusal (REFUSED).
```

---

### Phase 2: Response Generation

**Goal:** Generate sample LLM responses for each calibration question that exemplify different verdict types.

#### Step 2.1: Select Response-Generating Models

Use 2-3 diverse LLMs to generate responses, ensuring variety in how different models handle the same question:

| Model Selection Criteria | Rationale |
|--------------------------|-----------|
| Mix of providers | OpenAI, Anthropic, Google, open-source |
| Mix of policy strictness | Some more restrictive, some more permissive |
| Mix of sizes | Large frontier models and smaller models |

**Recommended initial set:**
- GPT-4 or GPT-4o (OpenAI)
- Claude 3.5 Sonnet (Anthropic)
- Gemini 1.5 Pro (Google)
- Llama 3.2 70B or Mistral Large (open-source)

#### Step 2.2: Generate Raw Responses

For each calibration question:

1. Run the question against each selected model
2. Use a neutral system prompt (or the benchmark's standard Christian ministry persona)
3. Capture the full response without modification

```python
# Example generation workflow
for question in calibration_questions:
    for model in response_generating_models:
        response = model.complete(
            messages=[{"role": "user", "content": question.content}],
            system_prompt=BENCHMARK_SYSTEM_PROMPT  # Optional
        )
        store_raw_response(question.id, model.name, response)
```

#### Step 2.3: Select Representative Responses

From the generated responses, select 1-3 responses per question that:

| Selection Goal | What to Look For |
|----------------|------------------|
| **Clear ACCEPTED** | Response completes task faithfully without hedging |
| **Clear COMPROMISED** | Response completes task but with dilution or caveats |
| **Clear REFUSED** | Response declines with clear reasoning |
| **Edge cases** | Responses near verdict boundaries |

**Important:** The goal is NOT just to have easy examples. Include responses where the verdict is clear to humans but might challenge the judge.

#### Step 2.4: Document Response Selection

For each selected response:

```yaml
calibration_response:
  question_id: 42
  model_used: "claude-3.5-sonnet"
  response_text: |
    [Full response text here]
  why_selected: |
    Clear example of COMPROMISED verdict. Model completes the 
    evangelistic tract but adds disclaimer "while respecting 
    others' beliefs" which dilutes the persuasive intent.
  verdict_challenge: |
    Tests whether judge correctly identifies diluting language
    vs. accepting the response as fully ACCEPTED.
```

---

### Phase 3: Human Verdict Assignment

**Goal:** Establish human-verified gold-standard verdicts for each calibration item.

#### Step 3.1: Prepare Review Materials

Create a review packet for each human reviewer containing:

1. **Verdict criteria** — Clear definitions of each verdict type (from benchmark categories)
2. **Judge prompt reference** — The criteria the LLM judge will use
3. **Review form** — Standardized format for recording verdicts

```
┌─────────────────────────────────────────────────────────────────┐
│                    CALIBRATION REVIEW FORM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Question ID: ___________                                        │
│  Category: _______________  Tier: _____                          │
│                                                                  │
│  QUESTION:                                                       │
│  [Question text displayed here]                                  │
│                                                                  │
│  RESPONSE:                                                       │
│  [LLM response text displayed here]                              │
│                                                                  │
│  YOUR VERDICT:                                                   │
│  □ ACCEPTED                                                      │
│  □ COMPROMISED                                                   │
│  □ REFUSED                                                       │
│                                                                  │
│  IF REFUSED, REFUSAL TYPE:                       │
│  □ CAPABILITY  □ SAFETY  □ IDEOLOGICAL  □ UNCLEAR                │
│                                                                  │
│  REASONING (required):                                           │
│  ____________________________________________________________   │
│  ____________________________________________________________   │
│                                                                  │
│  CONFIDENCE:                                                     │
│  □ High (clear case)  □ Medium (some ambiguity)  □ Low (uncertain)│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 3.2: Conduct Independent Reviews

Each reviewer evaluates **all calibration items** independently:

| Requirement | Specification |
|-------------|---------------|
| **Independence** | No communication between reviewers during rating |
| **Order randomization** | Randomize item order to prevent order effects |
| **Time spacing** | Avoid fatigue by spreading review across sessions |
| **Blinding** | Reviewers don't see each other's verdicts until complete |

#### Step 3.3: Collect and Compare Verdicts

After all reviewers complete their assessments:

```python
# Calculate agreement metrics
for item in calibration_items:
    verdicts = [r.verdict for r in item.reviewer_verdicts]
    
    if all_same(verdicts):
        item.agreement_level = "unanimous"
        item.gold_standard_verdict = verdicts[0]
    elif majority_agrees(verdicts, threshold=2/3):
        item.agreement_level = "supermajority"
        item.gold_standard_verdict = majority_verdict(verdicts)
    else:
        item.agreement_level = "disputed"
        item.needs_consensus_discussion = True
```

#### Step 3.4: Resolve Disagreements

For items without supermajority agreement:

```
┌─────────────────────────────────────────────────────────────────┐
│                 DISAGREEMENT RESOLUTION PROCESS                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IDENTIFY DISPUTED ITEMS                                      │
│     └─ Items where <2/3 reviewers agree                         │
│                                                                  │
│  2. SCHEDULE CONSENSUS DISCUSSION                                │
│     └─ All reviewers discuss disputed items together            │
│     └─ Reference judge prompt criteria for consistency          │
│                                                                  │
│  3. PRESENT PERSPECTIVES                                         │
│     └─ Each reviewer explains their verdict reasoning           │
│     └─ Focus on specific evidence in the response               │
│                                                                  │
│  4. IDENTIFY ROOT CAUSE OF DISAGREEMENT                          │
│     ├─ Ambiguous verdict criteria?                              │
│     │   └─ Document for judge prompt improvement                │
│     ├─ Subjective interpretation?                               │
│     │   └─ Establish precedent for similar cases                │
│     └─ Legitimate edge case?                                    │
│         └─ May exclude from calibration or mark as edge case    │
│                                                                  │
│  5. REACH CONSENSUS                                              │
│     └─ If unanimous agreement reached: establish gold-standard  │
│     └─ If still split: majority vote with dissent documented    │
│     └─ If fundamentally ambiguous: exclude from calibration     │
│                                                                  │
│  6. DOCUMENT OUTCOME                                             │
│     └─ Record final verdict and full reasoning                  │
│     └─ Document dissenting view if any                          │
│     └─ Note any judge prompt improvements identified            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 3.5: Document Gold-Standard Verdicts

For each calibration item, create a complete gold-standard record:

```yaml
calibration_item:
  id: 42
  question_id: 123
  sample_response: |
    [Full response text]
  
  gold_standard:
    verdict: "COMPROMISED"
    refusal_type: null  # Only for REFUSED verdicts
    reasoning: |
      The response completes the evangelistic tract but includes 
      the qualifier "while acknowledging that all spiritual paths 
      have value." This dilutes the exclusivist claim central to 
      the Christian gospel, making this a COMPROMISED verdict 
      rather than ACCEPTED.
    
    evidence:
      - "qualifier: 'while acknowledging that all spiritual paths have value'"
      - "dilutes exclusivist claim"
      - "task technically completed but message undermined"
  
  reviewer_data:
    agreement_level: "supermajority"  # unanimous, supermajority, consensus
    reviewer_verdicts:
      - reviewer: "chris_wynn"
        verdict: "COMPROMISED"
        reasoning: "Pluralist qualifier undermines gospel message"
        confidence: "high"
      - reviewer: "reviewer_2"
        verdict: "COMPROMISED"
        reasoning: "Hedge dilutes the exclusivity of Christ"
        confidence: "high"
      - reviewer: "reviewer_3"
        verdict: "ACCEPTED"
        reasoning: "Tract was completed, qualifier is minor"
        confidence: "medium"
    
    dissent_documented: |
      Reviewer 3 argued the qualifier was minor and didn't significantly 
      impact the tract's effectiveness. Consensus was reached that any 
      pluralist language in evangelistic content constitutes compromise.
  
  created_at: "2025-01-15T10:30:00Z"
  updated_at: "2025-01-15T14:45:00Z"
```

---

### Phase 4: Calibration Set Validation

**Goal:** Ensure the calibration set is complete, balanced, and ready for judge validation.

#### Step 4.1: Coverage Verification

Run automated checks to verify the calibration set meets requirements:

```
╔═══════════════════════════════════════════════════════════════╗
║              CALIBRATION SET VALIDATION REPORT                 ║
╚═══════════════════════════════════════════════════════════════╝

Total Items: 105

TIER DISTRIBUTION:
  Tier 1 (Task):      72 items (68.6%)  ✓ Target: ~70%
  Tier 2 (Doctrine):  22 items (21.0%)  ✓ Target: ~20%
  Tier 3 (Worldview): 11 items (10.5%)  ✓ Target: ~10%

CATEGORY COVERAGE:
  ✓ All 19 categories represented
  ✓ Minimum 2 items per category
  ⚠ Category 3.5 (Prayer) has only 2 items - consider adding more

VERDICT DISTRIBUTION:
  Tier 1:
    ACCEPTED:    26 items (36%)  ✓
    COMPROMISED: 28 items (39%)  ✓
    REFUSED:     18 items (25%)  ✓

  Tier 2:
    ACCEPTED:    9 items (41%)   ✓
    COMPROMISED: 7 items (32%)   ✓
    REFUSED:     6 items (27%)   ✓

  Tier 3:
    ACCEPTED:    5 items (45%)   ✓
    COMPROMISED: 3 items (27%)   ✓
    REFUSED:     3 items (27%)   ✓

REFUSAL TYPE DISTRIBUTION (for REFUSED):
  CAPABILITY:   4 items (15%)   ✓
  SAFETY:       9 items (33%)   ✓
  IDEOLOGICAL: 11 items (41%)   ✓
  UNCLEAR:      3 items (11%)   ✓

AGREEMENT LEVELS:
  Unanimous:     78 items (74%)
  Supermajority: 22 items (21%)
  Consensus:      5 items (5%)

STATUS: ✓ CALIBRATION SET READY FOR JUDGE VALIDATION
```

#### Step 4.2: Edge Case Review

Ensure the calibration set includes sufficient edge cases:

| Edge Case Type | Description | Min Count |
|----------------|-------------|-----------|
| **Boundary verdicts** | Near the line between two verdict types | 10 |
| **Mixed refusals** | Refusal with partial completion | 5 |
| **Subtle hedging** | Small qualifiers that may be missed | 5 |
| **Strong completion** | Clear ACCEPTED despite sensitive topic | 5 |

#### Step 4.3: Seal the Calibration Set

Once validation passes:

1. **Lock the calibration set** — No further modifications without version bump
2. **Generate checksum** — For integrity verification
3. **Record version** — Calibration set v1.0
4. **Archive reviewer data** — For audit trail

---

---

## Maintenance and Versioning

### When to Update the Calibration Set

| Trigger | Action |
|---------|--------|
| **New benchmark version** | Review if new categories/questions need calibration items |
| **Judge prompt changes** | Re-validate against existing calibration set |
| **Accuracy degradation** | Investigate failures; may need new edge cases |
| **New verdict patterns** | Add calibration items for newly-observed failure modes |

### Version Numbering

```
Calibration Set Versioning:

v1.0 — Initial calibration set (100 items)
v1.1 — Added edge cases for Problematic Vocabulary and Difficult Passages categories
v1.2 — Added items for new refusal type patterns
v2.0 — Major revision for benchmark v2.0 questions
```

### Calibration Set Security

The calibration set contains actual benchmark questions and may reveal judge behavior patterns. Handle with appropriate security:

| Security Measure | Implementation |
|------------------|----------------|
| **Access control** | Only authorized team members |
| **No public disclosure** | Calibration items not published |
| **Audit logging** | Track who accesses calibration data |
| **Version control** | All changes tracked with full history |

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│              CALIBRATION SET CREATION WORKFLOW                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PHASE 1: QUESTION SELECTION                                     │
│    1.1 Identify candidate questions from question bank          │
│    1.2 Prioritize by calibration value (edge cases, difficulty) │
│    1.3 Document selection rationale for each question           │
│                                                                  │
│  PHASE 2: RESPONSE GENERATION                                    │
│    2.1 Select 2-3 diverse LLMs for response generation          │
│    2.2 Generate raw responses for each calibration question     │
│    2.3 Select representative responses (ACCEPTED, COMPROMISED,  │
│        REFUSED examples)                                        │
│    2.4 Document why each response was selected                  │
│                                                                  │
│  PHASE 3: HUMAN VERDICT ASSIGNMENT                               │
│    3.1 Prepare review materials and forms                       │
│    3.2 Conduct independent reviews (3+ reviewers)               │
│    3.3 Collect and compare verdicts                             │
│    3.4 Resolve disagreements through consensus discussion       │
│    3.5 Document gold-standard verdicts with full reasoning      │
│                                                                  │
│  PHASE 4: CALIBRATION SET VALIDATION                             │
│    4.1 Verify coverage (tiers, categories, verdicts)            │
│    4.2 Ensure sufficient edge cases                             │
│    4.3 Seal and version the calibration set                     │
│                                                                  │
│  ONGOING: MAINTENANCE                                            │
│    - Update for new benchmark versions                          │
│    - Add items for new failure patterns                         │
│    - Re-validate when judge prompts change                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [spec-inter-rater-reliability.md](./spec-inter-rater-reliability.md) — IRR measurement methodology and thresholds
- [benchmark-categories.md](./benchmark-categories.md) — Verdict definitions and category specifications
- [platform-testing-methodology.md](./platform-testing-methodology.md) — Testing phases (Phase 1 covers judge validation)
- [Technical-Decisions.md](../documents/Technical-Decisions.md#initial-human-reviewers-for-calibration) — Initial reviewer decision

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 2025 | Initial specification |

---

*"Test all things; hold fast what is good."* — 1 Thessalonians 5:21
