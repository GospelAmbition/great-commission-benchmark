# Cross-System Consistency Specification

This document is the **canonical source of truth** for data structures and algorithms shared across the three GCB systems. Any system implementing these structures MUST conform to this specification to ensure cross-system compatibility.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM CONSISTENCY MAP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐     Questions     ┌─────────────────┐                 │
│   │                 │ ────────────────▶ │                 │                 │
│   │   CLI Builder   │                   │     Platform    │                 │
│   │   (gcb-builder) │     Format A      │   (FastAPI +    │                 │
│   │                 │                   │    Next.js)     │                 │
│   └────────┬────────┘                   └────────┬────────┘                 │
│            │                                     │                          │
│            │ Questions                           │ Scoring                  │
│            │ Format B                            │ Results                  │
│            ▼                                     │                          │
│   ┌─────────────────┐                            │                          │
│   │                 │     Results       ┌────────▼────────┐                 │
│   │   CLI Runner    │ ────────────────▶ │  Results Export │                 │
│   │   (gcb-runner)  │     Format C      │     Format      │                 │
│   │                 │                   └─────────────────┘                 │
│   └─────────────────┘                                                       │
│                                                                             │
│   This document defines:                                                    │
│   ────────────────────────                                                  │
│   • Format A: Question Set Export (Builder → Platform)                      │
│   • Format B: Question Bundle (Builder → Runner)                            │
│   • Format C: Test Results Export (Runner → Platform)                       │
│   • Scoring formulas (used by ALL systems)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Question Set Export (Builder → Platform)

This format is used when the CLI Builder exports questions for upload to the Platform's admin dashboard.

### 1.1 Canonical JSON Structure

```json
{
  "format_version": "1.0",
  "benchmark_version": "2.0",
  "name": "Version 2",
  "description": "Annual refresh of the Great Commission Benchmark",
  "locked_at": "2026-01-15T00:00:00Z",
  
  "questions": [
    {
      "id": 1,
      "content": "Write a gospel presentation for college students...",
      "category": "3.2",
      "tier": 1,
      "difficulty": "medium",
      "expected_verdict": "ACCEPTED",
      "expected_refusal_type": null,
      "tests_capability": true,
      "tests_willingness": true,
      "use_case_tags": ["content_generation", "chatbot"],
      "audience_context": "secular_western",
      "ministry_type": "campus_ministry"
    }
  ],
  
  "judge_prompts": {
    "tier1_task": "You are an evaluator for the Great Commission Benchmark...",
    "tier2_doctrine": "You are an evaluator assessing theological fidelity...",
    "tier3_worldview": "You are an evaluator assessing worldview alignment..."
  },
  
  "scoring": {
    "weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    },
    "formula": "(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)",
    "verdict_mapping": {
      "tier1": { "pass": "ACCEPTED", "partial": "COMPROMISED", "fail": "REFUSED" },
      "tier2": { "pass": "LOYAL", "partial": "COMPROMISED", "fail": "DISLOYAL" },
      "tier3": { "pass": "AFFIRMED", "partial": "HEDGED", "fail": "DENIED" }
    },
    "refusal_types": ["hard_refusal", "soft_refusal", "guardrail_triggered", "capability_limit"]
  },
  
  "metadata": {
    "total_questions": 300,
    "tier_counts": { "tier1": 210, "tier2": 60, "tier3": 30 },
    "category_counts": {
      "3.1": 35, "3.2": 35, "3.3": 35, "3.4": 35, "3.5": 35, "3.6": 35,
      "4.1": 10, "4.2": 10, "4.3": 10, "4.4": 10, "4.5": 10, "4.6": 10,
      "5.1": 5, "5.2": 5, "5.3": 5, "5.4": 5, "5.5": 5, "5.6": 5
    },
    "checksum": "sha256:a1b2c3d4e5f67890123456789012345678901234567890123456789012345678"
  }
}
```

### 1.2 Field Definitions

#### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format_version` | string | ✓ | Schema version (e.g., "1.0") |
| `benchmark_version` | string | ✓ | Semantic version of question set (e.g., "2.0") |
| `name` | string | ✓ | Marketing name (e.g., "Version 2") |
| `description` | string | ✓ | Human-readable description |
| `locked_at` | ISO 8601 | ✓ | Timestamp when version was locked |
| `questions` | array | ✓ | Array of question objects |
| `judge_prompts` | object | ✓ | Evaluation prompts by tier |
| `scoring` | object | ✓ | Scoring configuration |
| `metadata` | object | ✓ | Summary statistics and integrity |

#### Question Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✓ | Unique question identifier (1-based) |
| `content` | string | ✓ | The question/prompt text |
| `category` | string | ✓ | Category code (e.g., "3.2", "4.1", "5.3") |
| `tier` | integer | ✓ | 1, 2, or 3 |
| `difficulty` | string | ✓ | "easy", "medium", or "hard" |
| `expected_verdict` | string | ✓ | Expected judge verdict |
| `expected_refusal_type` | string\|null | ✓ | Expected refusal classification if REFUSED |
| `tests_capability` | boolean | ✓ | Whether question tests capability |
| `tests_willingness` | boolean | ✓ | Whether question tests willingness |
| `use_case_tags` | array | - | Optional use case classifications |
| `audience_context` | string | - | Optional audience context |
| `ministry_type` | string | - | Optional ministry type tag |

### 1.3 Checksum Calculation

**Algorithm:** SHA-256 of canonical JSON of the questions array.

```python
import hashlib
import json

def calculate_checksum(questions: list) -> str:
    """
    Calculate the canonical checksum for a question set.
    
    IMPORTANT: This algorithm MUST be identical in all systems.
    """
    # Sort questions by ID for deterministic ordering
    sorted_questions = sorted(questions, key=lambda q: q["id"])
    
    # Serialize to canonical JSON (sorted keys, no extra whitespace)
    canonical_json = json.dumps(sorted_questions, sort_keys=True, separators=(",", ":"))
    
    # Calculate SHA-256
    hash_value = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    
    return f"sha256:{hash_value}"
```

**Systems that MUST implement this algorithm:**
- CLI Builder (generates checksum on export)
- Platform (verifies checksum on upload)
- CLI Runner (verifies checksum on bundle decode)

---

## 2. Question Bundle Format (Builder → Runner)

This format embeds questions in the CLI Runner Python package for offline execution.

### 2.1 Bundle Module Structure

```python
# gcb_runner/versions/v2_0/bundle.py

"""
GCB Benchmark V2.0 - Question Bundle
Generated: 2026-01-15T00:00:00Z
Checksum: sha256:a1b2c3d4...

DO NOT MODIFY - Auto-generated by gcb-compile-bundle.
"""

import base64
import zlib
import json
from typing import Any

# Metadata (visible without decoding)
VERSION = "2.0"
RELEASE_DATE = "2026-01-15"
QUESTION_COUNT = 300
TIER_DISTRIBUTION = {"tier1": 210, "tier2": 60, "tier3": 30}
CHECKSUM = "sha256:a1b2c3d4e5f67890..."

# Bundle data (compressed + base64 encoded)
_BUNDLE_DATA = """
eJzVWNtu2zgQfV9g/4HwS+ILJUq2nTgI0KJFs0WLLrZAi32gKMoWI4kCScV2...
"""

def _decode_bundle() -> dict[str, Any]:
    """
    Decode the question bundle.
    
    Returns the same structure as the Question Set Export format.
    """
    compressed = base64.b64decode(_BUNDLE_DATA.strip())
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes)
```

### 2.2 Bundle Encoding Algorithm

**Algorithm:** Compress with zlib (level 9), then base64 encode.

```python
import base64
import json
import zlib

def encode_bundle(export_data: dict) -> str:
    """
    Encode a question set export for embedding in a Python bundle.
    
    IMPORTANT: This algorithm MUST be identical in Builder and Runner.
    """
    # Serialize to JSON
    json_bytes = json.dumps(export_data).encode("utf-8")
    
    # Compress with zlib (level 9 for maximum compression)
    compressed = zlib.compress(json_bytes, level=9)
    
    # Base64 encode for safe embedding in Python source
    encoded = base64.b64encode(compressed).decode("ascii")
    
    return encoded


def decode_bundle(encoded_data: str) -> dict:
    """
    Decode an embedded question bundle.
    
    IMPORTANT: This algorithm MUST be identical in Builder and Runner.
    """
    # Base64 decode
    compressed = base64.b64decode(encoded_data.strip())
    
    # Decompress
    json_bytes = zlib.decompress(compressed)
    
    # Parse JSON
    return json.loads(json_bytes)
```

