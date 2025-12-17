"""
CLI commands for judge prompt development.

Provides functionality for:
- Managing test cases
- Testing judge accuracy
- Viewing validation results
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
from gcb_builder.core.database import get_db, init_db
from gcb_builder.core.models import JudgeTestCase
from gcb_builder.judging.tester import JudgeTester, ValidationResult

app = typer.Typer(help="Judge prompt development commands")
console = Console()


def _display_test_cases(test_cases: list[JudgeTestCase]) -> None:
    """Display test cases in a table."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", width=5)
    table.add_column("Tier", width=4)
    table.add_column("Cat", width=4)
    table.add_column("Prompt Preview", width=40, no_wrap=True)
    table.add_column("Expected", width=12)
    table.add_column("Refusal", width=12)
    
    for tc in test_cases:
        prompt_preview = tc.prompt[:37] + "..." if len(tc.prompt) > 40 else tc.prompt
        prompt_preview = prompt_preview.replace("\n", " ")
        table.add_row(
            str(tc.id),
            str(tc.tier),
            tc.category or "-",
            prompt_preview,
            tc.expected_verdict,
            tc.expected_refusal_type or "-",
        )
    
    console.print(table)


def _display_validation_result(result: ValidationResult) -> None:
    """Display validation results."""
    tester = JudgeTester()
    report = tester.format_validation_report(result)
    console.print(report)


def interactive_judge() -> None:
    """Run the interactive judge development wizard."""
    init_db()
    
    console.print()
    console.print("[bold]Judge Prompt Development[/bold]")
    console.print("[dim]Test and refine judge accuracy[/dim]")
    console.print()
    
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Test judge accuracy", "test"),
                questionary.Choice("Add test case", "add"),
                questionary.Choice("List test cases", "list"),
                questionary.Choice("View test case", "view"),
                questionary.Choice("Delete test case", "delete"),
                questionary.Choice("← Back to main menu", "back"),
            ]
        ).ask()
        
        if choice == "back" or choice is None:
            return
        
        if choice == "test":
            _interactive_test_accuracy()
        elif choice == "add":
            _interactive_add_test_case()
        elif choice == "list":
            _interactive_list_test_cases()
        elif choice == "view":
            _interactive_view_test_case()
        elif choice == "delete":
            _interactive_delete_test_case()


def _interactive_test_accuracy() -> None:
    """Run judge accuracy testing."""
    # Select tier or all
    tier_choice = questionary.select(
        "Test which tier?",
        choices=[
            questionary.Choice("Tier 1 - Task Requests", 1),
            questionary.Choice("Tier 2 - Doctrinal Content", 2),
            questionary.Choice("Tier 3 - Worldview Questions", 3),
            questionary.Choice("All tiers", None),
        ]
    ).ask()
    
    if tier_choice == "back":
        return
    
    tier = tier_choice if isinstance(tier_choice, int) else None
    
    # Check if we have test cases
    tester = JudgeTester()
    test_cases = tester.list_test_cases(tier=tier)
    
    if not test_cases:
        console.print("[yellow]No test cases found. Add some test cases first.[/yellow]")
        return
    
    console.print(f"\nFound {len(test_cases)} test cases.")
    
    # Select backend
    available = list_available_backends()
    if not available:
        console.print("[red]No LLM backends configured.[/red]")
        return
    
    backend_choice = questionary.select(
        "Select LLM backend for judging:",
        choices=[questionary.Choice(bt.value, bt) for bt in available]
    ).ask()
    
    if not backend_choice:
        return
    
    # Select model
    model = asyncio.run(_select_judge_model(backend_choice))
    if not model:
        return
    
    # Run validation
    console.print()
    console.print(f"[bold]Running judge validation...[/bold]")
    console.print(f"  Tier: {'All' if tier is None else tier}")
    console.print(f"  Test cases: {len(test_cases)}")
    console.print(f"  Model: {model}")
    console.print()
    
    # Create backend-compatible tester
    backend = get_backend(backend_choice)
    
    # Wrap backend to match tester's expected interface
    class BackendWrapper:
        def __init__(self, backend):
            self._backend = backend
        
        async def complete(self, messages, model, system_prompt=None):
            from gcb_builder.backends.base import CompletionRequest
            request = CompletionRequest(
                messages=messages,
                model=model,
                system_prompt=system_prompt,
            )
            response = await self._backend.complete(request)
            return response.content
    
    tester_with_backend = JudgeTester(backend=BackendWrapper(backend))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Testing {len(test_cases)} cases...", total=None)
        
        try:
            result = asyncio.run(tester_with_backend.validate_judge(
                tier=tier,
                judge_model=model,
            ))
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]Error during validation: {e}[/red]")
            return
    
    console.print()
    _display_validation_result(result)


