"""
CLI commands for version building and publishing.

Provides functionality for:
- Creating benchmark versions
- Adding questions to versions
- Validating versions
- Publishing versions
"""

from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gcb_builder.core.categories import CATEGORIES
from gcb_builder.core.database import init_db
from gcb_builder.versioning.builder import VersionBuilder
from gcb_builder.versioning.publisher import VersionPublisher
from gcb_builder.versioning.validator import VersionValidator

app = typer.Typer(help="Version building commands")
console = Console()


def _display_version_stats(version_id: int) -> None:
    """Display statistics for a version."""
    builder = VersionBuilder()
    version = builder.get_version(version_id)
    stats = builder.get_version_stats(version_id)
    
    if not version:
        console.print("[red]Version not found[/red]")
        return
    
    # Version info panel
    info = f"""[bold]{version.name}[/bold] (v{version.version})
Status: {version.status}
Questions: {stats.total_questions} ({stats.locked_questions} locked 🔒)
"""
    console.print(Panel(info, title="Version Info"))
    
    # Tier distribution
    tier_table = Table(title="Tier Distribution")
    tier_table.add_column("Tier")
    tier_table.add_column("Count", justify="right")
    tier_table.add_column("Actual %", justify="right")
    tier_table.add_column("Target %", justify="right")
    tier_table.add_column("Status")
    
    targets = {1: 70, 2: 20, 3: 10}
    for tier in [1, 2, 3]:
        count = stats.tier_counts.get(tier, 0)
        actual_pct = stats.tier_percentages.get(tier, 0)
        target_pct = targets[tier]
        diff = abs(actual_pct - target_pct)
        status = "✓" if diff <= 5 else "✗"
        tier_table.add_row(
            f"Tier {tier}",
            str(count),
            f"{actual_pct:.1f}%",
            f"{target_pct}%",
            status,
        )
    
    console.print(tier_table)
    
    # Category coverage
    cat_table = Table(title="Category Coverage")
    cat_table.add_column("Category")
    cat_table.add_column("Name")
    cat_table.add_column("Count", justify="right")
    
    for cat_id in sorted(CATEGORIES.keys()):
        count = stats.category_counts.get(cat_id, 0)
        cat = CATEGORIES[cat_id]
        style = "" if count > 0 else "dim"
        cat_table.add_row(cat_id, cat.short_name, str(count), style=style)
    
    console.print(cat_table)
    
    # Capability/willingness balance
    console.print()
    console.print("[bold]Capability vs Willingness:[/bold]")
    console.print(f"  Capability-only: {stats.capability_only}")
    console.print(f"  Willingness-only: {stats.willingness_only}")
    console.print(f"  Both: {stats.both}")


def _display_validation_result(result) -> None:
    """Display validation results."""
    status = "[green]✓ PASSED[/green]" if result.is_valid else "[red]✗ FAILED[/red]"
    console.print(f"\n[bold]Validation: {status}[/bold]\n")
    
    if result.errors:
        console.print("[red]Errors:[/red]")
        for issue in result.errors:
            console.print(f"  ✗ {issue.message}")
            if issue.details:
                console.print(f"    {issue.details}")
    
    if result.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for issue in result.warnings:
            console.print(f"  ⚠ {issue.message}")
    
    if result.info:
        console.print("\n[dim]Info:[/dim]")
        for issue in result.info:
            console.print(f"  ℹ {issue.message}")


def interactive_version() -> None:
    """Run the interactive version building wizard."""
    init_db()
    
    console.print()
    console.print("[bold]Version Building[/bold]")
    console.print("[dim]Assemble questions into benchmark versions[/dim]")
    console.print()
    
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Create new version", "create"),
                questionary.Choice("View existing versions", "list"),
                questionary.Choice("Edit version in progress", "edit"),
                questionary.Choice("Validate version", "validate"),
                questionary.Choice("← Back to main menu", "back"),
            ]
        ).ask()
        
        if choice == "back" or choice is None:
            return
        
        if choice == "create":
            _interactive_create_version()
        elif choice == "list":
            _interactive_list_versions()
        elif choice == "edit":
            _interactive_edit_version()
        elif choice == "validate":
            _interactive_validate_version()


