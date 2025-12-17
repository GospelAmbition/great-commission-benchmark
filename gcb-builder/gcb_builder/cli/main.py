"""
Main CLI entry point for GCB Builder.

This module provides the main Typer application and the interactive menu system.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gcb_builder import __version__
from gcb_builder.core.categories import (
    CATEGORIES,
    TIER1_CATEGORIES,
    TIER2_CATEGORIES,
    TIER3_CATEGORIES,
    get_tier_weight,
)
from gcb_builder.core.database import get_db, init_db

# Import CLI submodules
from gcb_builder.cli import generate as generate_cli
from gcb_builder.cli import curate as curate_cli
from gcb_builder.cli import judge as judge_cli
from gcb_builder.cli import version as version_cli
from gcb_builder.cli import explore as explore_cli

# Create the main app
app = typer.Typer(
    name="gcb-builder",
    help="CLI tool for building official Great Commission Benchmark versions",
    no_args_is_help=False,
)

# Add subcommand groups
app.add_typer(generate_cli.app, name="generate", help="Question generation commands")
app.add_typer(curate_cli.app, name="curate", help="Question curation commands")
app.add_typer(judge_cli.app, name="judge", help="Judge prompt development")
app.add_typer(version_cli.app, name="version", help="Version building commands")
app.add_typer(explore_cli.app, name="explore", help="Database exploration")

console = Console()


def show_banner() -> None:
    """Display the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║              Great Commission Benchmark - Builder              ║
║                                                               ║
║  Build, curate, and publish official benchmark versions       ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold blue")


def show_status() -> None:
    """Show current question bank status."""
    try:
        with get_db() as db:
            from gcb_builder.core.models import Question
            
            total = db.query(Question).count()
            locked = db.query(Question).filter(Question.locked == True).count()
            approved = db.query(Question).filter(Question.status == "approved").count()
            review = db.query(Question).filter(Question.status == "review").count()
            draft = db.query(Question).filter(Question.status == "draft").count()
            
            status_line = (
                f"Question Bank: {total} total | "
                f"{locked} locked 🔒 | "
                f"{approved} approved | "
                f"{review} in review | "
                f"{draft} draft"
            )
            console.print(status_line, style="dim")
    except Exception:
        console.print("Question Bank: [dim]Database not initialized[/dim]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
) -> None:
    """
    GCB Builder - Create official Great Commission Benchmark versions.
    
    Run without arguments to start the interactive menu.
    """
    if version:
        console.print(f"gcb-builder version {__version__}")
        raise typer.Exit()
    
    # If no subcommand provided, show interactive menu
    if ctx.invoked_subcommand is None:
        interactive_menu()


def interactive_menu() -> None:
    """Display the main interactive menu."""
    import questionary
    
    show_banner()
    show_status()
    console.print()
    
    choices = [
        questionary.Choice("Generate Questions     - AI-assisted question creation", "generate"),
        questionary.Choice("Curate Questions       - Review, edit, and lock questions", "curate"),
        questionary.Choice("Develop Judge Prompts  - Test and refine judge accuracy", "judge"),
        questionary.Choice("Build Version          - Assemble questions into a version", "version"),
        questionary.Choice("Publish Version        - Lock and export for release", "publish"),
        questionary.Choice("Explore Database       - Launch Datasette for SQL exploration", "explore"),
        questionary.Choice("Settings               - Configure LLM backends and API keys", "settings"),
        questionary.Choice("Exit", "exit"),
    ]
    
    answer = questionary.select(
        "What would you like to do?",
        choices=choices,
    ).ask()
    
    if answer == "exit" or answer is None:
        console.print("\n[dim]Goodbye![/dim]")
        raise typer.Exit()
    elif answer == "generate":
        generate_cli.interactive_generate()
        interactive_menu()  # Return to menu
    elif answer == "curate":
        curate_cli.interactive_curate()
        interactive_menu()  # Return to menu
    elif answer == "judge":
        judge_cli.interactive_judge()
        interactive_menu()  # Return to menu
    elif answer == "version":
        version_cli.interactive_version()
        interactive_menu()  # Return to menu
    elif answer == "publish":
        version_cli.interactive_publish()
        interactive_menu()  # Return to menu
    elif answer == "explore":
        explore_cli.interactive_explore()
        interactive_menu()  # Return to menu
    elif answer == "settings":
        _interactive_settings()
        interactive_menu()  # Return to menu


