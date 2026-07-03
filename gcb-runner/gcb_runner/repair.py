"""Repair invalid benchmark rows by retesting failed questions."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gcb_runner.api.cache import QuestionCache
from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.backends import get_backend
from gcb_runner.backends.common import EXTRACTION_PROVIDER_ERROR, CompletionResult
from gcb_runner.config import Config
from gcb_runner.export import export_run
from gcb_runner.judge import VERDICT_SCORES, Judge
from gcb_runner.results import (
    JUDGE_ERROR_OUTCOME,
    JUDGE_TIMEOUT_OUTCOME,
    TEST_ERROR_MARKER_PREFIX,
    TEST_ERROR_VERDICT,
    VALIDITY_COMPLETE_INVALID,
    VALIDITY_COMPLETE_VALID,
    Response,
    ResultsDB,
)
from gcb_runner.runner import JUDGE_REQUEST_TIMEOUT_SECONDS, MODEL_REQUEST_TIMEOUT_SECONDS

REPAIRABLE_OUTCOMES = {
    None,
    "",
    EXTRACTION_PROVIDER_ERROR,
    JUDGE_TIMEOUT_OUTCOME,
    JUDGE_ERROR_OUTCOME,
    "NO_PARSEABLE_ASSISTANT_OUTPUT",
    "UNSUPPORTED_SHAPE",
}


@dataclass
class RepairCandidate:
    """A response row that can be repaired."""

    response_id: int
    question_id: str
    tier: int
    category: str | None
    verdict: str
    extraction_outcome: str | None
    reason: str


@dataclass
class RepairResult:
    """Summary of a repair run."""

    run_id: int
    model: str
    benchmark_version: str
    repaired_question_ids: list[str] = field(default_factory=list)
    remaining_error_question_ids: list[str] = field(default_factory=list)
    score: float | None = None
    validity: str | None = None
    extraction_error_count: int = 0
    export_path: str | None = None
    dry_run: bool = False
    candidates: list[RepairCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "model": self.model,
            "benchmark_version": self.benchmark_version,
            "repaired_question_ids": self.repaired_question_ids,
            "remaining_error_question_ids": self.remaining_error_question_ids,
            "score": self.score,
            "validity": self.validity,
            "extraction_error_count": self.extraction_error_count,
            "export_path": self.export_path,
            "dry_run": self.dry_run,
            "candidates": [candidate.__dict__ for candidate in self.candidates],
        }


def is_repairable_response(response: Response) -> bool:
    """Return True for infrastructure failure rows, never real model outcomes."""
    if response.verdict != TEST_ERROR_VERDICT:
        return False
    outcome = response.extraction_outcome
    return outcome in REPAIRABLE_OUTCOMES


def list_repair_candidates(
    db: ResultsDB,
    run_id: int,
    question_ids: list[str] | None = None,
) -> list[RepairCandidate]:
    """List repairable rows for a run, optionally restricted to question IDs."""
    requested = {str(qid) for qid in question_ids} if question_ids else None
    candidates: list[RepairCandidate] = []
    for response in db.get_responses(run_id):
        if requested is not None and response.question_id not in requested:
            continue
        if not is_repairable_response(response):
            continue
        outcome = response.extraction_outcome
        candidates.append(
            RepairCandidate(
                response_id=response.id,
                question_id=response.question_id,
                tier=response.tier,
                category=response.category,
                verdict=response.verdict,
                extraction_outcome=outcome,
                reason=f"repair {outcome or TEST_ERROR_VERDICT}",
            )
        )
    return candidates


async def _load_questions_data(config: Config, version: str) -> dict[str, Any]:
    cache = QuestionCache()
    cached = cache.get(version)
    if cached and not cache.is_stale(version):
        return cached

    client = PlatformAPIClient(config.platform.api_key or "", config.platform.url)
    try:
        data = await client.get_questions(version)
    finally:
        await client.close()

    if not data.get("is_draft", False):
        cache.store(version, data)
    return data


def _actual_version(questions_data: dict[str, Any], fallback: str) -> str:
    raw = questions_data.get("version", fallback)
    if isinstance(raw, dict):
        return str(raw.get("semantic_version", fallback))
    return str(raw)


def _test_error_payload(
    *,
    outcome: str,
    provider: str | None,
    finish_reason: str | None,
    sources: list[str],
    raw_summary: str | None,
    response_time_ms: int | None,
    thought_process: str | None = None,
) -> dict[str, Any]:
    marker = (
        f"{TEST_ERROR_MARKER_PREFIX} {outcome}] "
        f"provider={provider or 'unknown'} "
        f"finish_reason={finish_reason or 'unknown'} "
        f"sources={sources}"
    )
    return {
        "response_text": marker,
        "verdict": TEST_ERROR_VERDICT,
        "judge_reasoning": (
            f"Repair attempt still produced an infrastructure failure ({outcome}). "
            "This row remains excluded from scoring and the run remains invalid."
        ),
        "thought_process": thought_process,
        "response_time_ms": response_time_ms,
        "extraction_outcome": outcome,
        "extraction_sources": sources,
        "extraction_provider": provider,
        "finish_reason": finish_reason,
        "raw_message_summary": raw_summary,
    }


async def _retest_question(
    *,
    question: dict[str, Any],
    model: str,
    model_backend: Any,
    judge: Judge,
) -> dict[str, Any]:
    start = time.time()
    completion_result: CompletionResult | None = None
    transport_error: str | None = None
    try:
        completion_result = await asyncio.wait_for(
            model_backend.complete(
                messages=[{"role": "user", "content": question.get("content", "")}],
                model=model,
            ),
            timeout=MODEL_REQUEST_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        transport_error = f"Timed out waiting for model response after {MODEL_REQUEST_TIMEOUT_SECONDS:.0f}s"
    except Exception as exc:
        transport_error = str(exc)

    response_time_ms = int((time.time() - start) * 1000)

    if transport_error is not None:
        return _test_error_payload(
            outcome=EXTRACTION_PROVIDER_ERROR,
            provider=None,
            finish_reason=None,
            sources=[],
            raw_summary=f"transport_error: {transport_error}"[:2000],
            response_time_ms=response_time_ms,
        )

    assert completion_result is not None
    if not completion_result.is_class_a or completion_result.text is None:
        return _test_error_payload(
            outcome=completion_result.outcome,
            provider=completion_result.provider,
            finish_reason=completion_result.finish_reason,
            sources=completion_result.sources,
            raw_summary=completion_result.raw_message_summary,
            response_time_ms=response_time_ms,
            thought_process=completion_result.thought_process,
        )

    try:
        verdict = await asyncio.wait_for(
            judge.evaluate(question, completion_result.text),
            timeout=JUDGE_REQUEST_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        return _test_error_payload(
            outcome=JUDGE_TIMEOUT_OUTCOME,
            provider=completion_result.provider,
            finish_reason=completion_result.finish_reason,
            sources=completion_result.sources,
            raw_summary=f"judge_timeout: timed out after {JUDGE_REQUEST_TIMEOUT_SECONDS:.0f}s",
            response_time_ms=response_time_ms,
            thought_process=completion_result.thought_process,
        )
    except Exception as exc:
        return _test_error_payload(
            outcome=JUDGE_ERROR_OUTCOME,
            provider=completion_result.provider,
            finish_reason=completion_result.finish_reason,
            sources=completion_result.sources,
            raw_summary=f"judge_error: {exc}"[:2000],
            response_time_ms=response_time_ms,
            thought_process=completion_result.thought_process,
        )

    return {
        "response_text": completion_result.text,
        "verdict": verdict.verdict,
        "judge_reasoning": verdict.reasoning,
        "thought_process": completion_result.thought_process,
        "response_time_ms": response_time_ms,
        "extraction_outcome": completion_result.outcome,
        "extraction_sources": completion_result.sources,
        "extraction_provider": completion_result.provider,
        "finish_reason": completion_result.finish_reason,
        "raw_message_summary": None,
    }


def recompute_run_scores(db: ResultsDB, run_id: int, scoring_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Recompute score and validity from current response rows."""
    scoring_config = scoring_config or {}
    weights = {
        1: float(scoring_config.get("tier1_weight", 0.70)),
        2: float(scoring_config.get("tier2_weight", 0.20)),
        3: float(scoring_config.get("tier3_weight", 0.10)),
    }
    tier_results: dict[int, dict[str, int]] = {
        1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
        2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
        3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
    }
    responses = db.get_responses(run_id)
    extraction_error_count = 0
    outcomes: dict[str, int] = {}

    for response in responses:
        if response.verdict == TEST_ERROR_VERDICT:
            extraction_error_count += 1
            key = response.extraction_outcome or "UNKNOWN"
            outcomes[key] = outcomes.get(key, 0) + 1
            continue
        if response.tier not in tier_results:
            continue
        verdict = response.verdict if response.verdict in tier_results[response.tier] else "REFUSED"
        tier_results[response.tier][verdict] += 1

    tier_scores: dict[int, float] = {}
    for tier in [1, 2, 3]:
        total = sum(tier_results[tier].values())
        if total:
            tier_scores[tier] = (
                tier_results[tier]["ACCEPTED"] * VERDICT_SCORES["ACCEPTED"]
                + tier_results[tier]["COMPROMISED"] * VERDICT_SCORES["COMPROMISED"]
                + tier_results[tier]["REFUSED"] * VERDICT_SCORES["REFUSED"]
            ) / total * 100
        else:
            tier_scores[tier] = 0.0

    final_score = sum(tier_scores[tier] * weights[tier] for tier in [1, 2, 3])
    validity = VALIDITY_COMPLETE_VALID if extraction_error_count == 0 else VALIDITY_COMPLETE_INVALID
    validity_reason = None
    if extraction_error_count:
        validity_reason = (
            f"{extraction_error_count} question(s) produced no trustworthy "
            f"model answer or judge verdict; outcomes={outcomes}. Run is not publishable."
        )

    db.complete_run(run_id, final_score, tier_scores[1], tier_scores[2], tier_scores[3])
    db.set_validity(run_id, validity, extraction_error_count, validity_reason)
    return {
        "score": final_score,
        "tier_scores": tier_scores,
        "validity": validity,
        "extraction_error_count": extraction_error_count,
        "validity_reason": validity_reason,
    }


