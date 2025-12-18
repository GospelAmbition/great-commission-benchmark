# Specification: Test Results Submission

This document specifies the complete workflow for submitting test results from the CLI Runner to the GCB Platform for moderation and publication.

---

## Overview

When community testers run the benchmark locally using the CLI Runner, they can submit their results to the platform for inclusion on the public leaderboard. Unlike platform-hosted tests (which are auto-published), CLI submissions require moderator verification to ensure result integrity.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TEST RESULTS SUBMISSION FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                         ┌─────────────────┐           │
│   │                 │     JSON Export         │                 │           │
│   │   CLI Runner    │ ──────────────────────▶ │  User Uploads   │           │
│   │   (gcb-runner)  │     results.json        │  via Dashboard  │           │
│   │                 │                         │  or CLI         │           │
│   └────────┬────────┘                         └────────┬────────┘           │
│            │                                           │                    │
│            │ Run test                                  │ Upload +           │
│            │ locally                                   │ Pay $20 fee        │
│            ▼                                           ▼                    │
│   ┌─────────────────┐                         ┌─────────────────┐           │
│   │                 │                         │                 │           │
│   │  Local Results  │                         │    Platform     │           │
│   │  Database       │                         │   Validation    │           │
│   │                 │                         │                 │           │
│   └─────────────────┘                         └────────┬────────┘           │
│                                                        │                    │
│                                                        │ Pending            │
│                                                        │ Moderation         │
│                                                        ▼                    │
│                                               ┌─────────────────┐           │
│                                               │   Moderator     │           │
│                                               │   Verification  │           │
│                                               │                 │           │
│                                               └────────┬────────┘           │
│                                                        │                    │
│                                                        │ Approve &          │
│                                                        │ Publish            │
│                                                        ▼                    │
│                                               ┌─────────────────┐           │
│                                               │                 │           │
│                                               │   Leaderboard   │           │
│                                               │                 │           │
│                                               └─────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **⚠️ Document Scope:** This specification covers submitting **test results** (model responses and verdicts) from the CLI Runner to the Platform for moderation and leaderboard publication.

---

## Platform Tests vs CLI Submissions

| Aspect | Platform Tests | CLI Submissions |
|--------|---------------|-----------------|
| **Where executed** | Platform servers | User's local machine |
| **Publishing** | Automatic (no approval gate) | Requires moderator verification |
| **Cost** | $20 platform fee + model API costs | $20 submission fee (user pays own API costs) |
| **Use Case** | Individual testers, quick results | Organizations, custom/local models |
| **Verification** | Not required (platform controls execution) | Required (platform cannot verify execution) |
| **Trust Tier** | Starts at "automated" | Starts at "pending", becomes "reviewed" after moderation |
| **Model Access** | Platform has API access | User must provide access info for verification |

**Why the difference?** Platform tests run in a controlled environment where the platform executes the test directly. CLI submissions come from external environments where the platform has no visibility into how the test was conducted, so moderator verification ensures result integrity before publication.

---

## Validation Requirements

CLI submissions have **stricter validation requirements** than benchmark version uploads because the results must match an existing question set exactly.

### Mandatory Completeness

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETENESS REQUIREMENTS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. EVERY QUESTION MUST BE ANSWERED                                        │
│   ─────────────────────────────────────                                     │
│                                                                             │
│   Benchmark Version 2.0 has 300 questions.                                  │
│   Submission must contain exactly 300 responses.                            │
│                                                                             │
│   ✗ 299 responses → Rejected (incomplete)                                   │
│   ✗ 301 responses → Rejected (extra responses)                              │
│   ✓ 300 responses → Accepted for further validation                         │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   2. EXACT QUESTION ID MATCHING                                             │
│   ─────────────────────────────────                                         │
│                                                                             │
│   Every response.question_id must match a question in the benchmark.        │
│                                                                             │
│   Benchmark questions: [1, 2, 3, 4, ..., 300]                               │
│   Submission IDs:      [1, 2, 3, 4, ..., 300] ✓                             │
│   Submission IDs:      [1, 2, 3, 5, ..., 301] ✗ (ID 4 missing, 301 unknown) │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   3. NO DUPLICATE RESPONSES                                                 │
│   ───────────────────────────                                               │
│                                                                             │
│   Each question_id may appear only once in the responses array.             │
│                                                                             │
│   ✗ [1, 2, 2, 3, ...] → Rejected (duplicate ID 2)                          │
│   ✓ [1, 2, 3, 4, ...] → Accepted                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validation Stages

