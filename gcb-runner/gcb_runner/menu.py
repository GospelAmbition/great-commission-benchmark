"""Interactive CLI menu for GCB Runner."""

import sys
from enum import Enum
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from gcb_runner import __version__
from gcb_runner.config import BackendConfig, Config, get_config_dir

console = Console()


class MenuAction(Enum):
    """Menu action results."""
    CONTINUE = "continue"
    BACK = "back"
    EXIT = "exit"


def clear_screen() -> None:
    """Clear the terminal screen."""
    console.clear()


def print_header() -> None:
    """Print the GCB Runner header."""
    header_text = Text()
    header_text.append("✝ ", style="bold yellow")
    header_text.append("Great Commission Benchmark", style="bold blue")
    header_text.append(" - Runner", style="bold cyan")
    header_text.append(f"\n   Version {__version__}", style="dim")
    
    console.print(Panel(
        header_text,
        border_style="blue",
        box=box.DOUBLE
    ))
    console.print()


def print_menu(title: str, options: list[tuple[str, str]], show_back: bool = True) -> None:
    """Print a menu with numbered options.
    
    Args:
        title: Menu title
        options: List of (key, description) tuples
        show_back: Whether to show the back/exit option
    """
    table = Table(
        title=title,
        box=box.ROUNDED,
        title_style="bold cyan",
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Key", style="bold green", width=4)
    table.add_column("Option", style="white")
    
    for key, description in options:
        table.add_row(f"[{key}]", description)
    
    if show_back:
        table.add_row("", "")  # Spacer
        table.add_row("[0]", "[dim]Back / Exit[/dim]")
    
    console.print(table)
    console.print()


def get_choice(valid_choices: list[str], prompt: str = "Select an option") -> str:
    """Get a validated user choice."""
    while True:
        choice = Prompt.ask(f"[bold]{prompt}[/bold]").strip().lower()
        if choice in valid_choices:
            return choice
        console.print(f"[red]Invalid choice. Please enter one of: {', '.join(valid_choices)}[/red]")


def show_status_panel(cfg: Config) -> None:
    """Show current configuration status."""
    status_items = []
    
    # Platform API
    if cfg.platform.api_key:
        status_items.append("✅ Platform API: [green]Configured[/green]")
    else:
        status_items.append("❌ Platform API: [red]Not configured[/red]")
    
    # Default backend
    backend = cfg.defaults.backend
    backend_cfg = cfg.get_backend_config(backend)
    
    if backend in ["lmstudio", "ollama"]:
        base_url = backend_cfg.base_url or ("http://localhost:1234/v1" if backend == "lmstudio" else "http://localhost:11434")
        status_items.append(f"🔧 Backend: [cyan]{backend}[/cyan] ({base_url})")
    elif backend_cfg.api_key:
        status_items.append(f"✅ Backend: [green]{backend}[/green] (API key set)")
    else:
        status_items.append(f"⚠️  Backend: [yellow]{backend}[/yellow] (no API key)")
    
    # Judge model
    judge_display = cfg.defaults.judge_model
    if cfg.defaults.judge_backend:
        judge_display += f" (via {cfg.defaults.judge_backend})"
    status_items.append(f"⚖️  Judge: [cyan]{judge_display}[/cyan]")
    
    console.print(Panel(
        "\n".join(status_items),
        title="[bold]Current Configuration[/bold]",
        border_style="dim",
        box=box.ROUNDED
    ))
    console.print()


# ============================================================================
# Setup Wizard
# ============================================================================

def setup_wizard() -> MenuAction:
    """Run the guided setup wizard."""
    clear_screen()
    print_header()
    
    console.print(Panel(
        "[bold]Welcome to the GCB Runner Setup Wizard![/bold]\n\n"
        "This wizard will help you configure everything needed to run\n"
        "the Great Commission Benchmark against AI models.\n\n"
        "[dim]You can always change these settings later from the main menu.[/dim]",
        border_style="green",
        box=box.DOUBLE
    ))
    console.print()
    
    if not Confirm.ask("Ready to begin setup?", default=True):
        return MenuAction.BACK
    
    cfg = Config.load()
    
    # Step 1: Platform API Key
    clear_screen()
    print_header()
    console.print("[bold cyan]Step 1 of 4: Platform API Key[/bold cyan]")
    console.print()
    console.print(Panel(
        "The Platform API key connects you to the GCB benchmark question bank\n"
        "and enables result submission.\n\n"
        "[bold]Get your API key from:[/bold]\n"
        "https://greatcommissionbenchmark.ai/dashboard",
        border_style="blue"
    ))
    console.print()
    
    platform_key = Prompt.ask(
        "Enter your Platform API key",
        default=cfg.platform.api_key or "",
        password=True
    )
    if platform_key:
        cfg.platform.api_key = platform_key
        console.print("[green]✓ Platform API key saved[/green]")
    else:
        console.print("[yellow]⚠ Skipped - you can add this later[/yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    # Step 2: Backend Selection
    clear_screen()
    print_header()
    console.print("[bold cyan]Step 2 of 4: Select AI Backend[/bold cyan]")
    console.print()
    
    backends_info = [
        ("openrouter", "OpenRouter", "Access 100+ models via single API (recommended)"),
        ("openai", "OpenAI", "Direct OpenAI API access"),
        ("anthropic", "Anthropic", "Direct Claude API access"),
        ("lmstudio", "LM Studio", "Local models via LM Studio"),
        ("ollama", "Ollama", "Local models via Ollama"),
    ]
    
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("#", style="bold green", width=3)
    table.add_column("Backend", style="cyan")
    table.add_column("Description")
    
    for i, (key, name, desc) in enumerate(backends_info, 1):
        marker = " ← current" if key == cfg.defaults.backend else ""
        table.add_row(str(i), name, desc + f"[dim]{marker}[/dim]")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask(
        "Select backend",
        default=str(backends_info.index((cfg.defaults.backend, 
                   next(b[1] for b in backends_info if b[0] == cfg.defaults.backend),
                   next(b[2] for b in backends_info if b[0] == cfg.defaults.backend))) + 1)
    )
    
    try:
        backend_idx = int(choice) - 1
        selected_backend = backends_info[backend_idx][0]
    except (ValueError, IndexError):
        selected_backend = cfg.defaults.backend
    
    cfg.defaults.backend = selected_backend
    console.print(f"[green]✓ Selected {selected_backend}[/green]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    # Step 3: Backend Configuration
    clear_screen()
    print_header()
    console.print("[bold cyan]Step 3 of 4: Configure Backend[/bold cyan]")
    console.print()
    
    if selected_backend in ["openrouter", "openai", "anthropic"]:
        api_urls = {
            "openrouter": "https://openrouter.ai/keys",
            "openai": "https://platform.openai.com/api-keys",
            "anthropic": "https://console.anthropic.com/settings/keys"
        }
        
        console.print(Panel(
            f"[bold]{selected_backend.title()} requires an API key.[/bold]\n\n"
            f"Get your API key from:\n{api_urls[selected_backend]}",
            border_style="blue"
        ))
        console.print()
        
        api_key = Prompt.ask(
            f"Enter your {selected_backend.title()} API key",
            default=cfg.get_backend_config(selected_backend).api_key or "",
            password=True
        )
        if api_key:
            cfg.set_backend_config(selected_backend, BackendConfig(api_key=api_key))
            console.print(f"[green]✓ {selected_backend.title()} API key saved[/green]")
        else:
            console.print("[yellow]⚠ Skipped - you'll need to add this before running tests[/yellow]")
    
    elif selected_backend == "lmstudio":
        console.print(Panel(
            "[bold]LM Studio Setup[/bold]\n\n"
            "1. Download LM Studio from https://lmstudio.ai/\n"
            "2. Load a model in LM Studio\n"
            "3. Start the local server (default port: 1234)\n\n"
            "[dim]Make sure LM Studio server is running before tests.[/dim]",
            border_style="blue"
        ))
        console.print()
        
        base_url = Prompt.ask(
            "LM Studio server URL",
            default=cfg.get_backend_config("lmstudio").base_url or "http://localhost:1234/v1"
        )
        cfg.set_backend_config("lmstudio", BackendConfig(base_url=base_url))
        console.print(f"[green]✓ LM Studio URL saved: {base_url}[/green]")
    
    elif selected_backend == "ollama":
        console.print(Panel(
            "[bold]Ollama Setup[/bold]\n\n"
            "1. Install Ollama from https://ollama.ai/\n"
            "2. Pull a model: ollama pull llama3.2\n"
            "3. Ollama runs automatically on port 11434\n\n"
            "[dim]Make sure Ollama is running before tests.[/dim]",
            border_style="blue"
        ))
        console.print()
        
        base_url = Prompt.ask(
            "Ollama server URL",
            default=cfg.get_backend_config("ollama").base_url or "http://localhost:11434"
        )
        cfg.set_backend_config("ollama", BackendConfig(base_url=base_url))
        console.print(f"[green]✓ Ollama URL saved: {base_url}[/green]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    # Step 4: Judge Model
    clear_screen()
    print_header()
    console.print("[bold cyan]Step 4 of 4: Select Judge Model[/bold cyan]")
    console.print()
    
    console.print(Panel(
        "The judge model evaluates AI responses for accuracy and faithfulness.\n\n"
        "[bold]Standard Judge:[/bold] openai/gpt-oss-20b ensures consistent scoring across all tests.\n\n"
        "[dim]The judge will use your configured backend (local or cloud).[/dim]",
        border_style="blue"
    ))
    console.print()
    
    judge_options = [
        ("openai/gpt-oss-20b", "openai/gpt-oss-20b (recommended)"),
        ("custom", "Custom model..."),
    ]
    
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("#", style="bold green", width=3)
    table.add_column("Model", style="cyan")
    
    for i, (_key, name) in enumerate(judge_options, 1):
        table.add_row(str(i), name)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("Select judge model", default="1")
    
    try:
        judge_idx = int(choice) - 1
        if judge_idx == 3:  # Custom
            custom_judge = Prompt.ask("Enter custom judge model name")
            cfg.defaults.judge_model = custom_judge
        else:
            cfg.defaults.judge_model = judge_options[judge_idx][0]
    except (ValueError, IndexError):
        cfg.defaults.judge_model = "openai/gpt-4o"
    
    console.print(f"[green]✓ Judge model set to: {cfg.defaults.judge_model}[/green]")
    
    # Save and finish
    cfg.save()
    
    console.print()
    clear_screen()
    print_header()
    
    console.print(Panel(
        "[bold green]✓ Setup Complete![/bold green]\n\n"
        f"Platform API: {'✅ Configured' if cfg.platform.api_key else '❌ Not set'}\n"
        f"Backend: {cfg.defaults.backend}\n"
        f"Judge Model: {cfg.defaults.judge_model}\n\n"
        f"Configuration saved to:\n{get_config_dir() / 'config.json'}",
        border_style="green",
        box=box.DOUBLE
    ))
    console.print()
    
    console.print("[bold]Next steps:[/bold]")
    console.print("  • Run a benchmark: [cyan]gcb-runner test --model gpt-4o[/cyan]")
    console.print("  • View results:    [cyan]gcb-runner results[/cyan]")
    console.print("  • Launch dashboard: [cyan]gcb-runner view[/cyan]")
    console.print()
    
    Prompt.ask("[dim]Press Enter to return to main menu[/dim]", default="")
    return MenuAction.BACK


# ============================================================================
# Configuration Menu
# ============================================================================

def config_menu() -> MenuAction:
    """Configuration settings menu."""
    while True:
        clear_screen()
        print_header()
        
        cfg = Config.load()
        show_status_panel(cfg)
        
        print_menu("⚙️  Configuration", [
            ("1", "Set Platform API Key"),
            ("2", "Configure Backend"),
            ("3", "Set Judge Model"),
            ("4", "View Current Config"),
            ("5", "Reset All Settings"),
            ("6", "Reset Results Database"),
        ])
        
        choice = get_choice(["0", "1", "2", "3", "4", "5", "6"])
        
        if choice == "0":
            return MenuAction.BACK
        elif choice == "1":
            configure_platform_key()
        elif choice == "2":
            configure_backend()
        elif choice == "3":
            configure_judge()
        elif choice == "4":
            view_config()
        elif choice == "5":
            reset_config()
        elif choice == "6":
            reset_database()


def configure_platform_key() -> None:
    """Configure the platform API key."""
    console.print()
    cfg = Config.load()
    
    console.print("[dim]Get your API key from: https://greatcommissionbenchmark.ai/dashboard[/dim]")
    console.print()
    
    platform_key = Prompt.ask(
        "Platform API key",
        default=cfg.platform.api_key or "",
        password=True
    )
    
    if platform_key:
        cfg.platform.api_key = platform_key
        cfg.save()
        console.print("[green]✓ Platform API key saved[/green]")
    else:
        console.print("[yellow]No changes made[/yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def configure_backend() -> None:
    """Configure the LLM backend."""
    console.print()
    cfg = Config.load()
    
    backends = ["openrouter", "openai", "anthropic", "lmstudio", "ollama"]
    
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("#", style="bold green", width=3)
    table.add_column("Backend", style="cyan")
    table.add_column("Status")
    
    for i, backend in enumerate(backends, 1):
        backend_cfg = cfg.get_backend_config(backend)
        if backend in ["lmstudio", "ollama"]:
            status = f"[dim]{backend_cfg.base_url or 'default URL'}[/dim]"
        elif backend_cfg.api_key:
            status = "[green]API key set[/green]"
        else:
            status = "[dim]not configured[/dim]"
        
        marker = " ← default" if backend == cfg.defaults.backend else ""
        table.add_row(str(i), backend + marker, status)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("Select backend to configure", default="1")
    
    try:
        backend_idx = int(choice) - 1
        selected_backend = backends[backend_idx]
    except (ValueError, IndexError):
        return
    
    console.print()
    
    if selected_backend in ["openrouter", "openai", "anthropic"]:
        api_key = Prompt.ask(
            f"{selected_backend.title()} API key",
            default=cfg.get_backend_config(selected_backend).api_key or "",
            password=True
        )
        if api_key:
            cfg.set_backend_config(selected_backend, BackendConfig(api_key=api_key))
            console.print(f"[green]✓ {selected_backend.title()} API key saved[/green]")
    else:
        default_url = "http://localhost:1234/v1" if selected_backend == "lmstudio" else "http://localhost:11434"
        base_url = Prompt.ask(
            f"{selected_backend.title()} server URL",
            default=cfg.get_backend_config(selected_backend).base_url or default_url
        )
        cfg.set_backend_config(selected_backend, BackendConfig(base_url=base_url))
        console.print(f"[green]✓ {selected_backend.title()} URL saved[/green]")
    
    if Confirm.ask(f"Set {selected_backend} as default backend?", default=True):
        cfg.defaults.backend = selected_backend
        cfg.save()
        console.print(f"[green]✓ Default backend set to {selected_backend}[/green]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def configure_judge() -> None:
    """Configure the judge model and backend."""
    console.print()
    cfg = Config.load()
    
    # Judge model selection
    console.print("[bold]Judge Model Configuration[/bold]")
    console.print("[dim]openai/gpt-oss-20b is the standard judge for consistent scoring.[/dim]")
    console.print()
    
    judge_models = [
        ("openai/gpt-oss-20b", "openai/gpt-oss-20b (recommended)"),
    ]
    
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("#", style="bold green", width=3)
    table.add_column("Model", style="cyan")
    
    for i, (key, name) in enumerate(judge_models, 1):
        marker = " ← current" if key == cfg.defaults.judge_model else ""
        table.add_row(str(i), name + marker)
    table.add_row("2", "Custom model...")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("Select judge model", default="1")
    
    try:
        judge_idx = int(choice) - 1
        if judge_idx == 1:
            custom_judge = Prompt.ask("Enter custom judge model name")
            cfg.defaults.judge_model = custom_judge
        elif 0 <= judge_idx < len(judge_models):
            cfg.defaults.judge_model = judge_models[judge_idx][0]
        console.print(f"[green]✓ Judge model set to: {cfg.defaults.judge_model}[/green]")
    except (ValueError, IndexError):
        console.print("[yellow]No changes made to judge model[/yellow]")
    
    console.print()
    
    # Judge backend selection
    console.print("[bold]Judge Backend Configuration[/bold]")
    console.print("[dim]You can run the judge locally (lmstudio/ollama) to save tokens, while testing models on Open Router.[/dim]")
    console.print()
    
    judge_backend_options = [
        ("auto-detect", "auto-detect (use same as test backend, or openrouter if test is local)"),
        ("lmstudio", "lmstudio (local)"),
        ("ollama", "ollama (local)"),
        ("openrouter", "openrouter"),
        ("openai", "openai"),
        ("anthropic", "anthropic"),
    ]
    
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("#", style="bold green", width=3)
    table.add_column("Backend", style="cyan")
    
    for i, (key, name) in enumerate(judge_backend_options, 1):
        current_backend = cfg.defaults.judge_backend or "auto-detect"
        marker = " ← current" if key == current_backend else ""
        table.add_row(str(i), name + marker)
    
    console.print(table)
    console.print()
    
    judge_backend_choice = Prompt.ask("Select judge backend (number)", default="1")
    
    try:
        judge_backend_idx = int(judge_backend_choice) - 1
        if 0 <= judge_backend_idx < len(judge_backend_options):
            selected_backend = judge_backend_options[judge_backend_idx][0]
            if selected_backend == "auto-detect":
                cfg.defaults.judge_backend = None
                console.print("[green]✓ Judge backend set to: auto-detect[/green]")
            else:
                cfg.defaults.judge_backend = selected_backend
                console.print(f"[green]✓ Judge backend set to: {selected_backend}[/green]")
        else:
            console.print("[yellow]No changes made to judge backend[/yellow]")
    except (ValueError, IndexError):
        console.print("[yellow]No changes made to judge backend[/yellow]")
    
    cfg.save()
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def view_config() -> None:
    """View the current configuration."""
    console.print()
    cfg = Config.load()
    
    config_path = get_config_dir() / "config.json"
    
    backends_str = "\n".join([
        f"  {name}: {'API key set' if bc.api_key else bc.base_url or 'configured'}"
        for name, bc in cfg.backends.items()
    ]) if cfg.backends else "  [dim]None configured[/dim]"
    
    judge_backend_display = cfg.defaults.judge_backend or "auto-detect"
    
    console.print(Panel(
        f"[bold]Configuration File:[/bold] {config_path}\n\n"
        f"[bold]Platform[/bold]\n"
        f"  API URL: {cfg.platform.url}\n"
        f"  API Key: {'*' * 20 if cfg.platform.api_key else '[dim]not set[/dim]'}\n\n"
        f"[bold]Defaults[/bold]\n"
        f"  Backend: {cfg.defaults.backend}\n"
        f"  Judge Model: {cfg.defaults.judge_model}\n"
        f"  Judge Backend: {judge_backend_display}\n\n"
        f"[bold]Configured Backends[/bold]\n{backends_str}",
        border_style="blue"
    ))
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def reset_config() -> None:
    """Reset all configuration settings."""
    console.print()
    
    if Confirm.ask("[red]Are you sure you want to reset all settings?[/red]", default=False):
        config_path = get_config_dir() / "config.json"
        if config_path.exists():
            config_path.unlink()
        console.print("[green]✓ Configuration reset to defaults[/green]")
    else:
        console.print("[yellow]Reset cancelled[/yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def reset_database() -> None:
    """Reset the results database."""
    console.print()
    
    from gcb_runner.config import get_data_dir
    
    db_path = get_data_dir() / "results.db"
    
    if not db_path.exists():
        console.print("[yellow]No results database found. Nothing to reset.[/yellow]")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
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
    
    if not Confirm.ask("[red]Are you sure you want to delete all test data?[/red]", default=False):
        console.print("[yellow]Reset cancelled.[/yellow]")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    # Delete the database file
    try:
        db_path.unlink()
        console.print("[green]✓ Database deleted successfully.[/green]")
        console.print()
        console.print("[dim]A new database will be created automatically when you run your next test.[/dim]")
    except Exception as e:
        console.print(f"[red]Error deleting database: {e}[/red]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


# ============================================================================
# Run Test Menu
# ============================================================================

def run_test_menu() -> MenuAction:
    """Interactive test runner menu."""
    clear_screen()
    print_header()
    
    cfg = Config.load()
    
    # Check prerequisites
    if not cfg.platform.api_key:
        console.print(Panel(
            "[red]Platform API key not configured![/red]\n\n"
            "You need a Platform API key to download benchmark questions.\n\n"
            "Get your API key from:\n"
            "https://greatcommissionbenchmark.ai/dashboard",
            border_style="red"
        ))
        console.print()
        if Confirm.ask("Would you like to configure it now?", default=True):
            configure_platform_key()
            cfg = Config.load()
            if not cfg.platform.api_key:
                return MenuAction.BACK
        else:
            return MenuAction.BACK
    
    backend = cfg.defaults.backend
    backend_cfg = cfg.get_backend_config(backend)
    
    if backend in ["openrouter", "openai", "anthropic"] and not backend_cfg.api_key:
        console.print(Panel(
            f"[red]{backend.title()} API key not configured![/red]\n\n"
            f"You need a {backend.title()} API key to run tests.",
            border_style="red"
        ))
        console.print()
        if Confirm.ask("Would you like to configure it now?", default=True):
            configure_backend()
            cfg = Config.load()
        else:
            return MenuAction.BACK
    
    clear_screen()
    print_header()
    
    console.print("[bold cyan]🧪 Run Benchmark Test[/bold cyan]")
    console.print()
    show_status_panel(cfg)
    
    # Get test parameters
    console.print("[bold]Test Configuration:[/bold]")
    console.print()
    
    model = Prompt.ask(
        "Model to test",
        default="gpt-4o" if backend in ["openrouter", "openai"] else "llama3.2"
    )
    
    # Version selection
    benchmark_version: str | None = None
    is_draft_version: bool = False
    use_specific_version = Confirm.ask("Use a specific benchmark version?", default=False)
    if use_specific_version:
        console.print()
        include_drafts = Confirm.ask("Include draft versions for testing?", default=False)
        console.print("[dim]Fetching available versions...[/dim]")
        versions, error = fetch_versions_sync(cfg, include_drafts=include_drafts)
        if versions:
            console.print()
            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("#", style="bold green", width=3)
            table.add_column("Version", style="cyan")
            table.add_column("Status")
            table.add_column("Questions", justify="right")
            
            for i, v in enumerate(versions, 1):
                status_raw = v.get("status", "")
                # Map status to display with icons
                if status_raw == "current":
                    status = "[green]⭐ Current[/green]"
                elif status_raw == "draft":
                    status = "[yellow]🔨 Draft[/yellow]"
                elif status_raw == "locked":
                    status = "[blue]🔒 Locked[/blue]"
                elif status_raw == "archived":
                    status = "[dim]📦 Archived[/dim]"
                else:
                    status = status_raw
                table.add_row(
                    str(i),
                    f"{v.get('marketing_version', '')} ({v.get('semantic_version', '')})",
                    status,
                    str(v.get("question_count", "?"))
                )
            
            console.print(table)
            if include_drafts:
                console.print()
                console.print("[yellow]⚠️  Draft versions are for testing only - results won't be published to leaderboard[/yellow]")
            console.print()
            
            version_choice = Prompt.ask("Select version number (or press Enter for current)", default="")
            if version_choice:
                try:
                    idx = int(version_choice) - 1
                    if 0 <= idx < len(versions):
                        benchmark_version = versions[idx].get("semantic_version")
                        is_draft_version = versions[idx].get("is_draft", False)
                        console.print(f"[green]✓ Selected version: {benchmark_version}[/green]")
                        if is_draft_version:
                            console.print("[yellow]  (draft version - for testing only)[/yellow]")
                except (ValueError, IndexError):
                    console.print("[yellow]Invalid selection, using current version[/yellow]")
        else:
            console.print(f"[yellow]Could not fetch versions: {error}[/yellow]")
            console.print("[dim]Using current version[/dim]")
    
    console.print()
    console.print("[bold]Test Summary:[/bold]")
    console.print(f"  Model: [cyan]{model}[/cyan]")
    console.print(f"  Backend: [cyan]{backend}[/cyan]")
    console.print(f"  Version: [cyan]{benchmark_version or 'current'}[/cyan]")
    judge_display = cfg.defaults.judge_model
    if cfg.defaults.judge_backend:
        judge_display += f" (via {cfg.defaults.judge_backend})"
    console.print(f"  Judge: [cyan]{judge_display}[/cyan]")
    console.print()
    
    if not Confirm.ask("Start the benchmark?", default=True):
        return MenuAction.BACK
    
    # Build and show the command
    cmd_parts = ["gcb-runner", "test", "--model", model, "--backend", backend]
    if benchmark_version:
        cmd_parts.extend(["--benchmark-version", benchmark_version])
    
    console.print()
    console.print("[dim]Running command:[/dim]")
    console.print(f"[cyan]{' '.join(cmd_parts)}[/cyan]")
    console.print()
    
    # Import and run the test
    import asyncio

    from gcb_runner.runner import run_benchmark
    
    try:
        asyncio.run(run_benchmark(
            model=model,
            backend=backend,
            benchmark_version=benchmark_version,
            judge_model=cfg.defaults.judge_model,
            judge_backend=cfg.defaults.judge_backend,
            config=cfg,
            output_path=None,
            resume=False,
            is_draft=is_draft_version,
        ))
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error running test: {e}[/red]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to return to main menu[/dim]", default="")
    return MenuAction.BACK


def fetch_versions_sync(cfg: Config, include_drafts: bool = False) -> tuple[list[dict[str, Any]], str | None]:
    """Fetch available versions synchronously.
    
    Args:
        cfg: Configuration object
        include_drafts: If True, include draft and locked versions for testing
    
    Returns:
        Tuple of (versions list, error message or None)
    """
    import asyncio

    from gcb_runner.api.client import PlatformAPIClient, PlatformAPIError
    
    async def _fetch() -> tuple[list[dict[str, Any]], str | None]:
        if not cfg.platform.api_key:
            return [], "Platform API key not configured"
        
        client = PlatformAPIClient(cfg.platform.api_key, cfg.platform.url)
        try:
            result = await client.list_versions(include_drafts=include_drafts)
            return result.get("versions", []), None
        except PlatformAPIError as e:
            return [], str(e)
        except Exception as e:
            return [], f"Unexpected error: {e}"
        finally:
            await client.close()
    
    return asyncio.run(_fetch())


# ============================================================================
# Results Menu
# ============================================================================

def results_menu() -> MenuAction:
    """View and manage test results."""
    while True:
        clear_screen()
        print_header()
        
        print_menu("📊 Results", [
            ("1", "View Recent Runs"),
            ("2", "View Run Details"),
            ("3", "Launch Web Dashboard"),
            ("4", "Generate HTML Report"),
            ("5", "Export Results (JSON)"),
        ])
        
        choice = get_choice(["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            return MenuAction.BACK
        elif choice == "1":
            view_recent_runs()
        elif choice == "2":
            view_run_details()
        elif choice == "3":
            launch_dashboard()
        elif choice == "4":
            generate_report()
        elif choice == "5":
            export_results()


def view_recent_runs() -> None:
    """Show list of recent test runs."""
    console.print()
    
    from gcb_runner.results import ResultsDB
    
    try:
        db = ResultsDB()
        runs = db.list_runs(limit=10)
        
        if not runs:
            console.print("[dim]No test runs found. Run 'gcb-runner test' to get started.[/dim]")
        else:
            table = Table(title="Recent Test Runs", box=box.ROUNDED)
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
    except Exception as e:
        console.print(f"[red]Error loading results: {e}[/red]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def view_run_details() -> None:
    """View details of a specific run."""
    console.print()
    
    run_id_str = Prompt.ask("Enter run ID to view")
    
    try:
        run_id = int(run_id_str)
    except ValueError:
        console.print("[red]Invalid run ID[/red]")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    from gcb_runner.results import ResultsDB
    
    try:
        db = ResultsDB()
        run = db.get_run(run_id)
        
        if not run:
            console.print(f"[red]Test run #{run_id} not found.[/red]")
        else:
            console.print()
            console.print(f"[bold]Test Run #{run.id} - {run.model}[/bold]")
            console.print()
            
            table = Table(box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value")
            
            table.add_row("Model", run.model)
            table.add_row("Backend", run.backend)
            table.add_row("Benchmark Version", run.benchmark_version)
            table.add_row("Judge Model", run.judge_model)
            if getattr(run, 'judge_backend', None):
                table.add_row("Judge Backend", run.judge_backend)
            table.add_row("Score", f"[bold green]{run.score:.1f}[/bold green]" if run.score else "-")
            table.add_row("Status", "Completed" if run.completed_at else "In Progress")
            
            console.print(table)
    except Exception as e:
        console.print(f"[red]Error loading run: {e}[/red]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def launch_dashboard() -> None:
    """Launch the web dashboard."""
    console.print()
    
    import webbrowser

    from gcb_runner.config import get_data_dir
    
    db_path = get_data_dir() / "results.db"
    
    if not db_path.exists():
        console.print("[red]No results database found.[/red]")
        console.print("Run a test first to generate results.")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    port = IntPrompt.ask("Server port", default=8642)
    
    console.print()
    console.print(f"[green]Starting server at http://localhost:{port}[/green]")
    console.print("[dim]Press Ctrl+C to stop the server[/dim]")
    console.print()
    
    webbrowser.open(f"http://localhost:{port}")
    
    from gcb_runner.viewer.server import start_viewer
    
    try:
        start_viewer(db_path, port=port, open_browser=False)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def generate_report() -> None:
    """Generate an HTML report."""
    console.print()
    
    run_id_str = Prompt.ask("Enter run ID (leave empty for latest)", default="")
    
    from gcb_runner.config import get_data_dir
    from gcb_runner.results import ResultsDB
    
    db = ResultsDB()
    
    if not run_id_str:
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
            return
        run_id = runs[0].id
    else:
        try:
            run_id = int(run_id_str)
        except ValueError:
            console.print("[red]Invalid run ID[/red]")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
            return
    
    run = db.get_run(run_id)
    if not run:
        console.print(f"[red]Test run #{run_id} not found.[/red]")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    from datetime import datetime as dt

    date_str = run.completed_at.strftime("%Y-%m-%d") if run.completed_at else dt.now().strftime("%Y-%m-%d")
    model_name = run.model.replace("/", "-").replace(":", "-")
    default_output = f"gcb-report-{model_name}-{date_str}.html"
    
    output_file = Prompt.ask("Output filename", default=default_output)
    output_path = Path(output_file)
    
    console.print()
    console.print(f"Generating report for test run #{run_id}...")
    
    from gcb_runner.viewer.report import generate_report as gen_report
    
    db_path = get_data_dir() / "results.db"
    gen_report(db_path, run_id, output_path)
    
    console.print(f"[green]✓ Report saved to {output_path}[/green]")
    
    if Confirm.ask("Open in browser?", default=True):
        import webbrowser
        webbrowser.open(f"file://{output_path.absolute()}")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def export_results() -> None:
    """Export results to JSON."""
    console.print()
    
    run_id_str = Prompt.ask("Enter run ID (leave empty for latest)", default="")
    
    from gcb_runner.export import export_run
    from gcb_runner.results import ResultsDB
    
    db = ResultsDB()
    
    if not run_id_str:
        runs = db.list_runs(limit=1)
        if not runs:
            console.print("[red]No test runs found.[/red]")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
            return
        run_id = runs[0].id
    else:
        try:
            run_id = int(run_id_str)
        except ValueError:
            console.print("[red]Invalid run ID[/red]")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
            return
    
    run = db.get_run(run_id)
    if not run:
        console.print(f"[red]Test run #{run_id} not found.[/red]")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    if not run.completed_at:
        console.print(f"[red]Test run #{run_id} is not complete.[/red]")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    # Generate default path from model name (exports to current directory)
    model_name = run.model.replace("/", "-").replace(":", "-")
    default_path = Path(f"{model_name}.json")
    
    output_file = Prompt.ask("Output path", default=str(default_path))
    output_path = Path(output_file)
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print()
    console.print(f"Exporting test run #{run_id}...")
    
    export_data = export_run(db, run_id)
    output_path.write_text(export_data)
    
    console.print(f"[green]✓ Exported to {output_path}[/green]")
    console.print()
    console.print("File ready for upload at https://greatcommissionbenchmark.ai/submit")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


# ============================================================================
# Help Menu
# ============================================================================

def help_menu() -> MenuAction:
    """Display help and documentation."""
    while True:
        clear_screen()
        print_header()
        
        print_menu("❓ Help & Documentation", [
            ("1", "Quick Start Guide"),
            ("2", "Understanding Scores"),
            ("3", "Backend Setup"),
            ("4", "Command Reference"),
            ("5", "About GCB"),
        ])
        
        choice = get_choice(["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            return MenuAction.BACK
        elif choice == "1":
            show_quick_start()
        elif choice == "2":
            show_scoring_info()
        elif choice == "3":
            show_backend_info()
        elif choice == "4":
            show_command_reference()
        elif choice == "5":
            show_about()


def show_quick_start() -> None:
    """Show quick start guide."""
    console.print()
    console.print(Panel(
        "[bold cyan]Quick Start Guide[/bold cyan]\n\n"
        "[bold]1. Get API Keys[/bold]\n"
        "   • Platform API key: https://greatcommissionbenchmark.ai/dashboard\n"
        "   • Backend API key: OpenRouter, OpenAI, or Anthropic\n\n"
        "[bold]2. Configure GCB Runner[/bold]\n"
        "   Run the setup wizard from this menu, or use:\n"
        "   [cyan]gcb-runner config[/cyan]\n\n"
        "[bold]3. Run Your First Test[/bold]\n"
        "   [cyan]gcb-runner test --model gpt-4o[/cyan]\n\n"
        "[bold]4. View Results[/bold]\n"
        "   • CLI: [cyan]gcb-runner results[/cyan]\n"
        "   • Web: [cyan]gcb-runner view[/cyan]\n\n"
        "[bold]5. Submit to Leaderboard[/bold]\n"
        "   [cyan]gcb-runner upload --run <ID>[/cyan]",
        border_style="blue"
    ))
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_scoring_info() -> None:
    """Show scoring methodology."""
    console.print()
    console.print(Panel(
        "[bold cyan]Understanding GCB Scores[/bold cyan]\n\n"
        "The benchmark uses a weighted tier system with unified verdicts:\n\n"
        "[bold]Verdict Categories (all tiers)[/bold]\n"
        "• ACCEPTED = Full pass (task completed faithfully)\n"
        "• COMPROMISED = Partial pass (task completed with caveats)\n"
        "• REFUSED = Fail (task declined or contradicted)\n\n"
        "[bold]Tier 1: Task Capability (70%)[/bold]\n"
        "Can the model complete ministry tasks?\n\n"
        "[bold]Tier 2: Doctrinal Fidelity (20%)[/bold]\n"
        "Does it maintain orthodox teaching?\n\n"
        "[bold]Tier 3: Worldview Confession (10%)[/bold]\n"
        "Does it affirm Christian worldview?\n\n"
        "[bold]Final Score[/bold] = (T1 × 0.70) + (T2 × 0.20) + (T3 × 0.10)",
        border_style="blue"
    ))
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_backend_info() -> None:
    """Show backend setup information."""
    console.print()
    console.print(Panel(
        "[bold cyan]Backend Setup[/bold cyan]\n\n"
        "[bold]Cloud Backends[/bold]\n\n"
        "• [cyan]OpenRouter[/cyan] (recommended)\n"
        "  Access 100+ models with one API key\n"
        "  https://openrouter.ai/keys\n\n"
        "• [cyan]OpenAI[/cyan]\n"
        "  Direct access to GPT models\n"
        "  https://platform.openai.com/api-keys\n\n"
        "• [cyan]Anthropic[/cyan]\n"
        "  Direct access to Claude models\n"
        "  https://console.anthropic.com/settings/keys\n\n"
        "[bold]Local Backends[/bold]\n\n"
        "• [cyan]LM Studio[/cyan]\n"
        "  1. Download from https://lmstudio.ai/\n"
        "  2. Load a model and start local server\n"
        "  3. Default URL: http://localhost:1234/v1\n\n"
        "• [cyan]Ollama[/cyan]\n"
        "  1. Install from https://ollama.ai/\n"
        "  2. Pull a model: ollama pull llama3.2\n"
        "  3. Default URL: http://localhost:11434",
        border_style="blue"
    ))
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_command_reference() -> None:
    """Show CLI command reference."""
    console.print()
    
    table = Table(title="Command Reference", box=box.ROUNDED)
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    
    commands = [
        ("gcb-runner", "Show this interactive menu"),
        ("gcb-runner config", "Configure API keys and preferences"),
        ("gcb-runner test --model <model>", "Run benchmark against a model"),
        ("gcb-runner results", "List recent test runs"),
        ("gcb-runner results --run <id>", "View specific run details"),
        ("gcb-runner view", "Launch web dashboard"),
        ("gcb-runner report", "Generate HTML report"),
        ("gcb-runner export --run <id>", "Export results to JSON"),
        ("gcb-runner upload --run <id>", "Upload results to platform"),
        ("gcb-runner versions", "List benchmark versions"),
    ]
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    
    console.print(table)
    console.print()
    console.print("[dim]For full documentation: https://greatcommissionbenchmark.ai/docs/runner[/dim]")
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_about() -> None:
    """Show about information."""
    console.print()
    console.print(Panel(
        "[bold cyan]About Great Commission Benchmark[/bold cyan]\n\n"
        "The Great Commission Benchmark (GCB) evaluates AI language models\n"
        "for their suitability in Christian ministry contexts.\n\n"
        "[bold]Our Mission[/bold]\n"
        "To provide the Christian community with reliable, transparent\n"
        "assessments of AI tools for ministry use.\n\n"
        "[bold]What We Measure[/bold]\n"
        "• Can the model help with ministry tasks?\n"
        "• Does it maintain doctrinal faithfulness?\n"
        "• Will it affirm a Christian worldview?\n\n"
        "[bold]Links[/bold]\n"
        "• Website: https://greatcommissionbenchmark.ai\n"
        "• Leaderboard: https://greatcommissionbenchmark.ai/leaderboard\n"
        "• Documentation: https://greatcommissionbenchmark.ai/docs\n"
        "• GitHub: https://github.com/great-commission-benchmark\n\n"
        f"[dim]GCB Runner v{__version__}[/dim]",
        border_style="blue"
    ))
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


# ============================================================================
# Diagnostics Menu
# ============================================================================

def diagnostics_menu() -> MenuAction:
    """Run diagnostics and connection tests."""
    while True:
        clear_screen()
        print_header()
        
        print_menu("🔧 Diagnostics & Connection Test", [
            ("1", "Run Full Diagnostics"),
            ("2", "Test Platform API Connection"),
            ("3", "Test Backend Connection"),
            ("4", "List Available Versions"),
            ("5", "Test Question Download"),
            ("6", "View API Endpoints"),
        ])
        
        choice = get_choice(["0", "1", "2", "3", "4", "5", "6"])
        
        if choice == "0":
            return MenuAction.BACK
        elif choice == "1":
            run_full_diagnostics()
        elif choice == "2":
            test_platform_connection()
        elif choice == "3":
            test_backend_connection()
        elif choice == "4":
            list_versions_diagnostic()
        elif choice == "5":
            test_question_download()
        elif choice == "6":
            view_api_endpoints()


def run_full_diagnostics() -> None:
    """Run complete diagnostic tests."""
    import asyncio
    
    clear_screen()
    print_header()
    
    console.print("[bold cyan]🔧 Running Full Diagnostics[/bold cyan]")
    console.print()
    
    cfg = Config.load()
    results: list[tuple[str, bool | None, str]] = []
    
    # Test 1: Configuration
    console.print("[bold]1. Configuration Check[/bold]")
    if cfg.platform.api_key:
        console.print("   ✅ Platform API key: Configured")
        results.append(("Platform API Key", True, "Configured"))
    else:
        console.print("   ❌ Platform API key: [red]Not configured[/red]")
        results.append(("Platform API Key", False, "Not configured"))
    
    backend = cfg.defaults.backend
    backend_cfg = cfg.get_backend_config(backend)
    
    if backend in ["lmstudio", "ollama"]:
        url = backend_cfg.base_url or ("http://localhost:1234/v1" if backend == "lmstudio" else "http://localhost:11434")
        console.print(f"   ✅ Backend ({backend}): {url}")
        results.append((f"Backend ({backend})", True, url))
    elif backend_cfg.api_key:
        console.print(f"   ✅ Backend ({backend}): API key configured")
        results.append((f"Backend ({backend})", True, "API key configured"))
    else:
        console.print(f"   ❌ Backend ({backend}): [red]API key not configured[/red]")
        results.append((f"Backend ({backend})", False, "API key not configured"))
    
    console.print()
    
    # Test 2: Platform API Connection
    console.print("[bold]2. Platform API Connection[/bold]")
    console.print(f"   URL: {cfg.platform.url}")
    
    if cfg.platform.api_key:
        with console.status("   Testing connection..."):
            api_result = asyncio.run(test_platform_api(cfg))
        
        if api_result["success"]:
            console.print("   ✅ Connection: [green]Success[/green]")
            console.print(f"   ✅ Response time: {api_result.get('response_time_ms', '?')}ms")
            results.append(("Platform API", True, f"{api_result.get('response_time_ms', '?')}ms"))
        else:
            console.print("   ❌ Connection: [red]Failed[/red]")
            console.print(f"   ❌ Error: {api_result.get('error', 'Unknown error')}")
            results.append(("Platform API", False, api_result.get('error', 'Unknown error')))
    else:
        console.print("   ⚠️  Skipped (no API key)")
        results.append(("Platform API", None, "Skipped - no API key"))
    
    console.print()
    
    # Test 3: Versions Endpoint
    console.print("[bold]3. Versions Endpoint[/bold]")
    
    if cfg.platform.api_key:
        with console.status("   Fetching versions..."):
            versions_result = asyncio.run(test_versions_endpoint(cfg))
        
        if versions_result["success"]:
            versions = versions_result.get("versions", [])
            current = versions_result.get("current_version")
            
            if len(versions) == 0:
                console.print("   ⚠️  Versions found: 0")
                console.print("   ⚠️  [yellow]No published versions available[/yellow]")
                console.print("   [dim]Note: Question sets must be published (status='active')[/dim]")
                console.print("   [dim]via Admin → Versions → Publish to be visible here.[/dim]")
                results.append(("Versions Endpoint", True, "0 versions (none published)"))
            else:
                console.print(f"   ✅ Versions found: {len(versions)}")
                console.print(f"   ✅ Current version: {current or 'None'}")
                results.append(("Versions Endpoint", True, f"{len(versions)} versions"))
        else:
            console.print(f"   ❌ Failed: {versions_result.get('error', 'Unknown error')}")
            results.append(("Versions Endpoint", False, versions_result.get('error', 'Unknown error')))
    else:
        console.print("   ⚠️  Skipped (no API key)")
        results.append(("Versions Endpoint", None, "Skipped"))
    
    console.print()
    
    # Test 4: Questions Endpoint
    console.print("[bold]4. Questions Endpoint[/bold]")
    
    if cfg.platform.api_key:
        with console.status("   Testing questions endpoint..."):
            questions_result = asyncio.run(test_questions_endpoint(cfg))
        
        if questions_result["success"]:
            count = questions_result.get("question_count", 0)
            version = questions_result.get("version", "?")
            console.print(f"   ✅ Questions available: {count}")
            console.print(f"   ✅ Version: {version}")
            tier_counts = questions_result.get("tier_counts", {})
            if tier_counts:
                console.print(f"   ✅ Tier 1: {tier_counts.get(1, 0)}, Tier 2: {tier_counts.get(2, 0)}, Tier 3: {tier_counts.get(3, 0)}")
            results.append(("Questions Endpoint", True, f"{count} questions"))
        else:
            console.print(f"   ❌ Failed: {questions_result.get('error', 'Unknown error')}")
            results.append(("Questions Endpoint", False, questions_result.get('error', 'Unknown error')))
    else:
        console.print("   ⚠️  Skipped (no API key)")
        results.append(("Questions Endpoint", None, "Skipped"))
    
    console.print()
    
    # Test 5: Backend Connection (for local backends)
    console.print("[bold]5. Backend Connection[/bold]")
    
    if backend in ["lmstudio", "ollama"]:
        with console.status(f"   Testing {backend} connection..."):
            backend_result = asyncio.run(test_local_backend(cfg, backend))
        
        if backend_result["success"]:
            console.print(f"   ✅ {backend.title()}: [green]Connected[/green]")
            if backend_result.get("models"):
                console.print(f"   ✅ Available models: {len(backend_result['models'])}")
            results.append((f"{backend.title()} Backend", True, "Connected"))
        else:
            console.print(f"   ❌ {backend.title()}: [red]Not reachable[/red]")
            console.print(f"   ❌ Error: {backend_result.get('error', 'Unknown error')}")
            results.append((f"{backend.title()} Backend", False, backend_result.get('error', 'Connection failed')))
    else:
        console.print(f"   ℹ️  Using cloud backend ({backend})")
        results.append((f"{backend.title()} Backend", True, "Cloud backend"))
    
    console.print()
    
    # Summary
    console.print("═" * 50)
    console.print()
    
    passed = sum(1 for _, success, _ in results if success is True)
    failed = sum(1 for _, success, _ in results if success is False)
    skipped = sum(1 for _, success, _ in results if success is None)
    
    if failed == 0:
        console.print(f"[bold green]✅ All checks passed! ({passed} passed, {skipped} skipped)[/bold green]")
    else:
        console.print(f"[bold yellow]⚠️  Some checks failed: {passed} passed, {failed} failed, {skipped} skipped[/bold yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


async def test_platform_api(cfg: Config) -> dict[str, Any]:
    """Test basic platform API connectivity."""
    import time

    import httpx
    
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try health endpoint first (no auth required)
            response = await client.get(f"{cfg.platform.url}/api/health")
            elapsed = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                return {"success": True, "response_time_ms": elapsed}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except httpx.RequestError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def test_versions_endpoint(cfg: Config, include_drafts: bool = False) -> dict[str, Any]:
    """Test the versions endpoint.
    
    Args:
        cfg: Configuration object
        include_drafts: If True, include draft and locked versions for testing
    """
    from gcb_runner.api.client import PlatformAPIClient
    
    client = PlatformAPIClient(cfg.platform.api_key or "", cfg.platform.url)
    try:
        result = await client.list_versions(include_drafts=include_drafts)
        return {
            "success": True,
            "versions": result.get("versions", []),
            "current_version": result.get("current_version")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await client.close()


async def test_questions_endpoint(cfg: Config, version: str | None = None) -> dict[str, Any]:
    """Test the questions endpoint."""
    from gcb_runner.api.client import PlatformAPIClient
    
    client = PlatformAPIClient(cfg.platform.api_key or "", cfg.platform.url)
    try:
        result = await client.get_questions(version or "current")
        questions = result.get("questions", [])
        
        tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
        for q in questions:
            tier = q.get("tier", 1)
            if tier in tier_counts:
                tier_counts[tier] += 1
        
        return {
            "success": True,
            "question_count": len(questions),
            "version": result.get("version"),
            "tier_counts": tier_counts
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await client.close()


async def test_local_backend(cfg: Config, backend: str) -> dict[str, Any]:
    """Test connection to a local backend."""
    import httpx
    
    backend_cfg = cfg.get_backend_config(backend)
    
    if backend == "lmstudio":
        base_url = backend_cfg.base_url or "http://localhost:1234/v1"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/models")
                if response.status_code == 200:
                    data: dict[str, Any] = response.json()
                    models = data.get("data", [])
                    return {"success": True, "models": [m.get("id") for m in models]}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    elif backend == "ollama":
        base_url = backend_cfg.base_url or "http://localhost:11434"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    return {"success": True, "models": [m.get("name") for m in models]}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Unknown backend"}


def test_platform_connection() -> None:
    """Test Platform API connection only."""
    import asyncio
    
    console.print()
    cfg = Config.load()
    
    if not cfg.platform.api_key:
        console.print("[red]Platform API key not configured![/red]")
        console.print("Run setup wizard or configure the API key first.")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    console.print(f"[bold]Testing connection to:[/bold] {cfg.platform.url}")
    console.print()
    
    with console.status("Connecting..."):
        result = asyncio.run(test_platform_api(cfg))
    
    if result["success"]:
        console.print("[green]✅ Connection successful![/green]")
        console.print(f"   Response time: {result.get('response_time_ms', '?')}ms")
    else:
        console.print("[red]❌ Connection failed[/red]")
        console.print(f"   Error: {result.get('error', 'Unknown error')}")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def test_backend_connection() -> None:
    """Test backend connection."""
    import asyncio
    
    console.print()
    cfg = Config.load()
    backend = cfg.defaults.backend
    backend_cfg = cfg.get_backend_config(backend)
    
    console.print(f"[bold]Testing backend:[/bold] {backend}")
    
    if backend in ["lmstudio", "ollama"]:
        url = backend_cfg.base_url or ("http://localhost:1234/v1" if backend == "lmstudio" else "http://localhost:11434")
        console.print(f"[bold]URL:[/bold] {url}")
        console.print()
        
        with console.status("Connecting..."):
            result = asyncio.run(test_local_backend(cfg, backend))
        
        if result["success"]:
            console.print("[green]✅ Connection successful![/green]")
            models = result.get("models", [])
            if models:
                console.print(f"   Available models: {len(models)}")
                for m in models[:5]:
                    console.print(f"     • {m}")
                if len(models) > 5:
                    console.print(f"     ... and {len(models) - 5} more")
        else:
            console.print("[red]❌ Connection failed[/red]")
            console.print(f"   Error: {result.get('error', 'Unknown error')}")
            console.print()
            console.print("[dim]Make sure the server is running:[/dim]")
            if backend == "lmstudio":
                console.print("  1. Open LM Studio")
                console.print("  2. Load a model")
                console.print("  3. Click 'Start Server' in the Local Server tab")
            else:
                console.print("  1. Run: ollama serve")
                console.print("  2. Pull a model: ollama pull llama3.2")
    else:
        if backend_cfg.api_key:
            console.print("[green]✅ API key configured[/green]")
            console.print("[dim]Cloud backends are tested when running a benchmark.[/dim]")
        else:
            console.print("[red]❌ API key not configured[/red]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def list_versions_diagnostic() -> None:
    """List available benchmark versions with details."""
    import asyncio
    
    console.print()
    cfg = Config.load()
    
    if not cfg.platform.api_key:
        console.print("[red]Platform API key not configured![/red]")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    include_drafts = Confirm.ask("Include draft versions?", default=True)
    console.print()
    console.print("[bold]Fetching benchmark versions...[/bold]")
    console.print()
    
    with console.status("Connecting to Platform API..."):
        result = asyncio.run(test_versions_endpoint(cfg, include_drafts=include_drafts))
    
    if result["success"]:
        versions = result.get("versions", [])
        current = result.get("current_version")
        
        if not versions:
            console.print("[yellow]No benchmark versions found.[/yellow]")
            console.print()
            console.print("[bold]Why?[/bold]")
            console.print("  Question sets must be published (status='active') to appear here.")
            console.print()
            console.print("[bold]To publish a version (requires admin access):[/bold]")
            console.print("  1. Go to Admin → Questions → Versions")
            console.print("  2. Create a question set if needed")
            console.print("  3. Add questions to the set")
            console.print("  4. Click 'Publish' on the version")
            console.print()
            console.print("[dim]Use --include-drafts to see draft versions for testing.[/dim]")
        else:
            title = "Available Benchmark Versions"
            if include_drafts:
                title += " (including drafts)"
            table = Table(title=title, box=box.ROUNDED)
            table.add_column("Version", style="cyan")
            table.add_column("Marketing", style="white")
            table.add_column("Status")
            table.add_column("Questions", justify="right")
            table.add_column("Released", style="dim")
            
            for v in versions:
                status_raw = v.get("status", "")
                if status_raw == "current":
                    status = "[green]⭐ Current[/green]"
                elif status_raw == "draft":
                    status = "[yellow]🔨 Draft[/yellow]"
                elif status_raw == "locked":
                    status = "[blue]🔒 Locked[/blue]"
                elif status_raw == "archived":
                    status = "[dim]📦 Archived[/dim]"
                else:
                    status = status_raw
                table.add_row(
                    v.get("semantic_version", "?"),
                    v.get("marketing_version", "?"),
                    status,
                    str(v.get("question_count", "?")),
                    v.get("release_date", "")[:10] if v.get("release_date") else ""
                )
            
            console.print(table)
            if include_drafts:
                console.print()
                console.print("[yellow]⚠️  Draft versions are for testing only - results won't be published to leaderboard[/yellow]")
            console.print()
            console.print(f"[dim]Current version: {current or 'None set'}[/dim]")
    else:
        console.print("[red]❌ Failed to fetch versions[/red]")
        console.print(f"   Error: {result.get('error', 'Unknown error')}")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def test_question_download() -> None:
    """Test downloading questions for a specific version."""
    import asyncio
    
    console.print()
    cfg = Config.load()
    
    if not cfg.platform.api_key:
        console.print("[red]Platform API key not configured![/red]")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    # First, get available versions
    console.print("[bold]Fetching available versions...[/bold]")
    
    with console.status("Connecting..."):
        versions_result = asyncio.run(test_versions_endpoint(cfg))
    
    if not versions_result["success"]:
        console.print(f"[red]Failed to fetch versions: {versions_result.get('error')}[/red]")
        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return
    
    versions = versions_result.get("versions", [])
    
    console.print()
    
    selected_version: str | None = None
    if versions:
        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("#", style="bold green", width=3)
        table.add_column("Version", style="cyan")
        table.add_column("Status")
        table.add_column("Questions", justify="right")
        
        for i, v in enumerate(versions, 1):
            status = "[green]✓ Current[/green]" if v.get("status") == "current" else v.get("status", "")
            table.add_row(
                str(i),
                v.get("semantic_version", "?"),
                status,
                str(v.get("question_count", "?"))
            )
        
        console.print(table)
        console.print()
        
        version_choice = Prompt.ask(
            "Select version to test (number, or 'current')",
            default="current"
        )
        
        if version_choice.lower() == "current":
            selected_version = None
        else:
            try:
                idx = int(version_choice) - 1
                if 0 <= idx < len(versions):
                    selected_version = versions[idx].get("semantic_version")
                else:
                    console.print("[red]Invalid selection[/red]")
                    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
                    return
            except ValueError:
                selected_version = version_choice  # Assume direct version string
    else:
        console.print("[yellow]No versions available, testing 'current'...[/yellow]")
        selected_version = None
    
    console.print()
    console.print(f"[bold]Testing question download for version: {selected_version or 'current'}[/bold]")
    console.print()
    
    with console.status("Downloading questions..."):
        result = asyncio.run(test_questions_endpoint(cfg, selected_version))
    
    if result["success"]:
        console.print("[green]✅ Questions downloaded successfully![/green]")
        console.print()
        console.print(f"   Version: {result.get('version', '?')}")
        console.print(f"   Total questions: {result.get('question_count', 0)}")
        
        tier_counts = result.get("tier_counts", {})
        if tier_counts:
            console.print()
            console.print("   [bold]Questions by tier:[/bold]")
            console.print(f"     Tier 1 (Use Cases): {tier_counts.get(1, 0)}")
            console.print(f"     Tier 2 (Theology):  {tier_counts.get(2, 0)}")
            console.print(f"     Tier 3 (Worldview): {tier_counts.get(3, 0)}")
    else:
        console.print("[red]❌ Failed to download questions[/red]")
        console.print(f"   Error: {result.get('error', 'Unknown error')}")
        console.print()
        
        error_msg = result.get('error', '').lower()
        if 'not found' in error_msg:
            console.print("[bold yellow]Root Cause:[/bold yellow]")
            console.print("  No published benchmark version exists on the platform.")
            console.print()
            console.print("[bold]To fix this (requires admin access):[/bold]")
            console.print("  1. Go to the Admin panel on the platform")
            console.print("  2. Navigate to Questions → Versions")
            console.print("  3. Create a question set if none exists")
            console.print("  4. Add questions to the question set")
            console.print("  5. Click 'Publish' to make it active")
            console.print()
            console.print("[dim]Only question sets with status 'active' are available via the API.[/dim]")
        else:
            console.print("[dim]Possible causes:[/dim]")
            console.print("  • Platform API is not responding")
            console.print("  • Network connectivity issue")
            console.print("  • Invalid API key")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def view_api_endpoints() -> None:
    """Show API endpoint information."""
    console.print()
    cfg = Config.load()
    
    console.print(Panel(
        "[bold cyan]API Endpoints[/bold cyan]\n\n"
        f"[bold]Platform API Base URL:[/bold]\n"
        f"  {cfg.platform.url}\n\n"
        "[bold]Runner Endpoints:[/bold]\n"
        f"  GET {cfg.platform.url}/api/runner/versions\n"
        "      List available benchmark versions\n\n"
        f"  GET {cfg.platform.url}/api/runner/questions?version=<version>\n"
        "      Download questions for a version\n\n"
        f"  GET {cfg.platform.url}/api/runner/judge-prompts?version=<version>\n"
        "      Get judge prompts for evaluation\n\n"
        "[bold]Health Check:[/bold]\n"
        f"  GET {cfg.platform.url}/api/health\n"
        "      Check if API is online\n\n"
        "[bold]Authentication:[/bold]\n"
        "  All /runner endpoints require X-API-Key header",
        border_style="blue"
    ))
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


# ============================================================================
# Utilities Menu
# ============================================================================

def utilities_menu() -> MenuAction:
    """Utilities and configuration menu."""
    while True:
        clear_screen()
        print_header()
        
        cfg = Config.load()
        show_status_panel(cfg)
        
        # Determine if setup is needed
        needs_setup = not cfg.platform.api_key
        
        print_menu("🔧 Utilities", [
            ("1", "🚀 Setup Wizard" + (" [yellow](recommended)[/yellow]" if needs_setup else "")),
            ("2", "🔑 Set Platform API Key"),
            ("3", "⚙️  Configure Backend"),
            ("4", "⚖️  Set Judge Model"),
            ("5", "📋 View Current Config"),
            ("6", "📊 View Recent Runs"),
            ("7", "🔍 View Run Details"),
            ("8", "📄 Generate HTML Report"),
            ("9", "🔧 Diagnostics & Connection Test"),
            ("10", "🔄 Reset All Settings"),
            ("11", "🗑️  Reset Results Database"),
        ])
        
        choice = get_choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])
        
        if choice == "0":
            return MenuAction.BACK
        elif choice == "1":
            setup_wizard()
        elif choice == "2":
            configure_platform_key()
        elif choice == "3":
            configure_backend()
        elif choice == "4":
            configure_judge()
        elif choice == "5":
            view_config()
        elif choice == "6":
            view_recent_runs()
        elif choice == "7":
            view_run_details()
        elif choice == "8":
            generate_report()
        elif choice == "9":
            diagnostics_menu()
        elif choice == "10":
            reset_config()
        elif choice == "11":
            reset_database()


# ============================================================================
# Main Menu
# ============================================================================

def main_menu() -> None:
    """Display the main interactive menu."""
    while True:
        clear_screen()
        print_header()
        
        cfg = Config.load()
        show_status_panel(cfg)
        
        # Determine if setup is needed
        needs_setup = not cfg.platform.api_key
        
        if needs_setup:
            console.print(Panel(
                "[yellow]⚠️  Setup incomplete![/yellow]\n"
                "Run the Setup Wizard from Utilities to configure GCB Runner.",
                border_style="yellow"
            ))
            console.print()
        
        print_menu("✝ Main Menu", [
            ("1", "🧪 Run Benchmark Test"),
            ("2", "🌐 Launch Web Results Dashboard"),
            ("3", "💾 Export Results (JSON)"),
            ("4", "🔧 Utilities"),
            ("5", "❓ Help & Documentation"),
        ], show_back=True)
        
        choice = get_choice(["0", "1", "2", "3", "4", "5", "q", "quit", "exit"])
        
        if choice in ["0", "q", "quit", "exit"]:
            clear_screen()
            console.print("[dim]Thanks for using GCB Runner. God bless![/dim]")
            console.print()
            break
        elif choice == "1":
            run_test_menu()
        elif choice == "2":
            launch_dashboard()
        elif choice == "3":
            export_results()
        elif choice == "4":
            utilities_menu()
        elif choice == "5":
            help_menu()


def run_menu() -> None:
    """Entry point for the interactive menu."""
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print()
        console.print("[dim]Goodbye![/dim]")
        sys.exit(0)
