"""Test runner for executing benchmarks."""

import asyncio
import io
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from gcb_runner.api.cache import QuestionCache
from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.backends import (
    EXTRACTION_PROVIDER_ERROR,
    CompletionResult,
    get_backend,
)
from gcb_runner.config import Config
from gcb_runner.judge import Judge
from gcb_runner.results import (
    JUDGE_ERROR_OUTCOME,
    JUDGE_TIMEOUT_OUTCOME,
    TEST_ERROR_MARKER_PREFIX,
    TEST_ERROR_VERDICT,
    VALIDITY_COMPLETE_INVALID,
    VALIDITY_COMPLETE_VALID,
    ResultsDB,
)

console = Console()


def _timeout_from_env(name: str, default_seconds: float) -> float:
    """Read a positive timeout from the environment."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default_seconds
    try:
        value = float(raw)
    except ValueError:
        return default_seconds
    return value if value > 0 else default_seconds


MODEL_REQUEST_TIMEOUT_SECONDS = _timeout_from_env(
    "GCB_RUNNER_MODEL_TIMEOUT_SECONDS", 240.0
)
JUDGE_REQUEST_TIMEOUT_SECONDS = _timeout_from_env(
    "GCB_RUNNER_JUDGE_TIMEOUT_SECONDS", 360.0
)


def _infer_job_id_from_output_path(output_path: Path | None) -> str | None:
    """Infer MCP/job-worker job id from the conventional export filename."""
    if output_path is None:
        return None
    suffix = "-export.json"
    name = output_path.name
    if not name.endswith(suffix):
        return None
    job_id = name[: -len(suffix)]
    return job_id or None


def _record_job_progress(job_id: str | None, progress: dict) -> None:
    """Best-effort write to the shared jobs DB used by MCP/background runs."""
    if not job_id:
        return
    try:
        from gcb_runner.jobs import JobManager

        JobManager().update_progress(job_id, progress)
    except Exception:
        # Benchmark execution should not fail because observability failed.
        return


@dataclass
class BenchmarkResult:
    """Structured result from a benchmark run."""
    run_id: int
    model: str
    backend: str
    benchmark_version: str
    judge_model: str
    judge_backend: str
    score: float
    tier1_score: float
    tier2_score: float
    tier3_score: float
    tier_results: dict = field(default_factory=dict)
    total_questions: int = 0
    duration_seconds: float = 0.0
    completed_at: datetime | None = None
    is_draft: bool = False
    error: str | None = None
    validity: str = VALIDITY_COMPLETE_VALID
    extraction_error_count: int = 0
    validity_reason: str | None = None


async def run_benchmark(
    model: str,
    backend: str,
    config: Config,
    benchmark_version: str | None = None,
    judge_model: str | None = None,
    judge_backend: str | None = None,
    output_path: Path | None = None,
    resume: bool = False,
    is_draft: bool = False,
    quiet: bool = False,
) -> BenchmarkResult | None:
    """Run the benchmark against a model.
    
    Args:
        model: Model identifier (e.g., "openai/gpt-4o")
        backend: Backend name (e.g., "openrouter")
        config: GCB Runner configuration
        benchmark_version: Specific version to test, or None for current
        judge_model: Model to use as judge
        judge_backend: Backend for judge model
        output_path: Optional path to save export JSON
        resume: Whether to resume an interrupted run
        is_draft: Whether testing a draft version
        quiet: If True, suppress all console output (for batch/bulk usage)
    
    Returns:
        BenchmarkResult with structured data, or None on early failure
    """
    # Use a quiet console that discards output when in quiet mode
    out = Console(file=io.StringIO(), quiet=True) if quiet else console
    
    judge_model = judge_model or config.defaults.judge_model
    
    # Determine judge backend: explicit > config default > auto-detect
    if judge_backend is None:
        judge_backend = config.defaults.judge_backend
    
    # Initialize components
    api_client = PlatformAPIClient(config.platform.api_key or "", config.platform.url)
    cache = QuestionCache()
    db = ResultsDB()
    
    backend_config = config.get_backend_config(backend)
    
    # Validate API key for cloud backends before initializing
    if backend in ["openrouter", "openai", "anthropic"] and (
        not backend_config.api_key or not backend_config.api_key.strip()
    ):
        out.print(f"[red]Error: {backend.title()} API key is not configured.[/red]")
        out.print()
        out.print("Please configure it using one of these methods:")
        out.print("  • Run: [cyan]gcb-runner config[/cyan]")
        out.print("  • Run: [cyan]gcb-runner menu[/cyan] → Configure Backend")
        out.print()
        raise ValueError(f"{backend.title()} API key is required")
    
    model_backend = get_backend(
        backend,
        api_key=backend_config.api_key,
        base_url=backend_config.base_url,
    )
    
    # Determine judge backend if not explicitly set
    if judge_backend is None:
        # Auto-detect: use openrouter/openai for judge if model backend is local
        if backend in ["lmstudio", "ollama"]:
            # Try to use openrouter for judging, fall back to openai
            if config.get_backend_config("openrouter").api_key:
                judge_backend = "openrouter"
            elif config.get_backend_config("openai").api_key:
                judge_backend = "openai"
            else:
                out.print("[yellow]Warning: Using local model for judging. Results may be less reliable.[/yellow]")
                judge_backend = backend
        else:
            judge_backend = backend
    
    # Initialize judge backend
    judge_backend_config = config.get_backend_config(judge_backend)
    
    # Validate API key for cloud judge backends before initializing
    if judge_backend in ["openrouter", "openai", "anthropic"] and (
        not judge_backend_config.api_key or not judge_backend_config.api_key.strip()
    ):
        out.print(f"[red]Error: {judge_backend.title()} API key is not configured for judge backend.[/red]")
        out.print()
        out.print("Please configure it using one of these methods:")
        out.print("  • Run: [cyan]gcb-runner config[/cyan]")
        out.print("  • Run: [cyan]gcb-runner menu[/cyan] → Configure Backend")
        out.print()
        raise ValueError(f"{judge_backend.title()} API key is required for judge backend")
    
    judge_backend_instance = get_backend(
        judge_backend,
        api_key=judge_backend_config.api_key,
        base_url=judge_backend_config.base_url,
    )
    
    try:
        # Fetch questions
        out.print("Fetching questions from Platform API...")
        out.print(f"[dim]API URL: {config.platform.url}[/dim]")
        
        version = benchmark_version or "current"
        
        # Check cache first - but skip cache for draft versions since they can change
        cached_data = None
        skip_cache = is_draft
        
        if not skip_cache and version != "current":
            cached_data = cache.get(version)
            # Also skip cache if cached data indicates it's a draft (drafts can change)
            if cached_data and cached_data.get("is_draft", False):
                out.print("[dim]Skipping cache for draft version (content may have changed)[/dim]")
                cached_data = None
                skip_cache = True
        
        if skip_cache:
            out.print("[dim]Fetching fresh questions for draft version[/dim]")
        
        if cached_data and not cache.is_stale(version):
            out.print("[green]✓ Using cached questions[/green]")
            questions_data = cached_data
        else:
            try:
                questions_data = await api_client.get_questions(version if version != "current" else None)
                # Only cache non-draft versions (drafts can change frequently)
                if questions_data.get("is_draft", False):
                    # Clear any stale cached data for this draft version
                    cache.clear(version)
                else:
                    cache.store(version, questions_data)
                out.print("[green]✓ Connected to Platform API[/green]")
            except Exception as e:
                error_msg = str(e)
                if "not found" in error_msg.lower():
                    out.print("[red]Error: No benchmark questions available.[/red]")
                    out.print()
                    out.print("[dim]This could mean:[/dim]")
                    out.print("  • No benchmark version has been published yet")
                    out.print("  • The requested version doesn't exist")
                    out.print()
                    out.print("[dim]Run 'gcb-runner menu' → Utilities → Diagnostics to troubleshoot.[/dim]")
                    raise
                if cached_data:
                    out.print(f"[yellow]Warning: Could not fetch fresh questions ({e}), using cache[/yellow]")
                    questions_data = cached_data
                else:
                    raise
        
        # Get judge prompts
        judge_prompts = questions_data.get("judge_prompts") or questions_data.get("prompts")
        
        # Extract data
        actual_version = questions_data.get("version", version)
        if isinstance(actual_version, dict):
            actual_version = actual_version.get("semantic_version", version)
        
        questions = questions_data.get("questions", [])
        scoring_config = questions_data.get("scoring_config", {})
        
        # Default weights
        tier1_weight = scoring_config.get("tier1_weight", 0.70)
        tier2_weight = scoring_config.get("tier2_weight", 0.20)
        tier3_weight = scoring_config.get("tier3_weight", 0.10)
        
        # Check if this is a draft version
        is_draft_test = questions_data.get("is_draft", False)
        if is_draft_test:
            out.print("[yellow]⚠️  Testing draft version - results won't be published to leaderboard[/yellow]")
            out.print()
        
        # Count questions by tier
        tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
        for q in questions:
            tier = q.get("tier", 1)
            tier_counts[tier] += 1
        
        out.print(f"[green]✓ {len(questions)} questions loaded[/green]")
        out.print(f"  Tier 1: {tier_counts[1]}, Tier 2: {tier_counts[2]}, Tier 3: {tier_counts[3]}")
        out.print()
        
        # Check for resume
        run_id: int | None = None
        answered_ids: set[str] = set()
        
        if resume:
            existing_run = db.get_incomplete_run(model, actual_version)
            if existing_run:
                run_id = existing_run.id
                answered_ids = db.get_answered_question_ids(run_id)
                out.print(f"[yellow]Resuming test run #{run_id} ({len(answered_ids)} questions answered)[/yellow]")
        
        # Create new run if not resuming
        if run_id is None:
            run = db.create_run(
                model=model,
                backend=backend,
                benchmark_version=actual_version,
                judge_model=judge_model,
                judge_backend=judge_backend,
                is_draft_test=is_draft_test,
            )
            run_id = run.id

        background_job_id = _infer_job_id_from_output_path(output_path)

        def record_progress(phase: str, **fields: object) -> None:
            _record_job_progress(
                background_job_id,
                {
                    "phase": phase,
                    "model": model,
                    "backend": backend,
                    "judge_backend": judge_backend,
                    "updated_at": datetime.now().isoformat(),
                    **fields,
                },
            )
        
        out.print(f"[bold]Testing: {model} via {backend}[/bold]")
        out.print(f"[bold]Judge: {judge_model} via {judge_backend}[/bold]")
        out.print()
        
        # Record test start time
        test_start_time = datetime.now()
        out.print(f"[dim]Test started: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        out.print()
        record_progress(
            "run_started",
            questions_done=len(answered_ids),
            questions_total=len(questions),
        )
        
        # Initialize judge
        judge = Judge(judge_backend_instance, judge_model, judge_prompts)
        
        # Run tests by tier - track by verdict
        tier_results: dict[int, dict[str, int]] = {
            1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
        }
        total_question_count = len(questions)
        questions_seen = len(answered_ids)
        
        # Calculate actual tier counts from questions
        tier_counts = {1: 0, 2: 0, 3: 0}
        for q in questions:
            tier = q.get("tier")
            if tier in tier_counts:
                tier_counts[tier] += 1
        
        tier_names = {
            1: f"Tier 1 - Use Cases (70%) [{tier_counts[1]} questions]",
            2: f"Tier 2 - Theology (20%) [{tier_counts[2]} questions]",
            3: f"Tier 3 - Worldview (10%) [{tier_counts[3]} questions]",
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=out,
        ) as progress:
            for tier in [1, 2, 3]:
                tier_questions = [q for q in questions if q.get("tier") == tier]
                remaining = [q for q in tier_questions if str(q.get("id")) not in answered_ids]
                
                task = progress.add_task(tier_names[tier], total=len(tier_questions))
                
                # Update progress for already answered questions
                already_done = len(tier_questions) - len(remaining)
                progress.update(task, advance=already_done)
                
                for question in remaining:
                    question_id = str(question.get("id"))
                    questions_seen += 1
                    category = question.get("category") or "unknown"

                    start_time = time.time()
                    completion_result: CompletionResult | None = None
                    transport_error: str | None = None
                    out.print(
                        f"[dim]Question start: {questions_seen}/{total_question_count} "
                        f"tier={tier} id={question_id} category={category} "
                        f"step=model_request timeout={MODEL_REQUEST_TIMEOUT_SECONDS:.0f}s[/dim]"
                    )
                    record_progress(
                        "model_request",
                        questions_done=max(0, questions_seen - 1),
                        questions_total=total_question_count,
                        current_question=questions_seen,
                        tier=tier,
                        question_id=question_id,
                        category=category,
                        timeout_seconds=MODEL_REQUEST_TIMEOUT_SECONDS,
                    )
                    try:
                        completion_result = await asyncio.wait_for(
                            model_backend.complete(
                                messages=[{"role": "user", "content": question.get("content", "")}],
                                model=model,
                            ),
                            timeout=MODEL_REQUEST_TIMEOUT_SECONDS,
                        )
                        model_elapsed_ms = int((time.time() - start_time) * 1000)
                        out.print(
                            f"[dim]Question model_done: {questions_seen}/{total_question_count} "
                            f"tier={tier} id={question_id} outcome={completion_result.outcome} "
                            f"elapsed_ms={model_elapsed_ms}[/dim]"
                        )
                        record_progress(
                            "model_done",
                            questions_done=max(0, questions_seen - 1),
                            questions_total=total_question_count,
                            current_question=questions_seen,
                            tier=tier,
                            question_id=question_id,
                            category=category,
                            outcome=completion_result.outcome,
                            elapsed_ms=model_elapsed_ms,
                        )
                    except asyncio.TimeoutError:
                        transport_error = (
                            f"Timed out waiting for model response after "
                            f"{MODEL_REQUEST_TIMEOUT_SECONDS:.0f}s"
                        )
                        out.print(f"[red]Transport error for question {question_id}: {transport_error}[/red]")
                        record_progress(
                            "model_timeout",
                            questions_done=max(0, questions_seen - 1),
                            questions_total=total_question_count,
                            current_question=questions_seen,
                            tier=tier,
                            question_id=question_id,
                            category=category,
                            timeout_seconds=MODEL_REQUEST_TIMEOUT_SECONDS,
                        )
                    except Exception as e:
                        out.print(f"[red]Transport error for question {question_id}: {e}[/red]")
                        transport_error = str(e)
                        record_progress(
                            "model_error",
                            questions_done=max(0, questions_seen - 1),
                            questions_total=total_question_count,
                            current_question=questions_seen,
                            tier=tier,
                            question_id=question_id,
                            category=category,
                            error=str(e)[:500],
                        )

                    response_time_ms = int((time.time() - start_time) * 1000)

                    if completion_result is not None and completion_result.is_class_a and completion_result.text is not None:
                        response_text = completion_result.text
                        thought_process = completion_result.thought_process
                        judge_failure_outcome: str | None = None
                        judge_failure_summary: str | None = None
                        judge_failure_reasoning: str | None = None
                        try:
                            out.print(
                                f"[dim]Question judge_start: {questions_seen}/{total_question_count} "
                                f"tier={tier} id={question_id} "
                                f"timeout={JUDGE_REQUEST_TIMEOUT_SECONDS:.0f}s[/dim]"
                            )
                            record_progress(
                                "judge_request",
                                questions_done=max(0, questions_seen - 1),
                                questions_total=total_question_count,
                                current_question=questions_seen,
                                tier=tier,
                                question_id=question_id,
                                category=category,
                                timeout_seconds=JUDGE_REQUEST_TIMEOUT_SECONDS,
                            )
                            verdict = await asyncio.wait_for(
                                judge.evaluate(question, response_text),
                                timeout=JUDGE_REQUEST_TIMEOUT_SECONDS,
                            )
                            out.print(
                                f"[dim]Question judge_done: {questions_seen}/{total_question_count} "
                                f"tier={tier} id={question_id} verdict={verdict.verdict}[/dim]"
                            )
                            record_progress(
                                "judge_done",
                                questions_done=questions_seen,
                                questions_total=total_question_count,
                                current_question=questions_seen,
                                tier=tier,
                                question_id=question_id,
                                category=category,
                                verdict=verdict.verdict,
                            )
                        except asyncio.TimeoutError:
                            out.print(
                                f"[red]Error judging question {question_id}: "
                                f"timed out after {JUDGE_REQUEST_TIMEOUT_SECONDS:.0f}s[/red]"
                            )
                            record_progress(
                                "judge_timeout",
                                questions_done=max(0, questions_seen - 1),
                                questions_total=total_question_count,
                                current_question=questions_seen,
                                tier=tier,
                                question_id=question_id,
                                category=category,
                                    timeout_seconds=JUDGE_REQUEST_TIMEOUT_SECONDS,
                                )
                            judge_failure_outcome = JUDGE_TIMEOUT_OUTCOME
                            judge_failure_summary = (
                                f"judge_timeout: timed out after "
                                f"{JUDGE_REQUEST_TIMEOUT_SECONDS:.0f}s"
                            )
                            judge_failure_reasoning = (
                                f"Judge timeout ({JUDGE_TIMEOUT_OUTCOME}). The runner captured "
                                "a model answer but could not obtain a trustworthy judge verdict. "
                                "This row is excluded from scoring and marks the run as "
                                "COMPLETE_INVALID."
                            )
                        except Exception as e:
                            out.print(f"[red]Error judging question {question_id}: {e}[/red]")
                            record_progress(
                                "judge_error",
                                questions_done=max(0, questions_seen - 1),
                                questions_total=total_question_count,
                                current_question=questions_seen,
                                tier=tier,
                                question_id=question_id,
                                category=category,
                                    error=str(e)[:500],
                                )
                            judge_failure_outcome = JUDGE_ERROR_OUTCOME
                            judge_failure_summary = f"judge_error: {e}"[:2000]
                            judge_failure_reasoning = (
                                f"Judge error ({JUDGE_ERROR_OUTCOME}). The runner captured "
                                "a model answer but could not obtain a trustworthy judge verdict. "
                                "This row is excluded from scoring and marks the run as "
                                "COMPLETE_INVALID."
                            )

                        if judge_failure_outcome is None:
                            db.add_response(
                                run_id=run_id,
                                question_id=question_id,
                                tier=tier,
                                category=question.get("category"),
                                response_text=response_text,
                                verdict=verdict.verdict,
                                judge_reasoning=verdict.reasoning,
                                thought_process=thought_process,
                                response_time_ms=response_time_ms,
                                extraction_outcome=completion_result.outcome,
                                extraction_sources=completion_result.sources,
                                extraction_provider=completion_result.provider,
                                finish_reason=completion_result.finish_reason,
                            )

                            count_verdict = verdict.verdict if verdict.verdict in tier_results[tier] else "REFUSED"
                            tier_results[tier][count_verdict] += 1
                        else:
                            marker = (
                                f"{TEST_ERROR_MARKER_PREFIX} {judge_failure_outcome}] "
                                f"provider={completion_result.provider or 'unknown'} "
                                f"finish_reason={completion_result.finish_reason or 'unknown'} "
                                f"sources={completion_result.sources}"
                            )
                            db.add_response(
                                run_id=run_id,
                                question_id=question_id,
                                tier=tier,
                                category=question.get("category"),
                                response_text=marker,
                                verdict=TEST_ERROR_VERDICT,
                                judge_reasoning=judge_failure_reasoning,
                                thought_process=thought_process,
                                response_time_ms=response_time_ms,
                                extraction_outcome=judge_failure_outcome,
                                extraction_sources=completion_result.sources,
                                extraction_provider=completion_result.provider,
                                finish_reason=completion_result.finish_reason,
                                raw_message_summary=judge_failure_summary,
                            )
                            out.print(
                                f"[yellow]Judge failure on question {question_id} "
                                f"({judge_failure_outcome}); run will be marked COMPLETE_INVALID.[/yellow]"
                            )
                    else:
                        # Class B path: transport failure or unrecognized response
                        # shape. We do NOT ask the judge to score nothing, we do
                        # NOT count this as a model refusal, and we do NOT allow
                        # a null row. We store a structured marker so reviewers
                        # can tell this apart from real model behavior, and we
                        # flag the whole run as COMPLETE_INVALID later.
                        if transport_error is not None:
                            outcome = EXTRACTION_PROVIDER_ERROR
                            sources: list[str] = []
                            provider = None
                            finish_reason = None
                            raw_summary = f"transport_error: {transport_error}"[:2000]
                        else:
                            assert completion_result is not None
                            outcome = completion_result.outcome
                            sources = completion_result.sources
                            provider = completion_result.provider
                            finish_reason = completion_result.finish_reason
                            raw_summary = completion_result.raw_message_summary

                        marker = (
                            f"{TEST_ERROR_MARKER_PREFIX} {outcome}] "
                            f"provider={provider or 'unknown'} "
                            f"finish_reason={finish_reason or 'unknown'} "
                            f"sources={sources}"
                        )
                        reasoning = (
                            f"Extraction failure ({outcome}). The runner could not "
                            "obtain a trustworthy model answer for this question, so "
                            "it was not sent to the judge. This row is excluded from "
                            "scoring and marks the run as COMPLETE_INVALID."
                        )

                        db.add_response(
                            run_id=run_id,
                            question_id=question_id,
                            tier=tier,
                            category=question.get("category"),
                            response_text=marker,
                            verdict=TEST_ERROR_VERDICT,
                            judge_reasoning=reasoning,
                            thought_process=None,
                            response_time_ms=response_time_ms,
                            extraction_outcome=outcome,
                            extraction_sources=sources,
                            extraction_provider=provider,
                            finish_reason=finish_reason,
                            raw_message_summary=raw_summary,
                        )
                        out.print(
                            f"[yellow]Extraction failure on question {question_id} "
                            f"({outcome}); run will be marked COMPLETE_INVALID.[/yellow]"
                        )
                        record_progress(
                            "extraction_failure",
                            questions_done=questions_seen,
                            questions_total=total_question_count,
                            current_question=questions_seen,
                            tier=tier,
                            question_id=question_id,
                            category=category,
                            outcome=outcome,
                        )

                    progress.update(task, advance=1)
        
        # Calculate scores using VERDICT_SCORES
        from gcb_runner.judge import VERDICT_SCORES
        tier_scores: dict[int, float] = {}
        for tier in [1, 2, 3]:
            total = tier_results[tier]["ACCEPTED"] + tier_results[tier]["COMPROMISED"] + tier_results[tier]["REFUSED"]
            if total > 0:
                # ACCEPTED = 1.0, COMPROMISED = 0.5, REFUSED = 0.0
                score = (
                    tier_results[tier]["ACCEPTED"] * VERDICT_SCORES["ACCEPTED"] +
                    tier_results[tier]["COMPROMISED"] * VERDICT_SCORES["COMPROMISED"] +
                    tier_results[tier]["REFUSED"] * VERDICT_SCORES["REFUSED"]
                ) / total * 100
            else:
                score = 0.0
            tier_scores[tier] = score
        
        # Calculate weighted score
        final_score = (
            tier_scores[1] * tier1_weight +
            tier_scores[2] * tier2_weight +
            tier_scores[3] * tier3_weight
        )
        
        # Compute run validity BEFORE completing. A single Class B extraction
        # is enough to invalidate the run: the benchmark's statistical claim
        # depends on us actually having heard from the model on every
        # question we score.
        all_responses = db.get_responses(run_id)
        extraction_error_count = sum(
            1 for r in all_responses if r.verdict == TEST_ERROR_VERDICT
        )
        validity = (
            VALIDITY_COMPLETE_VALID
            if extraction_error_count == 0
            else VALIDITY_COMPLETE_INVALID
        )
        validity_reason: str | None
        if extraction_error_count == 0:
            validity_reason = None
        else:
            outcomes: dict[str, int] = {}
            for r in all_responses:
                if r.verdict == TEST_ERROR_VERDICT:
                    key = r.extraction_outcome or "UNKNOWN"
                    outcomes[key] = outcomes.get(key, 0) + 1
            validity_reason = (
                f"{extraction_error_count} question(s) produced no trustworthy "
                f"model answer; outcomes={outcomes}. Run is not publishable."
            )

        db.complete_run(
            run_id,
            score=final_score,
            tier1_score=tier_scores[1],
            tier2_score=tier_scores[2],
            tier3_score=tier_scores[3],
        )
        db.set_validity(
            run_id,
            validity=validity,
            extraction_error_count=extraction_error_count,
            reason=validity_reason,
        )

        test_end_time = datetime.now()
        test_duration = test_end_time - test_start_time
        
        # Display results
        out.print()
        out.print("═" * 60)
        out.print()
        out.print(f"[dim]Test started:  {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        out.print(f"[dim]Test ended:    {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        out.print(f"[dim]Duration:      {test_duration}[/dim]")
        out.print()
        out.print("[bold]RESULTS SUMMARY[/bold]")
        out.print()
        out.print(f"Model: {model}")
        out.print(f"Benchmark: v{actual_version}")
        out.print()
        
        table = Table()
        table.add_column("Tier", style="cyan")
        table.add_column("Accepted", style="green", justify="right")
        table.add_column("Compromised", style="yellow", justify="right")
        table.add_column("Refused", style="red", justify="right")
        table.add_column("Weight", justify="right")
        
        tier_display_names = {
            1: "Tier 1: Use Cases",
            2: "Tier 2: Theology",
            3: "Tier 3: Worldview",
        }
        tier_weights_str = {1: "70%", 2: "20%", 3: "10%"}
        
        for tier in [1, 2, 3]:
            stats = tier_results[tier]
            total = stats["ACCEPTED"] + stats["COMPROMISED"] + stats["REFUSED"]
            if total > 0:
                table.add_row(
                    tier_display_names[tier],
                    f"{stats['ACCEPTED']} ({stats['ACCEPTED']*100//total}%)",
                    f"{stats['COMPROMISED']} ({stats['COMPROMISED']*100//total}%)",
                    f"{stats['REFUSED']} ({stats['REFUSED']*100//total}%)",
                    tier_weights_str[tier],
                )
        
        # Add total row
        total_accepted = sum(tier_results[t]["ACCEPTED"] for t in [1, 2, 3])
        total_compromised = sum(tier_results[t]["COMPROMISED"] for t in [1, 2, 3])
        total_refused = sum(tier_results[t]["REFUSED"] for t in [1, 2, 3])
        total_all = total_accepted + total_compromised + total_refused
        
        if total_all > 0:
            table.add_row(
                "[bold]OVERALL (weighted)[/bold]",
                f"[bold]{total_accepted} ({total_accepted*100//total_all}%)[/bold]",
                f"[bold]{total_compromised} ({total_compromised*100//total_all}%)[/bold]",
                f"[bold]{total_refused} ({total_refused*100//total_all}%)[/bold]",
                "[bold]100%[/bold]",
            )
        
        out.print(table)
        out.print()
        
        # Show scoring breakdown
        out.print("[bold]Scoring breakdown:[/bold]")
        out.print(f"  Tier 1: {tier_scores[1]:.1f}% × 0.70 = {tier_scores[1] * tier1_weight:.1f}")
        out.print(f"  Tier 2: {tier_scores[2]:.1f}% × 0.20 = {tier_scores[2] * tier2_weight:.1f}")
        out.print(f"  Tier 3: {tier_scores[3]:.1f}% × 0.10 = {tier_scores[3] * tier3_weight:.1f}")
        out.print("  ─────────────────────────")
        out.print(f"  [bold green]GCB Score: {final_score:.1f}[/bold green]")
        out.print()

        if validity == VALIDITY_COMPLETE_INVALID:
            out.print(
                "[bold red]⚠️  Run validity: COMPLETE_INVALID[/bold red]"
            )
            out.print(f"[red]{validity_reason}[/red]")
            out.print(
                "[red]This run will NOT be uploaded to the leaderboard. "
                "Investigate the extraction failures before retrying.[/red]"
            )
        else:
            out.print("[green]Run validity: COMPLETE_VALID[/green]")

        out.print()
        out.print(f"Results saved. Run 'gcb-runner export --run {run_id}' to submit to the platform.")
        
        # Export if requested
        if output_path:
            from gcb_runner.export import export_run
            export_data = export_run(db, run_id)
            output_path.write_text(export_data)
            out.print(f"[green]Results exported to {output_path}[/green]")
        
        return BenchmarkResult(
            run_id=run_id,
            model=model,
            backend=backend,
            benchmark_version=actual_version,
            judge_model=judge_model,
            judge_backend=judge_backend,
            score=final_score,
            tier1_score=tier_scores[1],
            tier2_score=tier_scores[2],
            tier3_score=tier_scores[3],
            tier_results=tier_results,
            total_questions=len(questions),
            duration_seconds=test_duration.total_seconds(),
            completed_at=test_end_time,
            is_draft=is_draft_test,
            validity=validity,
            extraction_error_count=extraction_error_count,
            validity_reason=validity_reason,
        )
        
    finally:
        await model_backend.close()
        await judge_backend_instance.close()
        await api_client.close()
