"""
CLI commands for database exploration.

Launches Datasette for visual database exploration.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from gcb_builder.core.database import get_database_path, init_db

app = typer.Typer(help="Database exploration commands")
console = Console()


def _create_datasette_metadata() -> Path:
    """Create Datasette metadata configuration."""
    metadata = {
        "title": "GCB Builder - Question Bank",
        "description": "Explore and curate Great Commission Benchmark questions",
        "databases": {
            "gcb_builder": {
                "tables": {
                    "questions": {
                        "label_column": "content",
                        "description": "All benchmark questions with metadata",
                        "facets": ["tier", "category", "status", "locked", "difficulty"],
                    },
                    "benchmark_versions": {
                        "description": "Published and draft benchmark versions",
                    },
                    "version_questions": {
                        "description": "Links questions to versions",
                    },
                    "judge_test_cases": {
                        "description": "Test cases for validating judge prompts",
                    },
                },
                "queries": {
                    "category_coverage": {
                        "sql": "SELECT tier, category, COUNT(*) as count, SUM(locked) as locked_count FROM questions GROUP BY tier, category ORDER BY tier, category",
                        "title": "Category Coverage",
                        "description": "Question counts by tier and category",
                    },
                    "curation_queue": {
                        "sql": "SELECT id, substr(content, 1, 100) as content_preview, category, status, locked FROM questions WHERE status = 'review' ORDER BY created_at DESC",
                        "title": "Curation Queue",
                        "description": "Questions awaiting review",
                    },
                    "locked_questions": {
                        "sql": "SELECT id, substr(content, 1, 100) as content_preview, category, locked_at, locked_by FROM questions WHERE locked = 1 ORDER BY locked_at DESC",
                        "title": "Locked Questions",
                        "description": "Protected questions that won't be deleted",
                    },
                    "tier_distribution": {
                        "sql": "SELECT tier, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM questions), 1) as percentage FROM questions GROUP BY tier",
                        "title": "Tier Distribution",
                        "description": "Question distribution across tiers",
                    },
                    "capability_vs_willingness": {
                        "sql": "SELECT CASE WHEN tests_capability AND tests_willingness THEN 'Both' WHEN tests_capability THEN 'Capability Only' WHEN tests_willingness THEN 'Willingness Only' ELSE 'Neither' END as type, COUNT(*) as count FROM questions GROUP BY type",
                        "title": "Capability vs Willingness",
                        "description": "Question breakdown by what they test",
                    },
                },
            },
        },
    }
    
    import json
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    metadata_path = data_dir / "datasette-metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return metadata_path


def launch_datasette(
    port: int = 8001,
    open_browser: bool = True,
    host: str = "127.0.0.1",
) -> None:
    """
    Launch Datasette to explore the question bank.
    
    Args:
        port: Port number for the server
        open_browser: Whether to open browser automatically
        host: Host to bind to
    """
    init_db()  # Ensure database exists
    
    db_path = get_database_path()
    
    if not db_path.exists():
        console.print("[red]Database not found. Run 'gcb-builder init' first.[/red]")
        return
    
    # Create metadata
    metadata_path = _create_datasette_metadata()
    
    console.print()
    console.print("[bold]GCB Builder - Database Explorer[/bold]")
    console.print()
    console.print(f"  Database: {db_path}")
    console.print(f"  Server: http://{host}:{port}")
    console.print()
    
    # Build command
    cmd = [
        sys.executable, "-m", "datasette",
        str(db_path),
        "--port", str(port),
        "--host", host,
        "--metadata", str(metadata_path),
    ]
    
    console.print("[dim]Starting Datasette...[/dim]")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait a moment for server to start
        time.sleep(1.5)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process ended, check for errors
            _, stderr = process.communicate()
            console.print(f"[red]Failed to start Datasette:[/red]")
            console.print(stderr.decode() if stderr else "Unknown error")
            return
        
        url = f"http://{host}:{port}"
        console.print(f"[green]✓ Datasette running at {url}[/green]")
        
        if open_browser:
            console.print("[dim]Opening browser...[/dim]")
            webbrowser.open(url)
        
        console.print()
        console.print("[dim]Press Ctrl+C to stop the server.[/dim]")
        
        # Wait for process
        process.wait()
        
    except KeyboardInterrupt:
        console.print("\n[dim]Stopping Datasette...[/dim]")
        process.terminate()
        console.print("[green]✓ Datasette stopped.[/green]")
    except FileNotFoundError:
        console.print("[red]Datasette not found. Install with: pip install datasette[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def interactive_explore() -> None:
    """Run the interactive explore wizard."""
    import questionary
    
    console.print()
    console.print("[bold]Database Explorer[/bold]")
    console.print("[dim]Launch Datasette for SQL exploration[/dim]")
    console.print()
    
    port_str = questionary.text(
        "Port number:",
        default="8001",
        validate=lambda x: x.isdigit() and 1024 <= int(x) <= 65535,
    ).ask()
    
    if not port_str:
        return
    
    open_browser = questionary.confirm(
        "Open browser automatically?",
        default=True,
    ).ask()
    
    launch_datasette(
        port=int(port_str),
        open_browser=open_browser if open_browser is not None else True,
    )


@app.command("launch")
def explore_command(
    port: int = typer.Option(8001, "--port", "-p", help="Port number"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
) -> None:
    """Launch Datasette to explore the database."""
    launch_datasette(
        port=port,
        open_browser=not no_browser,
        host=host,
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Database exploration with Datasette."""
    if ctx.invoked_subcommand is None:
        launch_datasette()
