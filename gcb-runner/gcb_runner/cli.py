"""CLI interface for GCB Runner."""

import asyncio
import webbrowser
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from gcb_runner import __version__
from gcb_runner.config import BackendConfig, Config, get_config_dir
from gcb_runner.updater import (
    apply_update,
    check_for_updates_sync,
    cleanup_old_executable,
    download_update_sync,
    format_size,
    is_frozen,
)

app = typer.Typer(
    name="gcb-runner",
    help="Run Great Commission Benchmark tests against AI models.",
    no_args_is_help=False,  # We handle no-args case in callback to launch menu
)
console = Console()


def check_for_updates_notification() -> None:
    """Check for updates and show a notification if available (non-blocking)."""
    if not is_frozen():
        return  # Don't check when running from source
    
    # Clean up any old executables from previous updates (Windows)
    cleanup_old_executable()
    
    try:
        update_info = check_for_updates_sync()
        if update_info:
            console.print()
            console.print(Panel(
                f"[bold yellow]Update Available![/bold yellow]\n\n"
                f"Current version: {update_info['current_version']}\n"
                f"Latest version: {update_info['latest_version']}\n\n"
                f"Run [cyan]gcb-runner update[/cyan] to update.",
                border_style="yellow",
                title="New Version"
            ))
            console.print()
    except Exception:
        pass  # Silently ignore update check failures


def print_header() -> None:
    """Print the GCB Runner header."""
    console.print(Panel.fit(
        "[bold blue]Great Commission Benchmark - Runner[/bold blue]\n"
        f"[dim]Version {__version__}[/dim]",
        border_style="blue"
    ))


