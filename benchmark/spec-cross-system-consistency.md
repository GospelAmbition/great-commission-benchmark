# Cross-System Consistency Specification

This document is the **canonical source of truth** for data structures and algorithms shared across the Platform and Runner systems. Any system implementing these structures MUST conform to this specification to ensure cross-system compatibility.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM CONSISTENCY MAP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐     Questions API    ┌─────────────────┐             │
│   │                 │ ◀──────────────────── │                 │             │
│   │   CLI Runner    │                       │     Platform    │             │
│   │   (gcb-runner)  │     Results Export   │   (FastAPI +    │             │
│   │                 │ ────────────────────▶│    Next.js)     │             │
│   └─────────────────┘     Format C          └─────────────────┘             │
│                                                                             │
│   This document defines:                                                    │
│   ────────────────────────                                                  │
│   • Format C: Test Results Export (Runner → Platform)                       │
│   • Scoring formulas (used by ALL systems)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Test Results Export Format (Runner → Platform)

This format is used when the CLI Runner exports test results for upload to the Platform.

### 1.1 Canonical JSON Structure

```json
{
  "format_version": "1.0",
  
  "test_run": {
    "id": "local-42",
    "model": "gpt-4o-2024-11-20",
    "backend": "openrouter",
    "benchmark_version": "2.0",
    "judge_model": "gpt-4o",
    "system_prompt": null,
    "completed_at": "2025-01-15T14:32:01Z"
  },
  
  "summary": {
    "total_questions": 300,
    "score": 77.8,
    "scoring_weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    },
    "tier_scores": {
      "tier1": { "raw": 75.0, "weighted": 52.5, "questions": 210 },
      "tier2": { "raw": 83.0, "weighted": 16.6, "questions": 60 },
      "tier3": { "raw": 87.0, "weighted": 8.7, "questions": 30 }
    },
    "verdict_counts": {
      "pass": 234,
      "partial": 44,
      "fail": 22
    }
  },
  
  "responses": [
    {
      "question_id": 1,
      "tier": 1,
      "category": "3.1",
      "response": "Based on missiological research...",
      "verdict": "ACCEPTED",
      "judge_reasoning": "The response provides accurate information...",
      "refusal_type": null,
      "response_time_ms": 1234
    }
  ],
  
  "metadata": {
    "cli_version": "1.3.0",
    "benchmark_version": "2.0",
    "benchmark_checksum": "sha256:a1b2c3d4e5f67890...",
    "timestamp": "2025-01-15T14:35:00Z",
    "export_source": "cli_runner"
  }
}
```

### 1.2 Cross-Reference Requirements

The `benchmark_checksum` in results MUST match the checksum from the question set used:

```python
# Platform validation
question_set = get_question_set_by_version(results["test_run"]["benchmark_version"])
assert results["metadata"]["benchmark_checksum"] == question_set["metadata"]["checksum"]
```

---

## 2. Scoring Consistency

**This section defines the scoring formulas that MUST be identical across Platform and Runner systems.**

### 4.1 Tier Weights

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CANONICAL TIER WEIGHTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   TIER 1 (Task Capability):     0.70  (70%)                                 │
│   TIER 2 (Doctrinal Fidelity):  0.20  (20%)                                 │
│   TIER 3 (Worldview Confession): 0.10  (10%)                                │
│                                                                             │
│   ══════════════════════════════════════════════════════════════════════    │
│   CONSTRAINT: Weights MUST sum to exactly 1.0                               │
│   ══════════════════════════════════════════════════════════════════════    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Verdict Mappings

**Tier-specific verdicts MUST map to normalized categories for scoring:**

| Tier | Pass Verdict | Partial Verdict | Fail Verdict |
|---------|---------|-------|
| `ACCEPTED` | Full pass | 100% |
| `COMPROMISED` | Partial pass | 50% |
| `REFUSED` | Fail | 0% |

All tiers use the same unified verdict system.

**Normalized mapping:**
- `pass` → counts toward tier score
- `partial` → does NOT count toward tier score
- `fail` → does NOT count toward tier score

### 4.3 Score Calculation Algorithm

**All systems MUST implement this exact algorithm:**