def interactive_publish() -> None:
    """Run the interactive publishing wizard."""
    init_db()
    
    console.print()
    console.print("[bold]Publish Version[/bold]")
    console.print("[dim]Lock and export versions for release[/dim]")
    console.print()
    
    builder = VersionBuilder()
    versions = builder.list_versions()
    
    # Filter to publishable versions
    publishable = [v for v in versions if v.status in ("building", "validating", "locked")]
    
    if not publishable:
        console.print("[yellow]No versions available for publishing.[/yellow]")
        console.print("[dim]Create a version first using 'Build Version'.[/dim]")
        return
    
    choices = [
        questionary.Choice(f"v{v.version} - {v.name} ({v.status})", v.id)
        for v in publishable
    ]
    choices.append(questionary.Choice("← Back", None))
    
    version_id = questionary.select("Select version to publish:", choices=choices).ask()
    
    if not version_id:
        return
    
    version = builder.get_version(version_id)
    
    # Show current stats
    _display_version_stats(version_id)
    
    # Validate first
    console.print("\n[bold]Validating...[/bold]")
    validator = VersionValidator()
    result = validator.validate(version_id)
    _display_validation_result(result)
    
    if not result.is_valid:
        if not questionary.confirm(
            "Version has validation errors. Publish anyway?",
            default=False
        ).ask():
            return
    
    # Confirm publish
    console.print()
    console.print("[yellow]⚠️  Publishing will permanently lock this version.[/yellow]")
    console.print("[yellow]   No further edits will be possible.[/yellow]")
    
    if not questionary.confirm(f"Confirm publish v{version.version}?", default=False).ask():
        console.print("[dim]Cancelled.[/dim]")
        return
    
    # Publish
    publisher = VersionPublisher()
    
    if version.status != "locked":
        success, message = publisher.lock_version(version_id, force=True)
        if not success:
            console.print(f"[red]Lock failed: {message}[/red]")
            return
        console.print(f"[green]✓ Version locked[/green]")
    
    success, message = publisher.publish_version(version_id)
    if success:
        console.print(f"[green]✓ {message}[/green]")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Upload the JSON file to the platform")
        console.print("  2. Compile bundle for CLI distribution:")
        console.print(f"     gcb-builder compile-bundle --version {version.version}")
    else:
        console.print(f"[red]Publish failed: {message}[/red]")


def _interactive_create_version() -> None:
    """Create a new version interactively."""
    version_number = questionary.text(
        "Version number (e.g., 1.0.0):",
        validate=lambda x: len(x) > 0,
    ).ask()
    
    if not version_number:
        return
    
    name = questionary.text(
        "Version name (e.g., Initial Release):",
        validate=lambda x: len(x) > 0,
    ).ask()
    
    if not name:
        return
    
    description = questionary.text(
        "Description (optional):",
    ).ask()
    
    builder = VersionBuilder()
    
    try:
        version = builder.create_version(
            version_number=version_number,
            name=name,
            description=description if description else None,
        )
        console.print(f"[green]✓ Version v{version.version} created.[/green]")
        
        # Offer to add questions
        if questionary.confirm("Add questions now?", default=True).ask():
            _add_questions_to_version(version.id)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


def _interactive_list_versions() -> None:
    """List all versions."""
    builder = VersionBuilder()
    versions = builder.list_versions()
    
    if not versions:
        console.print("[dim]No versions found.[/dim]")
        return
    
    table = Table(title="Benchmark Versions")
    table.add_column("Version")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Questions", justify="right")
    table.add_column("Created")
    
    for v in versions:
        stats = builder.get_version_stats(v.id)
        table.add_row(
            v.version,
            v.name,
            v.status,
            str(stats.total_questions),
            v.created_at.strftime("%Y-%m-%d") if v.created_at else "-",
        )
    
    console.print(table)


def _interactive_edit_version() -> None:
    """Edit a version in progress."""
    builder = VersionBuilder()
    versions = builder.list_versions()
    
    # Filter to editable versions
    editable = [v for v in versions if v.status in ("building", "validating")]
    
    if not editable:
        console.print("[dim]No editable versions found.[/dim]")
        return
    
    choices = [
        questionary.Choice(f"v{v.version} - {v.name}", v.id)
        for v in editable
    ]
    choices.append(questionary.Choice("← Back", None))
    
    version_id = questionary.select("Select version to edit:", choices=choices).ask()
    
    if not version_id:
        return
    
    # Show stats
    _display_version_stats(version_id)
    
    # Edit menu
    while True:
        action = questionary.select(
            "Action:",
            choices=[
                questionary.Choice("Add questions", "add"),
                questionary.Choice("Remove question", "remove"),
                questionary.Choice("View questions", "view"),
                questionary.Choice("Validate", "validate"),
                questionary.Choice("Delete version", "delete"),
                questionary.Choice("← Back", "back"),
            ]
        ).ask()
        
        if action == "back" or action is None:
            return
        
        if action == "add":
            _add_questions_to_version(version_id)
        elif action == "remove":
            _remove_question_from_version(version_id)
        elif action == "view":
            _view_version_questions(version_id)
        elif action == "validate":
            validator = VersionValidator()
            result = validator.validate(version_id)
            _display_validation_result(result)
        elif action == "delete":
            if questionary.confirm("Delete this version?", default=False).ask():
                if builder.delete_version(version_id):
                    console.print("[red]Version deleted.[/red]")
                    return