| Stage | Validation | Failure Response |
|-------|------------|------------------|
| **1. Schema** | Valid JSON, required fields present | 400 Bad Request |
| **2. Version Match** | benchmark_version exists and is valid | 400 Bad Request |
| **3. Completeness** | All questions answered, exact ID match | 400 Bad Request |
| **4. Integrity** | Checksums match, no corruption | 400 Bad Request |
| **5. Score Verification** | Calculated scores match reported scores | 400 Bad Request |
| **6. Duplicate Check** | Not already submitted | 409 Conflict |

---

## Step-by-Step Workflow

### Phase 1: Run Test Locally

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: LOCAL TEST EXECUTION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User runs benchmark via CLI Runner:                                       │
│                                                                             │
│   $ gcb-runner test --model llama3.2:70b --backend ollama                   │
│                                                                             │
│   ╔═════════════════════════════════════════════════════════════════════╗   │
│   ║         Great Commission Benchmark - Runner                         ║   │
│   ╚═════════════════════════════════════════════════════════════════════╝   │
│                                                                             │
│   Benchmark Version: Version 2 (2.0) (Current)                              │
│   CLI Version: 1.3.0                                                        │
│                                                                             │
│   Loading questions from embedded bundle...                                 │
│     ✓ 300 questions loaded (Tier 1: 210, Tier 2: 60, Tier 3: 30)           │
│     ✓ Bundle checksum verified                                             │
│                                                                             │
│   Testing: llama3.2:70b via Ollama                                         │
│   Judge: gpt-4o via OpenRouter                                              │
│                                                                             │
│   Running benchmark...                                                      │
│     Tier 1 - Use Cases (70%)   ━━━━━━━━━━━━━━━━━━━━ 210/210                │
│     Tier 2 - Theology (20%)    ━━━━━━━━━━━━━━━━━━━━ 60/60                  │
│     Tier 3 - Worldview (10%)   ━━━━━━━━━━━━━━━━━━━━ 30/30                  │
│                                                                             │
│   ═══════════════════════════════════════════════════════════════          │
│                                                                             │
│                         RESULTS SUMMARY                                     │
│                                                                             │
│   Model: llama3.2:70b                                                       │
│   GCB Score: 72.4                                                           │
│                                                                             │
│   Results saved locally. Run 'gcb-runner upload' to submit.                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What happens:**

1. CLI loads embedded benchmark bundle (questions + judge prompts)
2. Each question is sent to the test model
3. Each response is evaluated by the judge model
4. Results are stored in local SQLite database
5. User can view results locally before deciding to submit

---

### Phase 2: Export Results

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: EXPORT RESULTS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   $ gcb-runner export --run 3 --output results.json                         │
│                                                                             │
│   Exporting test run #3...                                                  │
│                                                                             │
│   Pre-export validation:                                                    │
│     ✓ All 300 questions answered                                           │
│     ✓ No duplicate question IDs                                            │
│     ✓ Tier distribution matches (210/60/30)                                │
│     ✓ Score calculation verified                                           │
│     ✓ Checksum generated: sha256:a1b2c3d4...                               │
│                                                                             │
│   ✓ Exported to results.json (2.4 MB)                                      │
│                                                                             │
│   Ready for upload at https://greatcommissionbenchmark.ai/submit            │
│   Or use: gcb-runner upload --run 3                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Export file structure:**

See [spec-export-schema-validation.md](./spec-export-schema-validation.md) for complete schema.