def _interactive_settings() -> None:
    """Interactive settings menu."""
    import questionary
    from gcb_builder.backends.config import list_available_backends, get_config
    
    console.print()
    console.print("[bold]Settings[/bold]")
    console.print()
    
    # Show current configuration
    config = get_config()
    available = list_available_backends()
    
    console.print("[bold]Configured Backends:[/bold]")
    backend_status = [
        ("OpenRouter", "✓" if config.openrouter_api_key else "✗"),
        ("OpenAI", "✓" if config.openai_api_key else "✗"),
        ("Anthropic", "✓" if config.anthropic_api_key else "✗"),
        ("LM Studio", f"✓ ({config.lmstudio_base_url})" if config.lmstudio_base_url else "✗"),
        ("Ollama", f"✓ ({config.ollama_base_url})" if config.ollama_base_url else "✗"),
    ]
    
    for name, status in backend_status:
        console.print(f"  {name}: {status}")
    
    console.print()
    console.print("[dim]Configure backends by setting environment variables:[/dim]")
    console.print("  OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY")
    console.print("  LMSTUDIO_BASE_URL (default: http://localhost:1234/v1)")
    console.print("  OLLAMA_BASE_URL (default: http://localhost:11434)")
    console.print()
    
    questionary.press_any_key_to_continue("Press any key to continue...").ask()


# =============================================================================
# Subcommands
# =============================================================================

