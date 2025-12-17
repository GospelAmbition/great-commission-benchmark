"""
CLI commands for question generation.

Provides interactive prompts for:
- Category selection
- Question count input
- LLM model selection
- Generation workflow
"""

import asyncio
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gcb_builder.backends.base import BackendType
from gcb_builder.backends.config import get_backend, list_available_backends
from gcb_builder.core.categories import (
    CATEGORIES,
    TIER1_CATEGORIES,
    TIER2_CATEGORIES,
    TIER3_CATEGORIES,
    Category,
)
from gcb_builder.core.database import get_db, init_db
from gcb_builder.generation.generator import QuestionGenerator
from gcb_builder.generation.prompt_loader import get_available_categories

app = typer.Typer(help="Question generation commands")
console = Console()


def _select_tier() -> Optional[int]:
    """Prompt user to select a tier."""
    choices = [
        questionary.Choice("Tier 1: Task Capability (70%)", 1),
        questionary.Choice("Tier 2: Doctrinal Fidelity (20%)", 2),
        questionary.Choice("Tier 3: Worldview Confession (10%)", 3),
        questionary.Choice("← Back", None),
    ]
    return questionary.select("Select tier:", choices=choices).ask()


def _select_category(tier: int) -> Optional[str]:
    """Prompt user to select a category within a tier."""
    categories_by_tier = {
        1: TIER1_CATEGORIES,
        2: TIER2_CATEGORIES,
        3: TIER3_CATEGORIES,
    }
    
    categories = categories_by_tier.get(tier, [])
    available = dict(get_available_categories())
    
    choices = []
    for cat in categories:
        has_prompt = cat.id in available
        status = "" if has_prompt else " [dim](no prompt)[/dim]"
        choices.append(
            questionary.Choice(f"{cat.id} {cat.name}{status}", cat.id)
        )
    choices.append(questionary.Choice("← Back", None))
    
    return questionary.select("Select category:", choices=choices).ask()


def _select_backend() -> Optional[BackendType]:
    """Prompt user to select an LLM backend."""
    available = list_available_backends()
    
    if not available:
        console.print("[red]No LLM backends are configured.[/red]")
        console.print("Set up API keys in your environment or .env file:")
        console.print("  - OPENROUTER_API_KEY for OpenRouter")
        console.print("  - OPENAI_API_KEY for OpenAI")
        console.print("  - ANTHROPIC_API_KEY for Anthropic")
        console.print("  - LM Studio runs locally at http://localhost:1234")
        console.print("  - Ollama runs locally at http://localhost:11434")
        return None
    
    choices = [
        questionary.Choice(f"{bt.value}", bt)
        for bt in available
    ]
    choices.append(questionary.Choice("← Back", None))
    
    return questionary.select("Select LLM backend:", choices=choices).ask()


async def _select_model(backend_type: BackendType) -> Optional[str]:
    """Prompt user to select a model from the backend."""
    try:
        backend = get_backend(backend_type)
        models = await backend.list_models()
        
        if not models:
            console.print(f"[yellow]No models available from {backend_type.value}[/yellow]")
            return None
        
        # Show up to 20 models
        display_models = models[:20]
        choices = [
            questionary.Choice(f"{m.name} ({m.id})", m.id)
            for m in display_models
        ]
        
        if len(models) > 20:
            choices.append(
                questionary.Choice(f"[dim]... and {len(models) - 20} more[/dim]", None)
            )
        
        choices.append(questionary.Choice("← Back", None))
        
        return questionary.select("Select model:", choices=choices).ask()
    except Exception as e:
        console.print(f"[red]Error listing models: {e}[/red]")
        return None


def _get_question_count() -> Optional[int]:
    """Prompt user for number of questions to generate."""
    count_str = questionary.text(
        "How many questions to generate?",
        default="15",
        validate=lambda x: x.isdigit() and 1 <= int(x) <= 50,
    ).ask()
    
    if count_str is None:
        return None
    return int(count_str)


