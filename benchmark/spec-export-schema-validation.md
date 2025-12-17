# Export Format Schema Validation

This document defines the JSON schema validation rules for benchmark test results exported from the CLI Runner and uploaded to the GCB Platform.

---

## Overview

The export format serves as the contract between:
- **CLI Runner** → generates export files
- **GCB Platform** → receives and validates uploads
- **CLI Builder** → generates compatible exports for platform publication

All systems must validate against this schema to ensure data integrity and cross-system compatibility.

---

## Schema Version

| Field | Value | Notes |
|-------|-------|-------|
| **Schema Version** | `1.0` | Tracks schema evolution |
| **Format** | JSON | UTF-8 encoded |
| **File Extension** | `.json` | Recommended: `gcb-results-{model}-{date}.json` |

---

## Complete JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://gcb.example.com/schemas/export-v1.0.json",
  "title": "GCB Test Results Export",
  "description": "Schema for Great Commission Benchmark test result exports",
  "type": "object",
  "required": ["format_version", "test_run", "summary", "responses", "metadata"],
  "additionalProperties": false,
  
  "properties": {
    "format_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Schema version for this export format",
      "examples": ["1.0"]
    },
    
    "test_run": {
      "type": "object",
      "required": ["id", "model", "backend", "benchmark_version", "judge_model", "completed_at"],
      "additionalProperties": false,
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 64,
          "pattern": "^[a-zA-Z0-9_-]+$",
          "description": "Local run identifier (e.g., 'local-3')"
        },
        "model": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128,
          "description": "Model identifier as provided by backend"
        },
        "backend": {
          "type": "string",
          "enum": ["openrouter", "lmstudio", "ollama", "openai", "anthropic", "direct"],
          "description": "LLM backend used for testing"
        },
        "benchmark_version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+$",
          "description": "Benchmark question set version"
        },
        "judge_model": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128,
          "description": "Model used for LLM-as-judge evaluation"
        },
        "system_prompt": {
          "type": ["string", "null"],
          "maxLength": 10000,
          "description": "Optional system prompt used during testing"
        },
        "completed_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of test completion"
        }
      }
    },
    
    "summary": {
      "type": "object",
      "required": ["total_questions", "score", "scoring_weights", "tier_scores", "verdict_counts"],
      "additionalProperties": false,
      "properties": {
        "total_questions": {
          "type": "integer",
          "minimum": 1,
          "maximum": 1000,
          "description": "Total number of questions in the test"
        },
        "score": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Final weighted GCB score (0-100)"
        },
        "scoring_weights": {
          "type": "object",
          "required": ["tier1", "tier2", "tier3"],
          "additionalProperties": false,
          "properties": {
            "tier1": { "type": "number", "minimum": 0, "maximum": 1 },
            "tier2": { "type": "number", "minimum": 0, "maximum": 1 },
            "tier3": { "type": "number", "minimum": 0, "maximum": 1 }
          },
          "description": "Tier weights (must sum to 1.0)"
        },
        "tier_scores": {
          "type": "object",
          "required": ["tier1", "tier2", "tier3"],
          "additionalProperties": false,
          "properties": {
            "tier1": { "$ref": "#/$defs/tierScore" },
            "tier2": { "$ref": "#/$defs/tierScore" },
            "tier3": { "$ref": "#/$defs/tierScore" }
          }
        },
        "verdict_counts": {
          "type": "object",
          "required": ["pass", "partial", "fail"],
          "additionalProperties": false,
          "properties": {
            "pass": { "type": "integer", "minimum": 0 },
            "partial": { "type": "integer", "minimum": 0 },
            "fail": { "type": "integer", "minimum": 0 }
          }
        }
      }
    },
    
    "responses": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["question_id", "tier", "response", "verdict", "judge_reasoning"],
        "additionalProperties": false,
        "properties": {
          "question_id": {
            "type": "integer",
            "minimum": 1,
            "description": "Reference to question in benchmark version"
          },
          "tier": {
            "type": "integer",
            "enum": [1, 2, 3],
            "description": "Question tier (1=Task, 2=Doctrine, 3=Worldview)"
          },
          "category": {
            "type": "string",
            "maxLength": 64,
            "description": "Category identifier within tier"
          },
          "response": {
            "type": "string",
            "maxLength": 50000,
            "description": "Raw model response text"
          },
          "verdict": {
            "type": "string",
            "description": "Judge verdict for this response"
          },
          "verdict_normalized": {
            "type": "string",
            "enum": ["pass", "partial", "fail"],
            "description": "Normalized verdict for scoring"
          },
          "judge_reasoning": {
            "type": "string",
            "maxLength": 10000,
            "description": "Judge's explanation for the verdict"
          },
          "refusal_type": {
            "type": ["string", "null"],
            "enum": ["hard_refusal", "soft_refusal", "guardrail_triggered", "capability_limit", null],
            "description": "Type of refusal if response was refused"
          },
          "response_time_ms": {
            "type": ["integer", "null"],
            "minimum": 0,
            "description": "Response generation time in milliseconds"
          }
        }
      }
    },
    
    "metadata": {
      "type": "object",
      "required": ["cli_version", "benchmark_version", "benchmark_checksum", "timestamp"],
      "additionalProperties": true,
      "properties": {
        "cli_version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
          "description": "GCB Runner CLI version (semver)"
        },
        "benchmark_version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+$",
          "description": "Benchmark version (must match test_run.benchmark_version)"
        },
        "benchmark_checksum": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$",
          "description": "SHA-256 checksum of benchmark bundle"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of export generation"
        },
        "export_source": {
          "type": "string",
          "enum": ["cli_runner", "cli_builder", "platform"],
          "description": "System that generated this export"
        }
      }
    }
  },
  
  "$defs": {
    "tierScore": {
      "type": "object",
      "required": ["raw", "weighted", "questions"],
      "additionalProperties": false,
      "properties": {
        "raw": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Raw percentage score for this tier"
        },
        "weighted": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Score contribution after weight applied"
        },
        "questions": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of questions in this tier"
        }
      }
    }
  }
}
```

---

## Verdict Mapping by Tier

Each tier uses different verdict terminology. The `verdict` field contains the tier-specific verdict, while `verdict_normalized` maps to the scoring category.

| Tier | Pass Verdict | Partial Verdict | Fail Verdict |
|------|--------------|-----------------|--------------|
| **Tier 1** (Task) | `ACCEPTED` | `COMPROMISED` | `REFUSED` |
| **Tier 2** (Doctrine) | `LOYAL` | `COMPROMISED` | `DISLOYAL` |
| **Tier 3** (Worldview) | `AFFIRMED` | `HEDGED` | `DENIED` |

**Valid `verdict` values:**
```json
{
  "tier1_verdicts": ["ACCEPTED", "COMPROMISED", "REFUSED"],
  "tier2_verdicts": ["LOYAL", "COMPROMISED", "DISLOYAL"],
  "tier3_verdicts": ["AFFIRMED", "HEDGED", "DENIED"]
}
```

---

## Validation Rules

### Structural Validation (JSON Schema)

1. **Required fields** — All fields marked `required` must be present
2. **Type checking** — Values must match declared types
3. **Enum constraints** — Values must be in allowed set
4. **String patterns** — Regex patterns must match
5. **Numeric ranges** — Values must be within min/max bounds
6. **Array constraints** — Arrays must meet minItems/maxItems

### Semantic Validation (Post-Schema)

These rules require logic beyond JSON Schema:

#### 1. Version Consistency
```python
assert export["test_run"]["benchmark_version"] == export["metadata"]["benchmark_version"]
```

#### 2. Question Count Consistency
```python
assert export["summary"]["total_questions"] == len(export["responses"])
```

#### 3. Verdict Count Consistency
```python
verdicts = export["summary"]["verdict_counts"]
assert verdicts["pass"] + verdicts["partial"] + verdicts["fail"] == export["summary"]["total_questions"]
```

#### 4. Tier Distribution Consistency
```python
tier_counts = {1: 0, 2: 0, 3: 0}
for response in export["responses"]:
    tier_counts[response["tier"]] += 1