@app.command()
def init(
    reset: bool = typer.Option(
        False, "--reset", help="Reset database (DELETES ALL DATA)"
    ),
) -> None:
    """Initialize the database and data directory."""
    if reset:
        confirm = typer.confirm(
            "⚠️  This will DELETE ALL DATA. Are you sure?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()
    
    console.print("Initializing database...")
    init_db(reset=reset)
    console.print("[green]✓ Database initialized successfully.[/green]")


@app.command()
def categories() -> None:
    """List all benchmark categories."""
    show_banner()
    
    # Tier 1
    console.print("\n[bold]Tier 1: Task Capability[/bold] (70% weight)")
    table1 = Table(show_header=True, header_style="bold")
    table1.add_column("ID")
    table1.add_column("Name")
    table1.add_column("Short Name")
    
    for cat in TIER1_CATEGORIES:
        table1.add_row(cat.id, cat.name, cat.short_name)
    
    console.print(table1)
    
    # Tier 2
    console.print("\n[bold]Tier 2: Doctrinal Fidelity[/bold] (20% weight)")
    table2 = Table(show_header=True, header_style="bold")
    table2.add_column("ID")
    table2.add_column("Name")
    table2.add_column("Short Name")
    
    for cat in TIER2_CATEGORIES:
        table2.add_row(cat.id, cat.name, cat.short_name)
    
    console.print(table2)
    
    # Tier 3
    console.print("\n[bold]Tier 3: Worldview Confession[/bold] (10% weight)")
    table3 = Table(show_header=True, header_style="bold")
    table3.add_column("ID")
    table3.add_column("Name")
    table3.add_column("Short Name")
    
    for cat in TIER3_CATEGORIES:
        table3.add_row(cat.id, cat.name, cat.short_name)
    
    console.print(table3)
    
    console.print(f"\n[dim]Total: {len(CATEGORIES)} categories[/dim]")


@app.command("compile-bundle")
def compile_bundle_command(
    version: str = typer.Option(..., "--version", "-v", help="Version to compile (e.g., 1.0.0)"),
    output: str = typer.Option(..., "--output", "-o", help="Output directory for bundle"),
) -> None:
    """Compile a published version into a Python bundle for CLI distribution."""
    from pathlib import Path
    from gcb_builder.versioning.builder import VersionBuilder
    from gcb_builder.versioning.bundle_compiler import compile_from_version
    
    init_db()
    
    builder = VersionBuilder()
    ver = builder.get_version_by_number(version)
    
    if not ver:
        console.print(f"[red]Version {version} not found.[/red]")
        raise typer.Exit(1)
    
    if ver.status not in ("locked", "published"):
        console.print(f"[yellow]Warning: Version is in '{ver.status}' status. Consider publishing first.[/yellow]")
    
    console.print()
    console.print("[bold]Compiling Bundle for CLI Distribution[/bold]")
    console.print()
    console.print(f"  Source: v{ver.version} ({ver.name})")
    console.print(f"  Output: {output}")
    console.print()
    
    try:
        output_path, stats = compile_from_version(ver.id, Path(output))
        
        console.print("[green]✓ Bundle compiled successfully![/green]")
        console.print()
        console.print(f"  Questions: {stats['question_count']}")
        console.print(f"  Compressed: {stats['original_size']} → {stats['compressed_size']} bytes ({stats['compression_ratio']}% reduction)")
        console.print(f"  Checksum: {stats['checksum']}")
        console.print()
        console.print(f"Output: {output_path}")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Copy the bundle to gcb-runner/gcb_runner/versions/")
        console.print("  2. Update versions/loader.py to include the new version")
        console.print("  3. Bump gcb-runner version and publish to PyPI")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show current question bank status."""
    show_banner()
    
    try:
        with get_db() as db:
            from sqlalchemy import func
            from gcb_builder.core.models import Question, BenchmarkVersion
            
            # Question counts by status
            console.print("\n[bold]Question Status[/bold]")
            status_counts = (
                db.query(Question.status, func.count(Question.id))
                .group_by(Question.status)
                .all()
            )
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Status")
            table.add_column("Count", justify="right")
            
            total = 0
            for status, count in status_counts:
                table.add_row(status, str(count))
                total += count
            
            table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
            console.print(table)
            
            # Locked questions
            locked = db.query(Question).filter(Question.locked == True).count()
            console.print(f"\n[dim]Locked questions: {locked} 🔒[/dim]")
            
            # Category breakdown
            console.print("\n[bold]Questions by Category[/bold]")
            cat_counts = (
                db.query(Question.category, func.count(Question.id))
                .group_by(Question.category)
                .all()
            )
            
            if cat_counts:
                cat_table = Table(show_header=True, header_style="bold")
                cat_table.add_column("Category")
                cat_table.add_column("Name")
                cat_table.add_column("Count", justify="right")
                
                for cat_id, count in sorted(cat_counts):
                    cat = CATEGORIES.get(cat_id)
                    name = cat.short_name if cat else "Unknown"
                    cat_table.add_row(cat_id, name, str(count))
                
                console.print(cat_table)
            else:
                console.print("[dim]No questions yet.[/dim]")
            
            # Versions
            console.print("\n[bold]Benchmark Versions[/bold]")
            versions = db.query(BenchmarkVersion).order_by(BenchmarkVersion.created_at.desc()).all()
            
            if versions:
                ver_table = Table(show_header=True, header_style="bold")
                ver_table.add_column("Version")
                ver_table.add_column("Name")
                ver_table.add_column("Status")
                ver_table.add_column("Questions", justify="right")
                
                for v in versions:
                    ver_table.add_row(v.version, v.name, v.status, str(v.question_count))
                
                console.print(ver_table)
            else:
                console.print("[dim]No versions yet.[/dim]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Run 'gcb-builder init' to initialize the database.[/yellow]")


if __name__ == "__main__":
    app()
