# Export Format Schema Validation

This document defines the canonical JSON schema specifications for all export formats in the Great Commission Benchmark system. **This is the single source of truth for export schemas.**

---

## Overview

The GCB system uses two distinct export schemas:

| Schema | Producer | Consumer | Purpose |
|--------|----------|----------|---------|
| **Test Results Export** | CLI Runner | Platform | Model evaluation results for leaderboard |

All systems must validate against these schemas to ensure data integrity and cross-system compatibility.

---

## Quick Reference

| Schema | Format Version | File Naming Convention |
|--------|----------------|------------------------|
| Test Results | `1.0` | `gcb-results-{model}-{date}.json` |

---

# Test Results Export Schema

This schema defines the structure for test results exported from the CLI Runner for upload to the Platform.

## Test Results Schema

| Field | Value | Notes |
|-------|-------|-------|
| **Schema Version** | `2.0` | Tracks schema evolution |
| **Format** | JSON | UTF-8 encoded |
| **File Extension** | `.json` | Recommended: `gcb-v{version}.json` |

### Complete JSON Schema (Benchmark Version)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://greatcommissionbenchmark.ai/schemas/benchmark-v2.0.json",
  "title": "GCB Benchmark Version Export",
  "description": "Schema for Great Commission Benchmark question set exports",
  "type": "object",
  "required": ["format_version", "benchmark_version", "name", "locked_at", "questions", "judge_prompts", "scoring", "metadata"],
  "additionalProperties": false,
  
  "properties": {
    "format_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Schema version for this export format",
      "examples": ["2.0"]
    },
    
    "benchmark_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Benchmark version identifier",
      "examples": ["2.0", "1.2"]
    },
    
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128,
      "description": "Human-readable version name",
      "examples": ["Version 2"]
    },
    
    "description": {
      "type": ["string", "null"],
      "maxLength": 2000,
      "description": "Version description and changelog"
    },
    
    "locked_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when version was locked"
    },
    
    "questions": {
      "type": "array",
      "minItems": 1,
      "maxItems": 1000,
      "items": { "$ref": "#/$defs/question" },
      "description": "Array of benchmark questions"
    },
    
    "judge_prompts": {
      "type": "object",
      "required": ["tier1_task", "tier2_doctrine", "tier3_worldview"],
      "additionalProperties": false,
      "properties": {
        "tier1_task": {
          "type": "string",
          "minLength": 100,
          "maxLength": 20000,
          "description": "Judge prompt for Tier 1 Task Capability questions"
        },
        "tier2_doctrine": {
          "type": "string",
          "minLength": 100,
          "maxLength": 20000,
          "description": "Judge prompt for Tier 2 Doctrinal Fidelity questions"
        },
        "tier3_worldview": {
          "type": "string",
          "minLength": 100,
          "maxLength": 20000,
          "description": "Judge prompt for Tier 3 Worldview Confession questions"
        }
      }
    },
    
    "scoring": {
      "type": "object",
      "required": ["weights", "formula"],
      "additionalProperties": true,
      "properties": {
        "weights": {
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
        "formula": {
          "type": "string",
          "description": "Human-readable scoring formula"
        },
        "rationale": {
          "type": "string",
          "description": "Explanation for weight choices"
        },
        "refusal_analysis": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "types": {
              "type": "array",
              "items": { "type": "string" }
            },
            "report_breakdown": { "type": "boolean" }
          },
          "description": "Refusal type analysis configuration"
        }
      }
    },
    
    "metadata": {
      "type": "object",
      "required": ["total_questions", "checksum"],
      "additionalProperties": true,
      "properties": {
        "total_questions": {
          "type": "integer",
          "minimum": 1,
          "description": "Total question count"
        },
        "category_counts": {
          "type": "object",
          "additionalProperties": { "type": "integer" },
          "description": "Question count per category"
        },
        "tier_counts": {
          "type": "object",
          "properties": {
            "tier1": { "type": "integer", "minimum": 0 },
            "tier2": { "type": "integer", "minimum": 0 },
            "tier3": { "type": "integer", "minimum": 0 }
          },
          "description": "Question count per tier"
        },
        "tier_percentages": {
          "type": "object",
          "properties": {
            "tier1": { "type": "number", "minimum": 0, "maximum": 100 },
            "tier2": { "type": "number", "minimum": 0, "maximum": 100 },
            "tier3": { "type": "number", "minimum": 0, "maximum": 100 }
          },
          "description": "Percentage of questions per tier"
        },
        "checksum": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$",
          "description": "SHA-256 checksum for integrity verification"
        },
        "filter_dimensions": {
          "type": "object",
          "description": "Available filter values for actionable reporting"
        }
      }
    },
    
    "reporting": {
      "type": "object",
      "properties": {
        "supported_filters": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Available filter dimensions for results"
        },
        "actionable_questions": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Example questions this benchmark helps answer"
        }
      },
      "description": "Reporting configuration for actionable insights"
    }
  },
  
  "$defs": {
    "question": {
      "type": "object",
      "required": ["id", "content", "category", "tier", "difficulty", "expected_verdict"],
      "additionalProperties": false,
      "properties": {
        "id": {
          "type": "integer",
          "minimum": 1,
          "description": "Unique question identifier"
        },
        "content": {
          "type": "string",
          "minLength": 10,
          "maxLength": 10000,
          "description": "Question text/prompt"
        },
        "category": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+[a-z]?$",
          "description": "Category code (e.g., '3.1', '3.6')"
        },
        "tier": {
          "type": "integer",
          "enum": [1, 2, 3],
          "description": "Question tier (1=Task, 2=Doctrine, 3=Worldview)"
        },
        "difficulty": {
          "type": "string",
          "enum": ["easy", "medium", "hard"],
          "description": "Difficulty level"
        },
        "expected_verdict": {
          "type": "string",
          "description": "Expected passing verdict for this question"
        },
        "expected_refusal_type": {
          "type": ["string", "null"],
          "enum": ["capability", "safety", "ideological", "unclear", null],
          "description": "Expected refusal type if refusal is anticipated"
        },
        "tests_capability": {
          "type": "boolean",
          "description": "Whether question tests model capability"
        },
        "tests_willingness": {
          "type": "boolean",
          "description": "Whether question tests model willingness"
        },
        "use_case_tags": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Use case classifications (e.g., 'chatbot', 'content_generation')"
        },
        "audience_context": {
          "type": ["string", "null"],
          "description": "Target audience context"
        },
        "ministry_type": {
          "type": ["string", "null"],
          "description": "Ministry context classification"
        }
      }
    }
  }
}
```

### Benchmark Version Export Example

```json
{
  "format_version": "2.0",
  "benchmark_version": "2.0",
  "name": "Version 2",
  "description": "Annual refresh with expanded coverage",
  "locked_at": "2026-01-15T00:00:00Z",
  
  "questions": [
    {
      "id": 1,
      "content": "Write a gospel presentation for a university student who is skeptical of organized religion...",
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
    "tier1_task": "You are evaluating LLM responses for task capability...",
    "tier2_doctrine": "You are evaluating LLM responses for doctrinal fidelity...",
    "tier3_worldview": "You are evaluating LLM responses for worldview confession..."
  },
  
  "scoring": {
    "weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    },
    "formula": "(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)",
    "rationale": "70/20/10 weighting prioritizes practical task capability",
    "refusal_analysis": {
      "enabled": true,
      "types": ["capability", "safety", "ideological", "unclear"],
      "report_breakdown": true
    }
  },
  
  "metadata": {
    "total_questions": 300,
    "category_counts": {
      "3.1": 35, "3.2": 35, "3.3": 35, "3.4": 35, "3.5": 35, "3.6": 18, "3.7": 17,
      "4.1": 15, "4.2": 15, "4.3": 15, "4.4": 15,
      "5.1": 10, "5.2": 10, "5.3": 10
    },
    "tier_counts": { "tier1": 210, "tier2": 60, "tier3": 30 },
    "tier_percentages": { "tier1": 70.0, "tier2": 20.0, "tier3": 10.0 },
    "checksum": "sha256:a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd",
    "filter_dimensions": {
      "use_case_tags": ["content_generation", "chatbot", "research", "translation"],
      "audience_contexts": ["secular_western", "muslim_background", "hindu_background"],
      "ministry_types": ["campus_ministry", "church_planting", "discipleship"],
      "tests_capability_count": 280,
      "tests_willingness_count": 250
    }
  },
  
  "reporting": {
    "supported_filters": [
      "by_tier", "by_category", "by_use_case_tag",
      "by_audience_context", "by_ministry_type",
      "by_capability_vs_willingness", "by_refusal_type"
    ],
    "actionable_questions": [
      "Which models work best for chatbot deployments?",
      "Which models can create content for Muslim-background seekers?",
      "Are refusals due to safety policies or ideological bias?",
      "Does the model have capability gaps or willingness gaps?"
    ]
  }
}
```

### Benchmark Version Validation Rules

#### Structural Validation (JSON Schema)

Standard JSON Schema validation applies for types, required fields, patterns, and ranges.

#### Semantic Validation

```python
# 1. Weight Sum Validation
weights = export["scoring"]["weights"]
assert abs(weights["tier1"] + weights["tier2"] + weights["tier3"] - 1.0) < 0.001

# 2. Question Count Consistency
assert export["metadata"]["total_questions"] == len(export["questions"])

# 3. Tier Count Consistency
tier_counts = {1: 0, 2: 0, 3: 0}
for q in export["questions"]:
    tier_counts[q["tier"]] += 1

assert tier_counts[1] == export["metadata"]["tier_counts"]["tier1"]
assert tier_counts[2] == export["metadata"]["tier_counts"]["tier2"]
assert tier_counts[3] == export["metadata"]["tier_counts"]["tier3"]

# 4. Question ID Uniqueness
question_ids = [q["id"] for q in export["questions"]]
assert len(question_ids) == len(set(question_ids))

# 5. Valid Category-Tier Mapping
TIER1_CATEGORIES = {"3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"}
TIER2_CATEGORIES = {"4.1", "4.2", "4.3", "4.4"}
TIER3_CATEGORIES = {"5.1", "5.2", "5.3"}

for q in export["questions"]:
    if q["tier"] == 1:
        assert q["category"] in TIER1_CATEGORIES
    elif q["tier"] == 2:
        assert q["category"] in TIER2_CATEGORIES
    elif q["tier"] == 3:
        assert q["category"] in TIER3_CATEGORIES

# 6. Expected Verdict Matches Tier
# All tiers now use unified verdicts
TIER_PASS_VERDICTS = {
    1: "ACCEPTED",
    2: "ACCEPTED",
    3: "ACCEPTED"
}

for q in export["questions"]:
    if q["expected_verdict"]:
        assert q["expected_verdict"] == TIER_PASS_VERDICTS[q["tier"]]
```

---

# Part 2: Test Results Export Schema

This schema defines the structure for test results exported from the CLI Runner for submission to the Platform.

## Test Results Schema

| Field | Value | Notes |
|-------|-------|-------|
| **Schema Version** | `1.0` | Tracks schema evolution |
| **Format** | JSON | UTF-8 encoded |
| **File Extension** | `.json` | Recommended: `gcb-results-{model}-{date}.json` |

### Complete JSON Schema (Test Results)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://greatcommissionbenchmark.ai/schemas/results-v1.0.json",
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
          "enum": ["cli_runner", "platform"],
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

All tiers use unified verdict terminology. The `verdict` field contains the verdict, while `verdict_normalized` maps to the scoring category.

| Verdict | Category | Points |
|---------|----------|--------|
| `ACCEPTED` | Pass | 1.0 |
| `COMPROMISED` | Partial | 0.5 |
| `REFUSED` | Fail | 0.0 |

**Valid `verdict` values (all tiers):**
```json
{
  "verdicts": ["ACCEPTED", "COMPROMISED", "REFUSED"],
  "legacy_tier2": ["LOYAL", "DISLOYAL"],
  "legacy_tier3": ["AFFIRMED", "HEDGED", "DENIED"]
}
```

**Note:** Legacy verdict names are accepted for backward compatibility with existing data.

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
# Valid verdicts (unified across all tiers, plus legacy for backward compatibility)
TIER_VERDICTS = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"ACCEPTED", "COMPROMISED", "REFUSED", "LOYAL", "DISLOYAL"},  # Legacy: LOYAL, DISLOYAL
    3: {"ACCEPTED", "COMPROMISED", "REFUSED", "AFFIRMED", "HEDGED", "DENIED"}  # Legacy
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

# Valid verdicts (unified across all tiers, plus legacy for backward compatibility)
TIER_VERDICTS = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"ACCEPTED", "COMPROMISED", "REFUSED", "LOYAL", "DISLOYAL"},  # Legacy: LOYAL, DISLOYAL
    3: {"ACCEPTED", "COMPROMISED", "REFUSED", "AFFIRMED", "HEDGED", "DENIED"}  # Legacy
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
      "verdict": "ACCEPTED",
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

- [cli-runner-specifications.md](./cli-runner-specifications.md) — CLI Runner implementation (produces Test Results exports)
- [spec-questions-api.md](./spec-questions-api.md) — Questions API for Runner
- [benchmark-scoring.md](./benchmark-scoring.md) — Scoring methodology and formulas
- [platform-testing-methodology.md](./platform-testing-methodology.md) — Verdict classification framework

---

**Note:** This document (`spec-export-schema-validation.md`) is the **canonical source** for all GCB export schemas. Other documents should reference this specification rather than duplicating schema definitions.

---

*Last Updated: December 17, 2025*