@app.command()
def config() -> None:
    """Configure API keys and preferences."""
    print_header()
    console.print()
    
    cfg = Config.load()
    
    # Platform API key
    console.print("[bold]Configure Platform API access:[/bold]")
    console.print("[dim]Get your API key from https://greatcommissionbenchmark.ai/dashboard[/dim]")
    platform_key = Prompt.ask(
        "Platform API key",
        default=cfg.platform.api_key or "",
        password=True
    )
    if platform_key:
        cfg.platform.api_key = platform_key
    
    console.print()
    
    # Backend selection
    backends = ["openrouter", "openai", "anthropic", "lmstudio", "ollama"]
    console.print("[bold]Configure which backend?[/bold]")
    for i, b in enumerate(backends, 1):
        console.print(f"  {i}. {b}")
    
    backend_choice = Prompt.ask(
        "Select backend (number)",
        default="1"
    )
    
    try:
        backend_idx = int(backend_choice) - 1
        selected_backend = backends[backend_idx]
    except (ValueError, IndexError):
        selected_backend = "openrouter"
    
    # Backend-specific configuration
    if selected_backend in ["openrouter", "openai", "anthropic"]:
        api_key = Prompt.ask(
            f"{selected_backend.title()} API key",
            default=cfg.get_backend_config(selected_backend).api_key or "",
            password=True
        )
        if api_key:
            cfg.set_backend_config(selected_backend, BackendConfig(api_key=api_key))
    
    elif selected_backend == "lmstudio":
        base_url = Prompt.ask(
            "LM Studio base URL",
            default=cfg.get_backend_config("lmstudio").base_url or "http://localhost:1234/v1"
        )
        cfg.set_backend_config("lmstudio", BackendConfig(base_url=base_url))
    
    elif selected_backend == "ollama":
        base_url = Prompt.ask(
            "Ollama base URL",
            default=cfg.get_backend_config("ollama").base_url or "http://localhost:11434"
        )
        cfg.set_backend_config("ollama", BackendConfig(base_url=base_url))
    
    # Set default backend
    cfg.defaults.backend = selected_backend
    
    # Judge model selection
    console.print()
    console.print("[bold]Which model should judge responses?[/bold]")
    console.print("[dim]openai/gpt-oss-20b is the standard judge for consistent scoring.[/dim]")
    console.print()
    judge_models = [
        "openai/gpt-oss-20b (recommended)",
        "custom"
    ]
    for i, m in enumerate(judge_models, 1):
        console.print(f"  {i}. {m}")
    
    judge_choice = Prompt.ask("Select judge model (number)", default="1")
    
    try:
        judge_idx = int(judge_choice) - 1
        if judge_idx == 0:
            cfg.defaults.judge_model = "openai/gpt-oss-20b"
        else:
            custom_judge = Prompt.ask("Enter custom judge model name")
            cfg.defaults.judge_model = custom_judge
    except (ValueError, IndexError):
        cfg.defaults.judge_model = "openai/gpt-oss-20b"
    
    # Judge backend selection
    console.print()
    console.print("[bold]Which backend should the judge use?[/bold]")
    console.print("[dim]You can run the judge locally (lmstudio/ollama) to save tokens, while testing models on Open Router.[/dim]")
    console.print()
    judge_backend_options = [
        "auto-detect (use same as test backend, or openrouter if test is local)",
        "lmstudio (local)",
        "ollama (local)",
        "openrouter",
        "openai",
        "anthropic",
        "none (use auto-detect always)"
    ]
    for i, opt in enumerate(judge_backend_options, 1):
        console.print(f"  {i}. {opt}")
    
    judge_backend_choice = Prompt.ask("Select judge backend (number)", default="1")
    
    try:
        judge_backend_idx = int(judge_backend_choice) - 1
        if judge_backend_idx == 0:
            cfg.defaults.judge_backend = None  # Auto-detect
        elif judge_backend_idx == 1:
            cfg.defaults.judge_backend = "lmstudio"
        elif judge_backend_idx == 2:
            cfg.defaults.judge_backend = "ollama"
        elif judge_backend_idx == 3:
            cfg.defaults.judge_backend = "openrouter"
        elif judge_backend_idx == 4:
            cfg.defaults.judge_backend = "openai"
        elif judge_backend_idx == 5:
            cfg.defaults.judge_backend = "anthropic"
        else:
            cfg.defaults.judge_backend = None  # None = auto-detect
    except (ValueError, IndexError):
        cfg.defaults.judge_backend = None  # Auto-detect by default
    
    # Save configuration
    cfg.save()
    
    config_path = get_config_dir() / "config.json"
    console.print()
    console.print(f"[green]✓ Configuration saved to {config_path}[/green]")