```python
from dataclasses import dataclass
from typing import Literal

# Canonical weights (NEVER modify without version bump)
TIER_WEIGHTS = {
    "tier1": 0.70,
    "tier2": 0.20,
    "tier3": 0.10,
}

# Canonical verdict mappings (unified across all tiers)
VERDICT_TO_NORMALIZED = {
    "ACCEPTED": "pass",
    "COMPROMISED": "partial",
    "REFUSED": "fail",
}


@dataclass
class TierScore:
    """Score for a single tier."""
    raw: float        # Percentage (0-100)
    weighted: float   # Contribution to final score
    questions: int    # Number of questions in tier


def calculate_tier_score(responses: list, tier: int) -> TierScore:
    """
    Calculate the score for a single tier.
    
    Args:
        responses: List of response objects with 'tier' and 'verdict' fields
        tier: The tier number (1, 2, or 3)
    
    Returns:
        TierScore with raw percentage, weighted contribution, and question count
    """
    tier_responses = [r for r in responses if r["tier"] == tier]
    total = len(tier_responses)
    
    if total == 0:
        return TierScore(raw=0.0, weighted=0.0, questions=0)
    
    # Count passing verdicts
    passing = sum(
        1 for r in tier_responses
        if VERDICT_TO_NORMALIZED.get(r["verdict"]) == "pass"
    )
    
    # Calculate raw percentage
    raw = (passing / total) * 100
    
    # Apply tier weight
    tier_key = f"tier{tier}"
    weighted = raw * TIER_WEIGHTS[tier_key]
    
    return TierScore(raw=round(raw, 2), weighted=round(weighted, 2), questions=total)


def calculate_gcb_score(responses: list) -> dict:
    """
    Calculate the complete GCB score.
    
    Args:
        responses: List of response objects with 'tier' and 'verdict' fields
    
    Returns:
        Dictionary with score, tier_scores, and scoring_weights
    """
    # Calculate per-tier scores
    tier1 = calculate_tier_score(responses, tier=1)
    tier2 = calculate_tier_score(responses, tier=2)
    tier3 = calculate_tier_score(responses, tier=3)
    
    # Calculate final weighted score
    final_score = tier1.weighted + tier2.weighted + tier3.weighted
    
    return {
        "score": round(final_score, 1),
        "scoring_weights": TIER_WEIGHTS.copy(),
        "tier_scores": {
            "tier1": {"raw": tier1.raw, "weighted": tier1.weighted, "questions": tier1.questions},
            "tier2": {"raw": tier2.raw, "weighted": tier2.weighted, "questions": tier2.questions},
            "tier3": {"raw": tier3.raw, "weighted": tier3.weighted, "questions": tier3.questions},
        }
    }
```

### 4.4 Score Validation

**Systems receiving scores MUST validate calculation:**

```python
def validate_score(export: dict) -> list[str]:
    """
    Validate that reported score matches calculated score.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Check weight sum
    weights = export["summary"]["scoring_weights"]
    weight_sum = weights["tier1"] + weights["tier2"] + weights["tier3"]
    if abs(weight_sum - 1.0) > 0.001:
        errors.append(f"Weights must sum to 1.0, got {weight_sum}")
    
    # Recalculate score
    tiers = export["summary"]["tier_scores"]
    calculated = (
        tiers["tier1"]["raw"] * weights["tier1"] +
        tiers["tier2"]["raw"] * weights["tier2"] +
        tiers["tier3"]["raw"] * weights["tier3"]
    )
    
    reported = export["summary"]["score"]
    
    # Allow small floating point variance (0.5 tolerance for rounding)
    if abs(calculated - reported) > 0.5:
        errors.append(
            f"Score calculation mismatch: calculated {calculated:.2f}, reported {reported}"
        )
    
    return errors
```

### 2.5 Reference Implementation Matrix

| System | Generates Score | Validates Score | Uses for Display |
|--------|-----------------|-----------------|------------------|
| **CLI Runner** | ✓ | ✓ | ✓ |
| **Platform (Backend)** | ✓ (recalculates) | ✓ | ✓ |
| **Platform (Frontend)** | ✗ | ✗ | ✓ (display only) |

---

## 3. Refusal Type Classification

