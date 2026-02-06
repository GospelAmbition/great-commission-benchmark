"""CLI interface for the GCB Bulk Tester."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel

from bulk_tester import __version__

app = typer.Typer(
    name="gcb-bulk-test",
    help="Bulk benchmark tester for GCB leadership - retest all published models.",
    no_args_is_help=True,
)
console = Console()


def print_header() -> None:
    """Print the bulk tester header."""
    console.print(Panel.fit(
        "[bold blue]Great Commission Benchmark - Bulk Tester[/bold blue]\n"
        f"[dim]Version {__version__} (leadership tool)[/dim]",
        border_style="blue"
    ))


@app.command()
def run(
    backend: str = typer.Option(
        "openrouter", "--backend", "-b",
        help="Backend for testing models (openrouter recommended for bulk)"
    ),
    judge_model: str | None = typer.Option(
        None, "--judge-model",
        help="Model for judging responses (default: from gcb-runner config)"
    ),
    judge_backend: str | None = typer.Option(
        None, "--judge-backend", "-j",
        help="Backend for judge model (default: auto-detect)"
    ),
    exclude: str | None = typer.Option(
        None, "--exclude", "-e",
        help="Comma-separated model IDs to skip"
    ),
    include: str | None = typer.Option(
        None, "--include", "-i",
        help="Comma-separated model IDs to test (overrides full list)"
    ),
    resume: bool = typer.Option(
        False, "--resume", "-r",
        help="Skip models already tested on the current version"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Show what would be tested without running"
    ),
    no_submit: bool = typer.Option(
        False, "--no-submit",
        help="Run tests but don't auto-submit results"
    ),
) -> None:
    """Run bulk benchmark tests against all published models.
    
    Fetches the current benchmark version and the list of all published models,
    then tests each model sequentially and auto-submits results to the platform.
    
    Requires admin API key configured in gcb-runner.
    """
    print_header()
    console.print()
    
    from bulk_tester.orchestrator import run_bulk_test
    
    # Parse filter lists
    exclude_models = [m.strip() for m in exclude.split(",")] if exclude else []
    include_models = [m.strip() for m in include.split(",")] if include else []
    
    asyncio.run(run_bulk_test(
        backend=backend,
        judge_model=judge_model,
        judge_backend=judge_backend,
        exclude_models=exclude_models,
        include_models=include_models,
        resume=resume,
        dry_run=dry_run,
        no_submit=no_submit,
    ))


@app.command()
def models(
    backend: str = typer.Option(
        "openrouter", "--backend", "-b",
        help="Backend (used for context only)"
    ),
) -> None:
    """List all published models that would be tested."""
    print_header()
    console.print()
    
    from bulk_tester.models import fetch_published_models
    from bulk_tester.config import load_config
    
    cfg = load_config()
    
    if not cfg.platform.api_key:
        console.print("[red]Error: Platform API key not configured.[/red]")
        console.print("Run 'gcb-runner config' to set up your API key.")
        raise typer.Exit(1)
    
    with console.status("Fetching published models..."):
        try:
            result = asyncio.run(fetch_published_models(cfg))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None
    
    from rich.table import Table
    
    table = Table(title=f"Published Models ({result['total']} total)")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Model ID", style="cyan")
    table.add_column("Name")
    table.add_column("Provider", style="green")
    table.add_column("Last Tested", style="dim")
    
    for i, model in enumerate(result["models"], 1):
        last_tested = model.get("last_tested_at", "")
        if last_tested:
            last_tested = last_tested[:10]  # Just the date
        else:
            last_tested = "Never"
        
        table.add_row(
            str(i),
            model["model_id"],
            model["name"],
            model["provider"],
            last_tested,
        )
    
    console.print(table)
    console.print()
    console.print(f"[dim]Current benchmark version: {result.get('current_version', 'Unknown')}[/dim]")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"gcb-bulk-tester {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False, "--version", "-v",
        help="Show version",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """GCB Bulk Tester - Leadership tool for batch benchmark testing.
    
    This tool is for GCB leadership only. It requires an admin API key
    and uses the gcb-runner configuration (~/.gcb-runner/config.json).
    """
    _ = version


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
