"""Batch orchestration loop for bulk benchmark testing.

This is the core logic that:
1. Authenticates and verifies admin access
2. Fetches the current benchmark version and question set
3. Fetches the full list of published models
4. Applies include/exclude filters
5. Tests each model sequentially
6. Auto-submits results to the platform
7. Prints a final summary
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bulk_tester.config import load_config
from bulk_tester.models import fetch_published_models
from bulk_tester.submitter import BulkSubmitter
from gcb_runner.config import Config
from gcb_runner.export import export_run
from gcb_runner.results import ResultsDB
from gcb_runner.runner import BenchmarkResult, run_benchmark

console = Console()


@dataclass
class ModelTestResult:
    """Result of testing a single model in the bulk run."""
    model_id: str
    status: str  # "success", "failed", "skipped", "submit_failed"
    score: float | None = None
    tier1_score: float | None = None
    tier2_score: float | None = None
    tier3_score: float | None = None
    run_id: int | None = None
    duration_seconds: float = 0.0
    error: str | None = None
    submit_status: str | None = None
    platform_test_run_id: str | None = None


async def run_bulk_test(
    backend: str = "openrouter",
    judge_model: str | None = None,
    judge_backend: str | None = None,
    exclude_models: list[str] | None = None,
    include_models: list[str] | None = None,
    resume: bool = False,
    dry_run: bool = False,
    no_submit: bool = False,
) -> list[ModelTestResult]:
    """Run bulk benchmark tests against all published models.
    
    Args:
        backend: Backend for testing models
        judge_model: Model for judging responses
        judge_backend: Backend for judge model
        exclude_models: Model IDs to skip
        include_models: If provided, only test these model IDs
        resume: Skip models already tested on current version
        dry_run: Show what would be tested without running
        no_submit: Run tests but don't auto-submit
        
    Returns:
        List of ModelTestResult for each model processed
    """
    exclude_models = exclude_models or []
    include_models = include_models or []
    
    # Step 1: Load configuration
    config = load_config()
    
    if not config.platform.api_key:
        console.print("[red]Error: Platform API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        return []
    
    # Validate backend API key
    backend_config = config.get_backend_config(backend)
    if backend in ["openrouter", "openai", "anthropic"]:
        if not backend_config.api_key or not backend_config.api_key.strip():
            console.print(f"[red]Error: {backend} API key not configured.[/red]")
            console.print("Run 'gcb-runner config' to set up your API key.")
            return []
    
    # Step 2: Verify admin access
    console.print("Verifying admin access...")
    submitter = BulkSubmitter(config)
    
    try:
        user_info = await submitter.verify_admin_access()
        console.print(f"[green]✓ Authenticated as {user_info.get('name', 'Unknown')} ({user_info.get('email', '')})[/green]")
        console.print(f"[green]✓ Admin access confirmed[/green]")
    except PermissionError as e:
        console.print(f"[red]Error: {e}[/red]")
        await submitter.close()
        return []
    except Exception as e:
        console.print(f"[red]Error verifying access: {e}[/red]")
        await submitter.close()
        return []
    
    console.print()
    
    # Step 3: Fetch published models
    console.print("Fetching published models...")
    try:
        models_data = await fetch_published_models(config)
    except Exception as e:
        console.print(f"[red]Error fetching models: {e}[/red]")
        await submitter.close()
        return []
    
    all_models = models_data.get("models", [])
    current_version = models_data.get("current_version", "Unknown")
    console.print(f"[green]✓ {len(all_models)} published models found[/green]")
    console.print(f"[green]✓ Current benchmark version: {current_version}[/green]")
    console.print()
    
    # Step 4: Apply filters
    models_to_test = all_models.copy()
    
    # Apply include filter (overrides full list)
    if include_models:
        include_set = set(include_models)
        models_to_test = [m for m in models_to_test if m["model_id"] in include_set]
        console.print(f"[yellow]Include filter: {len(models_to_test)} models selected[/yellow]")
    
    # Apply exclude filter
    if exclude_models:
        exclude_set = set(exclude_models)
        before_count = len(models_to_test)
        models_to_test = [m for m in models_to_test if m["model_id"] not in exclude_set]
        excluded_count = before_count - len(models_to_test)
        if excluded_count > 0:
            console.print(f"[yellow]Exclude filter: {excluded_count} models removed[/yellow]")
    
    # Apply resume filter (skip models already tested on current version)
    skipped_models: list[str] = []
    if resume:
        before_count = len(models_to_test)
        filtered = []
        for m in models_to_test:
            if m.get("last_tested_version") == current_version:
                skipped_models.append(m["model_id"])
            else:
                filtered.append(m)
        models_to_test = filtered
        if skipped_models:
            console.print(f"[yellow]Resume: {len(skipped_models)} models already tested on v{current_version}, skipping[/yellow]")
    
    console.print()
    console.print(f"[bold]Models to test: {len(models_to_test)}[/bold]")
    
    if not models_to_test:
        console.print("[yellow]No models to test after applying filters.[/yellow]")
        await submitter.close()
        return []
    
    # Step 5: Display test plan
    plan_table = Table(title="Test Plan")
    plan_table.add_column("#", style="dim", justify="right")
    plan_table.add_column("Model ID", style="cyan")
    plan_table.add_column("Provider", style="green")
    plan_table.add_column("Status")
    
    for i, m in enumerate(models_to_test, 1):
        plan_table.add_row(
            str(i),
            m["model_id"],
            m["provider"],
            "Queued",
        )
    
    console.print(plan_table)
    console.print()
    
    if dry_run:
        console.print(Panel(
            f"[bold yellow]DRY RUN[/bold yellow]\n\n"
            f"Would test {len(models_to_test)} models on benchmark v{current_version}\n"
            f"Backend: {backend}\n"
            f"Judge: {judge_model or 'default'} via {judge_backend or 'auto-detect'}\n"
            f"Auto-submit: {'No' if no_submit else 'Yes'}\n\n"
            f"Skipped (resume): {len(skipped_models)}\n"
            f"Excluded: {len(exclude_models)}",
            border_style="yellow"
        ))
        await submitter.close()
        return []
    
    # Step 6: Run tests
    console.print(Panel(
        f"[bold]Starting bulk test run[/bold]\n\n"
        f"Models: {len(models_to_test)}\n"
        f"Benchmark: v{current_version}\n"
        f"Backend: {backend}\n"
        f"Judge: {judge_model or 'default'} via {judge_backend or 'auto-detect'}\n"
        f"Auto-submit: {'No' if no_submit else 'Yes'}",
        border_style="blue"
    ))
    console.print()
    
    bulk_start_time = datetime.now()
    results: list[ModelTestResult] = []
    db = ResultsDB()
    
    for idx, model_info in enumerate(models_to_test, 1):
        model_id = model_info["model_id"]
        
        console.print("═" * 60)
        console.print(f"[bold][{idx}/{len(models_to_test)}] Testing: {model_id}[/bold]")
        console.print("═" * 60)
        console.print()
        
        model_start = time.time()
        
        # Run the benchmark
        try:
            benchmark_result = await run_benchmark(
                model=model_id,
                backend=backend,
                config=config,
                judge_model=judge_model,
                judge_backend=judge_backend,
                quiet=False,  # Show progress for each model
            )
            
            if benchmark_result is None:
                results.append(ModelTestResult(
                    model_id=model_id,
                    status="failed",
                    duration_seconds=time.time() - model_start,
                    error="Benchmark returned no result",
                ))
                console.print(f"[red]✗ {model_id}: No result returned[/red]")
                console.print()
                continue
            
            model_result = ModelTestResult(
                model_id=model_id,
                status="success",
                score=benchmark_result.score,
                tier1_score=benchmark_result.tier1_score,
                tier2_score=benchmark_result.tier2_score,
                tier3_score=benchmark_result.tier3_score,
                run_id=benchmark_result.run_id,
                duration_seconds=benchmark_result.duration_seconds,
            )
            
        except Exception as e:
            results.append(ModelTestResult(
                model_id=model_id,
                status="failed",
                duration_seconds=time.time() - model_start,
                error=str(e),
            ))
            console.print(f"[red]✗ {model_id}: Test failed - {e}[/red]")
            console.print()
            continue
        
        # Step 7: Submit results
        if not no_submit and model_result.run_id is not None:
            try:
                console.print(f"Submitting results for {model_id}...")
                
                # Export the run to JSON format
                export_json_str = export_run(db, model_result.run_id)
                export_data = json.loads(export_json_str)
                
                # Submit via bulk-submit endpoint
                submit_response = await submitter.submit(export_data)
                
                model_result.submit_status = submit_response.get("status", "unknown")
                model_result.platform_test_run_id = submit_response.get("test_run_id")
                
                if submit_response.get("status") == "published":
                    console.print(f"[green]✓ Results published for {model_id} (score: {model_result.score:.1f})[/green]")
                else:
                    model_result.status = "submit_failed"
                    model_result.error = submit_response.get("message", "Unknown submission error")
                    console.print(f"[yellow]⚠ Submission issue for {model_id}: {model_result.error}[/yellow]")
                    
            except Exception as e:
                model_result.status = "submit_failed"
                model_result.error = f"Submit failed: {e}"
                console.print(f"[red]✗ Submit failed for {model_id}: {e}[/red]")
        elif no_submit:
            model_result.submit_status = "skipped"
            console.print(f"[yellow]⏭ Submission skipped (--no-submit) for {model_id}[/yellow]")
        
        results.append(model_result)
        console.print()
    
    # Step 8: Print summary
    await submitter.close()
    
    bulk_end_time = datetime.now()
    bulk_duration = bulk_end_time - bulk_start_time
    
    console.print()
    console.print("═" * 60)
    console.print("[bold]BULK TEST SUMMARY[/bold]")
    console.print("═" * 60)
    console.print()
    console.print(f"[dim]Started:  {bulk_start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    console.print(f"[dim]Ended:    {bulk_end_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    console.print(f"[dim]Duration: {bulk_duration}[/dim]")
    console.print()
    
    # Summary table
    summary_table = Table(title=f"Results - Benchmark v{current_version}")
    summary_table.add_column("#", style="dim", justify="right")
    summary_table.add_column("Model", style="cyan")
    summary_table.add_column("Status")
    summary_table.add_column("Score", justify="right")
    summary_table.add_column("T1", justify="right", style="dim")
    summary_table.add_column("T2", justify="right", style="dim")
    summary_table.add_column("T3", justify="right", style="dim")
    summary_table.add_column("Duration", style="dim")
    summary_table.add_column("Submitted")
    
    success_count = 0
    failed_count = 0
    
    for i, r in enumerate(results, 1):
        if r.status == "success":
            status_str = "[green]✓ Success[/green]"
            success_count += 1
        elif r.status == "submit_failed":
            status_str = "[yellow]⚠ Submit Failed[/yellow]"
            failed_count += 1
        elif r.status == "skipped":
            status_str = "[dim]⏭ Skipped[/dim]"
        else:
            status_str = "[red]✗ Failed[/red]"
            failed_count += 1
        
        score_str = f"{r.score:.1f}" if r.score is not None else "-"
        t1_str = f"{r.tier1_score:.0f}" if r.tier1_score is not None else "-"
        t2_str = f"{r.tier2_score:.0f}" if r.tier2_score is not None else "-"
        t3_str = f"{r.tier3_score:.0f}" if r.tier3_score is not None else "-"
        
        duration_str = _format_duration(r.duration_seconds)
        
        if r.submit_status == "published":
            submit_str = "[green]✓ Published[/green]"
        elif r.submit_status == "skipped":
            submit_str = "[dim]Skipped[/dim]"
        elif r.submit_status:
            submit_str = f"[yellow]{r.submit_status}[/yellow]"
        else:
            submit_str = "-"
        
        summary_table.add_row(
            str(i), r.model_id, status_str, score_str,
            t1_str, t2_str, t3_str, duration_str, submit_str,
        )
    
    console.print(summary_table)
    console.print()
    
    # Final stats
    console.print(f"[bold green]Successful: {success_count}[/bold green]")
    if failed_count > 0:
        console.print(f"[bold red]Failed: {failed_count}[/bold red]")
    if skipped_models:
        console.print(f"[dim]Skipped (already tested): {len(skipped_models)}[/dim]")
    console.print(f"[dim]Total duration: {bulk_duration}[/dim]")
    
    # List failures for easy retry
    failures = [r for r in results if r.status in ("failed", "submit_failed")]
    if failures:
        console.print()
        console.print("[bold yellow]Failed models (can retry with --include):[/bold yellow]")
        failed_ids = ",".join(r.model_id for r in failures)
        console.print(f"  [cyan]--include \"{failed_ids}\"[/cyan]")
        console.print()
        for r in failures:
            console.print(f"  [red]{r.model_id}[/red]: {r.error or 'Unknown error'}")
    
    return results


def _format_duration(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