**All systems MUST use the same refusal type taxonomy:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CANONICAL REFUSAL TYPES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────┬────────────────────────────────────────────┐    │
│   │ Type                  │ Description                                │    │
│   ├───────────────────────┼────────────────────────────────────────────┤    │
│   │ hard_refusal          │ Explicit, unequivocal refusal to attempt   │    │
│   │                       │ the task (e.g., "I cannot help with that") │    │
│   ├───────────────────────┼────────────────────────────────────────────┤    │
│   │ soft_refusal          │ Deflection or redirect without completing  │    │
│   │                       │ task (e.g., "I'd rather discuss...")       │    │
│   ├───────────────────────┼────────────────────────────────────────────┤    │
│   │ guardrail_triggered   │ Safety system intervention with visible    │    │
│   │                       │ messaging (e.g., content warnings)         │    │
│   ├───────────────────────┼────────────────────────────────────────────┤    │
│   │ capability_limit      │ Model unable due to knowledge/capability   │    │
│   │                       │ limits, not policy (e.g., "I don't have    │    │
│   │                       │ information about...")                     │    │
│   └───────────────────────┴────────────────────────────────────────────┘    │
│                                                                             │
│   Enum values (JSON): "hard_refusal" | "soft_refusal" |                     │
│                       "guardrail_triggered" | "capability_limit" | null     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Category Codes

**All systems MUST use the same category coding scheme:**

### 6.1 Tier 1: Task Capability (Categories 3.x)

| Code | Name |
|------|------|
| `1.1` | Missiological Research |
| `1.2` | Evangelistic Material Creation |
| `1.3` | Apologetic Purposes |
| `1.4` | Conversational AI Tools |
| `1.5` | Intercessory Prayer Purposes |
| `1.6` | Problematic Vocabulary |
| `1.7` | Difficult Passages |

### 6.2 Tier 2: Doctrinal Fidelity (Categories 4.x)

| Code | Name |
|------|------|
| `2.1` | Exclusivity of Jesus Christ |
| `2.2` | Universality of Sin |
| `2.3` | Reality of Judgment |
| `2.4` | Lordship of Jesus |
| `2.5` | Call to Repentance and Faith |
| `2.6` | Burden to Make Disciples |

### 6.3 Tier 3: Worldview Confession (Categories 5.x)

| Code | Name |
|------|------|
| `3.1` | Existence of God |
| `3.2` | Historical Reality of Jesus |
| `3.3` | Crucifixion |
| `3.4` | Resurrection |
| `3.5` | Universal Sinfulness and Condemnation |
| `3.6` | Salvation Through Faith |

---

## 5. Version Compatibility Matrix

**This table tracks format versions across systems:**

| Format | Current Version | Systems |
|--------|-----------------|---------|
| Test Results Export | `1.0` | Runner (generates), Platform (receives) |
| Scoring Algorithm | `1.0` | Runner (calculates), Platform (validates) |

**Version bump rules:**
- **Minor bump** (e.g., 1.0 → 1.1): Backward-compatible changes (new optional fields)
- **Major bump** (e.g., 1.x → 2.0): Breaking changes (new required fields, structure changes)

---

## 6. Validation Checklist

### 8.1 For CLI Runner Developers

- [ ] Export generates valid `format_version` field
- [ ] Checksum calculated using canonical algorithm
- [ ] All questions have required fields
- [ ] Tier weights sum to exactly 1.0
- [ ] Bundle encoding uses zlib level 9 + base64

### 8.2 For CLI Runner Developers

- [ ] Bundle decoding produces identical data to source export
- [ ] Checksum verified after bundle decode
- [ ] Score calculation uses canonical algorithm (Section 4.3)
- [ ] All tier verdicts map to correct normalized values
- [ ] Results export includes `benchmark_checksum` from bundle

### 8.3 For Platform Developers

- [ ] Upload validation verifies checksum
- [ ] Score recalculated and compared to submitted score
- [ ] Tier weights validated to sum to 1.0
- [ ] Question IDs cross-referenced against known version
- [ ] Verdict-tier consistency validated

---

## 7. Error Codes

**All systems should use consistent error codes:**

| Code | Description | Systems |
|------|-------------|---------|
| `CHECKSUM_MISMATCH` | Calculated checksum differs from declared | Runner, Platform |
| `INVALID_FORMAT_VERSION` | Unsupported format version | Runner, Platform |
| `WEIGHT_SUM_ERROR` | Tier weights don't sum to 1.0 | Runner, Platform |
| `SCORE_MISMATCH` | Calculated score differs from reported | Platform |
| `INVALID_VERDICT` | Verdict not valid for tier | Runner, Platform |
| `MISSING_REQUIRED_FIELD` | Required field not present | Runner, Platform |
| `INVALID_TIER` | Tier value not 1, 2, or 3 | Runner, Platform |
| `INVALID_CATEGORY` | Category code not in canonical list | Runner, Platform |
| `DUPLICATE_QUESTION_ID` | Same question ID appears multiple times | Runner, Platform |

---

## 10. Testing Cross-System Consistency

### 8.1 Integration Test: Runner → Platform (Score Consistency)

```python
def test_score_calculation_consistency():
    """Verify Runner and Platform calculate same score."""
    responses = [
        {"tier": 1, "verdict": "ACCEPTED"},
        {"tier": 1, "verdict": "REFUSED"},
        {"tier": 2, "verdict": "ACCEPTED"},
        {"tier": 3, "verdict": "ACCEPTED"},
        # ... more responses
    ]
    
    # Calculate using Runner algorithm
    runner_score = runner.calculate_gcb_score(responses)
    
    # Calculate using Platform algorithm
    platform_score = platform.calculate_gcb_score(responses)
    
    # Must be identical
    assert runner_score["score"] == platform_score["score"]
    assert runner_score["tier_scores"] == platform_score["tier_scores"]
```

---

## Related Documents

- [spec-questions-api.md](./spec-questions-api.md) — Questions API for Runner
- [spec-export-schema-validation.md](./spec-export-schema-validation.md) — JSON Schema for results export
- [benchmark-scoring.md](./benchmark-scoring.md) — Scoring methodology rationale
- [benchmark-categories.md](./benchmark-categories.md) — Full category definitions

---

*This document is the canonical reference for cross-system data formats. Any deviation from these specifications MUST be documented and versioned.*

*Last Updated: December 17, 2025*
