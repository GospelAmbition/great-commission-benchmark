"""CLI interface for GCB Runner."""

import asyncio
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from gcb_runner import __version__
from gcb_runner.config import Config, BackendConfig, get_config_dir, get_exports_dir

app = typer.Typer(
    name="gcb-runner",
    help="Run Great Commission Benchmark tests against AI models.",
    no_args_is_help=False,  # We handle no-args case in callback to launch menu
)
console = Console()


def print_header():
    """Print the GCB Runner header."""
    console.print(Panel.fit(
        "[bold blue]Great Commission Benchmark - Runner[/bold blue]\n"
        f"[dim]Version {__version__}[/dim]",
        border_style="blue"
    ))


@app.command()
def config():
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
    judge_models = ["openai/gpt-4o (recommended)", "anthropic/claude-3.5-sonnet", "custom"]
    for i, m in enumerate(judge_models, 1):
        console.print(f"  {i}. {m}")
    
    judge_choice = Prompt.ask("Select judge model (number)", default="1")
    
    try:
        judge_idx = int(judge_choice) - 1
        if judge_idx == 0:
            cfg.defaults.judge_model = "openai/gpt-4o"
        elif judge_idx == 1:
            cfg.defaults.judge_model = "anthropic/claude-3.5-sonnet"
        else:
            custom_judge = Prompt.ask("Enter custom judge model name")
            cfg.defaults.judge_model = custom_judge
    except (ValueError, IndexError):
        cfg.defaults.judge_model = "openai/gpt-4o"
    
    # Save configuration
    cfg.save()
    
    config_path = get_config_dir() / "config.json"
    console.print()
    console.print(f"[green]✓ Configuration saved to {config_path}[/green]")


