"""
CLI commands for question curation.

Provides functionality for:
- Listing and filtering questions
- Reviewing individual questions
- Approving and locking questions
- Bulk operations with lock protection
"""

from datetime import datetime
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import func, select

from gcb_builder.core.categories import CATEGORIES
from gcb_builder.core.database import get_db, init_db
from gcb_builder.core.models import Question

app = typer.Typer(help="Question curation commands")
console = Console()


def _show_question_detail(question: Question) -> None:
    """Display detailed view of a question."""
    lock_status = "🔒 LOCKED" if question.locked else ""
    
    content = f"""[bold]Question #{question.id}[/bold] {lock_status}
    
[bold]Category:[/bold] {question.category} {CATEGORIES.get(question.category, 'Unknown').name if question.category in CATEGORIES else ''}
[bold]Tier:[/bold] {question.tier} | [bold]Difficulty:[/bold] {question.difficulty} | [bold]Status:[/bold] {question.status}
{"[bold]Locked:[/bold] " + str(question.locked_at) + " by " + (question.locked_by or "unknown") if question.locked else ""}

[bold]Expected Verdict:[/bold] {question.expected_verdict}
{"[bold]Refusal Type:[/bold] " + question.expected_refusal_type if question.expected_refusal_type else ""}
[bold]Tests:[/bold] {'✓ Capability' if question.tests_capability else '✗ Capability'}  {'✓ Willingness' if question.tests_willingness else '✗ Willingness'}

[bold]Use Cases:[/bold] {question.use_case_tags or 'None'}
[bold]Audience:[/bold] {question.audience_context or 'None'}
[bold]Ministry:[/bold] {question.ministry_type or 'None'}

[bold]Content:[/bold]
{question.content}

{"[bold]Notes:[/bold] " + question.notes if question.notes else ""}
"""
    console.print(Panel(content, title=f"Question #{question.id}"))


def _list_questions(
    status: Optional[str] = None,
    category: Optional[str] = None,
    tier: Optional[int] = None,
    locked_only: bool = False,
    limit: int = 25,
) -> list[Question]:
    """List questions with optional filters."""
    with get_db() as db:
        query = select(Question)
        
        if status:
            query = query.where(Question.status == status)
        if category:
            query = query.where(Question.category == category)
        if tier:
            query = query.where(Question.tier == tier)
        if locked_only:
            query = query.where(Question.locked == True)
        
        query = query.order_by(Question.created_at.desc()).limit(limit)
        
        results = list(db.scalars(query).all())
        
        # Make transient
        from sqlalchemy.orm import make_transient
        for q in results:
            make_transient(q)
            _ = q.id, q.content, q.category, q.status, q.locked
        
        return results


def _display_question_table(questions: list[Question]) -> None:
    """Display questions in a table format."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", width=5)
    table.add_column("Content", width=50, no_wrap=True)
    table.add_column("Cat", width=4)
    table.add_column("Status", width=8)
    table.add_column("🔒", width=2)
    table.add_column("Cap", width=3)
    table.add_column("Wil", width=3)
    
    for q in questions:
        content_preview = q.content[:47] + "..." if len(q.content) > 50 else q.content
        content_preview = content_preview.replace("\n", " ")
        table.add_row(
            str(q.id),
            content_preview,
            q.category,
            q.status,
            "🔒" if q.locked else "",
            "✓" if q.tests_capability else "",
            "✓" if q.tests_willingness else "",
        )
    
    console.print(table)
    console.print(f"\n[dim]Showing {len(questions)} questions. Legend: Cap=Capability, Wil=Willingness[/dim]")


def _approve_question(question_id: int) -> bool:
    """Approve a question."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if question.locked:
            console.print("[yellow]Question is locked. Unlock first to modify.[/yellow]")
            return False
        question.status = "approved"
        db.commit()
        return True


def _lock_question(question_id: int, locked_by: str = "cli") -> bool:
    """Lock an approved question."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if question.status != "approved":
            console.print("[yellow]Only approved questions can be locked.[/yellow]")
            return False
        if question.locked:
            console.print("[yellow]Question is already locked.[/yellow]")
            return False
        question.locked = True
        question.locked_at = datetime.utcnow()
        question.locked_by = locked_by
        db.commit()
        return True


def _unlock_question(question_id: int) -> bool:
    """Unlock a locked question."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if not question.locked:
            console.print("[yellow]Question is not locked.[/yellow]")
            return False
        question.locked = False
        question.locked_at = None
        question.locked_by = None
        db.commit()
        return True