def _add_questions_to_version(version_id: int) -> None:
    """Add questions to a version."""
    builder = VersionBuilder()
    
    method = questionary.select(
        "Add questions by:",
        choices=[
            questionary.Choice("Add all locked questions (recommended)", "locked"),
            questionary.Choice("Add all approved questions", "approved"),
            questionary.Choice("Add by category", "category"),
            questionary.Choice("← Back", "back"),
        ]
    ).ask()
    
    if method == "back" or method is None:
        return
    
    if method == "locked":
        added = builder.add_locked_questions(version_id)
        console.print(f"[green]✓ Added {added} locked questions.[/green]")
    elif method == "approved":
        added = builder.add_approved_questions(version_id)
        console.print(f"[green]✓ Added {added} approved questions.[/green]")
    elif method == "category":
        cat_choices = [
            questionary.Choice(f"{c.id} {c.name}", c.id)
            for c in sorted(CATEGORIES.values(), key=lambda x: x.id)
        ]
        category = questionary.select("Select category:", choices=cat_choices).ask()
        
        if category:
            added = builder.add_questions_by_category(version_id, category)
            console.print(f"[green]✓ Added {added} questions from {category}.[/green]")
    
    # Show updated stats
    _display_version_stats(version_id)


def _remove_question_from_version(version_id: int) -> None:
    """Remove a question from a version."""
    question_id = questionary.text(
        "Enter question ID to remove:",
        validate=lambda x: x.isdigit(),
    ).ask()
    
    if question_id:
        builder = VersionBuilder()
        if builder.remove_question(version_id, int(question_id)):
            console.print(f"[yellow]Question #{question_id} removed.[/yellow]")
        else:
            console.print(f"[red]Question #{question_id} not found in version.[/red]")


def _view_version_questions(version_id: int) -> None:
    """View questions in a version."""
    builder = VersionBuilder()
    questions = builder.get_version_questions(version_id)
    
    if not questions:
        console.print("[dim]No questions in this version.[/dim]")
        return
    
    table = Table(title=f"Questions in Version ({len(questions)} total)")
    table.add_column("ID", width=5)
    table.add_column("Content", width=50, no_wrap=True)
    table.add_column("Cat", width=4)
    table.add_column("🔒", width=2)
    
    for q in questions[:50]:  # Limit display
        content_preview = q.content[:47] + "..." if len(q.content) > 50 else q.content
        content_preview = content_preview.replace("\n", " ")
        table.add_row(
            str(q.id),
            content_preview,
            q.category,
            "🔒" if q.locked else "",
        )
    
    console.print(table)
    
    if len(questions) > 50:
        console.print(f"[dim]Showing 50 of {len(questions)} questions.[/dim]")


def _interactive_validate_version() -> None:
    """Validate a version interactively."""
    builder = VersionBuilder()
    versions = builder.list_versions()
    
    if not versions:
        console.print("[dim]No versions found.[/dim]")
        return
    
    choices = [
        questionary.Choice(f"v{v.version} - {v.name} ({v.status})", v.id)
        for v in versions
    ]
    choices.append(questionary.Choice("← Back", None))
    
    version_id = questionary.select("Select version to validate:", choices=choices).ask()
    
    if not version_id:
        return
    
    _display_version_stats(version_id)
    
    validator = VersionValidator()
    result = validator.validate(version_id)
    _display_validation_result(result)


# Typer commands for non-interactive use

@app.command("create")
def create_command(
    version: str = typer.Option(..., "--version", "-v", help="Version number"),
    name: str = typer.Option(..., "--name", "-n", help="Version name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Description"),
) -> None:
    """Create a new benchmark version."""
    init_db()
    builder = VersionBuilder()
    
    try:
        v = builder.create_version(version, name, description)
        console.print(f"[green]✓ Version v{v.version} created.[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_command() -> None:
    """List all benchmark versions."""
    init_db()
    _interactive_list_versions()


@app.command("add-questions")
def add_questions_command(
    version_id: int = typer.Argument(..., help="Version ID"),
    locked: bool = typer.Option(False, "--locked", "-l", help="Add only locked questions"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Add from category"),
) -> None:
    """Add questions to a version."""
    init_db()
    builder = VersionBuilder()
    
    if locked:
        added = builder.add_locked_questions(version_id)
    elif category:
        added = builder.add_questions_by_category(version_id, category)
    else:
        added = builder.add_approved_questions(version_id)
    
    console.print(f"[green]✓ Added {added} questions.[/green]")


@app.command("validate")
def validate_command(
    version_id: int = typer.Argument(..., help="Version ID"),
) -> None:
    """Validate a version."""
    init_db()
    
    _display_version_stats(version_id)
    
    validator = VersionValidator()
    result = validator.validate(version_id)
    _display_validation_result(result)
    
    if not result.is_valid:
        raise typer.Exit(1)


@app.command("publish")
def publish_command(
    version_id: int = typer.Argument(..., help="Version ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip validation"),
) -> None:
    """Publish a version."""
    init_db()
    
    publisher = VersionPublisher()
    
    success, message = publisher.lock_version(version_id, force=force)
    if not success:
        console.print(f"[red]Lock failed: {message}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]✓ Version locked[/green]")
    
    success, message = publisher.publish_version(version_id)
    if success:
        console.print(f"[green]✓ {message}[/green]")
    else:
        console.print(f"[red]Publish failed: {message}[/red]")
        raise typer.Exit(1)