### 2.3 Data Equivalence Requirement

**The decoded bundle MUST contain the same data as the Question Set Export format.**

```python
# This assertion MUST pass for any valid bundle:

original_export = load_json("gcb-v2.0.json")
bundle = gcb_runner.versions.v2_0.bundle._decode_bundle()

# Core data must be identical
assert bundle["questions"] == original_export["questions"]
assert bundle["judge_prompts"] == original_export["judge_prompts"]
assert bundle["scoring"] == original_export["scoring"]
assert bundle["metadata"]["checksum"] == original_export["metadata"]["checksum"]
```

---

## 3. Test Results Export Format (Runner → Platform)

This format is used when the CLI Runner exports test results for upload to the Platform.

### 3.1 Canonical JSON Structure

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
      "verdict_normalized": "pass",
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

### 3.2 Cross-Reference Requirements

The `benchmark_checksum` in results MUST match the checksum from the question set used:

```python
# Platform validation
question_set = get_question_set_by_version(results["test_run"]["benchmark_version"])
assert results["metadata"]["benchmark_checksum"] == question_set["metadata"]["checksum"]
```

---

## 4. Scoring Consistency

**This section defines the scoring formulas that MUST be identical across all three systems.**

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
|------|--------------|-----------------|--------------|
| **Tier 1** (Task) | `ACCEPTED` | `COMPROMISED` | `REFUSED` |
| **Tier 2** (Doctrine) | `LOYAL` | `COMPROMISED` | `DISLOYAL` |
| **Tier 3** (Worldview) | `AFFIRMED` | `HEDGED` | `DENIED` |

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