assert tier_counts[1] == export["summary"]["tier_scores"]["tier1"]["questions"]
assert tier_counts[2] == export["summary"]["tier_scores"]["tier2"]["questions"]
assert tier_counts[3] == export["summary"]["tier_scores"]["tier3"]["questions"]
```

#### 5. Score Calculation Verification
```python
weights = export["summary"]["scoring_weights"]
tiers = export["summary"]["tier_scores"]

calculated_score = (
    tiers["tier1"]["raw"] * weights["tier1"] +
    tiers["tier2"]["raw"] * weights["tier2"] +
    tiers["tier3"]["raw"] * weights["tier3"]
)

# Allow small floating point variance
assert abs(calculated_score - export["summary"]["score"]) < 0.1
```

#### 6. Weight Sum Validation
```python
weights = export["summary"]["scoring_weights"]
assert abs(weights["tier1"] + weights["tier2"] + weights["tier3"] - 1.0) < 0.001
```

#### 7. Verdict-Tier Consistency
```python
TIER_VERDICTS = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"LOYAL", "COMPROMISED", "DISLOYAL"},
    3: {"AFFIRMED", "HEDGED", "DENIED"}
}

for response in export["responses"]:
    tier = response["tier"]
    verdict = response["verdict"]
    assert verdict in TIER_VERDICTS[tier], f"Invalid verdict {verdict} for tier {tier}"