@app.command()
def versions():
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
            result = asyncio.run(client.list_versions())
        except Exception as e:
            console.print(f"[red]Error connecting to Platform API: {e}[/red]")
            raise typer.Exit(1)
    
    console.print("[green]✓ Connected to Platform API[/green]")
    console.print()
    
    table = Table(title="Available Benchmark Versions")
    table.add_column("Version", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Questions", justify="right")
    table.add_column("Released", style="dim")
    
    for v in result.get("versions", []):
        status = "⭐ Current" if v.get("status") == "current" else v.get("status", "")
        table.add_row(
            f"{v.get('marketing_version', '')} ({v.get('semantic_version', '')})",
            status,
            str(v.get("question_count", 0)),
            v.get("release_date", "")[:10] if v.get("release_date") else ""
        )
    
    console.print(table)
    console.print()
    console.print("[dim]Question distribution follows 70/20/10 weighting:[/dim]")
    console.print("  • Tier 1 (Task Capability): 70%")
    console.print("  • Tier 2 (Doctrinal Fidelity): 20%")
    console.print("  • Tier 3 (Worldview Confession): 10%")
    console.print()
    console.print("[dim]Use --benchmark-version to select a specific version.[/dim]")


@app.command()
def test(
    model: str = typer.Option(..., "--model", "-m", help="Model identifier (e.g., gpt-4o)"),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Backend: openrouter, lmstudio, ollama, openai, anthropic"),
    benchmark_version: Optional[str] = typer.Option(None, "--benchmark-version", help="Benchmark version to run"),
    judge_model: Optional[str] = typer.Option(None, "--judge-model", help="Model for judging responses"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save results to JSON file"),
    resume: bool = typer.Option(False, "--resume", help="Resume interrupted test run"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate configuration without running tests"),
):
    """Run the benchmark against a model."""
    print_header()
    console.print()
    
    from gcb_runner.runner import run_benchmark
    
    cfg = Config.load()
    
    # Use defaults if not specified
    backend = backend or cfg.defaults.backend
    judge_model = judge_model or cfg.defaults.judge_model
    
    if not cfg.platform.api_key:
        console.print("[red]Error: Platform API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        raise typer.Exit(1)
    
    backend_config = cfg.get_backend_config(backend)
    if backend in ["openrouter", "openai", "anthropic"] and not backend_config.api_key:
        console.print(f"[red]Error: {backend} API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        raise typer.Exit(1)
    
    if dry_run:
        console.print("[green]✓ Configuration valid[/green]")
        console.print(f"  Model: {model}")
        console.print(f"  Backend: {backend}")
        console.print(f"  Judge: {judge_model}")
        console.print(f"  Benchmark version: {benchmark_version or 'latest'}")
        return
    
    # Run the benchmark
    asyncio.run(run_benchmark(
        model=model,
        backend=backend,
        benchmark_version=benchmark_version,
        judge_model=judge_model,
        config=cfg,
        output_path=output,
        resume=resume,
    ))


@app.command()
def results(
    run_id: Optional[int] = typer.Option(None, "--run", "-r", help="View specific run ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results to show"),
):
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
        table.add_row("Score", f"[bold green]{run.score:.1f}[/bold green]")
        table.add_row("Completed", run.completed_at.isoformat() if run.completed_at else "In Progress")
        
        console.print(table)
        
        # Show tier breakdown
        console.print()
        console.print("[bold]Tier Breakdown:[/bold]")
        
        responses = db.get_responses(run_id)
        tier_stats = {1: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}, 
                      2: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}, 
                      3: {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}}
        
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
    run_id: Optional[int] = typer.Option(None, "--run", "-r", help="Test run ID to export"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path (defaults to ~/.gcb-runner/exports/<model>.json)"),
):
    """Export results to JSON for platform submission."""
    print_header()
    console.print()
    
    from gcb_runner.results import ResultsDB
    from gcb_runner.export import export_run
    
    db = ResultsDB()
    
    if not run_id:
        # Get latest completed run
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            raise typer.Exit(1)
        run_id = runs[0].id
    
    run = db.get_run(run_id)
    if not run:
        console.print(f"[red]Test run #{run_id} not found.[/red]")
        raise typer.Exit(1)
    
    if not run.completed_at:
        console.print(f"[red]Test run #{run_id} is not complete.[/red]")
        raise typer.Exit(1)
    
    # Generate output path from model name if not specified
    if output is None:
        model_name = run.model.replace("/", "-").replace(":", "-")
        output = get_exports_dir() / f"{model_name}.json"
    
    console.print(f"Exporting test run #{run_id}...")
    
    export_data = export_run(db, run_id)
    output.write_text(export_data)
    
    console.print(f"[green]✓ Exported to {output}[/green]")
    console.print()
    console.print("File ready for upload at https://greatcommissionbenchmark.ai/submit")


@app.command()
def upload(
    run_id: Optional[int] = typer.Option(None, "--run", "-r", help="Test run ID to upload"),
):
    """Upload results to the platform for verification and publication."""
    print_header()
    console.print()
    
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
    
    # TODO: Implement full upload flow
    console.print("[yellow]Upload functionality coming soon.[/yellow]")
    console.print("For now, use 'gcb-runner export' and upload manually at:")
    console.print("https://greatcommissionbenchmark.ai/submit")


@app.command()
def view(
    run_id: Optional[int] = typer.Option(None, "--run", "-r", help="Open directly to a specific test run"),
    port: int = typer.Option(8642, "--port", "-p", help="Server port"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
):
    """Launch a local web dashboard to explore results visually."""
    print_header()
    console.print()
    
    from gcb_runner.viewer.server import start_viewer
    from gcb_runner.config import get_data_dir
    
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
):
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
    
    if not force:
        if not Confirm.ask("[red]Are you sure you want to delete all test data?[/red]", default=False):
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
        raise typer.Exit(1)


@app.command()
def report(
    run_id: Optional[int] = typer.Option(None, "--run", "-r", help="Test run ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output filename"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
    compare: Optional[int] = typer.Option(None, "--compare", "-c", help="Compare with another run"),
):
    """Generate a static HTML report."""
    print_header()
    console.print()
    
    from gcb_runner.results import ResultsDB
    from gcb_runner.viewer.report import generate_report
    from gcb_runner.config import get_data_dir
    
    db = ResultsDB()
    
    if not run_id:
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            raise typer.Exit(1)
        run_id = runs[0].id
    
    run = db.get_run(run_id)
    if not run:
        console.print(f"[red]Test run #{run_id} not found.[/red]")
        raise typer.Exit(1)
    
    console.print(f"Generating report for test run #{run_id}...")
    
    if not output:
        date_str = run.completed_at.strftime("%Y-%m-%d") if run.completed_at else datetime.now().strftime("%Y-%m-%d")
        model_name = run.model.replace("/", "-").replace(":", "-")
        output = Path(f"gcb-report-{model_name}-{date_str}.html")
    
    db_path = get_data_dir() / "results.db"
    generate_report(db_path, run_id, output, compare_run_id=compare)
    
    console.print(f"[green]✓ Report saved to {output}[/green]")
    
    if not no_browser:
        console.print("Opening in browser...")
        webbrowser.open(f"file://{output.absolute()}")


@app.command(name="help")
def show_help(ctx: typer.Context):
    """Show CLI command reference."""
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
    console.print("  2. Select [cyan]Setup Wizard[/cyan] to configure your API keys")
    console.print("  3. Select [cyan]Run Benchmark Test[/cyan] to test a model")


@app.command(name="menu")
def menu_command():
    """Launch the interactive menu interface."""
    from gcb_runner.menu import run_menu
    run_menu()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"gcb-runner {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version", callback=version_callback, is_eager=True),
):
    """GCB Runner - Great Commission Benchmark CLI
    
    Run without arguments to launch the interactive menu.
    Use 'gcb-runner help' for command reference.
    """
    if ctx.invoked_subcommand is None and not version:
        # Launch the interactive menu when no command is specified
        from gcb_runner.menu import run_menu
        run_menu()


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