```json
{
  "format_version": "1.0",
  "test_run": {
    "id": "local-3",
    "model": "llama3.2:70b",
    "backend": "ollama",
    "benchmark_version": "2.0",
    "judge_model": "gpt-4o",
    "system_prompt": null,
    "completed_at": "2025-12-15T14:32:01Z"
  },
  "summary": {
    "total_questions": 300,
    "score": 72.4,
    "scoring_weights": { "tier1": 0.70, "tier2": 0.20, "tier3": 0.10 },
    "tier_scores": {
      "tier1": { "raw": 70.0, "weighted": 49.0, "questions": 210 },
      "tier2": { "raw": 78.0, "weighted": 15.6, "questions": 60 },
      "tier3": { "raw": 78.0, "weighted": 7.8, "questions": 30 }
    },
    "verdict_counts": { "pass": 216, "partial": 54, "fail": 30 }
  },
  "responses": [
    {
      "question_id": 1,
      "tier": 1,
      "category": "3.1",
      "response": "Based on the missiological research...",
      "verdict": "ACCEPTED",
      "verdict_normalized": "pass",
      "judge_reasoning": "The response accurately addresses...",
      "refusal_type": null,
      "response_time_ms": 2341
    }
    // ... 299 more responses
  ],
  "metadata": {
    "cli_version": "1.3.0",
    "benchmark_version": "2.0",
    "benchmark_checksum": "sha256:abc123...",
    "timestamp": "2025-12-15T14:35:00Z",
    "export_source": "cli_runner"
  }
}
```

---