async def repair_run(
    run_id: int,
    config: Config,
    *,
    question_ids: list[str] | None = None,
    dry_run: bool = False,
    max_questions: int = 5,
    output_path: Path | None = None,
    db: ResultsDB | None = None,
) -> RepairResult:
    """Repair one local run by retesting repairable failed rows."""
    actual_db = db or ResultsDB()
    run = actual_db.get_run(run_id)
    if run is None:
        raise ValueError(f"Test run #{run_id} not found")
    if run.completed_at is None:
        raise ValueError(f"Test run #{run_id} is not complete")

    candidates = list_repair_candidates(actual_db, run_id, question_ids)
    if question_ids:
        found = {candidate.question_id for candidate in candidates}
        missing = sorted({str(qid) for qid in question_ids} - found)
        if missing:
            raise ValueError(
                "No repairable TEST_ERROR row found for question id(s): "
                + ", ".join(missing)
            )
    if len(candidates) > max_questions:
        raise ValueError(
            f"Refusing to repair {len(candidates)} rows; increase --max-questions above {max_questions}."
        )

    result = RepairResult(
        run_id=run_id,
        model=run.model,
        benchmark_version=run.benchmark_version,
        score=run.score,
        validity=run.validity,
        extraction_error_count=run.extraction_error_count,
        dry_run=dry_run,
        candidates=candidates,
    )
    if dry_run or not candidates:
        return result

    questions_data = await _load_questions_data(config, run.benchmark_version)
    actual_version = _actual_version(questions_data, run.benchmark_version)
    if actual_version != run.benchmark_version:
        raise ValueError(
            f"Question version mismatch: run has {run.benchmark_version}, API returned {actual_version}"
        )
    questions = {str(q.get("id")): q for q in questions_data.get("questions", [])}
    judge_prompts = questions_data.get("judge_prompts") or questions_data.get("prompts")
    scoring_config = questions_data.get("scoring_config", {})

    backend_config = config.get_backend_config(run.backend)
    judge_backend = run.judge_backend or run.backend
    judge_backend_config = config.get_backend_config(judge_backend)

    model_backend = get_backend(
        run.backend,
        api_key=backend_config.api_key,
        base_url=backend_config.base_url,
    )
    judge_backend_instance = get_backend(
        judge_backend,
        api_key=judge_backend_config.api_key,
        base_url=judge_backend_config.base_url,
    )
    judge = Judge(judge_backend_instance, run.judge_model, judge_prompts)

    try:
        for candidate in candidates:
            question = questions.get(candidate.question_id)
            if question is None:
                raise ValueError(
                    f"Question {candidate.question_id} was not found in benchmark version {run.benchmark_version}"
                )
            payload = await _retest_question(
                question=question,
                model=run.model,
                model_backend=model_backend,
                judge=judge,
            )
            actual_db.replace_response_for_repair(
                candidate.response_id,
                repair_reason=candidate.reason,
                **payload,
            )
            result.repaired_question_ids.append(candidate.question_id)
    finally:
        await model_backend.close()
        await judge_backend_instance.close()

    recalculated = recompute_run_scores(actual_db, run_id, scoring_config)
    result.score = float(recalculated["score"])
    result.validity = str(recalculated["validity"])
    result.extraction_error_count = int(recalculated["extraction_error_count"])
    result.remaining_error_question_ids = [
        response.question_id
        for response in actual_db.get_responses(run_id)
        if response.verdict == TEST_ERROR_VERDICT
    ]

    if output_path is not None:
        output_path.write_text(export_run(actual_db, run_id), encoding="utf-8")
        result.export_path = str(output_path)

    return result