# Canonical verdict mappings
VERDICT_TO_NORMALIZED = {
    # Tier 1
    "ACCEPTED": "pass",
    "REFUSED": "fail",
    # Tier 2
    "LOYAL": "pass",
    "DISLOYAL": "fail",
    # Tier 3
    "AFFIRMED": "pass",
    "DENIED": "fail",
    # Shared
    "COMPROMISED": "partial",
    "HEDGED": "partial",
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

### 4.5 Reference Implementation Matrix

| System | Generates Score | Validates Score | Uses for Display |
|--------|-----------------|-----------------|------------------|
| **CLI Builder** | ✗ | ✗ | ✗ |
| **CLI Runner** | ✓ | ✓ | ✓ |
| **Platform (Backend)** | ✓ (recalculates) | ✓ | ✓ |
| **Platform (Frontend)** | ✗ | ✗ | ✓ (display only) |

---

## 5. Refusal Type Classification

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

## 6. Category Codes

**All systems MUST use the same category coding scheme:**

### 6.1 Tier 1: Task Capability (Categories 3.x)

| Code | Name |
|------|------|
| `3.1` | Missiological Research |
| `3.2` | Evangelistic Material Creation |
| `3.3` | Apologetic Purposes |
| `3.4` | Conversational AI Tools |
| `3.5` | Intercessory Prayer Purposes |
| `3.6` | Scripture Processing |

### 6.2 Tier 2: Doctrinal Fidelity (Categories 4.x)

| Code | Name |
|------|------|
| `4.1` | Exclusivity of Jesus Christ |
| `4.2` | Universality of Sin |
| `4.3` | Reality of Judgment |
| `4.4` | Lordship of Jesus |
| `4.5` | Call to Repentance and Faith |
| `4.6` | Burden to Make Disciples |

### 6.3 Tier 3: Worldview Confession (Categories 5.x)

| Code | Name |
|------|------|
| `5.1` | Existence of God |
| `5.2` | Historical Reality of Jesus |
| `5.3` | Crucifixion |
| `5.4` | Resurrection |
| `5.5` | Universal Sinfulness and Condemnation |
| `5.6` | Salvation Through Faith |

---

## 7. Version Compatibility Matrix

**This table tracks format versions across systems:**

| Format | Current Version | Systems |
|--------|-----------------|---------|
| Question Set Export | `1.0` | Builder (generates), Platform (receives) |
| Question Bundle | `1.0` | Builder (generates), Runner (decodes) |
| Test Results Export | `1.0` | Runner (generates), Platform (receives) |
| Scoring Algorithm | `1.0` | Runner (calculates), Platform (validates) |

**Version bump rules:**
- **Minor bump** (e.g., 1.0 → 1.1): Backward-compatible changes (new optional fields)
- **Major bump** (e.g., 1.x → 2.0): Breaking changes (new required fields, structure changes)

---

## 8. Validation Checklist

### 8.1 For CLI Builder Developers

- [ ] Export generates valid `format_version` field
- [ ] Checksum calculated using canonical algorithm (Section 1.3)
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

## 9. Error Codes

**All systems should use consistent error codes:**

| Code | Description | Systems |
|------|-------------|---------|
| `CHECKSUM_MISMATCH` | Calculated checksum differs from declared | Builder, Runner, Platform |
| `INVALID_FORMAT_VERSION` | Unsupported format version | Runner, Platform |
| `WEIGHT_SUM_ERROR` | Tier weights don't sum to 1.0 | Runner, Platform |
| `SCORE_MISMATCH` | Calculated score differs from reported | Platform |
| `INVALID_VERDICT` | Verdict not valid for tier | Runner, Platform |
| `MISSING_REQUIRED_FIELD` | Required field not present | All |
| `INVALID_TIER` | Tier value not 1, 2, or 3 | All |
| `INVALID_CATEGORY` | Category code not in canonical list | All |
| `DUPLICATE_QUESTION_ID` | Same question ID appears multiple times | All |

---

## 10. Testing Cross-System Consistency

### 10.1 Integration Test: Builder → Platform

```python
def test_builder_to_platform_consistency():
    """Verify Builder export is accepted by Platform validation."""
    # Generate export from Builder
    export = builder.generate_export(version="2.0")
    
    # Validate using Platform validator
    errors = platform.validate_question_set_upload(export)
    assert errors == [], f"Validation errors: {errors}"
    
    # Verify checksum
    calculated = platform.calculate_checksum(export["questions"])
    assert calculated == export["metadata"]["checksum"]
```

### 10.2 Integration Test: Builder → Runner

```python
def test_builder_to_runner_consistency():
    """Verify Bundle decodes to same data as export."""
    # Generate export from Builder
    export = builder.generate_export(version="2.0")
    
    # Compile to bundle
    bundle_code = builder.compile_bundle(export)
    
    # Decode bundle (simulating Runner)
    decoded = runner.decode_bundle(bundle_code)
    
    # Verify data equivalence
    assert decoded["questions"] == export["questions"]
    assert decoded["scoring"] == export["scoring"]
    assert decoded["metadata"]["checksum"] == export["metadata"]["checksum"]
```

### 10.3 Integration Test: Runner → Platform (Score Consistency)

```python
def test_score_calculation_consistency():
    """Verify Runner and Platform calculate same score."""
    responses = [
        {"tier": 1, "verdict": "ACCEPTED"},
        {"tier": 1, "verdict": "REFUSED"},
        {"tier": 2, "verdict": "LOYAL"},
        {"tier": 3, "verdict": "AFFIRMED"},
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

- [spec-builder-to-platform.md](./spec-builder-to-platform.md) — Full upload workflow
- [spec-builder-to-runner.md](./spec-builder-to-runner.md) — Bundle compilation process
- [spec-export-schema-validation.md](./spec-export-schema-validation.md) — JSON Schema for results export
- [benchmark-scoring.md](./benchmark-scoring.md) — Scoring methodology rationale
- [benchmark-categories.md](./benchmark-categories.md) — Full category definitions

---

*This document is the canonical reference for cross-system data formats. Any deviation from these specifications MUST be documented and versioned.*

*Last Updated: December 17, 2025*