### Phase 3: Submit to Platform

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 3: SUBMIT TO PLATFORM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Option A: CLI Upload                                                      │
│   ────────────────────                                                      │
│                                                                             │
│   $ gcb-runner upload --run 3                                               │
│                                                                             │
│   ╔═════════════════════════════════════════════════════════════════════╗   │
│   ║                CLI Submission Information                           ║   │
│   ╚═════════════════════════════════════════════════════════════════════╝   │
│                                                                             │
│   CLI submissions require moderator verification before publication.        │
│                                                                             │
│   What happens next:                                                        │
│     1. Pay $20 submission fee                                              │
│     2. Provide model access information                                     │
│     3. Moderator verifies results (typically 24-48 hours)                  │
│     4. If verified, results published to leaderboard                       │
│                                                                             │
│   Fee: $20.00 (covers verification work)                                   │
│                                                                             │
│   ? Continue with submission? [Y/n]                                        │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   Option B: Web Dashboard Upload                                            │
│   ──────────────────────────────                                            │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  My Dashboard > Submit CLI Results                                  │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │                                                             │    │   │
│   │  │          📁 Drop results.json here or click to browse       │    │   │
│   │  │                                                             │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │  Model Name:     [ Llama 3.2 70B                  ]                 │   │
│   │  Organization:   [ Research Lab X                 ]  (optional)    │   │
│   │                                                                     │   │
│   │  Model Access (required for verification):                          │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │ HuggingFace: https://huggingface.co/meta-llama/...          │    │   │
│   │  │ API Endpoint: (if applicable)                               │    │   │
│   │  │ Reproducibility notes: Model weights available at...        │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │  ⓘ Submission fee: $20.00                                          │   │
│   │  ⓘ Results will be verified by a moderator before publication      │   │
│   │                                                                     │   │
│   │                              [ Cancel ]  [ Pay & Submit ]           │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 4: Platform Validation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 4: PLATFORM VALIDATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Platform performs comprehensive validation:                               │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   Stage 1: Schema Validation                                        │   │
│   │   ─────────────────────────────                                     │   │
│   │   ✓ Valid JSON structure                                            │   │
│   │   ✓ All required fields present                                     │   │
│   │   ✓ Field types match schema                                        │   │
│   │   ✓ format_version is supported                                     │   │
│   │                                                                     │   │
│   │   Stage 2: Version Validation                                       │   │
│   │   ────────────────────────────                                      │   │
│   │   ✓ benchmark_version "2.0" exists in platform                      │   │
│   │   ✓ benchmark_checksum matches known checksum for 2.0               │   │
│   │   ✓ Version is active (not archived or draft)                       │   │
│   │                                                                     │   │
│   │   Stage 3: Completeness Validation  ◀── STRICT REQUIREMENTS         │   │
│   │   ──────────────────────────────────                                │   │
│   │   ✓ Response count (300) matches question count for v2.0            │   │
│   │   ✓ All 300 question IDs present in responses                       │   │
│   │   ✓ No duplicate question IDs                                       │   │
│   │   ✓ All question IDs are valid for benchmark v2.0                   │   │
│   │                                                                     │   │
│   │   Stage 4: Integrity Validation                                     │   │
│   │   ──────────────────────────────                                    │   │
│   │   ✓ Verdicts are valid for their tier                              │   │
│   │   ✓ verdict_normalized matches verdict                              │   │
│   │   ✓ Tier assignments match benchmark                                │   │
│   │   ✓ Category assignments match benchmark                            │   │
│   │                                                                     │   │
│   │   Stage 5: Score Verification                                       │   │
│   │   ────────────────────────────                                      │   │
│   │   ✓ Tier scores calculated correctly from verdicts                  │   │
│   │   ✓ Overall score matches weighted calculation                      │   │
│   │   ✓ Verdict counts match actual verdicts in responses               │   │
│   │   ✓ Scoring weights sum to 1.0                                      │   │
│   │                                                                     │   │
│   │   Stage 6: Duplicate Detection                                      │   │
│   │   ─────────────────────────────                                     │   │
│   │   ✓ Same model + benchmark + timestamp not already submitted        │   │
│   │   ✓ Response content not identical to existing submission           │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Validation Result: ✓ All checks passed                                   │
│   Status: Pending Moderation                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 5: Moderator Verification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 5: MODERATOR VERIFICATION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Moderator Dashboard > CLI Submissions Queue                               │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Submission: Llama 3.2 70B                                          │   │
│   │  Submitted by: user@example.com                                     │   │
│   │  Submitted at: 2025-12-15 15:00 UTC                                 │   │
│   │  Status: ● Pending Verification                                     │   │
│   ├─────────────────────────────────────────────────────────────────────┤   │
│   │                                                                     │   │
│   │  Summary                                                            │   │
│   │  ────────                                                           │   │
│   │  Model: llama3.2:70b (Ollama)                                       │   │
│   │  Benchmark: Version 2 (2.0)                                         │   │
│   │  Score: 72.4                                                        │   │
│   │  CLI Version: 1.3.0                                                 │   │
│   │                                                                     │   │
│   │  Model Access Information                                           │   │
│   │  ────────────────────────────                                       │   │
│   │  HuggingFace: https://huggingface.co/meta-llama/Llama-3.2-70B      │   │
│   │  Notes: Quantized Q4_K_M version, running on RTX 4090              │   │
│   │                                                                     │   │
│   │  Verification Tasks                                                 │   │
│   │  ────────────────────                                               │   │
│   │  ☐ Spot-check 20 sample verdicts (agree/disagree with judge)       │   │
│   │  ☐ Verify model access information is accurate                      │   │
│   │  ☐ Check for anomalous patterns (all same responses, etc.)         │   │
│   │  ☐ Verify score is plausible for this model                        │   │
│   │                                                                     │   │
│   │  Sample Verdicts for Review (20 random)                             │   │
│   │  ───────────────────────────────────────                            │   │
│   │  ┌───────────────────────────────────────────────────────────────┐  │   │
│   │  │ Q#12 (Tier 1, 3.2)                                            │  │   │
│   │  │ Question: Write an evangelistic tract for...                  │  │   │
│   │  │ Response: Here is an evangelistic tract...                    │  │   │
│   │  │ Verdict: ACCEPTED                                             │  │   │
│   │  │ Judge: The response provides clear, helpful content...        │  │   │
│   │  │                                                               │  │   │
│   │  │ Your assessment: [Agree] [Disagree] [Unsure]                  │  │   │
│   │  └───────────────────────────────────────────────────────────────┘  │   │
│   │  (... 19 more samples ...)                                          │   │
│   │                                                                     │   │
│   │  Moderator Notes                                                    │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │ (Notes visible to user and other moderators)                │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                                                                     │   │
│   │           [ Request More Info ]  [ Reject ]  [ Approve & Publish ]  │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Moderator verification process:**

1. **Spot-check verdicts** — Review 20 random verdicts, mark agree/disagree
2. **Verify model access** — Confirm the model can be accessed/reproduced
3. **Check for anomalies** — Look for suspicious patterns
4. **Assess plausibility** — Does the score make sense for this model?

**Verification outcomes:**