def _retire_question(question_id: int) -> bool:
    """Retire a question."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if question.locked:
            console.print("[yellow]Question is locked. Unlock first to retire.[/yellow]")
            return False
        question.status = "retired"
        db.commit()
        return True


def _delete_question(question_id: int) -> bool:
    """Delete a question (only drafts and reviews, not locked)."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if question.locked:
            console.print("[red]Cannot delete locked question.[/red]")
            return False
        if question.status not in ("draft", "review"):
            console.print("[yellow]Only draft and review questions can be deleted.[/yellow]")
            return False
        db.delete(question)
        db.commit()
        return True


def _update_question_status(question_id: int, new_status: str) -> bool:
    """Update question status."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            return False
        if question.locked:
            console.print("[yellow]Question is locked. Unlock first to modify.[/yellow]")
            return False
        question.status = new_status
        db.commit()
        return True


def interactive_curate() -> None:
    """Run the interactive curation wizard."""
    init_db()
    
    console.print()
    console.print("[bold]Question Curation[/bold]")
    console.print("[dim]Review, approve, and lock questions[/dim]")
    console.print()
    
    while True:
        # Main menu
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("List questions", "list"),
                questionary.Choice("View specific question", "view"),
                questionary.Choice("Bulk operations", "bulk"),
                questionary.Choice("← Back to main menu", "back"),
            ]
        ).ask()
        
        if choice == "back" or choice is None:
            return
        
        if choice == "list":
            _interactive_list()
        elif choice == "view":
            _interactive_view()
        elif choice == "bulk":
            _interactive_bulk()


def _interactive_list() -> None:
    """Interactive question listing."""
    # Filter options
    filter_choice = questionary.select(
        "Filter by:",
        choices=[
            questionary.Choice("Status (draft/review/approved/retired)", "status"),
            questionary.Choice("Locked questions only", "locked"),
            questionary.Choice("Category", "category"),
            questionary.Choice("Tier", "tier"),
            questionary.Choice("Show all (last 25)", "all"),
        ]
    ).ask()
    
    if filter_choice is None:
        return
    
    status = None
    category = None
    tier = None
    locked_only = False
    
    if filter_choice == "status":
        status = questionary.select(
            "Select status:",
            choices=["draft", "review", "approved", "retired"]
        ).ask()
    elif filter_choice == "locked":
        locked_only = True
    elif filter_choice == "category":
        cat_choices = [questionary.Choice(f"{c.id} {c.name}", c.id) for c in sorted(CATEGORIES.values(), key=lambda x: x.id)]
        category = questionary.select("Select category:", choices=cat_choices).ask()
    elif filter_choice == "tier":
        tier = questionary.select("Select tier:", choices=[1, 2, 3]).ask()
    
    questions = _list_questions(
        status=status,
        category=category,
        tier=tier,
        locked_only=locked_only,
    )
    
    if not questions:
        console.print("[dim]No questions found matching filters.[/dim]")
        return
    
    _display_question_table(questions)
    
    # Offer to view a specific question
    view_id = questionary.text(
        "Enter question ID to view details (or press Enter to skip):",
    ).ask()
    
    if view_id and view_id.isdigit():
        _view_and_act_on_question(int(view_id))


def _interactive_view() -> None:
    """View and act on a specific question."""
    question_id = questionary.text(
        "Enter question ID:",
        validate=lambda x: x.isdigit(),
    ).ask()
    
    if question_id:
        _view_and_act_on_question(int(question_id))


def _view_and_act_on_question(question_id: int) -> None:
    """View a question and offer actions."""
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            console.print(f"[red]Question #{question_id} not found.[/red]")
            return
        
        from sqlalchemy.orm import make_transient
        make_transient(question)
        _ = question.id, question.content, question.category, question.status, question.locked
    
    _show_question_detail(question)
    
    # Build action choices based on question state
    choices = [questionary.Choice("View full content", "content")]
    
    if not question.locked:
        if question.status == "draft":
            choices.extend([
                questionary.Choice("Move to review", "review"),
                questionary.Choice("Approve directly", "approve"),
                questionary.Choice("Delete", "delete"),
            ])
        elif question.status == "review":
            choices.extend([
                questionary.Choice("Approve", "approve"),
                questionary.Choice("Return to draft", "draft"),
                questionary.Choice("Delete", "delete"),
            ])
        elif question.status == "approved":
            choices.extend([
                questionary.Choice("🔒 Lock question", "lock"),
                questionary.Choice("Retire", "retire"),
            ])
        elif question.status == "retired":
            choices.append(questionary.Choice("Restore to draft", "draft"))
    else:
        choices.append(questionary.Choice("🔓 Unlock question", "unlock"))
    
    choices.append(questionary.Choice("← Back", "back"))
    
    action = questionary.select("Action:", choices=choices).ask()
    
    if action == "back" or action is None:
        return
    
    if action == "content":
        console.print(Panel(question.content, title="Full Content"))
        return
    
    if action == "approve":
        if _approve_question(question_id):
            console.print(f"[green]✓ Question #{question_id} approved.[/green]")
            if questionary.confirm("Lock this question?", default=True).ask():
                if _lock_question(question_id):
                    console.print(f"[green]✓ Question #{question_id} locked.[/green]")
    elif action == "lock":
        if _lock_question(question_id):
            console.print(f"[green]✓ Question #{question_id} locked.[/green]")
    elif action == "unlock":
        if questionary.confirm("Unlock this question? It can then be edited or deleted.", default=False).ask():
            if _unlock_question(question_id):
                console.print(f"[yellow]Question #{question_id} unlocked.[/yellow]")
    elif action == "review":
        if _update_question_status(question_id, "review"):
            console.print(f"[green]✓ Question #{question_id} moved to review.[/green]")
    elif action == "draft":
        if _update_question_status(question_id, "draft"):
            console.print(f"[green]✓ Question #{question_id} returned to draft.[/green]")
    elif action == "retire":
        if _retire_question(question_id):
            console.print(f"[yellow]Question #{question_id} retired.[/yellow]")
    elif action == "delete":
        if questionary.confirm("Delete this question? This cannot be undone.", default=False).ask():
            if _delete_question(question_id):
                console.print(f"[red]Question #{question_id} deleted.[/red]")


def _interactive_bulk() -> None:
    """Bulk operations."""
    action = questionary.select(
        "Bulk operation:",
        choices=[
            questionary.Choice("Delete all draft questions", "delete_drafts"),
            questionary.Choice("Delete drafts in category", "delete_category_drafts"),
            questionary.Choice("Approve all review questions", "approve_reviews"),
            questionary.Choice("Lock all approved questions", "lock_approved"),
            questionary.Choice("← Back", "back"),
        ]
    ).ask()
    
    if action == "back" or action is None:
        return
    
    if action == "delete_drafts":
        _bulk_delete_drafts()
    elif action == "delete_category_drafts":
        _bulk_delete_category_drafts()
    elif action == "approve_reviews":
        _bulk_approve_reviews()
    elif action == "lock_approved":
        _bulk_lock_approved()


def _bulk_delete_drafts() -> None:
    """Delete all draft questions (respects locks)."""
    with get_db() as db:
        drafts = db.scalars(
            select(Question).where(Question.status == "draft")
        ).all()
        
        unlocked = [q for q in drafts if not q.locked]
        locked = [q for q in drafts if q.locked]
        
        console.print(f"\nFound {len(drafts)} draft questions:")
        console.print(f"  • {len(unlocked)} unlocked (will be deleted)")
        console.print(f"  • {len(locked)} locked (will be preserved)")
        
        if not unlocked:
            console.print("[dim]No unlocked drafts to delete.[/dim]")
            return
        
        if questionary.confirm(f"Delete {len(unlocked)} draft questions?", default=False).ask():
            for q in unlocked:
                db.delete(q)
            db.commit()
            console.print(f"[red]Deleted {len(unlocked)} draft questions.[/red]")
            if locked:
                console.print(f"[dim]{len(locked)} locked questions preserved.[/dim]")


def _bulk_delete_category_drafts() -> None:
    """Delete draft questions in a specific category."""
    cat_choices = [questionary.Choice(f"{c.id} {c.name}", c.id) for c in sorted(CATEGORIES.values(), key=lambda x: x.id)]
    category = questionary.select("Select category:", choices=cat_choices).ask()
    
    if not category:
        return
    
    with get_db() as db:
        drafts = db.scalars(
            select(Question).where(
                Question.status == "draft",
                Question.category == category
            )
        ).all()
        
        unlocked = [q for q in drafts if not q.locked]
        locked = [q for q in drafts if q.locked]
        
        cat_name = CATEGORIES[category].name
        console.print(f"\nFound {len(drafts)} draft questions in {category} {cat_name}:")
        console.print(f"  • {len(unlocked)} unlocked (will be deleted)")
        console.print(f"  • {len(locked)} locked (will be preserved)")
        
        if not unlocked:
            console.print("[dim]No unlocked drafts to delete.[/dim]")
            return
        
        if questionary.confirm(f"Delete {len(unlocked)} draft questions?", default=False).ask():
            for q in unlocked:
                db.delete(q)
            db.commit()
            console.print(f"[red]Deleted {len(unlocked)} draft questions.[/red]")


def _bulk_approve_reviews() -> None:
    """Approve all questions in review status."""
    with get_db() as db:
        reviews = db.scalars(
            select(Question).where(Question.status == "review")
        ).all()
        
        count = len(reviews)
        
        if not count:
            console.print("[dim]No questions in review status.[/dim]")
            return
        
        console.print(f"\nFound {count} questions in review status.")
        
        if questionary.confirm(f"Approve all {count} questions?", default=False).ask():
            for q in reviews:
                q.status = "approved"
            db.commit()
            console.print(f"[green]✓ Approved {count} questions.[/green]")


def _bulk_lock_approved() -> None:
    """Lock all approved questions."""
    with get_db() as db:
        approved = db.scalars(
            select(Question).where(
                Question.status == "approved",
                Question.locked == False
            )
        ).all()
        
        count = len(approved)
        
        if not count:
            console.print("[dim]No unlocked approved questions.[/dim]")
            return
        
        console.print(f"\nFound {count} unlocked approved questions.")
        
        if questionary.confirm(f"Lock all {count} questions?", default=False).ask():
            now = datetime.utcnow()
            for q in approved:
                q.locked = True
                q.locked_at = now
                q.locked_by = "bulk_lock"
            db.commit()
            console.print(f"[green]✓ Locked {count} questions.[/green]")


# Typer commands for non-interactive use

@app.command("list")
def list_command(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    tier: Optional[int] = typer.Option(None, "--tier", "-t", help="Filter by tier"),
    locked: bool = typer.Option(False, "--locked", "-l", help="Show only locked"),
    limit: int = typer.Option(25, "--limit", "-n", help="Max questions to show"),
) -> None:
    """List questions with optional filters."""
    init_db()
    questions = _list_questions(
        status=status,
        category=category,
        tier=tier,
        locked_only=locked,
        limit=limit,
    )
    
    if not questions:
        console.print("[dim]No questions found.[/dim]")
        return
    
    _display_question_table(questions)


@app.command("view")
def view_command(
    question_id: int = typer.Argument(..., help="Question ID to view"),
) -> None:
    """View details of a specific question."""
    init_db()
    with get_db() as db:
        question = db.get(Question, question_id)
        if not question:
            console.print(f"[red]Question #{question_id} not found.[/red]")
            raise typer.Exit(1)
        
        from sqlalchemy.orm import make_transient
        make_transient(question)
        _ = question.id, question.content
    
    _show_question_detail(question)


@app.command("approve")
def approve_command(
    question_id: int = typer.Argument(..., help="Question ID to approve"),
    lock: bool = typer.Option(False, "--lock", "-l", help="Also lock the question"),
) -> None:
    """Approve a question."""
    init_db()
    if _approve_question(question_id):
        console.print(f"[green]✓ Question #{question_id} approved.[/green]")
        if lock:
            if _lock_question(question_id):
                console.print(f"[green]✓ Question #{question_id} locked.[/green]")
    else:
        console.print(f"[red]Failed to approve question #{question_id}.[/red]")
        raise typer.Exit(1)


@app.command("lock")
def lock_command(
    question_id: int = typer.Argument(..., help="Question ID to lock"),
) -> None:
    """Lock an approved question."""
    init_db()
    if _lock_question(question_id):
        console.print(f"[green]✓ Question #{question_id} locked.[/green]")
    else:
        console.print(f"[red]Failed to lock question #{question_id}.[/red]")
        raise typer.Exit(1)


@app.command("unlock")
def unlock_command(
    question_id: int = typer.Argument(..., help="Question ID to unlock"),
) -> None:
    """Unlock a locked question."""
    init_db()
    if _unlock_question(question_id):
        console.print(f"[yellow]Question #{question_id} unlocked.[/yellow]")
    else:
        console.print(f"[red]Failed to unlock question #{question_id}.[/red]")
        raise typer.Exit(1)