@app.command()
def versions(
    include_drafts: bool = typer.Option(False, "--include-drafts", "-d", 
                                        help="Include draft versions for testing")
) -> None:
    """List available benchmark versions."""
    print_header()
    console.print()
    
    from gcb_runner.api.client import PlatformAPIClient
    
    cfg = Config.load()
    
    if not cfg.platform.api_key:
        console.print("[red]Error: Platform API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        raise typer.Exit(1)
    
    with console.status("Fetching versions from Platform API..."):
        try:
            client = PlatformAPIClient(cfg.platform.api_key, cfg.platform.url)
            result = asyncio.run(client.list_versions(include_drafts=include_drafts))
        except Exception as e:
            console.print(f"[red]Error connecting to Platform API: {e}[/red]")
            raise typer.Exit(1) from None
    
    console.print("[green]✓ Connected to Platform API[/green]")
    console.print()
    
    title = "Available Benchmark Versions"
    if include_drafts:
        title += " (including drafts)"
    
    table = Table(title=title)
    table.add_column("Version", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Questions", justify="right")
    table.add_column("Released", style="dim")
    
    for v in result.get("versions", []):
        status_raw = v.get("status", "")
        # Map status to display with icons
        if status_raw == "current":
            status = "⭐ Current"
        elif status_raw == "draft":
            status = "🔨 Draft"
        elif status_raw == "locked":
            status = "🔒 Locked"
        elif status_raw == "archived":
            status = "📦 Archived"
        else:
            status = status_raw
        
        table.add_row(
            f"{v.get('marketing_version', '')} ({v.get('semantic_version', '')})",
            status,
            str(v.get("question_count", 0)),
            v.get("release_date", "")[:10] if v.get("release_date") else ""
        )
    
    console.print(table)
    console.print()
    
    if include_drafts:
        console.print("[yellow]⚠️  Draft versions are for testing only - results won't be published to leaderboard[/yellow]")
        console.print()
    
    console.print("[dim]Question distribution follows 70/20/10 tier weighting:[/dim]")
    console.print("  • Tier 1 (Task Capability): 70% of questions")
    console.print("  • Tier 2 (Doctrinal Fidelity): 20% of questions")
    console.print("  • Tier 3 (Worldview Confession): 10% of questions")
    console.print()
    console.print("[dim]Use --benchmark-version to select a specific version.[/dim]")
    if not include_drafts:
        console.print("[dim]Use --include-drafts to see draft versions for testing.[/dim]")


@app.command()
def test(
    model: str = typer.Option(..., "--model", "-m", help="Model identifier (e.g., gpt-4o)"),
    backend: str | None = typer.Option(None, "--backend", "-b", help="Backend: openrouter, lmstudio, ollama, openai, anthropic"),
    benchmark_version: str | None = typer.Option(None, "--benchmark-version", help="Benchmark version to run"),
    judge_model: str | None = typer.Option(None, "--judge-model", help="Model for judging responses"),
    judge_backend: str | None = typer.Option(None, "--judge-backend", "-j", help="Backend for judge (e.g., lmstudio, openrouter). If not set, uses config default or auto-detects."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save results to JSON file"),  # noqa: B008
    resume: bool = typer.Option(False, "--resume", help="Resume interrupted test run"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate configuration without running tests"),
) -> None:
    """Run the benchmark against a model."""
    print_header()
    console.print()
    
    from gcb_runner.runner import run_benchmark
    
    cfg = Config.load()
    
    # Use defaults if not specified
    backend = backend or cfg.defaults.backend
    judge_model = judge_model or cfg.defaults.judge_model
    judge_backend = judge_backend or cfg.defaults.judge_backend
    
    if not cfg.platform.api_key:
        console.print("[red]Error: Platform API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        raise typer.Exit(1)
    
    backend_config = cfg.get_backend_config(backend)
    if backend in ["openrouter", "openai", "anthropic"]:
        if not backend_config.api_key or not backend_config.api_key.strip():
            console.print(f"[red]Error: {backend} API key not configured.[/red]")
            console.print("Run 'gcb-runner config' to set up your API key.")
            raise typer.Exit(1)
    
    # Validate judge backend if explicitly set
    if judge_backend:
        judge_backend_config = cfg.get_backend_config(judge_backend)
        if judge_backend in ["openrouter", "openai", "anthropic"]:
            if not judge_backend_config.api_key or not judge_backend_config.api_key.strip():
                console.print(f"[red]Error: {judge_backend} API key not configured for judge backend.[/red]")
                console.print("Run 'gcb-runner config' to set up your API key.")
                raise typer.Exit(1)
    
    if dry_run:
        console.print("[green]✓ Configuration valid[/green]")
        console.print(f"  Model: {model}")
        console.print(f"  Backend: {backend}")
        console.print(f"  Judge Model: {judge_model}")
        console.print(f"  Judge Backend: {judge_backend or 'auto-detect'}")
        console.print(f"  Benchmark version: {benchmark_version or 'latest'}")
        return
    
    # Run the benchmark
    asyncio.run(run_benchmark(
        model=model,
        backend=backend,
        benchmark_version=benchmark_version,
        judge_model=judge_model,
        judge_backend=judge_backend,
        config=cfg,
        output_path=output,
        resume=resume,
    ))


@app.command()
def results(
    run_id: int | None = typer.Option(None, "--run", "-r", help="View specific run ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results to show"),
) -> None:
    """View past test results."""
    print_header()
    console.print()
    
    from gcb_runner.results import ResultsDB
    
    db = ResultsDB()
    
    if run_id:
        run = db.get_run(run_id)
        if not run:
            console.print(f"[red]Test run #{run_id} not found.[/red]")
            raise typer.Exit(1)
        
        # Show detailed results
        console.print(f"[bold]Test Run #{run.id} - {run.model}[/bold]")
        console.print()
        
        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        
        table.add_row("Model", run.model)
        table.add_row("Backend", run.backend)
        table.add_row("Benchmark Version", run.benchmark_version)
        table.add_row("Judge Model", run.judge_model)
        if getattr(run, 'judge_backend', None):
            table.add_row("Judge Backend", run.judge_backend)
        table.add_row("Score", f"[bold green]{run.score:.1f}[/bold green]" if run.score else "-")
        table.add_row("Completed", run.completed_at.isoformat() if run.completed_at else "In Progress")
        
        console.print(table)
        
        # Show tier breakdown
        console.print()
        console.print("[bold]Tier Breakdown:[/bold]")
        
        responses = db.get_responses(run_id)
        tier_stats: dict[int, dict[str, int]] = {
            1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}, 
            2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}, 
            3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}
        }
        
        for resp in responses:
            # Map verdict (handle legacy/ERROR verdicts as REFUSED)
            verdict = resp.verdict if resp.verdict in tier_stats[resp.tier] else "REFUSED"
            tier_stats[resp.tier][verdict] += 1
        
        tier_table = Table()
        tier_table.add_column("Tier", style="cyan")
        tier_table.add_column("Accepted", style="green")
        tier_table.add_column("Compromised", style="yellow")
        tier_table.add_column("Refused", style="red")
        tier_table.add_column("Weight")
        
        tier_names = {1: "Tier 1: Use Cases", 2: "Tier 2: Theology", 3: "Tier 3: Worldview"}
        tier_weights = {1: "70%", 2: "20%", 3: "10%"}
        
        for tier in [1, 2, 3]:
            stats = tier_stats[tier]
            total = stats["ACCEPTED"] + stats["COMPROMISED"] + stats["REFUSED"]
            if total > 0:
                tier_table.add_row(
                    tier_names[tier],
                    f"{stats['ACCEPTED']} ({stats['ACCEPTED']*100//total}%)",
                    f"{stats['COMPROMISED']} ({stats['COMPROMISED']*100//total}%)",
                    f"{stats['REFUSED']} ({stats['REFUSED']*100//total}%)",
                    tier_weights[tier]
                )
        
        console.print(tier_table)
        
    else:
        # Show list of recent runs
        runs = db.list_runs(limit=limit)
        
        if not runs:
            console.print("[dim]No test runs found. Run 'gcb-runner test' to get started.[/dim]")
            return
        
        console.print("[bold]Recent Test Runs:[/bold]")
        console.print()
        
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Model")
        table.add_column("Version")
        table.add_column("Date")
        table.add_column("Score", justify="right")
        table.add_column("Status")
        
        for run in runs:
            status = "[green]✓ Done[/green]" if run.completed_at else "[yellow]⏳ Running[/yellow]"
            table.add_row(
                str(run.id),
                run.model,
                run.benchmark_version,
                run.started_at.strftime("%Y-%m-%d %H:%M") if run.started_at else "",
                f"{run.score:.1f}" if run.score else "-",
                status
            )
        
        console.print(table)
        console.print()
        console.print("[dim]Use 'gcb-runner results --run <ID>' to view details.[/dim]")


@app.command(name="export")
def export_results(
    run_id: int | None = typer.Option(None, "--run", "-r", help="Test run ID to export"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output path (defaults to ./<model>.json in current directory)"),  # noqa: B008
) -> None:
    """Export results to JSON for platform submission."""
    print_header()
    console.print()
    
    from gcb_runner.export import export_run
    from gcb_runner.results import ResultsDB
    
    db = ResultsDB()
    
    actual_run_id: int
    if not run_id:
        # Get latest completed run
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            raise typer.Exit(1)
        actual_run_id = runs[0].id
    else:
        actual_run_id = run_id
    
    run = db.get_run(actual_run_id)
    if not run:
        console.print(f"[red]Test run #{actual_run_id} not found.[/red]")
        raise typer.Exit(1)
    
    if not run.completed_at:
        console.print(f"[red]Test run #{actual_run_id} is not complete.[/red]")
        raise typer.Exit(1)
    
    # Generate output path from model name if not specified
    actual_output: Path
    if output is None:
        model_name = run.model.replace("/", "-").replace(":", "-")
        actual_output = Path(f"{model_name}.json")
    else:
        actual_output = output
    
    console.print(f"Exporting test run #{actual_run_id}...")
    
    export_data = export_run(db, actual_run_id)
    actual_output.write_text(export_data)
    
    console.print(f"[green]✓ Exported to {actual_output}[/green]")
    console.print()
    console.print("File ready for upload at https://greatcommissionbenchmark.ai/submit")


@app.command()
def upload(
    run_id: int | None = typer.Option(None, "--run", "-r", help="Test run ID to upload"),
) -> None:
    """Upload results to the platform for verification and publication."""
    print_header()
    console.print()
    
    _ = run_id  # Mark as intentionally unused for now
    
    console.print(Panel(
        "[bold]CLI Submission Information[/bold]\n\n"
        "CLI submissions require moderator verification before publication.\n\n"
        "[bold]What happens next:[/bold]\n"
        "  1. Pay $20 platform fee (covers verification work)\n"
        "  2. Provide model access info (API endpoint, or reproducibility details)\n"
        "  3. Moderator verifies results (typically 24-48 hours)\n"
        "  4. If verified, results published to leaderboard",
        border_style="yellow"
    ))
    
    if not Confirm.ask("Continue with submission?"):
        console.print("Upload cancelled.")
        return
    
    # Upload functionality is not yet implemented in the CLI
    # Users should export results and upload via the web interface
    # This command serves as a placeholder for future implementation
    console.print("[yellow]Upload functionality coming soon.[/yellow]")
    console.print("For now, use 'gcb-runner export' and upload manually at:")
    console.print("https://greatcommissionbenchmark.ai/submit")


@app.command()
def view(
    run_id: int | None = typer.Option(None, "--run", "-r", help="Open directly to a specific test run"),
    port: int = typer.Option(8642, "--port", "-p", help="Server port"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
) -> None:
    """Launch a local web dashboard to explore results visually."""
    print_header()
    console.print()
    
    from gcb_runner.config import get_data_dir
    from gcb_runner.viewer.server import start_viewer
    
    db_path = get_data_dir() / "results.db"
    
    if not db_path.exists():
        console.print("[red]No results database found.[/red]")
        console.print("Run 'gcb-runner test' first to generate results.")
        raise typer.Exit(1)
    
    console.print("Starting local server...")
    console.print(f"[green]✓ Server running at http://localhost:{port}[/green]")
    
    if not no_browser:
        url = f"http://localhost:{port}"
        if run_id:
            url += f"?run={run_id}"
        console.print("Opening browser...")
        webbrowser.open(url)
    
    console.print()
    console.print("Press Ctrl+C to stop the server.")
    
    start_viewer(db_path, port=port, open_browser=False)


@app.command(name="reset-db")
def reset_database(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """Delete and reinitialize the results database.
    
    Use this when you want to start testing from scratch. All test runs
    and results will be permanently deleted.
    """
    print_header()
    console.print()
    
    from gcb_runner.config import get_data_dir
    
    db_path = get_data_dir() / "results.db"
    
    if not db_path.exists():
        console.print("[yellow]No results database found. Nothing to reset.[/yellow]")
        return
    
    # Show what will be deleted
    from gcb_runner.results import ResultsDB
    
    try:
        db = ResultsDB()
        runs = db.list_runs(limit=100)
        total_runs = len(runs)
        completed_runs = len([r for r in runs if r.completed_at])
        
        console.print(Panel(
            f"[bold red]⚠️  Database Reset Warning[/bold red]\n\n"
            f"This will permanently delete:\n"
            f"  • {total_runs} test run(s) ({completed_runs} completed)\n"
            f"  • All response data and verdicts\n"
            f"  • All score history\n\n"
            f"Database location:\n"
            f"  {db_path}\n\n"
            "[dim]This action cannot be undone.[/dim]",
            border_style="red"
        ))
        console.print()
    except Exception:
        console.print(f"[dim]Database location: {db_path}[/dim]")
        console.print()
    
    if not force and not Confirm.ask("[red]Are you sure you want to delete all test data?[/red]", default=False):
        console.print("[yellow]Reset cancelled.[/yellow]")
        return
    
    # Delete the database file
    try:
        db_path.unlink()
        console.print("[green]✓ Database deleted successfully.[/green]")
        console.print()
        console.print("[dim]A new database will be created automatically when you run your next test.[/dim]")
    except Exception as e:
        console.print(f"[red]Error deleting database: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def report(
    run_id: int | None = typer.Option(None, "--run", "-r", help="Test run ID"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output filename"),  # noqa: B008
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
    compare: int | None = typer.Option(None, "--compare", "-c", help="Compare with another run"),
) -> None:
    """Generate a static HTML report."""
    print_header()
    console.print()
    
    from gcb_runner.config import get_data_dir
    from gcb_runner.results import ResultsDB
    from gcb_runner.viewer.report import generate_report
    
    db = ResultsDB()
    
    actual_run_id: int
    if not run_id:
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            raise typer.Exit(1)
        actual_run_id = runs[0].id
    else:
        actual_run_id = run_id
    
    run = db.get_run(actual_run_id)
    if not run:
        console.print(f"[red]Test run #{actual_run_id} not found.[/red]")
        raise typer.Exit(1)
    
    console.print(f"Generating report for test run #{actual_run_id}...")
    
    actual_output: Path
    if not output:
        date_str = run.completed_at.strftime("%Y-%m-%d") if run.completed_at else datetime.now().strftime("%Y-%m-%d")
        model_name = run.model.replace("/", "-").replace(":", "-")
        actual_output = Path(f"gcb-report-{model_name}-{date_str}.html")
    else:
        actual_output = output
    
    db_path = get_data_dir() / "results.db"
    generate_report(db_path, actual_run_id, actual_output, compare_run_id=compare)
    
    console.print(f"[green]✓ Report saved to {actual_output}[/green]")
    
    if not no_browser:
        console.print("Opening in browser...")
        webbrowser.open(f"file://{actual_output.absolute()}")


@app.command()
def update(
    check_only: bool = typer.Option(False, "--check", "-c", help="Only check for updates, don't install"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update even if already on latest version"),
) -> None:
    """Check for and install updates."""
    print_header()
    console.print()
    
    if not is_frozen():
        console.print("[yellow]Update command is only available for standalone executables.[/yellow]")
        console.print()
        console.print("You're running from source. Update using:")
        console.print("  [cyan]git pull[/cyan]")
        console.print("  [cyan]pip install -e .[/cyan]")
        return
    
    console.print("Checking for updates...")
    console.print()
    
    update_info = check_for_updates_sync()
    
    if not update_info and not force:
        console.print(f"[green]✓ You're running the latest version ({__version__})[/green]")
        return
    
    if update_info:
        console.print("[bold]Update available![/bold]")
        console.print(f"  Current version: {update_info['current_version']}")
        console.print(f"  Latest version:  [green]{update_info['latest_version']}[/green]")
        if update_info.get('release_notes'):
            console.print(f"  Release notes:   {update_info['release_notes']}")
        if update_info.get('size'):
            console.print(f"  Download size:   {format_size(update_info['size'])}")
        console.print()
    
    if check_only:
        return
    
    if not update_info:
        console.print("[yellow]No update info available. Cannot force update.[/yellow]")
        return
    
    if not Confirm.ask("Download and install update?"):
        console.print("Update cancelled.")
        return
    
    # Download with progress
    console.print()
    console.print("Downloading update...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading...", total=update_info.get('size', 0) or None)
        
        def update_progress(downloaded: int, total: int) -> None:
            if total > 0:
                progress.update(task, completed=downloaded, total=total)
        
        new_exe = download_update_sync(
            update_info['download_url'],
            update_info['sha256'],
            progress_callback=update_progress
        )
    
    if not new_exe:
        console.print("[red]Download failed or hash verification failed.[/red]")
        console.print("Please try again or download manually from:")
        console.print("  https://greatcommissionbenchmark.ai/runner")
        raise typer.Exit(1)
    
    console.print("[green]✓ Download complete and verified[/green]")
    console.print()
    console.print("Installing update...")
    
    if apply_update(new_exe):
        console.print("[green]✓ Update installed successfully![/green]")
        console.print()
        console.print("Please restart gcb-runner to use the new version.")
    else:
        console.print("[red]Failed to install update.[/red]")
        console.print("Please download manually from:")
        console.print("  https://greatcommissionbenchmark.ai/runner")
        raise typer.Exit(1)


@app.command(name="help")
def show_help(ctx: typer.Context) -> None:
    """Show CLI command reference."""
    _ = ctx  # Mark as intentionally unused
    print_header()
    console.print()
    console.print("[bold]Available Commands:[/bold]")
    console.print()
    
    commands = [
        ("gcb-runner", "Launch interactive menu (default)"),
        ("gcb-runner help", "Show this command reference"),
        ("gcb-runner config", "Configure API keys and preferences"),
        ("gcb-runner test", "Run benchmark against a model"),
        ("gcb-runner results", "View past test results"),
        ("gcb-runner view", "Launch web dashboard"),
        ("gcb-runner report", "Generate HTML report"),
        ("gcb-runner export", "Export results to JSON"),
        ("gcb-runner upload", "Upload results to platform"),
        ("gcb-runner versions", "List benchmark versions"),
        ("gcb-runner update", "Check for and install updates"),
        ("gcb-runner reset-db", "Delete and reinitialize results database"),
    ]
    
    table = Table(box=None, show_header=False, padding=(0, 2))
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    
    console.print(table)
    console.print()
    console.print("[dim]Use 'gcb-runner <command> --help' for detailed options.[/dim]")
    console.print("[dim]Example: gcb-runner test --help[/dim]")
    console.print()
    console.print("[bold]Quick Start:[/bold]")
    console.print("  1. Run [cyan]gcb-runner[/cyan] to launch the interactive menu")
    console.print("  2. Select [cyan]Utilities → Setup Wizard[/cyan] to configure your API keys")
    console.print("  3. Select [cyan]Run Benchmark Test[/cyan] to test a model")


@app.command(name="menu")
def menu_command() -> None:
    """Launch the interactive menu interface."""
    from gcb_runner.menu import run_menu
    run_menu()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"gcb-runner {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version", callback=version_callback, is_eager=True),
    no_update_check: bool = typer.Option(False, "--no-update-check", help="Skip automatic update check", hidden=True),
) -> None:
    """GCB Runner - Great Commission Benchmark CLI
    
    Run without arguments to launch the interactive menu.
    Use 'gcb-runner help' for command reference.
    """
    _ = version  # Mark as intentionally unused (handled by callback)
    
    # Check for updates on startup (non-blocking notification)
    if not no_update_check and ctx.invoked_subcommand not in ("update", None):
        check_for_updates_notification()
    
    if ctx.invoked_subcommand is None:
        # Check for updates before launching menu
        if not no_update_check:
            check_for_updates_notification()
        # Launch the interactive menu when no command is specified
        from gcb_runner.menu import run_menu
        run_menu()


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