async def _run_generation(
    category_id: str,
    count: int,
    backend_type: BackendType,
    model: str,
) -> None:
    """Run the generation process with progress display."""
    category = CATEGORIES.get(category_id)
    
    console.print()
    console.print(Panel(
        f"[bold]Generating {count} questions[/bold]\n\n"
        f"Category: {category_id} {category.name}\n"
        f"Backend: {backend_type.value}\n"
        f"Model: {model}",
        title="Generation Started",
    ))
    
    # Initialize database if needed
    init_db()
    
    # Get backend
    backend = get_backend(backend_type)
    
    # Run generation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating questions...", total=None)
        
        generator = QuestionGenerator(backend)
        result = await generator.generate(
            category_id=category_id,
            count=count,
            model=model,
        )
        
        progress.update(task, completed=True)
    
    # Show results
    console.print()
    
    if result.errors:
        console.print("[yellow]Errors during generation:[/yellow]")
        for error in result.errors[:5]:
            console.print(f"  • {error}")
        if len(result.errors) > 5:
            console.print(f"  ... and {len(result.errors) - 5} more errors")
        console.print()
    
    # Summary table
    table = Table(title="Generation Results")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    
    table.add_row("Questions Generated", str(result.total_generated))
    table.add_row("Questions Saved", str(result.saved_count))
    table.add_row("Failed", str(result.failed_count))
    table.add_row("Duration", f"{result.duration_seconds:.1f}s")
    table.add_row("Model Used", result.model_used)
    
    console.print(table)
    
    if result.questions:
        console.print()
        console.print(f"[green]✓ Successfully generated {result.saved_count} questions![/green]")
        console.print("[dim]Questions saved with status 'draft'. Use 'gcb-builder curate' to review.[/dim]")


def interactive_generate() -> None:
    """Run the interactive generation wizard."""
    console.print()
    console.print("[bold]Question Generation[/bold]")
    console.print("[dim]Generate benchmark questions using AI assistance[/dim]")
    console.print()
    
    # Select tier
    tier = _select_tier()
    if tier is None:
        return
    
    # Select category
    category_id = _select_category(tier)
    if category_id is None:
        return
    
    # Select backend
    backend_type = _select_backend()
    if backend_type is None:
        return
    
    # Select model
    model = asyncio.run(_select_model(backend_type))
    if model is None:
        return
    
    # Get count
    count = _get_question_count()
    if count is None:
        return
    
    # Confirm
    category = CATEGORIES.get(category_id)
    console.print()
    console.print(f"[bold]Ready to generate:[/bold]")
    console.print(f"  Category: {category_id} {category.name}")
    console.print(f"  Count: {count} questions")
    console.print(f"  Backend: {backend_type.value}")
    console.print(f"  Model: {model}")
    console.print()
    
    if not questionary.confirm("Proceed with generation?", default=True).ask():
        console.print("[dim]Cancelled.[/dim]")
        return
    
    # Run generation
    asyncio.run(_run_generation(category_id, count, backend_type, model))


@app.command("run")
def generate_command(
    category: str = typer.Option(None, "--category", "-c", help="Category ID (e.g., 3.2)"),
    count: int = typer.Option(15, "--count", "-n", help="Number of questions to generate"),
    backend: str = typer.Option(None, "--backend", "-b", help="LLM backend (openrouter, openai, etc.)"),
    model: str = typer.Option(None, "--model", "-m", help="Model ID to use"),
) -> None:
    """Generate questions (non-interactive mode)."""
    if not all([category, backend, model]):
        console.print("[yellow]Missing required options. Running interactive mode...[/yellow]")
        interactive_generate()
        return
    
    try:
        backend_type = BackendType(backend)
    except ValueError:
        console.print(f"[red]Invalid backend: {backend}[/red]")
        console.print(f"Valid backends: {[b.value for b in BackendType]}")
        raise typer.Exit(1)
    
    if category not in CATEGORIES:
        console.print(f"[red]Invalid category: {category}[/red]")
        raise typer.Exit(1)
    
    asyncio.run(_run_generation(category, count, backend_type, model))


@app.command("list-prompts")
def list_prompts() -> None:
    """List available generation prompts."""
    from gcb_builder.generation.prompt_loader import validate_prompt_completeness
    
    completeness = validate_prompt_completeness()
    
    table = Table(title="Generation Prompts")
    table.add_column("Category")
    table.add_column("Name")
    table.add_column("Status")
    
    for cat_id in sorted(completeness.keys()):
        category = CATEGORIES.get(cat_id)
        status = "[green]✓ Ready[/green]" if completeness[cat_id] else "[red]✗ Missing[/red]"
        table.add_row(cat_id, category.name if category else "Unknown", status)
    
    console.print(table)