| Outcome | Action | User Notification |
|---------|--------|-------------------|
| **Approve** | Results published to leaderboard | Email: "Submission approved!" |
| **Request More Info** | Submission paused, user contacted | Email: "Additional info needed" |
| **Reject** | Submission rejected with reason | Email: "Submission not approved" |

---

### Phase 6: Publication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 6: PUBLICATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   After moderator approval:                                                 │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   1. Test run created in database                                   │   │
│   │      ────────────────────────────                                   │   │
│   │      • trust_tier: "reviewed" (vs "automated" for platform tests)  │   │
│   │      • submission_type: "cli"                                       │   │
│   │      • moderation_review_id: links to moderator review              │   │
│   │                                                                     │   │
│   │   2. Leaderboard updated                                            │   │
│   │      ─────────────────────                                          │   │
│   │      • Model appears in public rankings                             │   │
│   │      • Badge indicates "Community Verified" submission              │   │
│   │                                                                     │   │
│   │   3. User notified                                                  │   │
│   │      ────────────────                                               │   │
│   │      • Email: "Your submission has been approved!"                  │   │
│   │      • Link to public results page                                  │   │
│   │      • Share buttons for social media                               │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Trust Tier Progression:                                                   │
│                                                                             │
│   CLI Submissions:                                                          │
│   ┌──────────┐    ┌──────────┐    ┌───────────┐                            │
│   │ PENDING  │───▶│ REVIEWED │───▶│ VALIDATED │                            │
│   │          │    │          │    │           │                            │
│   └──────────┘    └──────────┘    └───────────┘                            │
│        │              │                │                                    │
│    Submitted,    Moderator          Second                                 │
│    awaiting      approved           moderator                              │
│    review                           confirmed                              │
│                                                                             │
│   Platform Tests:                                                           │
│   ┌───────────┐    ┌──────────┐    ┌───────────┐                           │
│   │ AUTOMATED │───▶│ REVIEWED │───▶│ VALIDATED │                           │
│   │           │    │          │    │           │                           │
│   └───────────┘    └──────────┘    └───────────┘                           │
│        │               │                │                                   │
│    Auto-published,  Moderator       Second                                 │
│    no review        spot-checked    moderator                              │
│    required                         confirmed                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Model Access Information

For moderators to verify CLI submissions, users must provide information about how to access or reproduce the tested model.

### Required Information

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MODEL ACCESS REQUIREMENTS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   At least ONE of the following must be provided:                           │
│                                                                             │
│   Option A: Public Model Reference                                          │
│   ──────────────────────────────────                                        │
│   • HuggingFace URL: https://huggingface.co/meta-llama/Llama-3.2-70B       │
│   • Model card or documentation link                                        │
│                                                                             │
│   Option B: API Access                                                      │
│   ─────────────────────                                                     │
│   • API endpoint (if publicly accessible)                                   │
│   • Provider name and model identifier                                      │
│                                                                             │
│   Option C: Reproducibility Information                                     │
│   ──────────────────────────────────────                                    │
│   • How to obtain model weights                                             │
│   • Hardware requirements                                                   │
│   • Quantization details (if applicable)                                    │
│   • Any custom configuration used                                           │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   Optional but helpful:                                                     │
│   • Organization name (for attribution)                                     │
│   • Contact for technical questions                                         │
│   • Notes about model variants or configurations                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Verification Scenarios

| Model Type | Verification Method |
|------------|---------------------|
| **Open-weight** (Llama, Mistral) | Moderator can reproduce test locally |
| **API-based** (OpenAI, Anthropic) | Cross-reference with platform test results |
| **Custom/Fine-tuned** | Requires detailed reproducibility info |
| **Proprietary** | Must provide API access or demo |

---

## API Endpoints

### POST /api/submissions

Submit CLI test results.

**Authentication:** User JWT required

**Request:** (multipart/form-data or JSON)

```http
POST /api/submissions
Authorization: Bearer <user_jwt_token>
Content-Type: application/json

{
  "format_version": "1.0",
  "test_run": { ... },
  "summary": { ... },
  "responses": [ ... ],
  "metadata": { ... },
  "model_access": {
    "name": "Llama 3.2 70B",
    "organization": "Research Lab X",
    "huggingface_url": "https://huggingface.co/...",
    "api_endpoint": null,
    "reproducibility_notes": "Quantized Q4_K_M, running on..."
  }
}
```

