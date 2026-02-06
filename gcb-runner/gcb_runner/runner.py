"""Test runner for executing benchmarks."""

import io
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from gcb_runner.api.cache import QuestionCache
from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.backends import get_backend
from gcb_runner.config import Config
from gcb_runner.judge import Judge
from gcb_runner.results import ResultsDB

console = Console()


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
    if backend in ["openrouter", "openai", "anthropic"]:
        if not backend_config.api_key or not backend_config.api_key.strip():
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
    if judge_backend in ["openrouter", "openai", "anthropic"]:
        if not judge_backend_config.api_key or not judge_backend_config.api_key.strip():
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
        
        out.print(f"[bold]Testing: {model} via {backend}[/bold]")
        out.print(f"[bold]Judge: {judge_model} via {judge_backend}[/bold]")
        out.print()
        
        # Record test start time
        test_start_time = datetime.now()
        out.print(f"[dim]Test started: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        out.print()
        
        # Initialize judge
        judge = Judge(judge_backend_instance, judge_model, judge_prompts)
        
        # Run tests by tier - track by verdict
        tier_results: dict[int, dict[str, int]] = {
            1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
        }
        
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
                    
                    # Get model response
                    start_time = time.time()
                    try:
                        completion_result = await model_backend.complete(
                            messages=[{"role": "user", "content": question.get("content", "")}],
                            model=model,
                        )
                        response_text = completion_result.text
                        thought_process = completion_result.thought_process
                    except Exception as e:
                        out.print(f"[red]Error getting response for question {question_id}: {e}[/red]")
                        response_text = f"[ERROR: {e}]"
                        thought_process = None
                    
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Judge the response (using only response_text, not thought_process)
                    try:
                        verdict = await judge.evaluate(question, response_text)
                    except Exception as e:
                        out.print(f"[red]Error judging question {question_id}: {e}[/red]")
                        # Default to REFUSED on judge error
                        from gcb_runner.judge import Verdict
                        verdict = Verdict(
                            verdict="REFUSED",
                            reasoning=f"Judge error: {e}",
                        )
                    
                    # Store response
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
                    )
                    
                    # Track verdict (treat ERROR as REFUSED for counting)
                    count_verdict = verdict.verdict if verdict.verdict in tier_results[tier] else "REFUSED"
                    tier_results[tier][count_verdict] += 1
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
        
        # Complete the run
        db.complete_run(
            run_id,
            score=final_score,
            tier1_score=tier_scores[1],
            tier2_score=tier_scores[2],
            tier3_score=tier_scores[3],
        )
        
        # Record test end time
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
        out.print(f"Results saved. Run 'gcb-runner export --run {run_id}' to submit to the platform.")
        
        # Export if requested
        if output_path:
            from gcb_runner.export import export_run
            export_data = export_run(db, run_id)
            output_path.write_text(export_data)
            out.print(f"[green]Results exported to {output_path}[/green]")
        
        # Return structured result
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
        )
        
    finally:
        await model_backend.close()
        await judge_backend_instance.close()
        await api_client.close()