async def _select_judge_model(backend_type: BackendType) -> Optional[str]:
    """Select a model for judging."""
    try:
        backend = get_backend(backend_type)
        models = await backend.list_models()
        
        if not models:
            console.print(f"[yellow]No models available from {backend_type.value}[/yellow]")
            return None
        
        # Prefer GPT-4 or similar for judging
        display_models = models[:15]
        choices = [
            questionary.Choice(f"{m.name} ({m.id})", m.id)
            for m in display_models
        ]
        choices.append(questionary.Choice("← Back", None))
        
        return questionary.select("Select judge model:", choices=choices).ask()
    except Exception as e:
        console.print(f"[red]Error listing models: {e}[/red]")
        return None


def _interactive_add_test_case() -> None:
    """Add a new test case."""
    console.print("\n[bold]Add Test Case[/bold]")
    
    # Tier
    tier = questionary.select(
        "Tier:",
        choices=[
            questionary.Choice("Tier 1 - Task Requests", 1),
            questionary.Choice("Tier 2 - Doctrinal Content", 2),
            questionary.Choice("Tier 3 - Worldview Questions", 3),
        ]
    ).ask()
    
    if not tier:
        return
    
    # Category (optional)
    from gcb_builder.core.categories import CATEGORIES, get_categories_by_tier
    tier_categories = get_categories_by_tier(tier)
    cat_choices = [questionary.Choice(f"{c.id} {c.name}", c.id) for c in tier_categories]
    cat_choices.insert(0, questionary.Choice("No specific category", None))
    
    category = questionary.select("Category (optional):", choices=cat_choices).ask()
    
    # Prompt
    prompt = questionary.text(
        "Enter the prompt/question:",
        multiline=True,
    ).ask()
    
    if not prompt:
        return
    
    # Sample response
    sample_response = questionary.text(
        "Enter the sample response to evaluate:",
        multiline=True,
    ).ask()
    
    if not sample_response:
        return
    
    # Expected verdict
    verdict_choices = {
        1: ["ACCEPTED", "COMPROMISED", "REFUSED"],
        2: ["LOYAL", "COMPROMISED", "DISLOYAL"],
        3: ["AFFIRMED", "HEDGED", "DENIED"],
    }
    
    expected_verdict = questionary.select(
        "Expected verdict:",
        choices=verdict_choices[tier]
    ).ask()
    
    if not expected_verdict:
        return
    
    # Refusal type (if applicable)
    expected_refusal_type = None
    negative_verdicts = {"REFUSED", "DISLOYAL", "DENIED"}
    if expected_verdict in negative_verdicts:
        expected_refusal_type = questionary.select(
            "Expected refusal type:",
            choices=["CAPABILITY", "SAFETY", "IDEOLOGICAL", "UNCLEAR", "None"]
        ).ask()
        if expected_refusal_type == "None":
            expected_refusal_type = None
    
    # Reasoning
    reasoning = questionary.text(
        "Why is this the correct verdict? (optional):",
    ).ask()
    
    # Create test case
    tester = JudgeTester()
    try:
        test_case = tester.create_test_case(
            prompt=prompt,
            sample_response=sample_response,
            expected_verdict=expected_verdict,
            tier=tier,
            expected_refusal_type=expected_refusal_type,
            verdict_reasoning=reasoning if reasoning else None,
            category=category,
        )
        console.print(f"[green]✓ Test case #{test_case.id} created.[/green]")
    except Exception as e:
        console.print(f"[red]Error creating test case: {e}[/red]")


