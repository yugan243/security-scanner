import os
import typer
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from vigil.agents.workflow import create_workflow
from vigil.config import settings, reload_settings
from vigil.tools.git import clone_repo  
from vigil.core.models import FindingStatus
from vigil.setup_wizard import run_setup_wizard, is_configured

# Setup App
app = typer.Typer(
    name="vigil",
    help="🛡️ Vigil — AI-Powered Security Scanner",
    add_completion=False,
)
console = Console()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(settings.APP_NAME)

def run_workflow(repo_target: str, workflow):
    """Helper function to execute the graph and print the report."""
    inputs = {"repo_path": repo_target, "findings": [], "verified_findings": []}
    final_state = workflow.invoke(inputs)
    
    stats = final_state.get("scan_summary", {})
    report_obj = stats.get("report_object")
    
    if not report_obj:
        console.print("[red] Error: No report generated.[/red]")
        return

    # Print Executive Summary
    console.print("\n")
    console.print(Panel(
        Markdown(f"**CISO Executive Summary:**\n\n{report_obj.executive_summary}"),
        title="🛡️ Vigil Security Assessment",
        style="blue"
    ))

    # --- 1. FILTERING (The Bouncer) ---
    actionable_findings = [f for f in report_obj.findings if f.status in [FindingStatus.TRUE_POSITIVE, FindingStatus.NEEDS_REVIEW]]
    false_positives_blocked = len(report_obj.findings) - len(actionable_findings)

    # Print Findings Table
    table = Table(title="Actionable Vulnerabilities")
    table.add_column("Sev", style="red")
    table.add_column("Type", style="cyan")
    table.add_column("Location")
    table.add_column("Conf", justify="right")
    table.add_column("Status")

    # --- 2. CLEAN UP THE UI ---
    for f in actionable_findings:
        conf_color = "green" if f.confidence_score > 0.8 else "yellow"
        
        # Strip the long temporary path so it fits on screen
        try:
            clean_path = os.path.relpath(f.file_path, repo_target)
        except ValueError:
            clean_path = f.file_path
            
        display_location = f"{clean_path}:{f.line_number}"

        table.add_row(
            f.severity.value,
            f.vuln_type,
            display_location,
            f"[{conf_color}]{f.confidence_score:.2f}[/{conf_color}]",
            f.status.value
        )

    if actionable_findings:
        console.print(table)
    else:
        console.print("\n[bold green]No actionable vulnerabilities found! All warnings were filtered by AI.[/bold green]")

    # --- 3. THE SUPERVISOR METRIC ---
    console.print(f"\nScan Complete. Actionable Threats: [bold red]{len(actionable_findings)}[/bold red] | False Positives Blocked: [bold green]{false_positives_blocked}[/bold green]")


@app.command()
def init():
    """
    Configure Vigil's LLM provider and credentials.
    Run this to set up for the first time, or to change your LLM provider.
    """
    run_setup_wizard()
    reload_settings()


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path or URL to the repository to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs")
):
    """
    Scans a local repository or remote Git URL for security vulnerabilities.
    """
    # AUTO-DETECT: If not configured, handle appropriately
    if not is_configured():
        # Docker mode — can't run interactive wizard
        if os.environ.get("VIGIL_DOCKER"):
            console.print("[red]❌ No LLM configuration detected.[/red]\n")
            console.print("When running in Docker, pass your config as environment variables:\n")
            console.print("  [bold]docker run -e LLM_PROVIDER=groq -e GROQ_API_KEY=your_key \\[/bold]")
            console.print("  [bold]  vigil scan <repo-url>[/bold]\n")
            console.print("Supported providers: [cyan]groq[/cyan], [cyan]google[/cyan], [cyan]openai[/cyan], [cyan]ollama[/cyan]")
            raise typer.Exit(1)
        
        # Normal CLI — run interactive wizard
        console.print("[yellow]⚠️  No LLM configuration detected.[/yellow]\n")
        wizard_ok = run_setup_wizard()
        if not wizard_ok:
            console.print("[red]Setup cancelled. Cannot scan without an LLM provider.[/red]")
            raise typer.Exit(1)
        reload_settings()

    workflow = create_workflow()

    # ROUTING LOGIC: Remote URL vs Local Path
    is_url = path.startswith("http://") or path.startswith("https://")

    if is_url:
        console.print(Panel(f"Fetching Remote Repository: [bold]{path}[/bold]", style="cyan"))
        try:
            # The context manager handles cloning and automatic cleanup
            with clone_repo(path) as temp_dir:
                console.print(f"Starting Scan on temporary workspace...")
                run_workflow(repo_target=temp_dir, workflow=workflow)
        except Exception as e:
            console.print(f"[bold red]Failed to process remote repository:[/bold red] {e}")
    else:
        # Standard local scan
        console.print(Panel(f"Starting Local Scan on: [bold]{path}[/bold]", style="green"))
        try:
            run_workflow(repo_target=path, workflow=workflow)
        except Exception as e:
            console.print(f"[bold red]Fatal Error:[/bold red] {e}")


if __name__ == "__main__":
    app()