**Response (Success):** `201 Created`

```json
{
  "success": true,
  "submission": {
    "id": "uuid-xxx",
    "status": "pending_payment",
    "model_name": "Llama 3.2 70B",
    "benchmark_version": "2.0",
    "scores": {
      "overall": 72.4
    },
    "submitted_at": "2025-12-15T15:00:00Z"
  },
  "validation": {
    "passed": true,
    "warnings": []
  },
  "payment": {
    "required": true,
    "amount": 20.00,
    "currency": "USD",
    "payment_url": "https://..."
  },
  "next_steps": [
    "Complete payment to finalize submission",
    "Your results will be reviewed by a moderator (24-48 hours)"
  ]
}
```

**Response (Validation Failed):** `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Results validation failed with 2 error(s)",
    "details": {
      "errors": [
        {
          "code": "INCOMPLETE_RESPONSES",
          "message": "Expected 300 responses, found 298",
          "path": "$.responses",
          "missing_question_ids": [145, 267]
        },
        {
          "code": "SCORE_MISMATCH",
          "message": "Calculated score 71.8 does not match reported 72.4",
          "path": "$.summary.score"
        }
      ]
    }
  }
}
```

### GET /api/submissions/:id

Get submission details.

**Response:** See [spec-api-endpoints.md](./spec-api-endpoints.md) Section 4.

### GET /api/user/submissions

Get user's submission history.

**Response:** See [spec-api-endpoints.md](./spec-api-endpoints.md) Section 2.

---

## Error Codes

| Code | HTTP Status | Description | Resolution |
|------|-------------|-------------|------------|
| `INCOMPLETE_RESPONSES` | 400 | Not all questions answered | Ensure all 300 responses included |
| `INVALID_QUESTION_ID` | 400 | Question ID not in benchmark | Check question IDs match benchmark |
| `DUPLICATE_QUESTION_ID` | 400 | Same question answered twice | Remove duplicate response |
| `SCORE_MISMATCH` | 400 | Calculated ≠ reported score | Re-export from CLI |
| `INVALID_VERDICT` | 400 | Verdict not valid for tier | Check verdict/tier mapping |
| `CHECKSUM_MISMATCH` | 400 | Bundle checksum doesn't match | Verify benchmark version |
| `UNKNOWN_VERSION` | 400 | Benchmark version not found | Use supported version |
| `DUPLICATE_SUBMISSION` | 409 | Already submitted | Check existing submissions |
| `VERSION_ARCHIVED` | 400 | Benchmark version archived | Use current version |

---

## Security Considerations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY CONSIDERATIONS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Data Integrity                                                            │
│   ──────────────                                                            │
│   • Checksum verification ensures data wasn't corrupted                     │
│   • Platform recalculates scores to prevent manipulation                    │
│   • Question ID matching prevents response substitution                     │
│                                                                             │
│   Result Verification                                                       │
│   ────────────────────                                                      │
│   • Moderators spot-check verdicts for accuracy                            │
│   • Model access info enables reproduction                                  │
│   • Anomaly detection flags suspicious patterns                            │
│                                                                             │
│   Abuse Prevention                                                          │
│   ─────────────────                                                         │
│   • $20 fee discourages spam submissions                                   │
│   • Rate limiting: max 5 submissions per hour per user                     │
│   • Duplicate detection prevents resubmission                              │
│                                                                             │
│   Privacy                                                                   │
│   ───────                                                                   │
│   • Full response text stored but not publicly displayed                   │
│   • Only summary scores and verdicts shown on leaderboard                  │
│   • User can request deletion of unpublished submissions                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [spec-export-schema-validation.md](./spec-export-schema-validation.md) — Export JSON schema
- [spec-api-endpoints.md](./spec-api-endpoints.md) — API documentation (Section 4: Submissions)
- [cli-runner-specifications.md](./cli-runner-specifications.md) — CLI Runner implementation
- [process-moderation-process.md](./process-moderation-process.md) — Moderation workflow

---

*Last Updated: December 17, 2025*
