#!/usr/bin/env python3
"""
Interactive CLI wizard for running the Great Commission Benchmark pipeline.

Usage:
    python pipeline.py              # Auto-run all steps
    python pipeline.py --interactive  # Show interactive menu

This wizard guides you through each step of the benchmark process:
1. Prepare: Export questions to PromptFoo format
2. Execute: Run PromptFoo evaluation
3. Import: Import results into database
4. Evaluate: Use LLM to judge responses
5. Report: Generate benchmark statistics

Note: Database must be initialized separately using 'python -m gcb init'
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gcb.database import (
    get_db,
    AcceptanceLevel,
    PromptType,
)
from gcb.promptfoo_bridge import PromptFooBridge
from gcb.evaluator import Evaluator
from gcb.reporter import BenchmarkReporter

app = typer.Typer(
    name="pipeline",
    help="Great Commission Benchmark Pipeline Wizard",
    add_completion=False,
)
console = Console()


class PipelineWizard:
    """Interactive wizard for running benchmark pipeline steps."""
    
    def __init__(
        self,
        questions_db_path: str = "questions.db",
        responses_db_path: str = "responses.db",
        config_path: str = "config.yaml",
        output_dir: str = "prompts",
        results_dir: str = "output",
    ):
        self.questions_db_path = Path(questions_db_path)
        self.responses_db_path = Path(responses_db_path)
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.results_dir = Path(results_dir)
        self.db = None
        
    def show_banner(self):
        """Display welcome banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║     Great Commission Benchmark - Pipeline Wizard             ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
        
    def show_menu(self) -> str:
        """Display main menu and get user choice."""
        table = Table(title="Pipeline Steps", box=box.ROUNDED, show_header=True)
        table.add_column("Step", style="cyan", width=8)
        table.add_column("Action", style="white", width=30)
        table.add_column("Description", style="dim", width=40)
        
        table.add_row("1", "Prepare", "Export questions to PromptFoo format")
        table.add_row("2", "Execute", "Run PromptFoo evaluation")
        table.add_row("3", "Import", "Import results into database")
        table.add_row("4", "Evaluate", "Use LLM to judge responses")
        table.add_row("5", "Report", "Generate benchmark statistics")
        table.add_row("A", "Run All", "Execute all steps sequentially (default)")
        table.add_row("S", "Status", "Show current pipeline status")
        table.add_row("Q", "Quit", "Exit the wizard")
        
        console.print("\n")
        console.print(table)
        console.print("\n")
        
        choice = Prompt.ask(
            "Select a step to run",
            choices=["1", "2", "3", "4", "5", "A", "a", "S", "s", "Q", "q"],
            default="A"
        ).upper()
        
        return choice
    
    def check_prerequisites(self) -> dict:
        """Check prerequisites and return status."""
        status = {
            "database_exists": self.questions_db_path.exists() and self.responses_db_path.exists(),
            "config_exists": self.config_path.exists(),
            "promptfoo_available": False,
            "questions_count": 0,
        }
        
        # Check database
        if status["database_exists"]:
            try:
                self.db = get_db(str(self.questions_db_path), str(self.responses_db_path))
                stats = self.db.get_stats()
                status["questions_count"] = stats["questions"]
            except Exception as e:
                console.print(f"[yellow]Warning: Database exists but may be corrupted: {e}[/yellow]")
        
        # Check PromptFoo
        try:
            result = subprocess.run(
                ["npx", "promptfoo@latest", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            status["promptfoo_available"] = result.returncode == 0
        except Exception:
            status["promptfoo_available"] = False
        
        return status
    
    def show_status(self):
        """Show current pipeline status."""
        status = self.check_prerequisites()
        
        table = Table(title="Pipeline Status", box=box.ROUNDED)
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Status", width=15)
        table.add_column("Details", style="dim")
        
        # Database
        if status["database_exists"]:
            table.add_row(
                "Database",
                "[green]✓ Ready[/green]",
                f"{status['questions_count']} questions"
            )
        else:
            table.add_row(
                "Database",
                "[yellow]⚠ Missing[/yellow]",
"Initialize using 'python -m gcb init'"
            )
        
        # Config
        if status["config_exists"]:
            table.add_row(
                "Configuration",
                "[green]✓ Ready[/green]",
                str(self.config_path)
            )
        else:
            table.add_row(
                "Configuration",
                "[yellow]⚠ Missing[/yellow]",
                "Create config.yaml"
            )
        
        # PromptFoo
        if status["promptfoo_available"]:
            table.add_row(
                "PromptFoo",
                "[green]✓ Ready[/green]",
                "Available via npx"
            )
        else:
            table.add_row(
                "PromptFoo",
                "[yellow]⚠ Missing[/yellow]",
                "Install Node.js and run: npx promptfoo@latest --version"
            )
        
        # Check for exported files
        promptfoo_file = self.output_dir / "promptfoo.yaml"
        if promptfoo_file.exists():
            table.add_row(
                "PromptFoo Export",
                "[green]✓ Ready[/green]",
                str(promptfoo_file)
            )
        else:
            table.add_row(
                "PromptFoo Export",
                "[dim]○ Not created[/dim]",
                "Run step 2 to export"
            )
        
        # Check for results
        results_file = self.output_dir / "results.json"
        if results_file.exists():
            table.add_row(
                "Results File",
                "[green]✓ Ready[/green]",
                str(results_file)
            )
        else:
            table.add_row(
                "Results File",
                "[dim]○ Not created[/dim]",
                "Run step 3 to generate"
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n")
    
    def step_prepare(self) -> bool:
        """Step 1: Export questions to PromptFoo format."""
        console.print("\n[bold cyan]Step 1: Prepare - Export Questions[/bold cyan]")
        console.print("=" * 60)
        
        # Check database
        if not self.questions_db_path.exists() or not self.responses_db_path.exists():
            console.print("[red]✗ Database not found. Please initialize the database first using 'python -m gcb init'[/red]")
            return False
        
        if self.db is None:
            self.db = get_db(str(self.questions_db_path), str(self.responses_db_path))
        
        stats = self.db.get_stats()
        if stats["questions"] == 0:
            console.print("[yellow]⚠ No questions found in database.[/yellow]")
            console.print("   Add questions using the UI: streamlit run ui/app.py")
            if not Confirm.ask("Continue anyway?"):
                return False
        
        # Show current config
        bridge = PromptFooBridge(
            str(self.questions_db_path),
            str(self.responses_db_path),
            str(self.output_dir),
            str(self.config_path)
        )
        
        llm_config = bridge.get_llm_config()
        console.print("\n[cyan]Current Configuration:[/cyan]")
        console.print(f"   Model: {llm_config.get('test_model')}")
        console.print(f"   Provider: {bridge.config.get('llm', {}).get('provider', 'lmstudio')}")
        console.print(f"   Base URL: {llm_config.get('base_url')}")
        
        # Ask if user wants to override
        override_model = None
        override_provider = None
        override_base_url = None
        override_api_key = None
        
        if Confirm.ask("\nDo you want to override model settings?", default=False):
            override_model = Prompt.ask("Model name", default=llm_config.get('test_model'))
            override_provider = Prompt.ask("Provider (lmstudio/openrouter)", default=bridge.config.get('llm', {}).get('provider', 'lmstudio'))
            override_base_url = Prompt.ask("Base URL", default=llm_config.get('base_url'))
            if Confirm.ask("Override API Key?", default=False):
                override_api_key = Prompt.ask("API Key", password=True)
            else:
                override_api_key = None
        
        # Ask for filters
        level_filter = None
        type_filter = None
        
        if Confirm.ask("\nDo you want to filter questions?", default=False):
            level_choice = Prompt.ask(
                "Acceptance level (green/orange/red)",
                choices=["green", "orange", "red", ""],
                default=""
            )
            if level_choice:
                level_filter = AcceptanceLevel(level_choice)
            
            type_choice = Prompt.ask(
                "Prompt type (direct/roleplay/encoded/multiturn)",
                choices=["direct", "roleplay", "encoded", "multiturn", ""],
                default=""
            )
            if type_choice:
                type_filter = PromptType(type_choice)
        
        try:
            path = bridge.export_questions(
                level_filter=level_filter,
                type_filter=type_filter,
                model_override=override_model,
                provider_override=override_provider,
                base_url_override=override_base_url,
                api_key_override=override_api_key,
            )
            console.print(f"\n[green]✓ Exported to: {path}[/green]")
            console.print(f"   Total questions exported: {stats['questions']}")
            return True
        except Exception as e:
            console.print(f"\n[red]✗ Export failed: {e}[/red]")
            return False
    
    def step_execute(self) -> bool:
        """Step 2: Run PromptFoo evaluation."""
        console.print("\n[bold cyan]Step 2: Execute - Run PromptFoo Evaluation[/bold cyan]")
        console.print("=" * 60)
        
        promptfoo_file = self.output_dir / "promptfoo.yaml"
        if not promptfoo_file.exists():
            console.print(f"[red]✗ PromptFoo file not found: {promptfoo_file}[/red]")
            console.print("   Run step 1 first to export questions.")
            return False
        
        # Check PromptFoo availability
        try:
            result = subprocess.run(
                ["npx", "promptfoo@latest", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise Exception("PromptFoo not available")
        except Exception as e:
            console.print(f"[red]✗ PromptFoo not available: {e}[/red]")
            console.print("   Install Node.js and ensure 'npx' is available.")
            return False
        
        console.print(f"\n[cyan]Running PromptFoo evaluation...[/cyan]")
        console.print(f"   Config file: {promptfoo_file}")
        console.print("\n[yellow]This may take a while depending on the number of questions...[/yellow]\n")
        
        if not Confirm.ask("Continue with evaluation?", default=True):
            return False
        
        try:
            bridge = PromptFooBridge(
                str(self.questions_db_path),
                str(self.responses_db_path),
                str(self.output_dir),
                str(self.config_path)
            )
            success, message = bridge.run_promptfoo(verbose=True)
            
            if success:
                console.print(f"\n[green]✓ {message}[/green]")
                return True
            else:
                console.print(f"\n[red]✗ {message}[/red]")
                return False
        except Exception as e:
            console.print(f"\n[red]✗ Evaluation failed: {e}[/red]")
            return False
    
    def step_import(self) -> bool:
        """Step 3: Import results into database."""
        console.print("\n[bold cyan]Step 3: Import - Import Results[/bold cyan]")
        console.print("=" * 60)
        
        results_file = self.output_dir / "results.json"
        if not results_file.exists():
            console.print(f"[red]✗ Results file not found: {results_file}[/red]")
            console.print("   Run step 2 first to generate results.")
            return False
        
        if self.db is None:
            self.db = get_db(str(self.questions_db_path), str(self.responses_db_path))
        
        bridge = PromptFooBridge(
            str(self.questions_db_path),
            str(self.responses_db_path),
            str(self.output_dir),
            str(self.config_path)
        )
        
        # Get model name
        llm_config = bridge.get_llm_config()
        default_model = llm_config.get("test_model", "local-model")
        
        console.print(f"\n[cyan]Current model from config: {default_model}[/cyan]")
        model_name = Prompt.ask(
            "Model name for this test run",
            default=default_model
        )
        
        try:
            console.print("\n[cyan]Importing results...[/cyan]")
            imported, errors = bridge.import_results("results.json", model_name)
            
            console.print(f"\n[green]✓ Imported {imported} responses[/green]")
            
            if errors:
                console.print(f"\n[yellow]⚠ {len(errors)} errors occurred:[/yellow]")
                for err in errors[:5]:
                    console.print(f"   - {err}")
                if len(errors) > 5:
                    console.print(f"   ... and {len(errors) - 5} more")
            
            return True
        except Exception as e:
            console.print(f"\n[red]✗ Import failed: {e}[/red]")
            return False
    
    def step_evaluate(self) -> bool:
        """Step 4: Evaluate responses using LLM judge."""
        console.print("\n[bold cyan]Step 4: Evaluate - Judge Responses[/bold cyan]")
        console.print("=" * 60)
        
        if self.db is None:
            self.db = get_db(str(self.questions_db_path), str(self.responses_db_path))
        
        # Check if there are responses to evaluate
        stats = self.db.get_stats()
        if stats["responses"] == 0:
            console.print("[yellow]⚠ No responses found in database.[/yellow]")
            console.print("   Run step 4 first to import results.")
            return False
        
        evaluator = Evaluator(str(self.questions_db_path), str(self.responses_db_path), str(self.config_path))
        
        # Check if some responses are already evaluated
        with self.db.get_session() as session:
            from gcb.database import Response, Evaluation
            total_responses = session.query(Response).count()
            evaluated_count = session.query(Evaluation).count()
        
        if evaluated_count > 0:
            console.print(f"\n[cyan]Found {evaluated_count} already evaluated responses out of {total_responses}[/cyan]")
            force = Confirm.ask("Re-evaluate existing responses?", default=False)
        else:
            force = False
        
        console.print("\n[yellow]This may take a while depending on the number of responses...[/yellow]")
        
        if not Confirm.ask("Continue with evaluation?", default=True):
            return False
        
        try:
            console.print("\n[cyan]Evaluating responses...[/cyan]")
            evaluated, skipped, errors = evaluator.evaluate_test_run(
                test_run_id=None,
                skip_evaluated=not force,
            )
            
            console.print(f"\n[green]✓ Evaluated: {evaluated}[/green]")
            if skipped > 0:
                console.print(f"[yellow]  Skipped: {skipped}[/yellow]")
            
            if errors:
                console.print(f"\n[yellow]⚠ {len(errors)} errors occurred:[/yellow]")
                for err in errors[:5]:
                    console.print(f"   - {err}")
                if len(errors) > 5:
                    console.print(f"   ... and {len(errors) - 5} more")
            
            return True
        except Exception as e:
            console.print(f"\n[red]✗ Evaluation failed: {e}[/red]")
            return False
    
    def step_report(self) -> bool:
        """Step 5: Generate benchmark report."""
        console.print("\n[bold cyan]Step 5: Report - Generate Statistics[/bold cyan]")
        console.print("=" * 60)
        
        if self.db is None:
            self.db = get_db(str(self.questions_db_path), str(self.responses_db_path))
        
        reporter = BenchmarkReporter(str(self.questions_db_path), str(self.responses_db_path), str(self.results_dir))
        
        # Check if there are evaluations
        stats = self.db.get_stats()
        if stats["evaluations"] == 0:
            console.print("[yellow]⚠ No evaluations found in database.[/yellow]")
            console.print("   Run step 4 first to evaluate responses.")
            return False
        
        format_choice = Prompt.ask(
            "\nReport format",
            choices=["markdown", "json", "detailed"],
            default="markdown"
        )
        
        try:
            console.print(f"\n[cyan]Generating {format_choice} report...[/cyan]")
            
            if format_choice == "json":
                path = reporter.generate_json_report()
            elif format_choice == "detailed":
                path = reporter.generate_detailed_results()
            else:
                path = reporter.generate_markdown_report()
            
            console.print(f"\n[green]✓ Report generated: {path}[/green]")
            
            # Show summary
            summary = reporter.get_summary_stats()
            
            table = Table(title="Benchmark Summary", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green", justify="right")
            
            table.add_row("Questions", str(summary["total_questions"]))
            table.add_row("Responses", str(summary["total_responses"]))
            table.add_row("Evaluations", str(summary["total_evaluations"]))
            table.add_row("Models", str(summary["total_models"]))
            table.add_row("Test Runs", str(summary["total_test_runs"]))
            
            console.print("\n")
            console.print(table)
            
            if summary["verdict_counts"]:
                console.print("\n[bold]Verdicts:[/bold]")
                for verdict, count in summary["verdict_counts"].items():
                    emoji = {"approved": "✅", "refused": "❌", "ambiguous": "⚠️"}.get(verdict, "•")
                    console.print(f"   {emoji} {verdict}: {count}")
            
            return True
        except Exception as e:
            console.print(f"\n[red]✗ Report generation failed: {e}[/red]")
            return False
    
    def run_all(self) -> bool:
        """Run all pipeline steps sequentially."""
        console.print("\n[bold cyan]Running All Pipeline Steps[/bold cyan]")
        console.print("=" * 60)
        
        steps = [
            ("Prepare", self.step_prepare),
            ("Execute", self.step_execute),
            ("Import", self.step_import),
            ("Evaluate", self.step_evaluate),
            ("Report", self.step_report),
        ]
        
        results = {}
        
        for name, step_func in steps:
            console.print(f"\n[bold yellow]Running: {name}[/bold yellow]")
            try:
                success = step_func()
                results[name] = success
                
                if not success:
                    console.print(f"\n[red]Step '{name}' failed. Stopping pipeline.[/red]")
                    if not Confirm.ask("Continue with remaining steps anyway?", default=False):
                        break
            except KeyboardInterrupt:
                console.print("\n[yellow]Pipeline interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Unexpected error in '{name}': {e}[/red]")
                results[name] = False
                if not Confirm.ask("Continue with remaining steps anyway?", default=False):
                    break
        
        # Summary
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]Pipeline Summary[/bold cyan]\n")
        
        summary_table = Table(box=box.ROUNDED)
        summary_table.add_column("Step", style="cyan")
        summary_table.add_column("Status", width=15)
        
        for name, success in results.items():
            if success:
                summary_table.add_row(name, "[green]✓ Success[/green]")
            else:
                summary_table.add_row(name, "[red]✗ Failed[/red]")
        
        console.print(summary_table)
        
        all_success = all(results.values())
        return all_success
    
    def run(self, interactive: bool = False):
        """Main wizard loop.
        
        Args:
            interactive: If True, show interactive menu. If False, auto-run all steps.
        """
        self.show_banner()
        
        # Auto-run all steps by default
        if not interactive:
            try:
                self.run_all()
                return
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Pipeline interrupted by user. Exiting...[/yellow]")
                return
            except Exception as e:
                console.print(f"\n[red]Unexpected error: {e}[/red]")
                return
        
        # Interactive mode
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "Q":
                    console.print("\n[yellow]Exiting wizard. Goodbye![/yellow]")
                    break
                elif choice == "S":
                    self.show_status()
                elif choice == "A":
                    self.run_all()
                elif choice == "1":
                    self.step_prepare()
                elif choice == "2":
                    self.step_execute()
                elif choice == "3":
                    self.step_import()
                elif choice == "4":
                    self.step_evaluate()
                elif choice == "5":
                    self.step_report()
                
                # Pause before showing menu again
                if choice != "Q":
                    console.print("\n")
                    Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                    
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Unexpected error: {e}[/red]")
                if not Confirm.ask("Continue?", default=True):
                    break


@app.command()
def main(
    questions_db: str = typer.Option("questions.db", "--questions-db", help="Questions database file path"),
    responses_db: str = typer.Option("responses.db", "--responses-db", help="Responses database file path"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Config file path"),
    output_dir: str = typer.Option("prompts", "--output", "-o", help="Output directory"),
    results_dir: str = typer.Option("output", "--results", "-r", help="Results directory"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Show interactive menu instead of auto-running"),
):
    """Run the Great Commission Benchmark pipeline wizard.
    
    By default, runs all pipeline steps automatically.
    Use --interactive to show the menu instead.
    """
    wizard = PipelineWizard(
        questions_db_path=questions_db,
        responses_db_path=responses_db,
        config_path=config_path,
        output_dir=output_dir,
        results_dir=results_dir,
    )
    wizard.run(interactive=interactive)


if __name__ == "__main__":
    app()