def _interactive_list_test_cases() -> None:
    """List test cases."""
    tier_choice = questionary.select(
        "Filter by tier:",
        choices=[
            questionary.Choice("All tiers", None),
            questionary.Choice("Tier 1", 1),
            questionary.Choice("Tier 2", 2),
            questionary.Choice("Tier 3", 3),
        ]
    ).ask()
    
    tier = tier_choice if isinstance(tier_choice, int) else None
    
    tester = JudgeTester()
    test_cases = tester.list_test_cases(tier=tier)
    
    if not test_cases:
        console.print("[dim]No test cases found.[/dim]")
        return
    
    _display_test_cases(test_cases)


def _interactive_view_test_case() -> None:
    """View a specific test case."""
    tc_id = questionary.text(
        "Enter test case ID:",
        validate=lambda x: x.isdigit(),
    ).ask()
    
    if not tc_id:
        return
    
    tester = JudgeTester()
    test_case = tester.get_test_case(int(tc_id))
    
    if not test_case:
        console.print(f"[red]Test case #{tc_id} not found.[/red]")
        return
    
    content = f"""[bold]Test Case #{test_case.id}[/bold]

[bold]Tier:[/bold] {test_case.tier}
[bold]Category:[/bold] {test_case.category or 'None'}
[bold]Expected Verdict:[/bold] {test_case.expected_verdict}
[bold]Expected Refusal Type:[/bold] {test_case.expected_refusal_type or 'None'}

[bold]Prompt:[/bold]
{test_case.prompt}

[bold]Sample Response:[/bold]
{test_case.sample_response}

{"[bold]Reasoning:[/bold] " + test_case.verdict_reasoning if test_case.verdict_reasoning else ""}
"""
    console.print(Panel(content, title=f"Test Case #{test_case.id}"))


def _interactive_delete_test_case() -> None:
    """Delete a test case."""
    tc_id = questionary.text(
        "Enter test case ID to delete:",
        validate=lambda x: x.isdigit(),
    ).ask()
    
    if not tc_id:
        return
    
    if questionary.confirm(f"Delete test case #{tc_id}?", default=False).ask():
        tester = JudgeTester()
        if tester.delete_test_case(int(tc_id)):
            console.print(f"[red]Test case #{tc_id} deleted.[/red]")
        else:
            console.print(f"[yellow]Test case #{tc_id} not found.[/yellow]")


# Typer commands for non-interactive use

@app.command("list")
def list_command(
    tier: Optional[int] = typer.Option(None, "--tier", "-t", help="Filter by tier"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
) -> None:
    """List test cases."""
    init_db()
    tester = JudgeTester()
    test_cases = tester.list_test_cases(tier=tier, category=category)
    
    if not test_cases:
        console.print("[dim]No test cases found.[/dim]")
        return
    
    _display_test_cases(test_cases)


@app.command("add")
def add_command(
    prompt: str = typer.Option(..., "--prompt", "-p", help="The prompt/question"),
    response: str = typer.Option(..., "--response", "-r", help="Sample response"),
    verdict: str = typer.Option(..., "--verdict", "-v", help="Expected verdict"),
    tier: int = typer.Option(..., "--tier", "-t", help="Tier (1, 2, or 3)"),
    refusal_type: Optional[str] = typer.Option(None, "--refusal-type", help="Refusal type"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category ID"),
    reasoning: Optional[str] = typer.Option(None, "--reasoning", help="Why this is correct"),
) -> None:
    """Add a test case."""
    init_db()
    tester = JudgeTester()
    
    try:
        test_case = tester.create_test_case(
            prompt=prompt,
            sample_response=response,
            expected_verdict=verdict.upper(),
            tier=tier,
            expected_refusal_type=refusal_type.upper() if refusal_type else None,
            verdict_reasoning=reasoning,
            category=category,
        )
        console.print(f"[green]✓ Test case #{test_case.id} created.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_command(
    test_case_id: int = typer.Argument(..., help="Test case ID"),
) -> None:
    """Delete a test case."""
    init_db()
    tester = JudgeTester()
    
    if tester.delete_test_case(test_case_id):
        console.print(f"[red]Test case #{test_case_id} deleted.[/red]")
    else:
        console.print(f"[yellow]Test case #{test_case_id} not found.[/yellow]")
        raise typer.Exit(1)
