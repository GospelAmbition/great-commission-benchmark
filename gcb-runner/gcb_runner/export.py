"""Export and validation for test results."""

import hashlib
import json
from datetime import datetime
from typing import Any

from gcb_runner import __version__
from gcb_runner.results import (
    TEST_ERROR_VERDICT,
    VALIDITY_COMPLETE_INVALID,
    VALIDITY_COMPLETE_VALID,
    VALIDITY_PENDING,
    ResultsDB,
)


def export_run(db: ResultsDB, run_id: int) -> str:
    """Export a test run to JSON format for platform submission."""
    run = db.get_run(run_id)
    if not run:
        raise ValueError(f"Test run #{run_id} not found")
    
    responses = db.get_responses(run_id)
    
    # Import verdict scores
    from gcb_runner.judge import VERDICT_SCORES
    
    # Calculate tier statistics by verdict
    tier_stats: dict[int, dict[str, Any]] = {
        1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "questions": 0},
        2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "questions": 0},
        3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "questions": 0},
    }
    
    # TEST_ERROR rows are extraction failures and MUST NOT be counted as
    # model refusals. They are tallied separately so reviewers can see the
    # run was incomplete.
    test_error_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
    for resp in responses:
        tier = resp.tier
        if resp.verdict == TEST_ERROR_VERDICT:
            test_error_counts[tier] = test_error_counts.get(tier, 0) + 1
            continue
        verdict = resp.verdict if resp.verdict in tier_stats[tier] else "REFUSED"
        tier_stats[tier][verdict] += 1
        tier_stats[tier]["questions"] += 1
    
    # Calculate tier scores using VERDICT_SCORES
    def calc_tier_score(stats: dict[str, Any]) -> float:
        total: int = stats["questions"]
        if total == 0:
            return 0.0
        raw_score: float = (
            stats["ACCEPTED"] * VERDICT_SCORES["ACCEPTED"] * 100 +
            stats["COMPROMISED"] * VERDICT_SCORES["COMPROMISED"] * 100 +
            stats["REFUSED"] * VERDICT_SCORES["REFUSED"] * 100
        )
        return raw_score / total
    
    tier_scores = {
        "tier1": {
            "raw": run.tier1_score or calc_tier_score(tier_stats[1]),
            "weighted": (run.tier1_score or calc_tier_score(tier_stats[1])) * 0.70,
            "questions": tier_stats[1]["questions"],
        },
        "tier2": {
            "raw": run.tier2_score or calc_tier_score(tier_stats[2]),
            "weighted": (run.tier2_score or calc_tier_score(tier_stats[2])) * 0.20,
            "questions": tier_stats[2]["questions"],
        },
        "tier3": {
            "raw": run.tier3_score or calc_tier_score(tier_stats[3]),
            "weighted": (run.tier3_score or calc_tier_score(tier_stats[3])) * 0.10,
            "questions": tier_stats[3]["questions"],
        },
    }
    
    # Build responses array
    # Normalize verdict: ACCEPTED -> pass, COMPROMISED -> partial, REFUSED -> fail
    verdict_map = {
        "ACCEPTED": "pass",
        "COMPROMISED": "partial",
        "REFUSED": "fail",
    }
    
    responses_data = []
    for resp in responses:
        verdict_normalized = getattr(resp, 'verdict_normalized', None)
        if not verdict_normalized:
            verdict_normalized = verdict_map.get(resp.verdict.upper(), "fail")

        sources_raw = getattr(resp, "extraction_sources", None)
        sources_parsed: Any = None
        if sources_raw:
            try:
                sources_parsed = json.loads(sources_raw)
            except Exception:
                sources_parsed = sources_raw

        response_data = {
            "question_id": int(resp.question_id) if resp.question_id.isdigit() else resp.question_id,
            "tier": resp.tier,
            "category": resp.category,
            "response": resp.response_text,
            "verdict": resp.verdict,
            "verdict_normalized": verdict_normalized,
            "judge_reasoning": resp.judge_reasoning,
            "thought_process": resp.thought_process,
            "response_time_ms": resp.response_time_ms,
            "extraction_outcome": getattr(resp, "extraction_outcome", None),
            "extraction_sources": sources_parsed,
            "extraction_provider": getattr(resp, "extraction_provider", None),
            "finish_reason": getattr(resp, "finish_reason", None),
            "raw_message_summary": getattr(resp, "raw_message_summary", None),
        }

        repaired_at = getattr(resp, "repaired_at", None)
        if repaired_at is not None:
            original_snapshot = None
            raw_snapshot = getattr(resp, "repair_original_snapshot", None)
            if raw_snapshot:
                try:
                    parsed_snapshot = json.loads(raw_snapshot)
                    if isinstance(parsed_snapshot, dict):
                        original_snapshot = {
                            "verdict": parsed_snapshot.get("verdict"),
                            "extraction_outcome": parsed_snapshot.get("extraction_outcome"),
                            "raw_message_summary": parsed_snapshot.get("raw_message_summary"),
                            "judge_reasoning": parsed_snapshot.get("judge_reasoning"),
                        }
                except Exception:
                    original_snapshot = {"raw": raw_snapshot[:500]}

            response_data["repair"] = {
                "repaired_at": repaired_at.isoformat() + "Z",
                "attempts": getattr(resp, "repair_attempts", 0) or 0,
                "reason": getattr(resp, "repair_reason", None),
                "original": original_snapshot,
            }

        responses_data.append(response_data)
    
    # Calculate checksum of responses for integrity
    responses_json = json.dumps(responses_data, sort_keys=True)
    checksum = hashlib.sha256(responses_json.encode()).hexdigest()
    
    validity = getattr(run, "validity", VALIDITY_PENDING) or VALIDITY_PENDING
    extraction_error_count = getattr(run, "extraction_error_count", 0) or 0
    validity_reason = getattr(run, "validity_reason", None)

    # Summarise extraction outcomes for operators reviewing the export.
    extraction_outcome_counts: dict[str, int] = {}
    for resp in responses:
        if resp.verdict == TEST_ERROR_VERDICT:
            key = getattr(resp, "extraction_outcome", None) or "UNKNOWN"
            extraction_outcome_counts[key] = extraction_outcome_counts.get(key, 0) + 1

    export_data = {
        "format_version": "1.1",
        "test_run": {
            "id": f"local-{run.id}",
            "model": run.model,
            "backend": run.backend,
            "benchmark_version": run.benchmark_version,
            "judge_model": run.judge_model,
            "judge_backend": getattr(run, 'judge_backend', None),
            "completed_at": run.completed_at.isoformat() + "Z" if run.completed_at else None,
            "is_draft_test": getattr(run, 'is_draft_test', False),
            "validity": validity,
            "extraction_error_count": extraction_error_count,
            "validity_reason": validity_reason,
        },
        "summary": {
            "total_questions": len(responses),
            "scored_questions": sum(tier_stats[t]["questions"] for t in [1, 2, 3]),
            "score": round(run.score or 0, 1),
            "scoring_weights": {
                "tier1": 0.70,
                "tier2": 0.20,
                "tier3": 0.10,
            },
            "tier_scores": tier_scores,
            "verdict_counts": {
                "ACCEPTED": sum(tier_stats[t]["ACCEPTED"] for t in [1, 2, 3]),
                "COMPROMISED": sum(tier_stats[t]["COMPROMISED"] for t in [1, 2, 3]),
                "REFUSED": sum(tier_stats[t]["REFUSED"] for t in [1, 2, 3]),
            },
            "test_error_counts": {
                "total": sum(test_error_counts.values()),
                "by_tier": test_error_counts,
                "by_outcome": extraction_outcome_counts,
            },
            "validity": validity,
            "publishable": validity == VALIDITY_COMPLETE_VALID,
        },
        "responses": responses_data,
        "metadata": {
            "cli_version": __version__,
            "benchmark_version": run.benchmark_version,
            "benchmark_checksum": f"sha256:{checksum[:64]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "export_source": "cli_runner",
            "response_count_including_test_errors": len(responses),
        },
    }
    
    return json.dumps(export_data, indent=2)


