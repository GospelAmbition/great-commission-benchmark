"""Tests for failed-question repair support."""

import pytest

from gcb_runner.export import export_run, validate_export
from gcb_runner.repair import recompute_run_scores
from gcb_runner.results import (
    JUDGE_TIMEOUT_OUTCOME,
    TEST_ERROR_MARKER_PREFIX,
    TEST_ERROR_VERDICT,
    VALIDITY_COMPLETE_INVALID,
    VALIDITY_COMPLETE_VALID,
    ResultsDB,
)


def _create_completed_run(db: ResultsDB) -> int:
    run = db.create_run(
        model="provider/model",
        backend="openrouter",
        benchmark_version="2.0",
        judge_model="openai/gpt-oss-20b",
        judge_backend="openrouter",
    )
    db.add_response(
        run.id,
        "1",
        1,
        "answer",
        "ACCEPTED",
        category="1.1",
        judge_reasoning="ok",
        extraction_outcome="OK",
        extraction_sources=["message.content"],
        extraction_provider="openrouter",
    )
    db.add_response(
        run.id,
        "2",
        1,
        f"{TEST_ERROR_MARKER_PREFIX} JUDGE_TIMEOUT]",
        TEST_ERROR_VERDICT,
        category="1.1",
        judge_reasoning="judge timed out",
        extraction_outcome=JUDGE_TIMEOUT_OUTCOME,
        extraction_sources=["message.content"],
        extraction_provider="openrouter",
        raw_message_summary="judge_timeout",
    )
    for question_id in range(3, 11):
        tier = 1 if question_id <= 7 else (2 if question_id <= 9 else 3)
        db.add_response(
            run.id,
            str(question_id),
            tier,
            "answer",
            "ACCEPTED",
            category=f"{tier}.1",
            judge_reasoning="ok",
            extraction_outcome="OK",
            extraction_sources=["message.content"],
            extraction_provider="openrouter",
        )
    db.complete_run(run.id, 100.0, 100.0, 0.0, 0.0)
    db.set_validity(run.id, VALIDITY_COMPLETE_INVALID, 1, "1 failure")
    return run.id


def test_repair_columns_migrate_and_metadata_persists(tmp_path):
    db = ResultsDB(tmp_path / "results.db")
    run_id = _create_completed_run(db)
    failed = [r for r in db.get_responses(run_id) if r.verdict == TEST_ERROR_VERDICT][0]

    db.replace_response_for_repair(
        failed.id,
        response_text="repaired answer",
        verdict="ACCEPTED",
        judge_reasoning="accepted after retry",
        thought_process=None,
        response_time_ms=123,
        extraction_outcome="OK",
        extraction_sources=["message.content"],
        extraction_provider="openrouter",
        finish_reason="stop",
        raw_message_summary=None,
        repair_reason="repair JUDGE_TIMEOUT",
    )

    repaired = [r for r in db.get_responses(run_id) if r.question_id == "2"][0]
    assert repaired.verdict == "ACCEPTED"
    assert repaired.repair_attempts == 1
    assert repaired.repaired_at is not None
    assert repaired.repair_reason == "repair JUDGE_TIMEOUT"
    assert "JUDGE_TIMEOUT" in (repaired.repair_original_snapshot or "")


def test_recompute_after_repair_marks_complete_valid(tmp_path):
    db = ResultsDB(tmp_path / "results.db")
    run_id = _create_completed_run(db)
    failed = [r for r in db.get_responses(run_id) if r.verdict == TEST_ERROR_VERDICT][0]

    db.replace_response_for_repair(
        failed.id,
        response_text="repaired answer",
        verdict="REFUSED",
        judge_reasoning="refused after retry",
        thought_process=None,
        response_time_ms=123,
        extraction_outcome="OK",
        extraction_sources=["message.content"],
        extraction_provider="openrouter",
        finish_reason="stop",
        raw_message_summary=None,
        repair_reason="repair JUDGE_TIMEOUT",
    )
    recalculated = recompute_run_scores(
        db,
        run_id,
        {"tier1_weight": 1.0, "tier2_weight": 0.0, "tier3_weight": 0.0},
    )

    assert recalculated["validity"] == VALIDITY_COMPLETE_VALID
    assert recalculated["extraction_error_count"] == 0
    assert recalculated["score"] == pytest.approx(85.714285714)
    run = db.get_run(run_id)
    assert run is not None
    assert run.validity == VALIDITY_COMPLETE_VALID


def test_export_includes_repair_metadata_and_validates(tmp_path):
    db = ResultsDB(tmp_path / "results.db")
    run_id = _create_completed_run(db)
    failed = [r for r in db.get_responses(run_id) if r.verdict == TEST_ERROR_VERDICT][0]

    db.replace_response_for_repair(
        failed.id,
        response_text="repaired answer",
        verdict="ACCEPTED",
        judge_reasoning="accepted after retry",
        thought_process=None,
        response_time_ms=123,
        extraction_outcome="OK",
        extraction_sources=["message.content"],
        extraction_provider="openrouter",
        finish_reason="stop",
        raw_message_summary=None,
        repair_reason="repair JUDGE_TIMEOUT",
    )
    recompute_run_scores(db, run_id)

    import json

    data = json.loads(export_run(db, run_id))
    repaired_rows = [row for row in data["responses"] if row.get("repair")]
    assert len(repaired_rows) == 1
    assert repaired_rows[0]["repair"]["reason"] == "repair JUDGE_TIMEOUT"
    assert repaired_rows[0]["repair"]["original"]["extraction_outcome"] == JUDGE_TIMEOUT_OUTCOME
    assert data["summary"]["validity"] == VALIDITY_COMPLETE_VALID
    assert validate_export(data) == []


def test_judge_timeout_payload_is_test_error(monkeypatch):
    import asyncio

    from gcb_runner.repair import _retest_question

    class ModelBackend:
        async def complete(self, messages, model):
            from gcb_runner.backends.common import CompletionResult

            return CompletionResult(
                text="captured model answer",
                outcome="OK",
                sources=["message.content"],
                finish_reason="stop",
                provider="openrouter",
            )

    class TimeoutJudge:
        async def evaluate(self, question, response):
            raise TimeoutError

    async def fake_wait_for(awaitable, timeout):
        try:
            return await awaitable
        except TimeoutError:
            raise TimeoutError from None

    monkeypatch.setattr("gcb_runner.repair.asyncio.wait_for", fake_wait_for)
    payload = asyncio.run(
        _retest_question(
            question={"id": "1", "tier": 1, "content": "Q"},
            model="provider/model",
            model_backend=ModelBackend(),
            judge=TimeoutJudge(),
        )
    )

    assert payload["verdict"] == TEST_ERROR_VERDICT
    assert payload["extraction_outcome"] == JUDGE_TIMEOUT_OUTCOME
