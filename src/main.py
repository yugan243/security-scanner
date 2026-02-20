import typer
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from src.agents.workflow import create_workflow
from src.config import settings
from src.tools.git import clone_repo  # <-- NEW IMPORT

# Setup App
app = typer.Typer(help="AI-Powered Security Scanner")
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
        title="AI Security Assessment",
        style="blue"
    ))

    # Print Findings Table
    table = Table(title="Confirmed Vulnerabilities")
    table.add_column("Sev", style="red")
    table.add_column("Type", style="cyan")
    table.add_column("Location")
    table.add_column("Conf", justify="right")
    table.add_column("Status")

    for f in report_obj.findings:
        conf_color = "green" if f.confidence_score > 0.8 else "yellow"
        table.add_row(
            f.severity.value,
            f.vuln_type,
            f"{f.file_path}:{f.line_number}",
            f"[{conf_color}]{f.confidence_score:.2f}[/{conf_color}]",
            f.status.value
        )

    console.print(table)
    console.print(f"\nScan Complete. Total Issues: {report_obj.total_findings}")


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path or URL to the repository to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs")
):
    """
    Scans a local repository or remote Git URL for security vulnerabilities.
    """
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