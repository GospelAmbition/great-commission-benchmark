"""Test runner for executing benchmarks."""

import time
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.api.cache import QuestionCache
from gcb_runner.backends import get_backend
from gcb_runner.config import Config
from gcb_runner.judge import Judge
from gcb_runner.results import ResultsDB

console = Console()


async def run_benchmark(
    model: str,
    backend: str,
    config: Config,
    benchmark_version: str | None = None,
    judge_model: str | None = None,
    output_path: Path | None = None,
    resume: bool = False,
) -> None:
    """Run the benchmark against a model."""
    
    judge_model = judge_model or config.defaults.judge_model
    
    # Initialize components
    api_client = PlatformAPIClient(config.platform.api_key or "", config.platform.url)
    cache = QuestionCache()
    db = ResultsDB()
    
    backend_config = config.get_backend_config(backend)
    model_backend = get_backend(
        backend,
        api_key=backend_config.api_key,
        base_url=backend_config.base_url,
    )
    
    # Use openrouter for judge if model backend is local
    if backend in ["lmstudio", "ollama"]:
        # Try to use openrouter for judging, fall back to openai
        if config.get_backend_config("openrouter").api_key:
            judge_backend = get_backend("openrouter", api_key=config.get_backend_config("openrouter").api_key)
        elif config.get_backend_config("openai").api_key:
            judge_backend = get_backend("openai", api_key=config.get_backend_config("openai").api_key)
        else:
            console.print("[yellow]Warning: Using local model for judging. Results may be less reliable.[/yellow]")
            judge_backend = model_backend
    else:
        judge_backend = model_backend
    
    try:
        # Fetch questions
        console.print("Fetching questions from Platform API...")
        console.print(f"[dim]API URL: {config.platform.url}[/dim]")
        
        version = benchmark_version or "current"
        
        # Check cache first
        cached_data = cache.get(version) if version != "current" else None
        
        if cached_data and not cache.is_stale(version):
            console.print("[green]✓ Using cached questions[/green]")
            questions_data = cached_data
        else:
            try:
                questions_data = await api_client.get_questions(version if version != "current" else None)
                cache.store(version, questions_data)
                console.print("[green]✓ Connected to Platform API[/green]")
            except Exception as e:
                error_msg = str(e)
                if "not found" in error_msg.lower():
                    console.print("[red]Error: No benchmark questions available.[/red]")
                    console.print()
                    console.print("[dim]This could mean:[/dim]")
                    console.print("  • No benchmark version has been published yet")
                    console.print("  • The requested version doesn't exist")
                    console.print()
                    console.print("[dim]Run 'gcb-runner menu' → Diagnostics to troubleshoot.[/dim]")
                    raise
                if cached_data:
                    console.print(f"[yellow]Warning: Could not fetch fresh questions ({e}), using cache[/yellow]")
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
        
        # Count questions by tier
        tier_counts = {1: 0, 2: 0, 3: 0}
        for q in questions:
            tier = q.get("tier", 1)
            tier_counts[tier] += 1
        
        console.print(f"[green]✓ {len(questions)} questions loaded[/green]")
        console.print(f"  Tier 1: {tier_counts[1]}, Tier 2: {tier_counts[2]}, Tier 3: {tier_counts[3]}")
        console.print()
        
        # Check for resume
        run_id = None
        answered_ids: set[str] = set()
        
        if resume:
            existing_run = db.get_incomplete_run(model, actual_version)
            if existing_run:
                run_id = existing_run.id
                answered_ids = db.get_answered_question_ids(run_id)
                console.print(f"[yellow]Resuming test run #{run_id} ({len(answered_ids)} questions answered)[/yellow]")
        
        # Create new run if not resuming
        if run_id is None:
            run = db.create_run(
                model=model,
                backend=backend,
                benchmark_version=actual_version,
                judge_model=judge_model,
            )
            run_id = run.id
        
        console.print(f"[bold]Testing: {model} via {backend}[/bold]")
        console.print(f"[bold]Judge: {judge_model}[/bold]")
        console.print()
        
        # Record test start time
        test_start_time = datetime.now()
        console.print(f"[dim]Test started: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        console.print()
        
        # Initialize judge
        judge = Judge(judge_backend, judge_model, judge_prompts)
        
        # Run tests by tier - track by verdict
        tier_results: dict[int, dict[str, int]] = {
            1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
            3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0},
        }
        
        tier_names = {1: "Tier 1 - Use Cases (70%)", 2: "Tier 2 - Theology (20%)", 3: "Tier 3 - Worldview (10%)"}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
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
                        response_text = await model_backend.complete(
                            messages=[{"role": "user", "content": question.get("content", "")}],
                            model=model,
                        )
                    except Exception as e:
                        console.print(f"[red]Error getting response for question {question_id}: {e}[/red]")
                        response_text = f"[ERROR: {e}]"
                    
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Judge the response
                    try:
                        verdict = await judge.evaluate(question, response_text)
                    except Exception as e:
                        console.print(f"[red]Error judging question {question_id}: {e}[/red]")
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
                        response_time_ms=response_time_ms,
                    )
                    
                    # Track verdict (treat ERROR as REFUSED for counting)
                    count_verdict = verdict.verdict if verdict.verdict in tier_results[tier] else "REFUSED"
                    tier_results[tier][count_verdict] += 1
                    progress.update(task, advance=1)
        
        # Calculate scores using VERDICT_SCORES
        from gcb_runner.judge import VERDICT_SCORES
        tier_scores = {}
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
                score = 0
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
        console.print()
        console.print("═" * 60)
        console.print()
        console.print(f"[dim]Test started:  {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        console.print(f"[dim]Test ended:    {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        console.print(f"[dim]Duration:      {test_duration}[/dim]")
        console.print()
        console.print("[bold]RESULTS SUMMARY[/bold]")
        console.print()
        console.print(f"Model: {model}")
        console.print(f"Benchmark: v{actual_version}")
        console.print()
        
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
        tier_weights = {1: "70%", 2: "20%", 3: "10%"}
        
        for tier in [1, 2, 3]:
            stats = tier_results[tier]
            total = stats["ACCEPTED"] + stats["COMPROMISED"] + stats["REFUSED"]
            if total > 0:
                table.add_row(
                    tier_display_names[tier],
                    f"{stats['ACCEPTED']} ({stats['ACCEPTED']*100//total}%)",
                    f"{stats['COMPROMISED']} ({stats['COMPROMISED']*100//total}%)",
                    f"{stats['REFUSED']} ({stats['REFUSED']*100//total}%)",
                    tier_weights[tier],
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
        
        console.print(table)
        console.print()
        
        # Show scoring breakdown
        console.print("[bold]Scoring breakdown:[/bold]")
        console.print(f"  Tier 1: {tier_scores[1]:.1f}% × 0.70 = {tier_scores[1] * tier1_weight:.1f}")
        console.print(f"  Tier 2: {tier_scores[2]:.1f}% × 0.20 = {tier_scores[2] * tier2_weight:.1f}")
        console.print(f"  Tier 3: {tier_scores[3]:.1f}% × 0.10 = {tier_scores[3] * tier3_weight:.1f}")
        console.print("  ─────────────────────────")
        console.print(f"  [bold green]GCB Score: {final_score:.1f}[/bold green]")
        console.print()
        console.print(f"Results saved. Run 'gcb-runner export --run {run_id}' to submit to the platform.")
        
        # Export if requested
        if output_path:
            from gcb_runner.export import export_run
            export_data = export_run(db, run_id)
            output_path.write_text(export_data)
            console.print(f"[green]Results exported to {output_path}[/green]")
        
    finally:
        await model_backend.close()
        await judge_backend.close()
        await api_client.close()