def validate_export(data: dict[str, Any]) -> list[str]:
    """
    Validate an export against the schema and semantic rules.
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []
    
    # Check required top-level fields
    required_fields = ["format_version", "test_run", "summary", "responses", "metadata"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors  # Can't continue if basic structure is wrong
    
    # Validate test_run
    test_run = data.get("test_run", {})
    required_test_run = ["id", "model", "backend", "benchmark_version", "judge_model", "completed_at"]
    for field in required_test_run:
        if field not in test_run:
            errors.append(f"Missing required test_run field: {field}")
    
    # Validate summary
    summary = data.get("summary", {})
    required_summary = ["total_questions", "score", "scoring_weights", "tier_scores", "verdict_counts"]
    for field in required_summary:
        if field not in summary:
            errors.append(f"Missing required summary field: {field}")
    
    errors.extend(_validate_version_consistency(data))
    errors.extend(_validate_question_counts(data))
    errors.extend(_validate_verdict_counts(data))
    errors.extend(_validate_tier_distribution(data))
    errors.extend(_validate_tier_balance(data))
    errors.extend(_validate_score_calculation(data))
    errors.extend(_validate_weight_sum(data))
    errors.extend(_validate_verdict_tier_consistency(data))
    errors.extend(_validate_question_uniqueness(data))
    errors.extend(_validate_run_validity(data))

    return errors


def _validate_run_validity(data: dict[str, Any]) -> list[str]:
    """Block uploads of runs that are not marked COMPLETE_VALID.

    This is the primary protection against publishing a run that failed to
    capture trustworthy model output. Legacy exports that predate the
    validity field are accepted (treated as VALID) for backward compat.
    """
    summary = data.get("summary", {})
    test_run = data.get("test_run", {})
    validity = summary.get("validity") or test_run.get("validity")
    if validity is None:
        return []  # legacy export, nothing to check
    if validity == VALIDITY_COMPLETE_VALID:
        return []
    if validity == VALIDITY_COMPLETE_INVALID:
        reason = test_run.get("validity_reason") or "extraction failures"
        return [f"Run validity is COMPLETE_INVALID and cannot be published ({reason})"]
    if validity == VALIDITY_PENDING:
        return ["Run validity is PENDING; finish the run before exporting"]
    return [f"Unknown run validity: {validity!r}"]


def _validate_version_consistency(data: dict[str, Any]) -> list[str]:
    if data.get("test_run", {}).get("benchmark_version") != data.get("metadata", {}).get("benchmark_version"):
        return ["Version mismatch between test_run and metadata"]
    return []


def _validate_question_counts(data: dict[str, Any]) -> list[str]:
    expected = data.get("summary", {}).get("total_questions", 0)
    actual = len(data.get("responses", []))
    if expected != actual:
        return [f"Question count mismatch: summary says {expected}, responses has {actual}"]
    return []


def _validate_verdict_counts(data: dict[str, Any]) -> list[str]:
    summary = data.get("summary", {})
    counts = summary.get("verdict_counts", {})
    total = counts.get("ACCEPTED", 0) + counts.get("COMPROMISED", 0) + counts.get("REFUSED", 0)
    # Scoring verdict counts must equal scored_questions (fallback to
    # total_questions for legacy exports that pre-date the scored/total split).
    expected = summary.get("scored_questions")
    if expected is None:
        expected = summary.get("total_questions", 0)
    if total != expected:
        return [f"Verdict counts sum to {total}, expected {expected}"]
    return []


def _validate_tier_distribution(data: dict[str, Any]) -> list[str]:
    """Compare per-tier scored counts against the response list (excluding
    TEST_ERROR rows, which are not part of scoring)."""
    errors: list[str] = []
    tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}

    for response in data.get("responses", []):
        if response.get("verdict") == TEST_ERROR_VERDICT:
            continue
        tier = response.get("tier", 1)
        if tier in tier_counts:
            tier_counts[tier] += 1

    tier_scores = data.get("summary", {}).get("tier_scores", {})
    tier_map = {1: "tier1", 2: "tier2", 3: "tier3"}

    for tier_num, tier_key in tier_map.items():
        expected = tier_scores.get(tier_key, {}).get("questions", 0)
        actual = tier_counts[tier_num]
        if expected != actual:
            errors.append(f"Tier {tier_num} count mismatch: summary says {expected}, found {actual}")

    return errors


# Percentage-based balance targets
TIER_PERCENTAGES: dict[int, float] = {1: 0.70, 2: 0.20, 3: 0.10}
BALANCE_TOLERANCE: float = 0.01  # ±1%


def _validate_tier_balance(data: dict[str, Any]) -> list[str]:
    """Validate tier distribution is within tolerance of 70/20/10 target.

    Excludes TEST_ERROR rows so extraction failures do not poison the
    structural balance check for an otherwise-publishable run.
    """
    errors: list[str] = []
    responses = [
        r for r in data.get("responses", [])
        if r.get("verdict") != TEST_ERROR_VERDICT
    ]
    total = len(responses)

    if total == 0:
        return ["No responses to validate"]

    tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
    for response in responses:
        tier = response.get("tier", 1)
        if tier in tier_counts:
            tier_counts[tier] += 1

    for tier, target_pct in TIER_PERCENTAGES.items():
        actual_pct = tier_counts.get(tier, 0) / total
        if abs(actual_pct - target_pct) > BALANCE_TOLERANCE:
            errors.append(
                f"Tier {tier} balance: {actual_pct:.1%} (expected {target_pct:.0%} ±{BALANCE_TOLERANCE:.0%})"
            )

    return errors


def _validate_score_calculation(data: dict[str, Any]) -> list[str]:
    weights = data.get("summary", {}).get("scoring_weights", {})
    tiers = data.get("summary", {}).get("tier_scores", {})
    
    if not weights or not tiers:
        return []
    
    calculated = (
        tiers.get("tier1", {}).get("raw", 0) * weights.get("tier1", 0.7) +
        tiers.get("tier2", {}).get("raw", 0) * weights.get("tier2", 0.2) +
        tiers.get("tier3", {}).get("raw", 0) * weights.get("tier3", 0.1)
    )
    
    reported = data.get("summary", {}).get("score", 0)
    if abs(calculated - reported) > 0.5:
        return [f"Score calculation error: calculated {calculated:.2f}, reported {reported}"]
    return []


def _validate_weight_sum(data: dict[str, Any]) -> list[str]:
    weights = data.get("summary", {}).get("scoring_weights", {})
    if not weights:
        return []
    
    total = weights.get("tier1", 0) + weights.get("tier2", 0) + weights.get("tier3", 0)
    if abs(total - 1.0) > 0.001:
        return [f"Weights must sum to 1.0, got {total}"]
    return []


# Valid verdicts for each tier (unified across all tiers)
TIER_VERDICTS: dict[int, set[str]] = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    3: {"ACCEPTED", "COMPROMISED", "REFUSED"},
}


def _validate_verdict_tier_consistency(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for i, response in enumerate(data.get("responses", [])):
        tier = response.get("tier", 1)
        verdict = response.get("verdict", "")

        # Allow ERROR verdict for legacy judge failures, and TEST_ERROR for
        # new extraction-failure rows which are excluded from scoring.
        if verdict in ("ERROR", TEST_ERROR_VERDICT):
            continue

        if tier in TIER_VERDICTS and verdict not in TIER_VERDICTS[tier]:
            valid = ", ".join(TIER_VERDICTS[tier])
            errors.append(f"Response {i}: invalid verdict '{verdict}' for tier {tier} (valid: {valid})")

    return errors


def _validate_question_uniqueness(data: dict[str, Any]) -> list[str]:
    question_ids = [r.get("question_id") for r in data.get("responses", [])]
    if len(question_ids) != len(set(question_ids)):
        duplicates = [qid for qid in question_ids if question_ids.count(qid) > 1]
        return [f"Duplicate question IDs: {set(duplicates)}"]
    return []