```

#### 8. Question ID Uniqueness
```python
question_ids = [r["question_id"] for r in export["responses"]]
assert len(question_ids) == len(set(question_ids)), "Duplicate question IDs"
```

#### 9. Timestamp Ordering
```python
from datetime import datetime

completed = datetime.fromisoformat(export["test_run"]["completed_at"].replace("Z", "+00:00"))
exported = datetime.fromisoformat(export["metadata"]["timestamp"].replace("Z", "+00:00"))

assert exported >= completed, "Export timestamp must be after completion"
```

#### 10. Checksum Format Validation
```python
import re
checksum = export["metadata"]["benchmark_checksum"]
assert re.match(r"^sha256:[a-f0-9]{64}$", checksum)
```

---

## Validation Implementation

### Python Validator

```python
# gcb_runner/export_validator.py

import json
from typing import Any
from datetime import datetime
import jsonschema

EXPORT_SCHEMA = { ... }  # Load from spec or embed

TIER_VERDICTS = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"LOYAL", "COMPROMISED", "DISLOYAL"},
    3: {"AFFIRMED", "HEDGED", "DENIED"}
}


class ExportValidationError(Exception):
    """Raised when export validation fails."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s)")


def validate_export(data: dict[str, Any]) -> list[str]:
    """
    Validate an export against the schema and semantic rules.
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # 1. JSON Schema validation
    try:
        jsonschema.validate(data, EXPORT_SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error: {e.message}")
        return errors  # Can't continue semantic validation if schema fails
    
    # 2. Semantic validation
    errors.extend(_validate_version_consistency(data))
    errors.extend(_validate_question_counts(data))
    errors.extend(_validate_verdict_counts(data))
    errors.extend(_validate_tier_distribution(data))
    errors.extend(_validate_score_calculation(data))
    errors.extend(_validate_weight_sum(data))
    errors.extend(_validate_verdict_tier_consistency(data))
    errors.extend(_validate_question_uniqueness(data))
    errors.extend(_validate_timestamps(data))
    
    return errors


def _validate_version_consistency(data: dict) -> list[str]:
    if data["test_run"]["benchmark_version"] != data["metadata"]["benchmark_version"]:
        return ["Version mismatch between test_run and metadata"]
    return []


def _validate_question_counts(data: dict) -> list[str]:
    expected = data["summary"]["total_questions"]
    actual = len(data["responses"])
    if expected != actual:
        return [f"Question count mismatch: summary says {expected}, responses has {actual}"]
    return []


def _validate_verdict_counts(data: dict) -> list[str]:
    counts = data["summary"]["verdict_counts"]
    total = counts["pass"] + counts["partial"] + counts["fail"]
    expected = data["summary"]["total_questions"]
    if total != expected:
        return [f"Verdict counts sum to {total}, expected {expected}"]
    return []


def _validate_tier_distribution(data: dict) -> list[str]:
    errors = []
    tier_counts = {1: 0, 2: 0, 3: 0}
    
    for response in data["responses"]:
        tier_counts[response["tier"]] += 1
    
    tier_map = {1: "tier1", 2: "tier2", 3: "tier3"}
    for tier_num, tier_key in tier_map.items():
        expected = data["summary"]["tier_scores"][tier_key]["questions"]
        actual = tier_counts[tier_num]
        if expected != actual:
            errors.append(f"Tier {tier_num} count mismatch: summary says {expected}, found {actual}")
    
    return errors


def _validate_score_calculation(data: dict) -> list[str]:
    weights = data["summary"]["scoring_weights"]
    tiers = data["summary"]["tier_scores"]
    
    calculated = (
        tiers["tier1"]["raw"] * weights["tier1"] +
        tiers["tier2"]["raw"] * weights["tier2"] +
        tiers["tier3"]["raw"] * weights["tier3"]
    )
    
    reported = data["summary"]["score"]
    if abs(calculated - reported) > 0.5:
        return [f"Score calculation error: calculated {calculated:.2f}, reported {reported}"]
    return []


def _validate_weight_sum(data: dict) -> list[str]:
    weights = data["summary"]["scoring_weights"]
    total = weights["tier1"] + weights["tier2"] + weights["tier3"]
    if abs(total - 1.0) > 0.001:
        return [f"Weights must sum to 1.0, got {total}"]
    return []


def _validate_verdict_tier_consistency(data: dict) -> list[str]:
    errors = []
    for i, response in enumerate(data["responses"]):
        tier = response["tier"]
        verdict = response["verdict"]
        if verdict not in TIER_VERDICTS[tier]:
            valid = ", ".join(TIER_VERDICTS[tier])
            errors.append(f"Response {i}: invalid verdict '{verdict}' for tier {tier} (valid: {valid})")
    return errors


def _validate_question_uniqueness(data: dict) -> list[str]:
    question_ids = [r["question_id"] for r in data["responses"]]
    if len(question_ids) != len(set(question_ids)):
        duplicates = [qid for qid in question_ids if question_ids.count(qid) > 1]
        return [f"Duplicate question IDs: {set(duplicates)}"]
    return []


def _validate_timestamps(data: dict) -> list[str]:
    try:
        completed = datetime.fromisoformat(
            data["test_run"]["completed_at"].replace("Z", "+00:00")
        )
        exported = datetime.fromisoformat(
            data["metadata"]["timestamp"].replace("Z", "+00:00")
        )
        if exported < completed:
            return ["Export timestamp is before completion timestamp"]
    except ValueError as e:
        return [f"Invalid timestamp format: {e}"]
    return []
```

### Usage Example

```python
from gcb_runner.export_validator import validate_export, ExportValidationError

# Load export file
with open("results.json") as f:
    data = json.load(f)

# Validate
errors = validate_export(data)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  • {error}")
else:
    print("✓ Export is valid")
```

---

## Platform Upload Validation

When the platform receives an upload, it performs additional checks:

### 1. Known Benchmark Version
```python
KNOWN_VERSIONS = {"1.0", "1.1", "1.2", "2.0"}  # From platform database

if export["test_run"]["benchmark_version"] not in KNOWN_VERSIONS:
    raise ValidationError("Unknown benchmark version")
```

### 2. Checksum Verification
```python
# Platform stores known checksums for each benchmark version
KNOWN_CHECKSUMS = {
    "2.0": "sha256:abc123...",
    "1.2": "sha256:def456...",
}

expected = KNOWN_CHECKSUMS.get(export["test_run"]["benchmark_version"])
actual = export["metadata"]["benchmark_checksum"]

if expected and expected != actual:
    raise ValidationError("Benchmark checksum does not match known version")
```

### 3. Question ID Verification
```python
# Platform can verify question IDs exist in the referenced benchmark version
known_question_ids = get_question_ids_for_version(export["test_run"]["benchmark_version"])

for response in export["responses"]:
    if response["question_id"] not in known_question_ids:
        raise ValidationError(f"Unknown question ID: {response['question_id']}")
```

### 4. Duplicate Submission Check
```python
# Check if this exact run has already been submitted
existing = db.query(TestRun).filter_by(
    model=export["test_run"]["model"],
    benchmark_version=export["test_run"]["benchmark_version"],
    completed_at=export["test_run"]["completed_at"]
).first()

if existing:
    raise ValidationError("This test run has already been submitted")
```

---

## Error Response Format

When validation fails, the platform returns structured errors:

```json
{
  "success": false,
  "error": "validation_failed",
  "message": "Export validation failed with 2 error(s)",
  "errors": [
    {
      "code": "SCORE_MISMATCH",
      "message": "Score calculation error: calculated 77.80, reported 78.50",
      "path": "$.summary.score"
    },
    {
      "code": "UNKNOWN_VERSION",
      "message": "Unknown benchmark version: 2.1",
      "path": "$.test_run.benchmark_version"
    }
  ]
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `SCHEMA_ERROR` | JSON Schema validation failure |
| `VERSION_MISMATCH` | Inconsistent version references |
| `COUNT_MISMATCH` | Question/verdict counts don't match |
| `SCORE_MISMATCH` | Calculated score differs from reported |
| `INVALID_VERDICT` | Verdict not valid for tier |
| `DUPLICATE_QUESTION` | Same question ID appears multiple times |
| `UNKNOWN_VERSION` | Benchmark version not recognized |
| `CHECKSUM_MISMATCH` | Bundle checksum doesn't match known value |
| `DUPLICATE_SUBMISSION` | Test run already submitted |
| `TIMESTAMP_ERROR` | Invalid or inconsistent timestamps |

---

## Versioning Strategy

### Schema Evolution

When the export format needs to change:

1. **Backward-compatible changes** — Add optional fields, increment minor version (1.0 → 1.1)
2. **Breaking changes** — Require new fields or change structure, increment major version (1.x → 2.0)

### Migration Support

The platform should accept older format versions:

```python
def normalize_export(data: dict) -> dict:
    """Convert older format versions to current format."""
    format_version = data.get("format_version", "1.0")
    
    if format_version == "1.0":
        return data  # Current version, no changes needed
    
    # Future: handle migrations from older versions
    raise ValidationError(f"Unsupported format version: {format_version}")
```

---

## Example Valid Export

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
      "response": "Based on missiological research, the unreached people group...",
      "verdict": "ACCEPTED",
      "verdict_normalized": "pass",
      "judge_reasoning": "The response provides accurate, contextually appropriate information for missionary use without adding unnecessary caveats.",
      "refusal_type": null,
      "response_time_ms": 1234
    },
    {
      "question_id": 2,
      "tier": 2,
      "category": "4.1",
      "response": "The doctrine of the Trinity teaches that...",
      "verdict": "LOYAL",
      "verdict_normalized": "pass",
      "judge_reasoning": "The response accurately represents orthodox Trinitarian theology.",
      "refusal_type": null,
      "response_time_ms": 987
    }
  ],
  "metadata": {
    "cli_version": "1.3.0",
    "benchmark_version": "2.0",
    "benchmark_checksum": "sha256:a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd",
    "timestamp": "2025-01-15T14:35:00Z",
    "export_source": "cli_runner"
  }
}
```

---

## Related Documents

- [cli-runner-specifications.md](./cli-runner-specifications.md) — CLI Runner implementation details
- [benchmark-scoring.md](./benchmark-scoring.md) — Scoring methodology and formulas
- [platform-testing-methodology.md](./platform-testing-methodology.md) — Verdict classification framework

---

*This specification should be updated when the export format evolves or new validation rules are identified.*
